"""Count fresh-food and ready-to-eat outlets by CLUE neighbourhood.

Run after prepare_melbourne_food_outlets.py, or against its existing formatted
CSV. Uses the source's CLUE small area field, retained as `neighbourhood`.
No spatial reassignment, population weighting or rounding before division.
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    'Supermarkets and groceries': 'Fresh food and groceries',
    'Fruit and vegetable shops': 'Fresh food and groceries',
    'Takeaway food': 'Takeaway',
    'Cafes and restaurants': 'Cafes and restaurants',
    'Other specialised food shops': 'Other specialised food shops',
}


def prepare():
    with (ROOT / 'Formatted Data/melbourne_food_outlets_2024.csv').open(encoding='utf-8-sig', newline='') as f:
        outlets = list(csv.DictReader(f))
    boundaries = json.loads((ROOT / 'topojson files/Melbourne_CLUE_small_areas.geojson').read_text(encoding='utf-8'))
    areas = [feature['properties']['featurenam'] for feature in boundaries['features']]
    assert len(areas) == len(set(areas)), 'Duplicate neighbourhood boundary names'
    assert len(outlets) == len({row['outlet_id'] for row in outlets}), 'Duplicate outlet IDs'
    assert all(row['year'] == '2024' for row in outlets)
    assert {row['neighbourhood'] for row in outlets} <= set(areas), 'Unmatched CLUE small area'
    counts = {area: Counter() for area in areas}
    for row in outlets:
        counts[row['neighbourhood']][GROUPS[row['category']]] += 1
    summary = []
    for area in sorted(areas):
        c = counts[area]
        fresh = c['Fresh food and groceries']
        ready = c['Takeaway'] + c['Cafes and restaurants']
        summary.append({
            'neighbourhood': area,
            'fresh_food_outlets': fresh,
            'takeaway_outlets': c['Takeaway'],
            'cafe_restaurant_outlets': c['Cafes and restaurants'],
            'ready_to_eat_outlets': ready,
            'other_specialised_outlets': c['Other specialised food shops'],
            'total_outlets': sum(c.values()),
            # Empty means undefined, not zero, when there is no denominator.
            'fresh_per_10_ready_to_eat': 10 * fresh / ready if ready else '',
        })
    assert sum(row['total_outlets'] for row in summary) == len(outlets)
    target = ROOT / 'Formatted Data/melbourne_food_access_by_neighbourhood.csv'
    with target.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    fresh = sum(row['fresh_food_outlets'] for row in summary)
    outside = [row for row in summary if row['neighbourhood'] != 'Melbourne (CBD)']
    print(f'{fresh}/{len(outlets)} fresh-food and grocery outlets ({100 * fresh / len(outlets):.1f}%).')
    print(f'{sum(row["fresh_food_outlets"] <= 5 for row in outside)}/{len(outside)} non-CBD neighbourhoods have five or fewer.')
    print(f'{len(summary)} neighbourhoods matched to boundaries; saved {target.name}.')


if __name__ == '__main__':
    prepare()
