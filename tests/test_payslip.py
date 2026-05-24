# NOTE: These tests run only for PAYE_PERIOD == 'monthly'
# (see conftest.py)

from decimal import Decimal

from fiscalyear import FiscalDate

from paye import DescribedAmount, Payslip, TaxCode


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

def test_pbiks():
    payslip = Payslip(
        pay_date=FiscalDate(2026, 4, 30),
        code=TaxCode('1257L'),
        basic_pay=Decimal('1056.25'),
        pbiks=[DescribedAmount('', Decimal('100.00'))],
        pay_to_date=Decimal('1156.25'),
        tax_to_date_non_inclusive=Decimal(0)
    )
    assert payslip.income_tax == Decimal('21.40')

