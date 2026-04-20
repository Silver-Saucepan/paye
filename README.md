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
Version 24, dated January 2026

## HMRC Constants

The algorithms use a set of constants that are dependent on tax year
and defined in the Specification.

This package reads the constants from a TOML file 'hmrc.toml'
which needs to be updated for each new tax year.

## Exported Objects

1. the TaxCode class
2. the Payslip class
3. utility functions str_to_decimal and uk_tax_period_start_date

## Usage

Weekly vs Monthly pay is selected by the environment variable PAYE_PERIOD:
PAYE_PERIOD=weekly
or
PAYE_PERIOD=monthly

if unset, monthly is assumed

The inputs are:

1. Your basic pay for the week / month
2. Your tax code for the week / month (as given by HMRC via a letter or your
   Personal Tax Account on gov.uk)
3. Any pay adjustments for the week / month (e.g. bonus)
4. Any payrolled benefits in kind
... and for cumulative tax codes;
5. The tax period number
6. Your total gross pay for the tax year including this week / month
7. The income tax you've paid so far this tax year, NOT including this week/month

Use these to create an instance of the Payslip class

The income tax for this week / month is provided by the income tax property
of the payslip.

## Testing

This module is validated against the test cases provided by HMRC
