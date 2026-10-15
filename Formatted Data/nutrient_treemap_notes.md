# Daily nutrient treemap (ages 2–17)

`Nutrients_Ages_2_17_Grouped_Treemap.csv` is the current chart-specific dataset. All original CSVs, workbooks and the earlier `Nutrients_Ages_2_17_Treemap.csv` are unchanged. `daily_kJ_treemap_u18.vg.json` uses the grouped file; its existing filename is retained even though the chart measures nutrient amounts, not kilojoules.

## Source and units

The reported amounts come from `Nutrients_Ages_2_17.csv`, checked against `Raw Data/NNPASDC01.xlsx`, sheet `Table 1.1_Means Persons`, column K (persons aged 2–17). `Source_cells` identifies the workbook cell. These are population means from food and beverages reported on the day before the interview, not dietary recommendations or modelled usual intake.

- `Mean_Value_Ages_2_17` and `Unit` retain the source amount and unit for labels and tooltips.
- `Value_g` is the rectangle weight: g stays unchanged; mg is divided by 1,000; µg is divided by 1,000,000. The new file uses UTF-8.
- Grouping nodes have zero weight in the CSV. The overview sums component masses and draws only four category tiles: Macronutrients (blue), Vitamins (gold), Minerals (green) and Other (purple). The list also shows only those four totals.
- Selecting a category rebuilds the hierarchy with that group as its root and displays its individual components. Every component keeps its parent's colour. Each amount is counted once. Sizes are relative to that view; tooltip percentages describe displayed mass, not energy, dietary requirements or nutritional importance.

## Selecting additive measures

This is a breakdown of **selected reported nutrient amounts**, not a complete chemical mass balance of all consumed food. Water and other unreported food constituents are outside its scope.

- Protein, total fat, carbohydrate and dietary fibre are the macronutrient tiles. Fatty acid and sugar subcomponents are not additional tiles because they are included in their totals. Fat and carbohydrate tooltips retain component detail. Free sugars include added sugars, so those two amounts cannot be added as independent components.
- The vitamin view uses preformed vitamin A, provitamin A, B1, B2, niacin, natural folate, folic acid, B6, B12, C and E amounts. Vitamin A retinol equivalents, niacin equivalents, total folates and folate equivalents are not added as further nutrients: they are alternative summaries of overlapping amounts or nutritional activity.
- Vitamin D3 equivalents (4.2 µg/day, cell K42) are shown as a separate note in the vitamin view: an activity-equivalent amount is not a directly additive physical mass.
- All nine reported minerals are included. Iodine and selenium are converted from micrograms before comparison with minerals reported in milligrams.
- Other contains alcohol (0.1 g/day, K26) and caffeine (22 mg/day, K55). This is a chart grouping: the source workbook lists alcohol with macronutrients. Cholesterol (256 mg/day, K56) remains within total fat and is mentioned in its tooltip instead of being added again under Other. Energy (kJ) and moisture are excluded.

Vitamins and Other occupy very little area in the overview because their combined masses are small. The group selector enlarges these comparisons without inflating small amounts. Long labels are truncated within their tiles; labels on very small tiles are hidden. The list beside the treemap displays the same categories or individual components as the current view, with daily amounts and tooltips.

## References

- [ABS 2023 survey and Table 1 download](https://www.abs.gov.au/statistics/health/food-and-nutrition/national-nutrition-and-physical-activity-survey/2023).
- [ABS: energy and nutrient intake, including interpretation of overlapping totals](https://www.abs.gov.au/statistics/detailed-methodology-information/concepts-sources-methods/intergenerational-health-and-mental-health-study-concepts-sources-and-methods/2020-24/food-and-nutrient-collections/energy-and-nutrient-intake).
- [ABS: free sugars include added sugars](https://www.abs.gov.au/statistics/health/food-and-nutrition/sweetened-beverages/2023).
- [Vega treemap transform](https://vega.github.io/vega/docs/transforms/treemap/).
