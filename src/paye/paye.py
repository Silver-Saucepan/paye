"""
A partial implementation of PAYE income tax rules for England.

In the UK, employees and pensioners usually pay their income tax in
monthly or weekly installments deducted automatically from their pay
throughout the tax year under a scheme called 'PAYE' (Pay As You Earn).

This module provides a partial implementation of:

    'HMRC Specification for PAYE Tax Table Routines'
    Version 23.0, January 2025

Exported classes:
    TaxCode: Analyses an HMRC tax code
    Payslip: All the data normally shown on a payslip

Exported functions:
    tax_due: calculate tax due for monthly income
    constants_from_csv: Obtain HMRC yearly constants from a CSV file
    constants_from_google_sheets: Obtain HMRC yearly constants from Google Sheets

Currently not implemented:
* Weekly pay
* Scottish tax codes
* Welsh tax codes
"""

import csv
import datetime
import os.path
import re
from dataclasses import dataclass, field
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

PROGNOSTICATOR_ID = "180xcr-5WQ_6W4pwSpbxTkwydLfdQUN5nUqut6PufO0E"
HMRC_DATA = "HMRC & ONS Parameters!A4:P"
CONSTANTS = {}

TAX_CODE_REGEX = r'^([SC])?(BR|NT|0T|D|K)?(\d*)([LMNTPY])?[\s/]*(.*)'
# Meaning of the groups:
# Group 1: Indicates if Scottish or Welsh rules apply
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
# Group 5: The basis (cumulative vs week 1/month 1) identified by the following codes

MONTH_1_BASIS_CODES = ('1', '(M1)', 'X')


class TaxCode:
    """
    Attributes and methods for holding and interrogating HMRC tax codes.

    Attributes:
        nation: 'S', 'C' if Scottish or Welsh, or none if English or NI
        prefix: 'BR', 'NT', '0T', 'D', 'K' or none
        numeric_part: The numbers used to calculate tax-free amount
        suffix: Indicates various conditions like Personal Allowance
        basis: Cumulative or month 1
    """

    nation: str | None
    prefix: str | None
    numeric_part: str | None
    suffix: str | None
    basis: str | None

    def __init__(self, code: str) -> None:
        """Parse a Tax Code into its component parts and check for unsupported features."""
        self.code = code.strip()
        if self.code:
            p = re.compile(TAX_CODE_REGEX)
            r = p.match(self.code)
            if r:
                (
                    self.nation,
                    self.prefix,
                    self.numeric_part,
                    self.suffix,
                    self.basis,
                ) = r.groups()
            if self.nation == 'C':
                raise ValueError("Welsh tax codes not currently supported")
            if self.nation == 'S':
                raise ValueError("Scottish tax codes not currently supported")

    def __str__(self):
        return str(
            (
                self.nation,
                self.prefix,
                self.numeric_part,
                self.suffix,
                self.basis,
            )
        )

    def is_br(self) -> bool:
        """Return True if it's a basic rate code."""
        return self.prefix == 'BR'

    def is_nt(self) -> bool:
        """Return True if it's a 'No Tax' code."""
        return self.prefix == 'NT'

    def is_na(self) -> bool:
        """Return True if the code is '#N/A'."""
        return self.code == '#N/A'

    def d_index(self) -> int | None:
        """
        If the code prefix is 'D' indicating all income is to be taxed
        at the Higher or Additional tax rate, return the following
        character as an integer which says which rate to use.
        Otherwise, return None
        """
        if self.prefix == 'D':
            if self.numeric_part:
                return int(self.numeric_part)
        return None

    def is_month1(self) -> bool:
        """Return True if the code indicates a 'Month 1' code."""
        # HMRC and individual payroll systems use different suffixes to
        # indicate month 1
        return self.basis in MONTH_1_BASIS_CODES

    def is_cumulative(self) -> bool:
        """Return True if the code does not indicate a 'Month 1' code."""
        return not self.is_month1()

    def free_pay_m1(self) -> Decimal:
        """
        Calculate the Free Pay or Additional Pay for Month 1.

        Implementation of algorithm specified in section 4.3.1 of
        "HMRC Specification for PAYE Tax Table Routines".
        """
        if self.numeric_part:
            numeric = Decimal(self.numeric_part)
        else:
            numeric = Decimal('0.00')

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
            free_pay_r = ((r * 10 + 9) / 12).quantize(Decimal('0.01'), rounding=ROUND_CEILING)
            free_pay_q = q * Decimal('416.67')
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
        period (int): The tax period (1 to 12)
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
    pay_date: datetime.date
    code: TaxCode
    pay_to_date: Decimal
    tax_to_date: Decimal
    pbik: Decimal = Decimal('0.00')
    total_gross: Decimal = field(init=False, default=Decimal('0.00'))
    total_deductions: Decimal = field(init=False, default=Decimal('0.00'))
    net_pay: Decimal = field(init=False)
    _basic_pay: Decimal = field(init=False)
    _pay_adjustments: list[Decimal] = field(init=False, default_factory=list)
    _income_tax: Decimal = field(init=False)
    _other_deductions: list[Decimal] = field(init=False, default_factory=list)

    @property
    def basic_pay(self) -> Decimal:
        return self._basic_pay

    @basic_pay.setter
    def basic_pay(self, value: Decimal) -> None:
        self._basic_pay = value
        self.total_gross = self.basic_pay + sum(self.pay_adjustments)
        self.net_pay = self.total_gross - self.total_deductions

    @property
    def pay_adjustments(self) -> list[Decimal]:
        return self._pay_adjustments

    @pay_adjustments.setter
    def pay_adjustments(self, value: list[Decimal]) -> None:
        self._pay_adjustments = value
        self.total_gross = self.basic_pay + sum(self.pay_adjustments)
        self.net_pay = self.total_gross - self.total_deductions

    @property
    def income_tax(self) -> Decimal:
        return self._income_tax

    @income_tax.setter
    def income_tax(self, value: Decimal) -> None:
        self._income_tax = value
        self.total_deductions = self.income_tax + sum(self.other_deductions)
        self.net_pay = self.total_gross - self.total_deductions

    @property
    def other_deductions(self) -> list[Decimal]:
        return self._other_deductions

    @other_deductions.setter
    def other_deductions(self, value: list[Decimal]):
        self._other_deductions = value
        self.total_deductions = self.income_tax + sum(self.other_deductions)
        self.net_pay = self.total_gross - self.total_deductions


