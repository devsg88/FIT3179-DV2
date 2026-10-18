# Australia on a Plate: code study guide

This document explains how the website and each active Vega-Lite chart work. It is written as a study guide rather than a line-by-line API reference.

## 1. How the project fits together

The basic flow is:

```text
index.html chart container
        ↓
visualisation.js matches the container to a .vg.json file
        ↓
vegaEmbed loads and compiles the Vega-Lite specification
        ↓
the specification loads a CSV or TopoJSON file
        ↓
Vega-Lite transforms the data and draws SVG marks
```

The three shared code files are:

- [`index.html`](index.html): page structure, written findings, chart containers and accessibility labels.
- [`visualisation.js`](visualisation.js): loads every chart and controls the embedding behaviour.
- [`style.css`](style.css): page layout, responsive behaviour, chart alignment and presentation.

The `.vg.json` files describe the charts. The files inside [`Formatted Data`](Formatted%20Data) contain the values used by those charts. The files inside [`topojson files`](topojson%20files) contain geographic shapes.

## 2. Vega-Lite vocabulary used throughout the project

### `$schema`

```json
"$schema": "https://vega.github.io/schema/vega-lite/v5.json"
```

This identifies the file as a Vega-Lite version 5 specification. Editors can use it for validation and suggestions.

### `data`

```json
"data": {
  "url": "Formatted Data/example.csv",
  "format": {
    "type": "csv",
    "parse": {"Percent": "number"}
  }
}
```

This loads the dataset. `parse` explicitly converts fields to numbers so that Vega-Lite does not treat numeric values as text.

### `transform`

Transforms reshape, select or derive data before marks are drawn. They form a pipeline: the output of one transform becomes the input to the next transform.

```json
"transform": [
  {"filter": "datum.Value > 0"},
  {"calculate": "datum.Value * 100", "as": "ValuePercent"}
]
```

In a Vega expression, `datum` means the current row. The first transform removes rows where `Value` is zero or negative. The second adds `ValuePercent` to each remaining row.

A transform at the top level affects the complete visualisation. A transform inside one layer affects only that layer. This is useful in the dumbbell chart, where only the point layer needs the two year columns folded.

#### `filter`

`filter` removes rows that do not satisfy a condition. It does not change the surviving rows.

```json
{"filter": "datum.Age_Group === ageGroup"}
```

In the waffle chart, `ageGroup` comes from the dropdown parameter. If the user selects adults, only adult tile records continue to the mark and encoding stages.

Filters can also use literal values:

```json
{"filter": "datum.Category === 'Discretionary'"}
```

This creates the discretionary half of the paired choropleth. A common debugging problem is an incorrect field name or value causing a filter to remove every row.

#### `calculate`

`calculate` creates a new field without changing the source file:

```json
{
  "calculate": "datum['2023 (%)'] - datum['1995 (%)']",
  "as": "Change"
}
```

Every row receives a new `Change` property. Later encodings and tooltips can refer to it as if it were an original CSV column.

Calculations can contain arithmetic, comparisons, string formatting and conditional expressions. For example, the dumbbell chart categorises the calculated change:

```json
{
  "calculate": "datum.Change > 0 ? 'Increase' : datum.Change < 0 ? 'Decrease' : 'No change'",
  "as": "Direction"
}
```

The `condition ? resultA : resultB` syntax is a ternary expression. It is a compact `if/else` statement.

#### `fold`

`fold` converts wide data into long data. Suppose one source row is:

| Age group | 1995 (%) | 2023 (%) |
|---|---:|---:|
| 18–29 | 60 | 25 |

This transform:

```json
{
  "fold": ["1995 (%)", "2023 (%)"],
  "as": ["YearField", "Consumption"]
}
```

produces two rows:

| Age group | YearField | Consumption |
|---|---|---:|
| 18–29 | 1995 (%) | 60 |
| 18–29 | 2023 (%) | 25 |

This is useful because one `Consumption` field can now control x-position, while `YearField` can control colour. The beverage dumbbell and both drink heatmaps use this pattern.

#### `lookup`

`lookup` joins fields from a second dataset using matching keys. It is similar to a spreadsheet lookup or a SQL left join.

```json
{
  "lookup": "State/Territory",
  "from": {
    "data": {"url": "states.json"},
    "key": "properties.StateName"
  },
  "as": "geometry"
}
```

For every statistical row, Vega-Lite finds the geographic record with the same state name and attaches its geometry. The choropleth can then use the percentage from the CSV and the shape from the TopoJSON in one mark.

The key values must match exactly. Differences such as `NSW` versus `New South Wales`, spelling changes or extra spaces produce missing joins.

In the graduated-symbol map, `lookup` instead attaches longitude and latitude from the inline `state_centres` dataset. In the cartograms, it attaches percentage and state-label fields to existing geometry.

