from decimal import Decimal

import pytest
from fiscalyear import FiscalDateTime

import paye
from paye.paye import TaxCode


def test_invalid_code_raises():
    with pytest.raises(ValueError):
        paye.TaxCode('Z1234L')


def test_non_matching_code_raises():
    with pytest.raises(ValueError):
        paye.TaxCode('1234L$')


def test_no_pay_to_date_raises():

    with pytest.raises(ValueError):
        paye.Payslip(FiscalDateTime(2026, 6, 1), Decimal('100.00'), TaxCode('1257L'))


def test_no_tax_to_date_raises():
    with pytest.raises(ValueError):
        paye.Payslip(
            FiscalDateTime(2026, 6, 1),
            Decimal('100.00'),
            TaxCode('1257L'),
            pay_to_date=Decimal('10'),
        )
