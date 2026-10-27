"""Rebuild verified chart inputs from the original ABS workbooks.

Usage: python scripts/prepare_audit_sources.py "C:/FIT3179-DV2/Raw Data"
Requires xlrd (legacy .xls) and openpyxl (.xlsx).
"""
import csv
import json
import sys
from pathlib import Path

import openpyxl
import xlrd

ROOT = Path(__file__).resolve().parents[1]


def prepare(raw):
    centres = json.loads((ROOT / 'sodium_graduated_symbol.vg.json').read_text(encoding='utf-8')).get('datasets', {}).get('state_centres')
    # Coordinates are the existing map centres; offsets are screen pixels.
    if centres is None:
        with (ROOT / 'Formatted Data/Australian_Sodium_Potassium_19plus.csv').open(encoding='utf-8-sig') as f:
            centres = [dict(state=r['State/Territory'], **{k: r[k] for k in ['longitude', 'latitude', 'abbr']}) for r in csv.DictReader(f)]
    records = []
    for centre in centres:
        state = centre['state']
        matches = []
        for path in (raw / 'chloropleth map data (discret vs non discret)').glob('*.xls'):
            book = xlrd.open_workbook(str(path))
            if book.sheet_by_name('Table1.1').cell_value(1, 0).endswith(state):
                matches.append((path, book))
        assert len(matches) == 1, (state, len(matches))
        path, book = matches[0]
        estimate, error = book.sheet_by_name('Table1.1'), book.sheet_by_name('Table1.2')
        assert 'Persons' in estimate.row_values(103)
        assert 'Persons' in error.row_values(103)
        assert estimate.cell_value(5, 3) == '19 and over'
        record = {'State/Territory': state}
        for nutrient, row in [('Sodium', 145), ('Potassium', 143)]:
            assert nutrient in estimate.cell_value(row, 0)
            assert nutrient in error.cell_value(row, 0)
            value, rse = estimate.cell_value(row, 3), error.cell_value(row, 3)
            record[f'{nutrient} Intake (mg) - 19 and over'] = value
            record[f'{nutrient} RSE (%)'] = rse
            record[f'{nutrient} MOE (mg)'] = round(1.96 * rse / 100 * value, 6)
        record.update({k: centre[k] for k in ['longitude', 'latitude', 'abbr']})
        dx, dy, align = {
            'Victoria': (-22, 11, 'right'),
            'New South Wales': (22, -16, 'left'),
            'Australian Capital Territory': (22, 15, 'left'),
            'Tasmania': (22, 10, 'left'),
            'Queensland': (22, 0, 'left'),
        }.get(state, (22, 0, 'left'))
        record.update(labelDx=dx, labelDy=dy, labelAlign=align, source_workbook=path.name)
        records.append(record)
    write_csv('Australian_Sodium_Potassium_19plus.csv', records)

    book = openpyxl.load_workbook(raw / 'household food security.xlsx', read_only=True, data_only=True)
    estimates, errors = book['Table 13.3_Proportions'], book['Table 13.4_MoEs']
    records = []
    names = ['Lowest income', 'Lower-middle income', 'Middle income', 'Upper-middle income', 'Highest income']
    for row, name in zip(range(18, 23), names):
        for status, col in [('Food secure', 'B'), ('Experienced food insecurity', 'G')]:
            value, moe = estimates[f'{col}{row}'].value, errors[f'{col}{row}'].value
            records.append({'Income group': name, 'Status': status, 'Share (%)': value,
                            'MOE (percentage points)': moe, 'Lower (%)': round(value - moe, 1),
                            'Upper (%)': round(value + moe, 1)})
    write_csv('Household_Food_Security_Published_Rates.csv', records)


def write_csv(name, records):
    with (ROOT / 'Formatted Data' / name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


if __name__ == '__main__':
    prepare(Path(sys.argv[1]))
