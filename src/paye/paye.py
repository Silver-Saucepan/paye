"""An implementation of PAYE income tax rules for England.

In the UK, employees and pensioners usually pay their income tax in
monthly or weekly installments deducted automatically from their pay
throughout the tax year under a scheme called 'PAYE' (Pay As You Earn).

This module provides an implementation of:

    'HMRC Specification for PAYE Tax Table Routines'
    Version 24.0, January 2026

Exported classes:
    TaxCode: Analyses an HMRC tax code
    Payslip: All the data normally shown on a payslip

Exported functions:
    tax_due: calculate tax due


"""

import datetime
import os
import re
import tomllib
from dataclasses import dataclass, field
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from importlib import resources
from typing import Any, Final, final

TAX_CODE_REGEX: Final[str] = (
    r'^(?P<nation>[SC])?(?P<prefix>BR|NT|0T|D|K)?(?P<numeric>\d*)(?P<suffix>[LMNTPY])?[\s/]*(?P<basis>[\w ]*)$'
)
# Meaning of the groups:
# Group 1: Indicates if Scottish (S) or Welsh (C for Cymru) rules apply
# Group 2: The Prefix
#   BR = Basic Rate on whole amount
#   NT = No Tax
#   0T = Personal allowance has been used up or employer doesn't have all the details
#   D = All income taxed at higher or additional rate (which is determined by group 3)
#   K = Negative numeric part
# Group 3: The Numeric Part
# Group 4: The Suffix
#   L = Standard tax free personal allowance applies
#   M = 10% of partner's personal allowance (marriage allowance tax break)
#   N = Some personal allowance passed to partner (marriage allowance tax break)
#   T = "Other calculations" included
#   P = Disused?
#   Y = Disused?
# Group 5: The basis (cumulative vs week 1/month 1)

N_PERIODS = 12 if os.environ.get('PAYE_PERIOD', 'monthly').lower() == 'monthly' else 52


def tax_rates(code: TaxCode, year: int) -> list[Decimal]:
    """Return a list of tax rates for the year/nation"""
    if code.nation == 'S':
        return CONSTANTS[year]['SR']
    elif code.nation == 'C':
        return CONSTANTS[year]['WR']
    else:
        return CONSTANTS[year]['R']


def basic_rate(code: TaxCode, year: int) -> Decimal:
    """Return the basic tax rate applicable"""
    if code.nation == 'S':
        rate_pointer = CONSTANTS[year]['G1']
        return CONSTANTS[year]['SR'][rate_pointer]
    elif code.nation == 'C':
        rate_pointer = CONSTANTS[year]['G2']
        return CONSTANTS[year]['WR'][rate_pointer]
    else:
        rate_pointer = CONSTANTS[year]['G']
        return CONSTANTS[year]['R'][rate_pointer]


def additional_rate(code: TaxCode, year: int) -> Decimal:
    """Return the additionl tax rate applicable"""
    if code.nation == 'S':
        rate_pointer = CONSTANTS[year]['G1'] + 1 + code.d_index()
        return CONSTANTS[year]['SR'][rate_pointer]
    elif code.nation == 'C':
        rate_pointer = CONSTANTS[year]['G2'] + 1 + code.d_index()
        return CONSTANTS[year]['WR'][rate_pointer]
    else:
        rate_pointer = CONSTANTS[year]['G'] + 1 + code.d_index()
        return CONSTANTS[year]['R'][rate_pointer]


