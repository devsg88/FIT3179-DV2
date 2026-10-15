# Food-group intake CSVs

## Actual intake

`actual_food_group_intake.csv` contains mean daily serves per person for all persons aged 2 years and over in 2023.

Source: `Raw Data/ADGDC01-05.xlsx`, sheet `Table 2.1_Means`, column L (`Total 2 years and over`), within the Persons section. The source cells are recorded in the CSV. The [official ABS workbook](https://www.abs.gov.au/statistics/health/food-and-nutrition/national-nutrition-and-physical-activity-survey/2023/ADGDC01-05.xlsx) is part of the 2023 survey release.

- Footnote (d) says these means are based on food and beverages reported on a single day of dietary recall. They are daily means, not modelled usual-intake estimates.
- Non-discretionary rows are selected for comparison with dietary recommendations. The separate discretionary and combined-total rows are excluded. "Total 2 years and over" refers to the population column, not the combined food-status rows.
- Five rows are core food groups. Unsaturated spreads and oils are retained as a sixth, non-core group; use `is_core_food_group` to select the five core groups.
- `Lean meats and alternatives` abbreviates the source's meat, poultry, fish, eggs, tofu, nuts, seeds and legumes/beans category. The full source labels are retained in `source_food_group`.
- Values retain the workbook's one-decimal precision. The means are read directly from the population total, not averaged across age groups.
- `NNPASDC05.xlsx` was not used for these CSVs: that workbook reports grams and uses different food categories.

## Recommendations

`recommended_food_group_intake.csv` transcribes all eight demographic/life-stage rows from the user-provided image. Fractional serves are stored as decimals. The age labels are retained as shown, including `70+`; the image does not give age bands for pregnancy or lactation.

- Each demographic group has one row per intake food group. Filter `recommendation_group` to one group before joining on `food_group`.
- The extra `All persons 2+` profile has null targets because the image supplies no combined recommendation for that population. No average across adult targets was invented.
- The image's footnote provides a shared allowance for unsaturated spreads or oils and nuts or seeds: 4 serves (28-40 g) for men under 70, and 2 serves (14-20 g) for women and older men. It does not give a separate oils-only target, so `Unsaturated spreads and oils` has a null target in these files.
- The additional-serves ranges for taller or more active adults are not separate food-group targets and are not added to the five core targets.
- Missing recommendations are the literal text `null`, as requested. CSV has no native null type; convert these entries to actual null values when loading the chart, and do not replace them with zero.

The intake population includes children and adults, while the image's numeric targets describe adult groups. A comparison to a selected adult target must label that target as an adult benchmark; it does not establish whether the overall population meets its dietary recommendations.

Both CSVs use the same `food_group` labels. The chart's actual measure is `mean_daily_serves`; its target measure is `recommended_daily_serves`.