def uk_tax_period_start_date(tax_year: int, tax_period: int) -> datetime.date:
    """Return the start date of the tax_period in tax_year
    tax_periods in the range 1 to 12
    """
    q, r = divmod(tax_period + 3, 12)
    d = datetime.date(year=tax_year + q, month=r, day=6)
    return d


def str_to_decimal(amount: str) -> Decimal:
    """
    Remove characters from 'amount' that are not allowed in the Decimal
    constructor and return the result as a Decimal. Note: does not fully
    implement the spec at:
    https://docs.python.org/3/library/decimal.html#decimal.Decimal
    """
    if amount == '#N/A':
        return Decimal('NaN')
    return Decimal(re.sub(r'[^+\-.0-9]', '', amount))


def __taxable_pay_to_date(
    period: int,
    code: TaxCode,
    cumulative_pay_to_date: Decimal,
) -> Decimal:
    # pylint: disable=invalid-name
    """Stage 2: Calculation of Taxable Pay to date (section 4.3)."""
    if code.is_nt():
        U_n = cumulative_pay_to_date
    elif code.d_index() is not None:
        U_n = cumulative_pay_to_date
    else:
        # Free pay or Additional pay for Month n
        na_1 = code.free_pay_m1() * period

        # 4.3.2 Calculation of Taxable Pay to date, U_n
        U_n = cumulative_pay_to_date - na_1

    return U_n