@final
class TaxCode:
    """
    Attributes and methods for holding and interrogating HMRC tax codes.

    Attributes:
        nation: 'S', 'C' if Scottish or Welsh, or none if English or NI
        prefix: 'BR', 'NT', '0T', 'D', 'K' or none
        numeric_part: The numbers used to calculate tax-free amount
        suffix: Indicates various conditions like Personal Allowance
        basis: Cumulative or week1/month 1
    """

    def __init__(self, code: str) -> None:
        """Parse a tax code into its component parts and check for unsupported features

        Args:
            code: The tax code as a string

        Raises:
            ValueError if code is not a valid Tax Code
        """
        self.code = code.strip()
        if self.code:
            p = re.compile(TAX_CODE_REGEX)
            r = p.match(self.code)
            if r:
                if r.group('basis') == self.code:
                    raise ValueError(f'Invalid tax code: {self.code}')
                (
                    self.nation,
                    self.prefix,
                    self.numeric_part,
                    self.suffix,
                    self.basis,
                ) = r.groups()
            else:
                raise ValueError(f'Invalid tax code: {self.code}')

    def __str__(self):
        return f"""Tax code {self.code}
    Nation: {self.nation}
    Prefix: {self.prefix}
    Numeric: {self.numeric_part}
    Suffix: {self.suffix}
    Basis: {self.basis}

    BR: {self.is_br()}
    NT: {self.is_nt()}
    D-Index: {self.d_index()}
    W1M1: {self.is_w1m1()}"""

    def is_br(self) -> bool:
        """Return True if it's a basic rate code."""
        return self.prefix == 'BR'

    def is_nt(self) -> bool:
        """Return True if it's a 'No Tax' code."""
        return self.prefix == 'NT'

    def d_index(self) -> int | None:
        """The tax code indicates all income is subject to Higher or Additional rate tax

        Returns:
            An integer that acts as a pointer to the relevant tax rate or None if not applicable
        """
        if self.prefix == 'D' and self.numeric_part:
            return int(self.numeric_part)

    def is_w1m1(self) -> bool:
        """Return True if the code indicates a 'Week 1/Month 1' code."""
        return not self.is_cumulative()

    def is_cumulative(self) -> bool:
        """Return True if the code is a cumulative basis code."""
        return self.basis == '' or 'C' in self.basis.upper()

    def free_pay_w1m1(self) -> Decimal:
        """
        Calculate the Free Pay or Additional Pay for Week 1/Month 1.

        Implementation of algorithm specified in section 4.3.1 of
        "HMRC Specification for PAYE Tax Table Routines".
        """
        numeric = Decimal(self.numeric_part) if self.numeric_part else Decimal('0.00')

        if self.is_br():
            # 5.2 Whole of cumulative pay is to be taxed at basic rate
            free_pay = Decimal('0.00')
        elif self.d_index():
            # Whole of cumulative pay is to be taxed at Higher or Additional rate
            free_pay = Decimal('0.00')
        elif numeric == 0:
            free_pay = Decimal('0.00')
        else:
            # Using the "Note for programmers" method
            # at the end of 4.3.1
            q, r = divmod(numeric - 1, Decimal('500'))
            r += 1
            free_pay_r = ((r * 10 + 9) / N_PERIODS).quantize(
                Decimal('0.01'), rounding=ROUND_CEILING
            )
            free_pay_q = q * (
                Decimal('416.67')
                if os.environ.get('PAYE_PERIOD', 'monthly').lower() == 'monthly'
                else Decimal('96.16')
            )
            free_pay = free_pay_q + free_pay_r
            if self.prefix == 'K':
                free_pay *= -1

        return free_pay