#### `density`

`density` estimates a smooth distribution from individual numeric observations. It creates new sampled x-values and corresponding density values.

```json
{
  "density": "Value",
  "groupby": ["Food_Group"],
  "extent": [0, 100],
  "steps": 300,
  "as": ["NutrientValue", "Density"]
}
```

- `density: "Value"` selects the numeric field being estimated.
- `groupby` produces a separate distribution for each food group.
- `extent` fixes the minimum and maximum generated x-values.
- `steps` controls how many points are generated along the curve.
- `as` names the generated x and y fields.

The resulting rows are not the original foods. They are points along an estimated curve. In the ridgeline chart, an area mark connects these generated points.

#### `joinaggregate`

`joinaggregate` calculates a grouped summary but preserves the original rows. The summary is copied onto each row in its group.

```json
{
  "joinaggregate": [
    {"op": "max", "field": "BaselineCandidate", "as": "BaselinePercent"}
  ],
  "groupby": ["Nutrient"]
}
```

If Protein has eight age rows, Vega-Lite calculates one protein baseline and attaches it to all eight rows. Each row can then subtract that baseline.

This differs from `aggregate`. A normal `aggregate` usually collapses many rows into one summary row per group. `joinaggregate` retains the detailed observations, which is why the subsequent line chart can still display every age group.

The ridgeline chart also uses `joinaggregate` to attach each food group's maximum density before dividing every density value by that peak.

#### Transform summary

| Transform | Changes row count? | Adds fields? | Project example |
|---|---|---|---|
| `filter` | Usually reduces rows | No | Select one age group or map category |
| `calculate` | No | Yes | Percentage-point change or formatted label |
| `fold` | Usually increases rows | Yes | Turn year/frequency columns into key/value rows |
| `lookup` | Normally preserves rows | Yes | Attach geometry, coordinates or statistics |
| `density` | Replaces observations with sampled curve points | Yes | Generate nutrient distribution ridges |
| `joinaggregate` | Preserves rows | Yes | Attach nutrient baseline or peak density |

### `mark`

The mark is the geometric object used to represent data. A simple mark can be written as a string:

```json
"mark": "bar"
```

A mark definition object adds constant styling:

```json
"mark": {
  "type": "point",
  "filled": true,
  "size": 100,
  "stroke": "white"
}
```

Properties inside `mark` apply the same styling to every generated mark. Properties inside `encoding` can vary according to data. For example, `"color": "#0072B2"` in a mark is constant, whereas a colour encoding using a field can produce a different colour for each category.

Most marks create one visible item per row. `line` and `area` are important exceptions: they connect multiple rows into a continuous path.

#### `rect`

`rect` draws rectangles. The rectangle's boundaries can be determined by x/y bands or by explicit `x`, `x2`, `y` and `y2` positions.

In the waffle chart, each CSV row supplies an ordinal column and row, so every record becomes one square tile. In the heatmaps, ordinal age and frequency bands define each cell, while quantitative colour shows the percentage.

White strokes between rectangles create visible separation without changing the data.

#### `line`

`line` connects observations into an ordered path. It is appropriate for trajectories across age or time.

Vega-Lite normally follows the x-axis order. For ordinal age groups, the explicit x sort is essential because alphabetical ordering would be incorrect.

If multiple lines use the same layer, a categorical encoding such as `color` or `detail` groups rows into separate series. Without grouping, Vega-Lite may incorrectly connect unrelated categories.

Line marks show continuity and direction, but exact observations are often clearer when a point layer is placed above them.

#### `point` and `circle`

Both marks show individual observations.

- `circle` always draws a circle.
- `point` is more general and supports circles, squares and custom SVG paths through `shape`.

The nutrient deviation chart uses points to expose every age observation. The supplement pictogram uses a custom person-shaped point. The graduated-symbol map uses circles because circular area encodes intake.

For point and circle marks, `size` normally refers to symbol area rather than radius. Doubling `size` therefore does not double the circle's diameter.

#### `area`

`area` connects ordered points like a line and fills the space between the path and a baseline. It can also fill between `y` and `y2`.

The ridgeline chart uses an area mark from relative density down to zero. Because each food group is faceted into its own small row, the filled distribution resembles a ridge.

`interpolate: "monotone"` smooths the connection between generated density points. It changes the drawn curve, not the underlying data values.

#### `bar`

`bar` extends from a baseline, usually zero, to a quantitative value. Its thickness is controlled by a band scale or `size`.

The bullet charts place a thick grey recommendation bar behind a thinner coloured actual-intake bar. The butterfly chart uses horizontal bars on mirrored scales.

Bars are good for magnitude comparisons because length is read against a common baseline.

