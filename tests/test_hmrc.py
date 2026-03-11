import csv
from decimal import Decimal
import unittest
import paye


def load_test_cases(
    file_name: str,
    year: int,
    case_type: str,
) -> list[paye.Payslip]:

    field_names = ('type', 'pay', 'pay_to_date', 'tax_code', 'w1m1', 'period', 'tax', 'tax_to_date')

    cases = []

    with open(file_name, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=field_names)
        for row in reader:
            if row['type'] != case_type:
                continue
            period = int(row['period'])
            code = paye.TaxCode(row['tax_code'] + row['w1m1'])
            ptd = Decimal(row['pay_to_date'])
            ttd = Decimal(row['tax_to_date'])
            payslip = paye.Payslip(
                payer_name='', year=year, period=period, code=code, pay_to_date=ptd, tax_to_date=ttd
            )
            payslip.basic_pay = Decimal(row['pay'])
            payslip.income_tax = Decimal(row['tax'])
            cases.append(payslip)

    return cases


class test_rest_gen_cumul_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Gen_cumul_mthly.csv', 2026, 'Gen_cumul_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                hmrc_tax_due = self.payslips[i].income_tax
                paye_tax_due = paye.tax_due(
                    self.payslips[i],
                    Decimal('0.0')
                    if self.payslips[i].period == 1
                    else self.payslips[i - 1].tax_to_date,
                )
                self.assertEqual(paye_tax_due, hmrc_tax_due)


class test_rest_gen_w1m1_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Gen_W1M1_mthly.csv', 2026, 'Gen_W1M1_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                hmrc_tax_due = self.payslips[i].income_tax
                paye_tax_due = paye.tax_due(
                    self.payslips[i],
                    Decimal('0.0')
                    if self.payslips[i].period == 1
                    else self.payslips[i - 1].tax_to_date,
                )
                self.assertEqual(paye_tax_due, hmrc_tax_due)


class test_rest_br_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases('tests/hmrc/2026/rest/BR_monthly.csv', 2026, 'BR_Monthly')

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                hmrc_tax_due = self.payslips[i].income_tax
                paye_tax_due = paye.tax_due(
                    self.payslips[i],
                    Decimal('0.0')
                    if self.payslips[i].period == 1
                    else self.payslips[i - 1].tax_to_date,
                )
                self.assertEqual(paye_tax_due, hmrc_tax_due)


class test_rest_k_cumul_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/K_cumul_mthly.csv', 2026, 'K_cumul_Mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                hmrc_tax_due = self.payslips[i].income_tax
                paye_tax_due = paye.tax_due(
                    self.payslips[i],
                    Decimal('0.0')
                    if self.payslips[i].period == 1
                    else self.payslips[i - 1].tax_to_date,
                )
                self.assertEqual(paye_tax_due, hmrc_tax_due)


class test_rest_k_w1m1_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/K_W1M1_mthly.csv', 2026, 'K_W1M1_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                hmrc_tax_due = self.payslips[i].income_tax
                paye_tax_due = paye.tax_due(
                    self.payslips[i],
                    Decimal('0.0')
                    if self.payslips[i].period == 1
                    else self.payslips[i - 1].tax_to_date,
                )
                self.assertEqual(paye_tax_due, hmrc_tax_due)


class test_rest_large_code_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Large_code_mthly.csv', 2026, 'Large_code_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                hmrc_tax_due = self.payslips[i].income_tax
                paye_tax_due = paye.tax_due(
                    self.payslips[i],
                    Decimal('0.0')
                    if self.payslips[i].period == 1
                    else self.payslips[i - 1].tax_to_date,
                )
                self.assertEqual(paye_tax_due, hmrc_tax_due)


if __name__ == "__main__":
    unittest.main()