@dataclass
class Payslip:
    """Payslip Model

    Attributes:
        payer_name (str): Name of organisation making payment
        year (int): The calendar year in which the tax year starts
        period (int): The tax period (1 to 52)
        code (TaxCode): The tax code provided by HMRC
        pay_to_date (Decimal): The pay received this tax year (including this period)
        tax_to_date (Decimal): The tax paid this tax year (including this period)
        pbik (Decimal): payrolled benefits in kind

    Properties:
        basic_pay (Decimal): The basic pay
        income_tax (Decimal): The income tax deducted this period
        pay_adjustment (Decimal): Adjustment to basic_pay
        other_deductions (Decimal): Other deductions

    """

    payer_name: str
    year: int
    period: int
    code: TaxCode
    pay_to_date: Decimal
    tax_to_date: Decimal
    pay_date: datetime.date = datetime.date(1970, 1, 1)
    pbik: Decimal = Decimal('0.00')
    total_gross: Decimal = field(init=False, default=Decimal('0.00'))
    total_deductions: Decimal = field(init=False, default=Decimal('0.00'))
    net_pay: Decimal = field(init=False)
    _basic_pay: Decimal = field(init=False)
    _pay_adjustments: list[Decimal] = field(init=False, default_factory=list)
    _income_tax: Decimal = field(init=False)
    _other_deductions: list[Decimal] = field(init=False, default_factory=list)

    # FIXME: _pay_adjustments defaults to zero, total_gross should be read-only
    # clients then have to set basic_pay rather than total_gross.

    @property
    def basic_pay(self) -> Decimal:
        return self._basic_pay

    @basic_pay.setter
    def basic_pay(self, value: Decimal) -> None:
        self._basic_pay = value
        self.total_gross = self._basic_pay + sum(self._pay_adjustments)
        self.net_pay = self.total_gross - self.total_deductions

    @property
    def pay_adjustments(self) -> list[Decimal]:
        return self._pay_adjustments

    @pay_adjustments.setter
    def pay_adjustments(self, value: list[Decimal]) -> None:
        self._pay_adjustments = value
        self.total_gross = self._basic_pay + sum(self._pay_adjustments)
        self.net_pay = self.total_gross - self.total_deductions

    @property
    def income_tax(self) -> Decimal:
        return self._income_tax

    @income_tax.setter
    def income_tax(self, value: Decimal) -> None:
        self._income_tax = value
        self.total_deductions = self._income_tax + sum(self._other_deductions)
        self.net_pay = self.total_gross - self.total_deductions

    @property
    def other_deductions(self) -> list[Decimal]:
        return self._other_deductions

    @other_deductions.setter
    def other_deductions(self, value: list[Decimal]):
        self._other_deductions = value
        self.total_deductions = self._income_tax + sum(self._other_deductions)
        self.net_pay = self.total_gross - self.total_deductions


def uk_tax_period_start_date(tax_year: int, tax_period: int) -> datetime.date:
    """Return the start date of the given monthly tax period in the given tax year

    Args:
        tax_year: The year in which the tax year starts
        tax_period: The tax period number in the range 1 to 12

    Returns:
        The start date of the tax period

    Raises:
        ValueError if tax_period not in range 1..12
    """
    if not 1 <= tax_period <= 12:
        raise ValueError('tax_period must be in the range 1..12')

    q, r = divmod(tax_period + 2, 12)
    return datetime.date(year=tax_year + q, month=r + 1, day=6)


def str_to_decimal(amount: str) -> Decimal:
    """Convert a string to a Decimal by removing unsupported characters

    Note: only partial implements the spec at https://docs.python.org/3/library/decimal.html#decimal.Decimal

    Args:
        amount: The amount represented as a string

    Returns:
        The amount as a Decimal
    """
    if amount == '#N/A':
        return Decimal('NaN')
    return Decimal(re.sub(r'[^+\-.0-9]', '', amount))


def _taxable_pay_to_date(
    period: int,
    code: TaxCode,
    cumulative_pay_to_date: Decimal,
) -> Decimal:
    """Stage 2: Calculation of Taxable Pay to date (section 4.3)."""
    if code.is_nt():
        U_n = cumulative_pay_to_date
    elif code.d_index() is not None:
        U_n = cumulative_pay_to_date
    else:
        # Free pay or Additional pay for Month n
        na_1 = code.free_pay_w1m1() * period

        # 4.3.2 Calculation of Taxable Pay to date, U_n
        U_n = cumulative_pay_to_date - na_1

    return U_n


def _tax_due_to_date(
    year: int,
    period: int,
    code: TaxCode,
    taxable_pay_to_date: Decimal,
) -> Decimal:
    """Stage 3: Calculation of tax due to date (section 4.4)."""
    # 4.4.4 round down to nearest pound
    # Added Decimal('0.00') to restore two decimal points
    T_n = taxable_pay_to_date.quantize(Decimal('0'), rounding=ROUND_FLOOR) + Decimal('0.00')

    if code.is_nt():
        L_n = Decimal('0.00')
    elif taxable_pay_to_date <= 0:
        # 4.3.3 No tax liability if Free Pay exceeds Taxable Pay
        L_n = Decimal('0.00')  # L_n, or Tax due to date is zero
    elif code.is_br():
        # Section 5.4, whole of rounded pay to date taxed at rate G
        L_n = T_n * basic_rate(code, year)
    elif code.d_index() is not None:
        # Section 6: Whole of taxable pay taxed at Higher or Additional rate
        L_n = T_n * additional_rate(code, year)
    else:
        # Threshold values, Definition 9
        cs = [
            C * period / N_PERIODS
            for C in CONSTANTS[year][('S' if code.nation == 'S' else '') + 'C']
        ]

        # Rounded threshold taxes, Definition 10
        vs = [c.quantize(Decimal('0'), rounding=ROUND_CEILING) for c in cs]

        # Threshold taxes, Definition 11
        ks = [
            K * period / N_PERIODS
            for K in CONSTANTS[year][('S' if code.nation == 'S' else '') + 'K']
        ]

        rates = tax_rates(code, year)

        L_n = ks[-1] + (T_n - cs[-1]) * rates[-1]
        for v, k, c, r in zip(vs[1:], ks[0:], cs[0:], rates[1:]):
            if taxable_pay_to_date <= v:
                L_n = k + (T_n - c) * r
                break

        L_n = L_n.quantize(Decimal('0.00'), rounding=ROUND_FLOOR)

    return L_n