#### `tick`

`tick` draws a short line centred at a position. It is useful for targets or reference values that should not look like another bar.

The bullet charts place a red tick at the recommended number of serves. The tick repeats information encoded by the grey background bar but makes the exact target endpoint easier to locate.

#### `rule`

`rule` draws a straight line. Its use depends on the supplied positional channels:

- A constant `y` draws a horizontal reference line.
- `x` and `x2` draw a horizontal interval.
- `y` and `y2` draw a vertical interval.

The deviation chart uses a horizontal rule at zero and vertical dashed rules for annotation connectors. The dumbbell chart uses `x` and `x2` to connect 1995 and 2023 values.

#### `geoshape`

`geoshape` draws geographic or already transformed polygon geometry. It normally works with a geographic `projection`.

In the choropleth, a Mercator projection converts Australian state geometry to screen coordinates. In the precomputed cartograms, an identity projection is used because the TopoJSON coordinates are already distorted and laid out.

Colour can encode a statistical field joined to each shape. A stroke separates neighbouring regions.

#### `text`

`text` draws labels from a data field or a constant value. Position comes from x/y encodings, and `dx`/`dy` can offset the label from its mark.

This project uses text marks for:

- Exact values beside dumbbell points.
- Percentages at the end of pictogram rows.
- State abbreviations on cartograms.
- The centre labels in the butterfly chart.
- Selective annotations in the nutrient deviation chart.

The deviation annotations use two identical text layers: thick white text underneath creates a halo, and dark text on top remains readable. The order matters because later layers are painted above earlier layers.

#### Mark summary

| Mark | What the reader perceives | Project use |
|---|---|---|
| `rect` | Cell, tile or bounded region | Waffle and heatmaps |
| `line` | Trend or trajectory | Nutrient changes across age |
| `point` | Individual observation or custom symbol | Line points and pictograms |
| `circle` | Observation whose area may encode magnitude | Graduated-symbol maps |
| `area` | Filled distribution or interval | Ridgelines |
| `bar` | Magnitude from a baseline | Bullet and butterfly charts |
| `tick` | Target or precise reference position | Recommendation markers |
| `rule` | Baseline, interval or connector | Deviation and dumbbell charts |
| `geoshape` | Geographic region | Choropleths and cartograms |
| `text` | Label or annotation | Values, state labels and callouts |

### `encoding`

Encodings map fields to visual properties:

```json
"x": {"field": "Age_Group", "type": "ordinal"},
"y": {"field": "Percent", "type": "quantitative"},
"color": {"field": "Category", "type": "nominal"}
```

The main data types are:

- `quantitative`: numeric magnitude.
- `nominal`: named categories without a natural order.
- `ordinal`: categories with a meaningful order.
- `temporal`: dates or times.

### `layer`, `facet`, `hconcat` and `vconcat`

- `layer` draws marks on top of one another in the same coordinate system.
- `facet` repeats one chart for each category.
- `hconcat` places charts horizontally.
- `vconcat` places charts vertically.

### `scale`, `legend`, `axis` and `resolve`

- `scale` translates data values into positions, colours or sizes.
- `axis` controls positional labels and ticks.
- `legend` explains colour or size encodings.
- `resolve` decides whether composed charts share or independently calculate scales.

### `tooltip`

Tooltips reveal exact values on hover without permanently cluttering the visualisation.

### `config`

`config` supplies chart-wide styling defaults such as fonts, axis colours, view borders and spacing.

## 3. Shared webpage files

## `index.html`

### Document setup

The `<head>` sets the character encoding, mobile viewport, description and title. It loads:

1. Vega, which performs the final rendering.
2. Vega-Lite, which compiles the declarative chart specifications.
3. Vega-Embed, which inserts charts into HTML containers.
4. `visualisation.js`, which coordinates all chart loading.
5. `style.css`, which styles the page.

### Semantic story structure

The `<main>` element contains four story chapters:

1. Composition.
2. Life course.
3. Guidelines and access.
4. Place and health.

Each visualisation is contained in a `<figure class="chart-block">`. A typical chart block contains:

```html
<header class="figure-heading">...</header>
<div class="chart-frame" aria-busy="true">
  <div id="chart-id" class="vis" aria-label="..."></div>
</div>
<aside class="chart-annotation">...</aside>
<figcaption>...</figcaption>
```

- The `id` is how JavaScript finds the chart container.
- `aria-busy="true"` tells assistive technology the chart is loading.
- `aria-label` provides a concise chart description.
- The `aside` contains the written key finding.
- The `figcaption` explains how to read the chart and links to its specification.

The chart IDs must exactly match the selectors in `visualisation.js`.

### Interview explanation

