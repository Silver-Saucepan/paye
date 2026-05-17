# NOTE: These tests run only for PAYE_PERIOD == 'monthly'
# (see conftest.py)

from paye import Payslip, TaxCode, DescribedAmount
from decimal import Decimal
from fiscalyear import FiscalDate

def test_total_gross():
    ps = Payslip(
        pay_date=FiscalDate(2026, 4, 6),
        basic_pay=Decimal('1156.25'),
        code=TaxCode('1257L'),
        pay_adjustments=[
            DescribedAmount("Bonus", Decimal('100.00')),
            DescribedAmount("Overtime", Decimal('200.00'))
        ],
        pay_to_date=Decimal('0.00'),
        tax_to_date_non_inclusive=Decimal('0.00')
    )

    assert ps.total_gross == Decimal('1456.25')

def test_total_deductions():
    ps = Payslip(
        pay_date=FiscalDate(2026, 4, 6),
        basic_pay=Decimal('1156.25'),
        code=TaxCode('1257L'),
        pay_adjustments=[
            DescribedAmount("Bonus", Decimal('100.00')),
            DescribedAmount("Overtime", Decimal('200.00'))
        ],
        pay_to_date=Decimal('1156.25'),
        tax_to_date_non_inclusive=Decimal('0.00'),
        other_deductions=[
            DescribedAmount("National Insurance", Decimal('100.00')),
            DescribedAmount("Student Loan", Decimal('200.00')),
        ]
    )

    assert ps.total_deductions == Decimal('321.40')

def test_net_pay():
    ps = Payslip(
        pay_date=FiscalDate(2026, 4, 6),
        basic_pay=Decimal('1156.25'),
        code=TaxCode('1257L'),
        pay_adjustments=[
            DescribedAmount("Bonus", Decimal('100.00')),
            DescribedAmount("Overtime", Decimal('200.00'))
        ],
        pay_to_date=Decimal('1156.25'),
        tax_to_date_non_inclusive=Decimal('0.00'),
        other_deductions=[
            DescribedAmount("National Insurance", Decimal('100.00')),
            DescribedAmount("Student Loan", Decimal('200.00')),
        ]
    )

    assert ps.net_pay == Decimal('1134.85')
