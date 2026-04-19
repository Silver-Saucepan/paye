import os
import zipfile
from decimal import Decimal

import pandas as pd
import pytest

import paye

ZIP_PATH = 'tests/data/Tax-test-data-examples-2026-27-v1-1.zip'
HEADER_ROW = 4


@pytest.fixture(
    scope='module',
    params=[
        'Gen_cumul-mthly',
        'Gen_W1M1_mthly',
        'BR_monthly',
        'K_cumul_mthly',
        'K_W1M1_mthly',
        'Large_code_mthly',
    ]
    if os.environ.get('PAYE_PERIOD', 'monthly').lower() == 'monthly'
    else [
        'Gen_cumul-wkly',
        'Gen_W1M1_wkly',
        'BR_weekly',
        'K_cumul_wkly',
        'K_W1M1_wkly',
        'Large_code_wkly',
    ],
)
def uk_test_data(request):
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        xlsx = pd.ExcelFile(
            z.open('Tax-test-data-examples-2026-27-v1-1/2026 - 27 rest of UK tax v1.0.xlsx')
        )
        df = pd.read_excel(
            xlsx,
            sheet_name=request.param,
            header=HEADER_ROW,
            names=[
                'type_freq',
                'gross',
                'gross_to_date',
                'code',
                'w1m1',
                'period',
                'tax_due',
                'tax_due_to_date',
            ],
            nrows=3,
        )
        df['period'].astype('Int64')
        df['gross'] = df['gross'].apply(lambda x: Decimal(str(x)).quantize(Decimal('0.00')))
        df['gross_to_date'] = df['gross_to_date'].apply(
            lambda x: Decimal(str(x)).quantize(Decimal('0.00'))
        )
        df['tax_due'] = df['tax_due'].apply(lambda x: Decimal(str(x)).quantize(Decimal('0.00')))
        df['tax_due_to_date'] = df['tax_due_to_date'].apply(
            lambda x: Decimal(str(x)).quantize(Decimal('0.00'))
        )
        df['w1m1'] = df['w1m1'].fillna('')
        df = df.dropna()
    return df


@pytest.fixture(
    scope='module',
    params=[
        'Gen_cumul_mthly',
        'Gen_W1M1_mthly',
        'K_cumul_mthly',
    ]
    if os.environ.get('PAYE_PERIOD', 'monthly').lower() == 'monthly'
    else [
        'Gen_cumul_wkly',
        'Gen_W1M1_wkly',
        'K_cumul_wkly',
    ],
)
def scotland_test_data(request):
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        xlsx = pd.ExcelFile(
            z.open('Tax-test-data-examples-2026-27-v1-1/2026 - 27 Scottish tax v1.1.xlsx')
        )
        df = pd.read_excel(
            xlsx,
            sheet_name=request.param,
            header=HEADER_ROW,
            names=[
                'type_freq',
                'gross',
                'gross_to_date',
                'code',
                'w1m1',
                'period',
                'tax_due',
                'tax_due_to_date',
            ],
            nrows=3,
        )
        df['period'].astype('Int64')
        df['gross'] = df['gross'].apply(lambda x: Decimal(str(x)).quantize(Decimal('0.00')))
        df['gross_to_date'] = df['gross_to_date'].apply(
            lambda x: Decimal(str(x)).quantize(Decimal('0.00'))
        )
        df['tax_due'] = df['tax_due'].apply(lambda x: Decimal(str(x)).quantize(Decimal('0.00')))
        df['tax_due_to_date'] = df['tax_due_to_date'].apply(
            lambda x: Decimal(str(x)).quantize(Decimal('0.00'))
        )
        df['w1m1'] = df['w1m1'].fillna('')
        df = df.dropna()
    return df

@pytest.fixture(
    scope='module',
    params=[
        'Gen_cumul_mthly',
        'Gen_W1M1_mthly',
    ]
    if os.environ.get('PAYE_PERIOD', 'monthly').lower() == 'monthly'
    else [
        'Gen_cumul_wkly',
        'Gen_W1M1_wkly',
    ],
)
def wales_test_data(request):
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        xlsx = pd.ExcelFile(
            z.open('Tax-test-data-examples-2026-27-v1-1/2026- 27 Welsh tax v1.0.xlsx')
        )
        df = pd.read_excel(
            xlsx,
            sheet_name=request.param,
            header=HEADER_ROW,
            names=[
                'type_freq',
                'gross',
                'gross_to_date',
                'code',
                'w1m1',
                'period',
                'tax_due',
                'tax_due_to_date',
            ],
            nrows=3,
        )
        df['period'].astype('Int64')
        df['gross'] = df['gross'].apply(lambda x: Decimal(str(x)).quantize(Decimal('0.00')))
        df['gross_to_date'] = df['gross_to_date'].apply(
            lambda x: Decimal(str(x)).quantize(Decimal('0.00'))
        )
        df['tax_due'] = df['tax_due'].apply(lambda x: Decimal(str(x)).quantize(Decimal('0.00')))
        df['tax_due_to_date'] = df['tax_due_to_date'].apply(
            lambda x: Decimal(str(x)).quantize(Decimal('0.00'))
        )
        df['w1m1'] = df['w1m1'].fillna('')
        df = df.dropna()
    return df

def test_uk(uk_test_data):
    for test_case in uk_test_data.itertuples():
        tax_code = paye.TaxCode(test_case.code)
        payslip = paye.Payslip(
            2026,
            test_case.gross,
            tax_code,
            period=test_case.period,
            pay_to_date=test_case.gross_to_date,
        )
        tax_due = paye.tax_due(payslip, test_case.tax_due_to_date - test_case.tax_due)
        assert tax_due == test_case.tax_due

def test_scotland(scotland_test_data):
    for test_case in scotland_test_data.itertuples():
        tax_code = paye.TaxCode(test_case.code)
        payslip = paye.Payslip(
            2026,
            test_case.gross,
            tax_code,
            period=test_case.period,
            pay_to_date=test_case.gross_to_date,
        )
        tax_due = paye.tax_due(payslip, test_case.tax_due_to_date - test_case.tax_due)
        assert tax_due == test_case.tax_due

def test_wales(wales_test_data):
    for test_case in wales_test_data.itertuples():
        tax_code = paye.TaxCode(test_case.code)
        payslip = paye.Payslip(
            2026,
            test_case.gross,
            tax_code,
            period=test_case.period,
            pay_to_date=test_case.gross_to_date,
        )
        tax_due = paye.tax_due(payslip, test_case.tax_due_to_date - test_case.tax_due)
        assert tax_due == test_case.tax_due