def _tax_due_cumulative(
    year: int,
    period: int,
    code: TaxCode,
    p_n: Decimal,
    P_n: Decimal,
    L_n_1: Decimal,
    pbik: Decimal,
) -> Decimal:
    """Calculate the income tax due for cumulative suffix codes and cumulative prefix k."""
    # 4.2 Stage 1 Calculation of Cumulative Pay to date is delegated
    # to the calling function which provides P_n

    # 4.3 Stage 2 Calculation of Taxable Pay to date U_n
    U_n = _taxable_pay_to_date(period=period, code=code, cumulative_pay_to_date=P_n)

    # 4.4 Stage 3 Calculation of tax due to date L_n
    L_n = _tax_due_to_date(period=period, code=code, taxable_pay_to_date=U_n, year=year)

    # 4.5 Stage 4 Calculation of Tax Deduction or Refund
    maxrate = CONSTANTS[year]['M'] * (p_n - pbik)
    l_n = min(
        L_n - L_n_1,
        maxrate,
    ).quantize(Decimal('0.00'), rounding=ROUND_FLOOR)

    return l_n


def _tax_due_w1m1(
    year: int,
    code: TaxCode,
    p_n: Decimal,
    pbik: Decimal,
) -> Decimal:
    """Calculate the tax due on a 'Week 1/Month 1' basis.

    Each payment is treated IN ISOLATION, as if it were the first
    payment of the Income Tax year to be taxed on a normal suffix or
    prefix K code.
    """
    # Stage 1: Taxable pay for the weeek/month, section 8.2
    U_n = p_n - code.free_pay_w1m1()

    # Stage 2: Tax due, section 8.3
    L_n = _tax_due_to_date(year=year, period=1, code=code, taxable_pay_to_date=U_n)
    l_n = L_n - 0
    maxrate = CONSTANTS[year]['M'] * (p_n - pbik)
    l_n = min(
        l_n,
        maxrate,
    ).quantize(Decimal('0.00'), rounding=ROUND_FLOOR)
    return l_n


def tax_due(payslip: Payslip, tax_to_date: Decimal) -> Decimal:
    """Calculate the tax due

    Args:
        payslip: Populated with year, period, code, gross, gross to date and any benefits in kind
        tax_to_date: Income tax already paid in periods up to but not including this payslip

    Returns:
        Income tax due for this tax period

    Raises:
        ValueError: If the HMRC constants are not available for the tax year
    """

    if payslip.total_gross.is_nan():
        return Decimal('NaN')
    if payslip.year not in CONSTANTS:
        raise ValueError(f"HMRC constants for year {payslip.year} is missing")
    if payslip.code.is_cumulative():
        return _tax_due_cumulative(
            year=payslip.year,
            period=payslip.period,
            code=payslip.code,
            p_n=payslip.total_gross,
            P_n=payslip.pay_to_date,
            L_n_1=tax_to_date,
            pbik=payslip.pbik,
        )
    else:
        return _tax_due_w1m1(
            year=payslip.year,
            code=payslip.code,
            p_n=payslip.total_gross,
            pbik=payslip.pbik,
        )


