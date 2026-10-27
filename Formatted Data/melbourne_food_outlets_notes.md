# Melbourne food outlets, 2024

Source: [City of Melbourne, Business establishments location and industry classification](https://data.melbourne.vic.gov.au/explore/dataset/business-establishments-with-address-and-industry-classification/).

The formatted CSV selects census year 2024 and ANZSIC classes 4511 (cafes and restaurants), 4512 (takeaway food services), 4110 (supermarkets and grocery stores), 4129 (other specialised food retailing), and 4122 (fruit and vegetable retailing). It contains 2,592 establishments. Other industries are outside this selection; the map is not a complete inventory of every business selling food.

Run `python scripts/prepare_melbourne_food_outlets.py` from the project directory to reproduce the formatted CSV and the compact `Melbourne_food_outlets_2024.json` from the supplied CSV and TopoJSON exports. The script checks duplicate name/address/industry combinations and verifies that every selected establishment has matching coordinates in both sources. Shared coordinates are retained: multiple businesses may occupy the same property.

Each equal-sized dot represents one establishment at its supplied coordinates. Categories describe business activity, not nutritional quality. The coverage is the City of Melbourne municipality, not metropolitan Melbourne. Density does not measure food consumption, population-adjusted access, or walking distance.

Background: [City of Melbourne CLUE small areas](https://data.melbourne.vic.gov.au/explore/dataset/small-areas-for-census-of-land-use-and-employment-clue/), CC BY, downloaded 25 October 2026. These are CLUE statistical neighbourhoods, not necessarily gazetted suburbs. The boundary export is stored locally as `Melbourne_CLUE_small_areas.geojson`.
