# PAYE

Partial implementation of UK Income Tax Pay-As-You-Earn algorithms

In the UK, many employees and pensioners pay income tax in weekly
or monthly installments as a deduction on their payslip under a
system known as Pay-As-You-Earn or PAYE.

In this system, His/Her Majesty's Revenue and Customs (HMRC) gives
the employer/pension provider a "Tax Code" which they use to calculate
how much income tax to deduct.

This package partially implements the algorithms for calculating the income tax
due as defined by HMRC in their "SPECIFICATION FOR PAYE TAX TABLE ROUTINES"
Version 24, dated January 2026

## HMRC Constants

The algorithms use a set of constants that are dependent on tax year
and defined in the Specification.

This package reads the constants from a TOML file 'hmrc.toml'
which needs to be updated for each new tax year.

## Not Implemented

1. Scottish and Welsh tax codes