> `index.html` provides the narrative and semantic structure. It does not draw the charts itself; it provides named containers that `visualisation.js` fills using Vega-Embed.

## `visualisation.js`

### Chart registry

```js
const visualisations = [
  { container: "#energy-waffle", specification: "daily_energy_waffle.vg.json" },
  // ...other charts
];
```

This array is a central mapping between HTML container IDs and Vega-Lite files. Adding a chart requires a matching HTML container and registry entry.

### Preventing duplicate loads

```js
const loadedVisualisations = new Set();
```

The set remembers which selectors have already been embedded. `embedVisualisation` returns early if a chart is already present.

### Loading and error states

`setFrameState` finds the surrounding `.chart-frame`, clears `aria-busy` and adds either `is-ready` or `has-error`.

`showChartError` replaces the chart with a readable error message and logs the technical error to the browser console.

### Vega embedding

```js
window.vegaEmbed(container, specification, {
  actions: false,
  renderer: "svg",
  tooltip: { theme: "light" }
});
```

- `actions: false` removes the three-dot export/source menu.
- `renderer: "svg"` produces scalable vector graphics.
- `tooltip` uses Vega-Tooltip's light theme.
- `.then(...)` marks a successful load.
- `.catch(...)` displays an error state.

### Lazy loading

`IntersectionObserver` watches each chart frame. A chart is embedded only when it approaches the viewport. The `rootMargin: "700px 0px"` setting starts loading it 700 pixels before it becomes visible.

This reduces initial page work while avoiding a visible delay during normal scrolling. Browsers without `IntersectionObserver` load every chart immediately.

### Printing

The `beforeprint` event embeds every chart before the browser creates a print preview, including charts the user has not scrolled to.

### Interview explanation

> The JavaScript centralises chart loading, disables the Vega actions menu, renders SVG, handles errors, and lazy-loads charts with `IntersectionObserver`. A `Set` prevents duplicate embedding, and `beforeprint` ensures every chart appears in print output.

## `style.css`

### Design tokens and global rules

The `:root` block defines reusable colours and the `1180px` maximum page width. Global rules establish typography, link states, box sizing and accessible keyboard focus.

### Page and story layout

`.page` constrains and centres content. `.chapter-heading`, `.figure-heading` and `.chart-annotation` use CSS Grid so labels and text align consistently.

### Chart presentation

- `.chart-frame` reserves loading space and clips accidental overflow.
- `.vis` and `.vega-embed` expand to the available width and centre the SVG.
- `.vega-embed svg` uses `max-width: 100%` and `height: auto`, allowing oversized SVG charts to shrink proportionally.
- `#macro-deviation` has additional centring rules because it is a large faceted chart.
- `.chart-pair` creates the two-column children/adults heatmap layout.
- The fixed minimum height on paired figure headings keeps the two heatmaps vertically aligned.

### Responsive rules

Below `900px`, chart pairs and the footer change to one column. Below `680px`, headings and annotations also switch to one column and page margins become smaller.

`prefers-reduced-motion` disables smooth scrolling for users who request reduced motion. Print rules remove navigation and prevent charts from splitting across pages where possible.

### Interview explanation

> CSS controls the narrative layout around the charts and makes the SVG output responsive. Vega-Lite controls the internal chart grammar, while CSS controls how the resulting SVG fits into the webpage.

## 4. Chart 1: daily energy waffle

Files:

- [`daily_energy_waffle.vg.json`](daily_energy_waffle.vg.json)
- [`Formatted Data/daily_energy_waffle.csv`](Formatted%20Data/daily_energy_waffle.csv)

### What the chart answers

It shows the percentage contribution of mutually exclusive energy sources using 100 tiles. Approximately one tile represents one percentage point.

### Important code blocks

`params` defines the `ageGroup` dropdown. Its selected value becomes a Vega expression variable.

The first transform filters the CSV to the selected age group:

```json
{"filter": "datum.Age_Group === ageGroup"}
```

The second transform estimates energy in kilojoules:

```text
exact percentage × mean daily energy ÷ 100
```

The `rect` mark draws each tile. `Column` and `Row` position the pre-generated tile records, while the axes are hidden because the grid position is only structural.

`color` maps `Energy_Source` to an explicit colour-blind-friendly palette. The explicit `domain` and `range` guarantee stable category-to-colour mappings.

The opacity condition fades `Unallocated / rounding` tiles to show that they are not a nutritional category.

The tooltip retains exact percentage and kilojoule values even though the visible waffle rounds values to whole tiles.

### Interview explanation

> The CSV is already expanded into tile positions. Vega-Lite filters those tiles using a bound dropdown, draws them as rectangles, colours them by energy source, and provides exact values through tooltips. The waffle gives an intuitive part-to-whole view while the tooltip preserves precision.