def _constants_from_toml(
    file_name: str = 'hmrc.toml',
) -> dict[int, dict]:
    """Obtains the HMRC constants by parsing a toml file"""
    with resources.files('paye.data').joinpath(file_name).open('rb') as f:
        data = tomllib.load(f, parse_float=Decimal)  # The percentages need to be parsed as Decimals

    constants: dict[int, dict] = {}
    for year, cnsts in data['Common'].items():
        year = int(year)
        constants[year] = {}
        constants[year]['B'] = (
            Decimal('NaN'),
            Decimal(cnsts[0]),
            Decimal(cnsts[1]),
            Decimal(cnsts[2]),
        )
        constants[year]['C'] = (
            # See notes in section 4.4.4 re additional parameter c0
            Decimal('0.00'),
            Decimal(sum(cnsts[0:1])),
            Decimal(sum(cnsts[0:2])),
            Decimal(sum(cnsts[0:3])),
        )
        constants[year]['K'] = (
            # See notes in section 4.4.4 re additional parameter k0
            Decimal('0.00'),
            Decimal(sum([a * b for a, b in zip(cnsts[0:1], cnsts[3:4])])),
            Decimal(sum([a * b for a, b in zip(cnsts[0:2], cnsts[3:5])])),
            Decimal(sum([a * b for a, b in zip(cnsts[0:3], cnsts[3:6])])),
        )
        constants[year]['R'] = (
            Decimal('NaN'),
            Decimal(cnsts[3]),
            Decimal(cnsts[4]),
            Decimal(cnsts[5]),
            Decimal(cnsts[6]),
        )
        constants[year]['G'] = cnsts[7]
        constants[year]['M'] = Decimal(cnsts[8])

    for year, cnsts in data['Scotland'].items():
        year = int(year)
        constants[year]['SB'] = (
            Decimal('NaN'),
            Decimal(cnsts[0]),
            Decimal(cnsts[1]),
            Decimal(cnsts[2]),
            Decimal(cnsts[3]),
            Decimal(cnsts[4]),
        )
        constants[year]['SC'] = (
            # See notes in section 4.4.4 re additional parameter Sc0
            Decimal('0.00'),
            Decimal(sum(cnsts[0:1])),
            Decimal(sum(cnsts[0:2])),
            Decimal(sum(cnsts[0:3])),
            Decimal(sum(cnsts[0:4])),
            Decimal(sum(cnsts[0:5])),
        )
        constants[year]['SK'] = (
            # See notes in section 4.4.4 re additional parameter Sk0
            Decimal('0.00'),
            Decimal(sum([a * b for a, b in zip(cnsts[0:1], cnsts[5:6])])),
            Decimal(sum([a * b for a, b in zip(cnsts[0:2], cnsts[5:7])])),
            Decimal(sum([a * b for a, b in zip(cnsts[0:3], cnsts[5:8])])),
            Decimal(sum([a * b for a, b in zip(cnsts[0:4], cnsts[5:9])])),
            Decimal(sum([a * b for a, b in zip(cnsts[0:5], cnsts[5:10])])),
        )
        constants[year]['SR'] = (
            Decimal('NaN'),
            Decimal(cnsts[5]),
            Decimal(cnsts[6]),
            Decimal(cnsts[7]),
            Decimal(cnsts[8]),
            Decimal(cnsts[9]),
            Decimal(cnsts[10]),
        )
        constants[year]['G1'] = cnsts[11]
        constants[year]['M1'] = Decimal(cnsts[12])

    for year, cnsts in data['Wales'].items():
        year = int(year)
        constants[year]['WK'] = (
            # See notes in section 4.4.4 re additional parameter Wk0
            Decimal('0.00'),
            Decimal(sum([a * b for a, b in zip(constants[year]['B'][1:2], cnsts[0:1])])),
            Decimal(sum([a * b for a, b in zip(constants[year]['B'][1:3], cnsts[0:2])])),
            Decimal(sum([a * b for a, b in zip(constants[year]['B'][1:4], cnsts[0:3])])),
        )
        constants[year]['WR'] = (
            Decimal('NaN'),
            Decimal(cnsts[0]),
            Decimal(cnsts[1]),
            Decimal(cnsts[2]),
            Decimal(cnsts[3]),
        )
        constants[year]['G2'] = cnsts[4]
        constants[year]['M2'] = Decimal(cnsts[5])

    return constants


# Load the constants when the module is imported
CONSTANTS: dict[int, dict[str, Any]] = _constants_from_toml()