def __tax_due_to_date(
    year: int,
    period: int,
    code: TaxCode,
    taxable_pay_to_date: Decimal,
) -> Decimal:
    """Stage 3: Calculation of tax due to date (section 4.4)."""
    # pylint: disable=invalid-name
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
        rate_pointer = CONSTANTS[year]['G']
        L_n = T_n * CONSTANTS[year]['R'][rate_pointer]
    elif code.d_index() is not None:
        # Section 6: Whole of taxable pay taxed at Higher
        # or Additional rate
        rate_pointer = CONSTANTS[year]['G'] + 1 + code.d_index()
        L_n = T_n * CONSTANTS[year]['R'][rate_pointer]
    else:
        # Threshold values, Definition 9
        c = [C * period / 12 for C in CONSTANTS[year]['C']]

        # Rounded threshold taxes, Definition 10
        v = [item.quantize(Decimal('1'), rounding=ROUND_CEILING) for item in c]

        # Threshold taxes, Definition 11
        k = [K * period / 12 for K in CONSTANTS[year]['K']]

        if taxable_pay_to_date <= v[1]:
            # Tax Formula 1
            L_n = k[0] + (T_n - c[0]) * CONSTANTS[year]['R'][1]
        elif taxable_pay_to_date <= v[2]:
            # Tax Formula 2
            L_n = k[1] + (T_n - c[1]) * CONSTANTS[year]['R'][2]
        elif taxable_pay_to_date <= v[3]:
            # Tax Formula 3
            L_n = k[2] + (T_n - c[2]) * CONSTANTS[year]['R'][3]
        else:
            # Tax Formula x + 1
            L_n = k[3] + (T_n - c[3]) * CONSTANTS[year]['R'][4]

    L_n = L_n.quantize(Decimal('0.00'), rounding=ROUND_FLOOR)

    return L_n


def __tax_due_cumulative(
    year: int,
    period: int,
    code: TaxCode,
    p_n: Decimal,
    P_n: Decimal,
    L_n_1: Decimal,
    pbik: Decimal,
) -> Decimal:
    """
    Calculate the income tax due for cumulative suffix codes and
    cumulative prefix k, - employees paid monthly.
    """
    # pylint: disable=invalid-name

    # 4.2 Stage 1 Calculation of Cumulative Pay to date is delegated
    # to the calling function which provides P_n

    # 4.3 Stage 2 Calculation of Taxable Pay to date U_n
    U_n = __taxable_pay_to_date(period=period, code=code, cumulative_pay_to_date=P_n)

    # 4.4 Stage 3 Calculation of tax due to date L_n
    L_n = __tax_due_to_date(period=period, code=code, taxable_pay_to_date=U_n, year=year)

    # 4.5 Stage 4 Calculation of Tax Deduction or Refund
    maxrate = CONSTANTS[year]['M'] * (p_n - pbik)
    l_n = min(
        L_n - L_n_1,
        maxrate,
    ).quantize(Decimal('0.00'), rounding=ROUND_FLOOR)

    return l_n


def __tax_due_month1(
    year: int,
    code: TaxCode,
    p_n: Decimal,
    pbik: Decimal,
) -> Decimal:
    """
    Calculate the tax due on a 'Month 1' basis.

    Each payment is treated IN ISOLATION, as if it were the first
    payment of the Income Tax year to be taxed on a normal suffix or
    prefix K code.
    """
    # pylint: disable=invalid-name
    # Stage 1: Taxable pay for the month, section 8.2
    U_n = p_n - code.free_pay_m1()

    # Stage 2: Tax due, section 8.3
    L_n = __tax_due_to_date(year=year, period=1, code=code, taxable_pay_to_date=U_n)
    l_n = L_n - 0
    maxrate = CONSTANTS[year]['M'] * (p_n - pbik)
    l_n = min(
        l_n,
        maxrate,
    ).quantize(Decimal('0.00'), rounding=ROUND_FLOOR)
    return l_n