## 5. Chart 2: faceted nutrient deviation lines

Files:

- [`macronutrient_age_deviation.vg.json`](macronutrient_age_deviation.vg.json)
- [`Formatted Data/macronutrient_parallel_coordinates.csv`](Formatted%20Data/macronutrient_parallel_coordinates.csv)

### What the chart answers

It shows how each nutrient's energy contribution changes relative to the ages 2–4 baseline.

### Baseline transforms

The first calculation keeps the ages 2–4 percentage and returns `null` for other ages. `joinaggregate` then calculates the maximum non-null candidate within each nutrient group and attaches it as `BaselinePercent` to every row for that nutrient.

The deviation is calculated as:

```text
PercentagePointChange = Energy_Percent − BaselinePercent
```

This produces percentage-point change, not percentage change. For example, moving from 20% to 15% is `−5 percentage points`.

### Annotation transforms

`AnnotationText` conditionally creates a label only for selected interesting observations. Other rows receive `null`. `AnnotationY` supplies a deliberate vertical position for each label.

### Faceting

`facet` repeats the same chart for each nutrient. `columns: 3` wraps five nutrient panels across two rows. The explicit nutrient sort keeps the intended order.

The row and column spacing values separately control vertical and horizontal gaps.

### Layers

The panel contains six layers:

1. A horizontal `rule` at zero, representing the ages 2–4 baseline.
2. A `line` showing the age trajectory.
3. Coloured `point` marks showing individual observations and tooltips.
4. Dashed `rule` marks connecting selected points to annotations.
5. White annotation text, used as a background halo.
6. Dark annotation text drawn above the halo.

Points are teal when the change is zero or positive and orange when it is negative.

The fixed y-domain `[-9, 4]` and shared y-scale make vertical distances comparable across all nutrients.

### Interview explanation

> I derive a baseline separately for each nutrient using `joinaggregate`, subtract it to obtain percentage-point change, and facet the same layered line chart by nutrient. All panels share a y-scale, so a one-point change has the same visual distance everywhere. Extra rule and text layers create selective Tableau-style annotations.

## 6. Chart 3: food-category nutrient ridgelines

Files:

- [`food_category_nutrient_ridgeline.vg.json`](food_category_nutrient_ridgeline.vg.json)
- [`Formatted Data/ausnut_ridgeline_nutrients.csv`](Formatted%20Data/ausnut_ridgeline_nutrients.csv)

### What the chart answers

It compares the distributions of total sugars, dietary fibre and sodium among individual AUSNUT foods within broad food categories.

### Horizontal composition

`hconcat` creates three nutrient columns. Each column filters to one nutrient before calculating its distribution.

### Density and normalization

For each nutrient, `density` estimates the distribution of `Value`, grouped by `Food_Group`. The result contains generated x-values (`NutrientValue`) and density values (`Density`).

`joinaggregate` finds `PeakDensity` within every food group. The next calculation divides each density by its own peak:

```text
RelativeDensity = Density ÷ PeakDensity
```

This makes every ridge reach a maximum height of 1. It helps compare distribution shapes, but ridge height must not be interpreted as the number of foods or consumption frequency.

### Row facets and area marks

Each nutrient column facets vertically by `Food_Group`. An `area` mark with monotone interpolation creates each ridge.

Only the first column displays food-group labels. The long final group name is changed through `labelExpr`, and the `guide-label` line-break style wraps it rather than truncating it.

### Different nutrient scales

- Sugars use a linear 0–100 g/100 g scale.
- Fibre uses a linear 0–45 g/100 g scale.
- Sodium uses a 0–8500 mg/100 g symlog scale.

The sodium symlog scale retains zero and low values while compressing extreme high-sodium observations. Therefore, horizontal distances in the sodium column are not linearly proportional across the entire axis.

### Interview explanation

> Each ridge is a kernel density estimate for one food group. I normalise each density to its own peak so the shapes remain readable, facet the distributions by food group, and concatenate three nutrient-specific views. Sodium uses symlog because its extreme values would otherwise compress most of the distribution.

## 7. Chart 4: supplement-use pictogram

Files:

- [`supplement_use_life_course_pictogram.vg.json`](supplement_use_life_course_pictogram.vg.json)
- [`Formatted Data/supplement_use_life_course_pictogram.csv`](Formatted%20Data/supplement_use_life_course_pictogram.csv)

### What the chart answers

It shows the proportion of each age group that used a dietary supplement. Every person icon represents five people out of 100.

### Shared y-encoding

Age group is encoded once at the top level. Every layer inherits the same row position.

### Pictogram layers

