# PAYE

Implementation of UK Income Tax Pay-As-You-Earn algorithms

In the UK, many employees and pensioners pay income tax in weekly
or monthly installments as a deduction on their payslip under a
system known as Pay-As-You-Earn or PAYE.

In this system, His/Her Majesty's Revenue and Customs (HMRC) gives
the employer/pension provider a "Tax Code" which they use to calculate
how much income tax to deduct.

This package implements the algorithms for calculating the income tax
due as defined by HMRC in their "SPECIFICATION FOR PAYE TAX TABLE ROUTINES"
from version 18, dated March 2020 onwards.

## HMRC Constants

The algorithms use a set of constants that are dependent on tax year
and defined in the Specification.

This package reads the constants from a TOML file 'hmrc.toml'
which needs to be updated for each new tax year.

## Exported Objects

1. the TaxCode class
2. the Payslip class
3. utility function str_to_decimal

## Usage

Weekly vs Monthly pay is selected by the environment variable PAYE_PERIOD:
PAYE_PERIOD=weekly
or
PAYE_PERIOD=monthly

if unset, monthly is assumed

The inputs are:

1. The pay date
2. Your basic pay for the week / month
3. Your tax code for the week / month (as given by HMRC via a letter or your
   Personal Tax Account on gov.uk)
4. Any pay adjustments for the week / month (e.g. bonus)
5. Any payrolled benefits in kind
... and for cumulative tax codes;
6. The tax period number
7. Your total gross pay for the tax year including this week / month
8. The income tax you've paid so far this tax year, NOT including this week/month

Use these to create an instance of the Payslip class

The income tax for this week / month is provided by the income tax property
of the payslip.

For example:

``` python
import paye
from decimal import Decimal
from fiscalyear import FiscalDateTime

payslip = paye.Payslip(
  pay_date = FiscalDateTime(2026, 4, 30),
  basic_pay=Decimal('1156.25'),
  code=paye.TaxCode('1257L'),
  pay_to_date=Decimal('1156.25'),
  tax_to_date_non_inclusive=Decimal('0.00')
)
print(f"Income tax due this period = {payslip.income_tax}")

```

## Testing

This module is validated against the test cases provided by HMRC