def tax_due(payslip: Payslip, tax_to_date: Decimal) -> Decimal | None:
    """Calculate the income tax due for employees paid monthly
    :param payslip: populated with year, period, code, gross, gross to date and
    benefits in kind if any
    :param tax_to_date: Income tax paid up to, but not including, this payslip
    :returns: Income tax due for the tax period
    :raises: ValueError if HMRC constants aren't available
    """
    # pylint: disable=invalid-name
    global CONSTANTS
    if not CONSTANTS:
        CONSTANTS = constants_from_google_sheets()

    if payslip.total_gross.is_nan():
        return Decimal('NaN')
    if payslip.year not in CONSTANTS:
        raise ValueError(f"HMRC constants for year {payslip.year} is missing")
    if payslip.code.is_cumulative():
        return __tax_due_cumulative(
            year=payslip.year,
            period=payslip.period,
            code=payslip.code,
            p_n=payslip.total_gross,
            P_n=payslip.pay_to_date,
            L_n_1=tax_to_date,
            pbik=payslip.pbik,
        )
    else:
        return __tax_due_month1(
            year=payslip.year,
            code=payslip.code,
            p_n=payslip.total_gross,
            pbik=payslip.pbik,
        )


def constants_from_csv(
    file_name: str = 'Income Prognosticator - HMRC & ONS Parameters.csv',
) -> dict[int, dict]:
    """
    Obtains the HMRC constants by parsing a CSV file

    As obtained by downloading from my Income Prognosticator Google
    spreadsheet into the active directory.
    """
    consts: dict[int, dict] = {}
    fieldnames = (
        'Tax year',
        'B_1',
        'B_2',
        'B_3',
        'C_1',
        'C_2',
        'C_3',
        'K_1',
        'K_2',
        'K_3',
        'R_1',
        'R_2',
        'R_3',
        'R_4',
        'G',
        'M',
    )
    with open(file_name, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        for _ in range(3):
            # Skip the header rows
            next(reader)
        for row in reader:
            if '#N/A' in row.values():
                # Only process years when all the data are present
                continue
            tax_year = int(row['Tax year'][-4:])

            consts[tax_year] = {
                'B': (
                    Decimal('0'),
                    str_to_decimal(row['B_1']),
                    str_to_decimal(row['B_2']),
                    str_to_decimal(row['B_3']),
                ),
                'C': (
                    Decimal('0'),
                    str_to_decimal(row['C_1']),
                    str_to_decimal(row['C_2']),
                    str_to_decimal(row['C_3']),
                ),
                'K': (
                    Decimal('0'),
                    str_to_decimal(row['K_1']),
                    str_to_decimal(row['K_2']),
                    str_to_decimal(row['K_3']),
                ),
                'R': (
                    Decimal('0'),
                    str_to_decimal(row['R_1']) / 100,
                    str_to_decimal(row['R_2']) / 100,
                    str_to_decimal(row['R_3']) / 100,
                    str_to_decimal(row['R_4']) / 100,
                ),
                'G': int(row['G']),
                'M': str_to_decimal(row['M']) / 100,
            }
    return consts


def constants_from_google_sheets():
    """
    Obtains the HMRC constants directly from Google Sheets

    From my Income Prognosticator spreadsheet using the Sheets API.
    """
    consts: dict[int, dict] = {}

    creds = None
    # The file token.json stores the user's access and refresh tokens,
    # and is created automatically when the authorization flow completes
    # for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available,
    # let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=PROGNOSTICATOR_ID, range=HMRC_DATA).execute()
        values = result.get("values", [])

        if not values:
            raise ValueError("No data found.")

        for row in values:
            if '#N/A' in row:
                # Only process years when all the data are present
                continue
            tax_year = int(row[0][-4:])

            consts[tax_year] = {
                'B': (
                    Decimal('0'),
                    str_to_decimal(row[1]),
                    str_to_decimal(row[2]),
                    str_to_decimal(row[3]),
                ),
                'C': (
                    Decimal('0'),
                    str_to_decimal(row[4]),
                    str_to_decimal(row[5]),
                    str_to_decimal(row[6]),
                ),
                'K': (
                    Decimal('0'),
                    str_to_decimal(row[7]),
                    str_to_decimal(row[8]),
                    str_to_decimal(row[9]),
                ),
                'R': (
                    Decimal('0'),
                    str_to_decimal(row[10]) / 100,
                    str_to_decimal(row[11]) / 100,
                    str_to_decimal(row[12]) / 100,
                    str_to_decimal(row[13]) / 100,
                ),
                'G': int(row[14]),
                'M': str_to_decimal(row[15]) / 100,
            }

    except HttpError as err:
        print(err)

    return consts