1. The first point layer draws all person icons in grey.
2. The second layer filters to `Fill_Amount > 0` and redraws used icons in green.
3. Green opacity is driven by `Fill_Amount`, allowing the final icon to be partially faded for a non-multiple-of-five estimate.
4. The final text layer keeps one record per age group (`Icon_Index === 1`), calculates a fixed label position and prints the exact percentage.

The long SVG path stored in `shape` defines the custom person silhouette.

### Interview explanation

> The dataset contains 20 icon records per age group. I first draw a complete grey background row, then overlay green icons where `Fill_Amount` is positive. Opacity represents a partial final icon, while a separate text layer reports the exact percentage.

## 8. Chart 5: beverage dumbbell chart

Files:

- [`beverage_consumption_dumbbell.vg.json`](beverage_consumption_dumbbell.vg.json)
- [`Formatted Data/Beverage_Consumption_Dumbbell_Data.csv`](Formatted%20Data/Beverage_Consumption_Dumbbell_Data.csv)

### What the chart answers

It compares beverage-consumption percentages in 1995 and 2023 for each age group.

### Derived fields

`Change` subtracts the 1995 value from the 2023 value. `Direction` converts its sign into Increase, Decrease or No change for the tooltip.

### Faceting

Column facets separate sugar-sweetened and intense-sweetened beverages while sharing the same age ordering and x-scale.

### Layers

1. A thick grey `rule` runs from `x = 1995 (%)` to `x2 = 2023 (%)`.
2. `fold` turns the two year columns into a common `Consumption` field and a `YearField` key.
3. A calculation cleans `YearField` into the legend values `1995` and `2023`.
4. Coloured point marks show the endpoints.
5. Two text layers label the 1995 and 2023 values above and below the points.

The distance and direction between endpoints communicate change more directly than two separate bars.

### Interview explanation

> A dumbbell uses a rule for the before-to-after interval and two points for the endpoints. I use `fold` to convert the two year columns into long form so one point layer can encode both years consistently.

## 9. Charts 6 and 7: children and adult drink heatmaps

Files:

- [`kids_prevelance_of_sugar_drink_heatmap.vg.json`](kids_prevelance_of_sugar_drink_heatmap.vg.json)
- [`adults_prevelance_of_sugar_drink_heatmap.vg.json`](adults_prevelance_of_sugar_drink_heatmap.vg.json)
- [`Formatted Data/kids_data_no_ci.csv`](Formatted%20Data/kids_data_no_ci.csv)
- [`Formatted Data/adults_data_no_ci.csv`](Formatted%20Data/adults_data_no_ci.csv)

### What the charts answer

They show how drink-consumption frequency differs by age, separately for children and adults.

### Reshaping the data

The original files contain separate columns such as `Daily (%)` and `1-3 days (%)`. `fold` converts them into:

- `Consumption Frequency`: the original column name.
- `Percentage`: the value from that column.

The following calculation removes ` (%)` from the frequency names for cleaner x-axis labels.

### Marks and encodings

Each age/frequency combination becomes a `rect` cell. Age group is on y, cleaned frequency is on x, and percentage controls colour.

The children chart uses `tealblues`; the adult chart uses `oranges`. Both use a symlog colour scale with constant 10, which preserves more visible variation among small percentages while compressing the very large non-consumption values.

`tooltip: true` asks Vega-Lite to generate a tooltip from the encoded fields automatically.

### Interview explanation

> The main transformation is `fold`, which converts several frequency columns into one categorical field and one numeric field. This long format maps naturally to a heatmap: age on y, frequency on x and percentage as colour.

## 10. Chart 8: actual versus recommended intake bullet charts

Files:

- [`male_female_intake_bullets.vg.json`](male_female_intake_bullets.vg.json)
- The six actual/recommended CSV files for male and female age groups in `Formatted Data`.

### What the chart answers

It compares actual daily serves with recommended serves across sex, age group and food group.

### 2×2 composition

The outer `vconcat` creates two rows. Each row contains an `hconcat` with two panels:

```text
Male 18–29       Male 30–49
Female 18–29     Female 30–49
```

### Three layers per panel

1. A thick grey bar shows the recommended serves.
2. A thinner coloured bar overlays the actual mean intake.
3. A red tick marks the precise recommendation.

Each layer can load a different CSV. Repeating the same x and y encodings places the marks in one coordinate system.

The visual is called a bullet graph because it combines a background benchmark, a measured bar and a target marker in much less space than a gauge.

### Interview explanation

> I construct each bullet graph from three aligned layers: recommendation background, actual intake foreground, and a target tick. Horizontal and vertical concatenation then form the four demographic panels.

## 11. Chart 9: food-security butterfly chart

Files:

- [`food_security_income.vg.json`](food_security_income.vg.json)
- [`Formatted Data/Household_Food_Security_by_Income.csv`](Formatted%20Data/Household_Food_Security_by_Income.csv)

