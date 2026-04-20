from decimal import Decimal
import pytest
import paye
from paye.paye import TaxCode

def test_invalid_code_raises():
    with pytest.raises(ValueError):
        paye.TaxCode('Z1234L')

def test_non_matching_code_raises():
    with pytest.raises(ValueError):
        paye.TaxCode('1234L$')

def test_tax_period_not_in_range_raises():
    with pytest.raises(ValueError):
        paye.uk_tax_period_start_date(2026, 0)

def test_no_period_raises():
    with pytest.raises(ValueError):
        paye.Payslip(2026, Decimal('100.00'), TaxCode('1257L'))

def test_no_pay_to_date_raises():
    with pytest.raises(ValueError):
        paye.Payslip(2026, Decimal('100.00'), TaxCode('1257L'), period=1)

def test_no_tax_to_date_raises():
    with pytest.raises(ValueError):
        paye.Payslip(2026, Decimal('100.00'), TaxCode('1257L'), period=1, pay_to_date=Decimal('10'))

