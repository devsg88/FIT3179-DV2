# Verified sources for the audit follow-up

Checked against the supplied workbooks on 27 October 2026. Original estimates retain their precision in the CSV; map labels and tooltips display whole milligrams.

## Sodium and potassium

Source: [ABS Australian Health Survey: Nutrition — State and Territory results, 2011–12](https://www.abs.gov.au/statistics/health/food-and-nutrition/food-and-nutrients-state-and-territory-findings/2011-12), released 10 June 2015. Each state's workbook is named in the CSV's `source_workbook` column.

- Population: Persons (both sexes), aged 19 and over; mean daily Day 1 intake.
- Estimates: `Table1.1`, potassium `D144`, sodium `D146`.
- Relative standard errors: `Table1.2`, potassium `D144`, sodium `D146`.
- Approximate 95% margin of error: `1.96 × RSE / 100 × estimate`. CSV margins retain six decimal places; displayed values are rounded.
- Sodium excludes salt added by consumers during home preparation or at the table.

| State / territory | Sodium RSE (%) | Sodium MOE (± mg) | Potassium RSE (%) | Potassium MOE (± mg) |
| --- | ---: | ---: | ---: | ---: |
| New South Wales | 1.2 | 57 | 1.3 | 75 |
| Victoria | 1.7 | 83 | 1.7 | 96 |
| Queensland | 2.0 | 93 | 1.4 | 80 |
| South Australia | 1.7 | 80 | 1.4 | 78 |
| Western Australia | 1.9 | 90 | 1.5 | 86 |
| Tasmania | 1.7 | 83 | 1.9 | 115 |
| Northern Territory | 3.1 | 147 | 2.6 | 146 |
| Australian Capital Territory | 3.2 | 155 | 2.2 | 127 |

The highest sodium estimate is only 115.7 mg above the lowest, and their approximate intervals overlap. All eight sodium intervals share an overlap. Tasmania's potassium interval (approximately 2,968–3,198 mg) overlaps the ACT's (2,814–3,068 mg). The page therefore avoids asserting a uniquely highest state. Overlapping intervals alone do not constitute a formal pairwise significance test, and they do not prove equality across states.

The sodium reference is the [NHMRC Suggested Dietary Target of 2,000 mg/day](https://www.eatforhealth.gov.au/nutrient-reference-values/nutrients/sodium), introduced in 2017. It is not an Upper Level of Intake, and its population target is defined in terms of median intake. The maps display survey means against this reference for context, not compliance by individuals. The potassium reference is [WHO's adult minimum of 3,510 mg/day](https://www.who.int/tools/elena/interventions/potassium-cvd-adults), not the sex-specific Australian adequate intake.

Both map panels use the identical linear size mapping: domain `[0, 3500]`, range `[0, 900]`. Clamping is explicitly disabled: the 3,510 mg reference ring extrapolates to an area of approximately 902.57 square pixels. This preserves proportionality without silently clipping the WHO benchmark. White inner rings denote the sodium target; teal outer rings denote the potassium minimum. Rings do not encode uncertainty.

## Food security

Source: supplied `household food security.xlsx`, `Table 13.3_Proportions`, rows 18–22: column B (food secure) and G (experienced food insecurity). Published margins of error come from the same cells in `Table 13.4_MoEs`. These agree with the [ABS Food insecurity, 2023 income table](https://www.abs.gov.au/statistics/health/food-and-nutrition/food-insecurity/2023).

The displayed food-insecurity rates, in ascending income order, are **23.2%, 15.3%, 14.3%, 9.7%, 3.6%**. The corresponding food-secure rates are **75.6%, 84.0%, 85.5%, 89.4%, 96.3%**. Paired bars use a common 0–100% scale. These are published proportions, not ratios reconstructed from perturbed counts or rescaled complements. The first-to-last food-insecurity ratio is about 6.4. Thin lines display the published 95% intervals for both series.

Plain-language income labels refer to the original income quintiles. Income is adjusted for household size and composition. Households with income unknown are excluded; each group need not contain exactly 20% of households. The original count CSV is retained but is no longer used by the displayed chart.

## Heatmaps and intake comparisons

The two heatmaps match `Poor-diet-supplementary-tables.xlsx`, `Table S2` and `Table S3`, Persons sections, **2017–18**, sourced there to ABS 2018. They are not 2022 or 2023 observations. The children's 2–3 daily rate is 4.1%; the adult 75+ non-consumption rate is 81.3%.

The intake comparison uses the existing mean-intake CSVs for 2023, from the supplied `ADGDC01-05.xlsx`. Recommendations apply to ages 19–50, while observed groups are 18–29 and 30–49. This mismatch remains disclosed in the caption. The original ABS workbook is linked from that caption.

## Reproduction

Run `python scripts/prepare_audit_sources.py "C:/FIT3179-DV2/Raw Data"` with `xlrd` and `openpyxl` installed to rebuild the nutrient CSV and published food-security-rate CSV. The script validates the Persons heading, age column and nutrient rows before extracting them. Original workbooks are read only.