### What the chart answers

It compares estimated food-secure and food-insecure household counts across income quintiles.

### Three horizontal views

`hconcat` creates:

1. Food-secure bars on the left.
2. Income labels in the centre.
3. Food-insecure bars on the right.

The left x-scale has `reverse: true`, so the bars extend away from the centre toward the left. The right scale uses the normal direction.

Both sides use a 0–2000 thousand-household domain. The shared y-scale guarantees that matching income quintiles stay aligned.

The centre view uses a `text` mark instead of an axis, giving both halves a clean shared label column.

### Important interpretation

The bars display estimated household counts, not within-quintile percentages. The percentage comparison in the HTML key finding was calculated separately from the totals.

### Interview explanation

> A butterfly chart mirrors two horizontal bar charts around a shared categorical centre. I reverse the left scale, preserve a common numeric domain on both sides, and use a separate text view for aligned income labels.

## 12. Chart 10: discretionary/non-discretionary choropleths

Files:

- [`discret_vs_nondiscret.vg.json`](discret_vs_nondiscret.vg.json)
- [`Formatted Data/Australian_Energy_Proportions_by_State.csv`](Formatted%20Data/Australian_Energy_Proportions_by_State.csv)
- [`topojson files/STE_2021_AUST_GDA2020.json`](topojson%20files/STE_2021_AUST_GDA2020.json)

### What the chart answers

It maps the percentage of daily energy from discretionary and non-discretionary foods for each state and territory.

### Geographic lookup

The main data is the CSV. `lookup` matches `State/Territory` to `properties.STE_NAME21` in the TopoJSON and attaches the corresponding geometry to each CSV row.

### Paired maps

`hconcat` creates two maps. A filter selects `Discretionary` rows for the first and `Non-discretionary` rows for the second.

`projection: mercator` converts longitude/latitude geometry into screen coordinates. `geoshape` draws each attached state geometry.

Colour uses the actual `Total 2 years and over (%)` values with linear sequential scales:

- Orange domain: 32–39% discretionary.
- Blue domain: 61–68% non-discretionary.

The legends use array titles to wrap long descriptions. `resolve` makes the two colour scales independent because the two percentage ranges differ.

### Normalisation

The underlying data is already normalized: the two categories sum to 100% in every state. It is not an absolute population total, so it is suitable for a choropleth. The restricted colour domains reveal regional differences but make small percentage-point differences visually prominent.

### Interview explanation

> I join normalized state percentages to TopoJSON geometry, filter the two food categories into separate maps, and encode percentage with independent linear colour scales. A choropleth is appropriate because the variable is a within-state share rather than an absolute count.

## 13. Chart 11: sodium and potassium graduated-symbol maps

Files:

- [`sodium_potassium_graduated_symbol.vg.json`](sodium_potassium_graduated_symbol.vg.json)
- [`Formatted Data/Australian_Sodium_Potassium_19plus.csv`](Formatted%20Data/Australian_Sodium_Potassium_19plus.csv)
- Australian state TopoJSON.

### What the chart answers

It compares estimated sodium and potassium intake across states and territories.

### Named inline dataset

`datasets.state_centres` stores one manually chosen longitude/latitude position for every state. These points position the graduated circles.

### Two layers per map

1. A grey `geoshape` layer draws the state basemap.
2. A circle layer loads the nutrient CSV and looks up each state's centre coordinates.

`longitude` and `latitude` position each circle. `size` represents nutrient intake.

The size scales have `zero: false` and restricted domains, deliberately magnifying the fairly small differences between states. Sodium and potassium use independent size scales and therefore must only be compared within their own maps.

### Interview explanation

> The basemap provides geographic context, while proportional circles encode nutrient intake. A lookup joins each state to a representative centre point. Restricted independent size scales reveal within-nutrient variation, so the subtitle explicitly warns against comparing circle sizes across the two maps.

## 14. Chart 12: health-risk contiguous cartograms

Files:

- [`health_risk_condition_contiguous_cartograms.vg.json`](health_risk_condition_contiguous_cartograms.vg.json)
- [`Formatted Data/health_cartogram_values_2022.csv`](Formatted%20Data/health_cartogram_values_2022.csv)
- The two precomputed cartogram TopoJSON files.

### What the chart answers

It compares overweight/obesity and diabetes prevalence by resizing states according to their percentages.

### Precomputed geometry

The cartogram transformation is not calculated live in Vega-Lite. Each panel loads a pre-generated TopoJSON file whose state shapes and areas have already been distorted.

Because the coordinates are already laid out, the maps use an `identity` projection instead of Mercator. `reflectY: false` preserves the direction of the supplied screen-like coordinates.

### Lookup and layers

`lookup` matches the geometry's `properties.join_key` to `JoinKey` in the values CSV, attaching percent, metric, state name and abbreviation.

Each map then layers:

1. Coloured `geoshape` marks for the resized states.
2. Text marks positioned at precomputed `properties.label_x` and `properties.label_y` coordinates.

The two panels use independent colour scales because overweight/obesity and diabetes have very different percentage ranges.

### Interview explanation

> These are contiguous area cartograms: state area, not colour alone, represents prevalence. The distorted geometries were generated beforehand, then Vega-Lite joins the statistical values, draws the shapes with an identity projection, and adds state abbreviations at stored label coordinates.

## 15. Legacy specification: `macronutrient_parallel_coordinates.vg.json`

[`macronutrient_parallel_coordinates.vg.json`](macronutrient_parallel_coordinates.vg.json) is no longer loaded by the website. `visualisation.js` now loads `macronutrient_age_deviation.vg.json` instead.

Despite its filename, the current legacy specification is a multi-series line chart:

- Age group is the ordered x-axis.
- Energy percentage is the y-axis.
- Colour and `detail` group observations into one line per nutrient.
- Tooltips show the original percentage.

Keep this distinction clear in an interview: the filename is historical, but it is not the active Chart 2 and it is not currently a parallel-coordinates visualisation.

## 16. Quick interview questions and answers

### Why use long-form data?

Long-form data provides one observation per row and works naturally with grammar-of-graphics mappings such as `field → x`, `field → colour`, and `field → facet`. `fold` converts wide source tables to this structure when necessary.

### What is the difference between layering and faceting?

Layering places different marks in the same coordinate system. Faceting repeats the same chart for different subsets of the data.

### What is the difference between `lookup` and `joinaggregate`?

`lookup` joins fields from a separate table using a key. `joinaggregate` calculates a summary from the current table and attaches the grouped result to its rows.

### Why explicitly sort age groups?

Age groups are strings. Without an explicit sort, Vega-Lite may use alphabetical order rather than chronological order.

### Why use tooltips?

Tooltips preserve exact values without placing permanent labels on every mark. They support detail-on-demand while keeping the visual uncluttered.

### Why set `actions: false` in `vegaEmbed`?

It removes Vega-Embed's three-dot export/source/editor menu. It does not disable chart interactions such as tooltips, dropdowns or selections.

### Why use SVG?

SVG stays sharp when resized and printed, and CSS can constrain it responsively with `max-width: 100%`.

### Why use lazy loading?

Loading twelve visualisations at once increases initial work. `IntersectionObserver` loads charts shortly before they enter the viewport.

### When is a choropleth appropriate?

A choropleth should normally encode a normalized rate, percentage or density rather than a raw count, because geographic regions have different populations and sizes.

### Why use independent scales?

Independent scales are useful when panels measure different variables or occupy very different ranges. The trade-off is that mark sizes or colours may no longer be directly comparable across panels, so the chart must say so.

### Why use a shared scale?

A shared scale makes equal visual distances represent equal numeric differences across panels. Chart 2 uses this so nutrient changes remain directly comparable.

### What does symlog do?

Symlog behaves approximately linearly near zero and logarithmically for larger magnitudes. It retains zero while compressing extreme values.

### What is the difference between percentage change and percentage-point change?

If a value falls from 20% to 15%, the percentage-point change is `15 − 20 = −5 pp`. The relative percentage change is `(15 − 20) / 20 = −25%`. Chart 2 uses percentage points.

## 17. A reusable way to explain any chart

Use this five-part structure:

1. **Question:** What does the chart help the reader compare?
2. **Data:** Which file is loaded, and what does one row represent?
3. **Transform:** How is the source data filtered, joined, folded or calculated?
4. **Visual grammar:** Which marks are used, and which fields control position, colour, size or facets?
5. **Interpretation:** What should and should not be compared?

Example:

> This chart compares beverage consumption in 1995 and 2023. Each source row represents one beverage type and age group. I calculate the change, then fold the two year columns so they can share one point layer. A rule connects the two endpoints, colour identifies the year, and facets separate beverage types. The distance between the points represents percentage-point change.

## 18. Debugging checklist

If a chart does not appear or looks incorrect, check:

1. Does the HTML container ID match `visualisation.js`?
2. Does the JSON filename in `visualisation.js` exist?
3. Does the JSON parse successfully?
4. Is the CSV/TopoJSON path relative to the webpage correct?
5. Do field names match exactly, including spaces and punctuation?
6. Are numeric fields explicitly parsed when needed?
7. Are ordinal categories explicitly sorted?
8. Are layered axes and scales being shared or suppressed unintentionally?
9. Does a filter remove all rows?
10. Does the browser console show a Vega-Lite warning or loading error?

