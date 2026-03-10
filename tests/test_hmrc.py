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

    def test_period_01(self):
        hmrc_tax_due = self.payslips[0].income_tax
        paye_tax_due = paye.tax_due(self.payslips[0], Decimal('0.00'))
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_02(self):
        hmrc_tax_due = self.payslips[1].income_tax
        paye_tax_due = paye.tax_due(self.payslips[1], self.payslips[0].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_03(self):
        hmrc_tax_due = self.payslips[2].income_tax
        paye_tax_due = paye.tax_due(self.payslips[2], self.payslips[1].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_04(self):
        hmrc_tax_due = self.payslips[3].income_tax
        paye_tax_due = paye.tax_due(self.payslips[3], self.payslips[2].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_05(self):
        hmrc_tax_due = self.payslips[4].income_tax
        paye_tax_due = paye.tax_due(self.payslips[4], self.payslips[3].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_06(self):
        hmrc_tax_due = self.payslips[5].income_tax
        paye_tax_due = paye.tax_due(self.payslips[5], self.payslips[4].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_07(self):
        hmrc_tax_due = self.payslips[6].income_tax
        paye_tax_due = paye.tax_due(self.payslips[6], self.payslips[5].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_08(self):
        hmrc_tax_due = self.payslips[7].income_tax
        paye_tax_due = paye.tax_due(self.payslips[7], self.payslips[6].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_09(self):
        hmrc_tax_due = self.payslips[8].income_tax
        paye_tax_due = paye.tax_due(self.payslips[8], self.payslips[7].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_10(self):
        hmrc_tax_due = self.payslips[9].income_tax
        paye_tax_due = paye.tax_due(self.payslips[9], self.payslips[8].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)


class test_rest_gen_w1m1_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Gen_W1M1_mthly.csv', 2026, 'Gen_W1M1_mthly'
        )

    def test_period_01(self):
        hmrc_tax_due = self.payslips[0].income_tax
        paye_tax_due = paye.tax_due(self.payslips[0], Decimal('0.00'))
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_02(self):
        hmrc_tax_due = self.payslips[1].income_tax
        paye_tax_due = paye.tax_due(self.payslips[1], self.payslips[0].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_03(self):
        hmrc_tax_due = self.payslips[2].income_tax
        paye_tax_due = paye.tax_due(self.payslips[2], self.payslips[1].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_04(self):
        hmrc_tax_due = self.payslips[3].income_tax
        paye_tax_due = paye.tax_due(self.payslips[3], self.payslips[2].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_05(self):
        hmrc_tax_due = self.payslips[4].income_tax
        paye_tax_due = paye.tax_due(self.payslips[4], self.payslips[3].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_06(self):
        hmrc_tax_due = self.payslips[5].income_tax
        paye_tax_due = paye.tax_due(self.payslips[5], self.payslips[4].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_07(self):
        hmrc_tax_due = self.payslips[6].income_tax
        paye_tax_due = paye.tax_due(self.payslips[6], self.payslips[5].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_08(self):
        hmrc_tax_due = self.payslips[7].income_tax
        paye_tax_due = paye.tax_due(self.payslips[7], self.payslips[6].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_09(self):
        hmrc_tax_due = self.payslips[8].income_tax
        paye_tax_due = paye.tax_due(self.payslips[8], self.payslips[7].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_10(self):
        hmrc_tax_due = self.payslips[9].income_tax
        paye_tax_due = paye.tax_due(self.payslips[9], self.payslips[8].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_11(self):
        hmrc_tax_due = self.payslips[10].income_tax
        paye_tax_due = paye.tax_due(self.payslips[10], self.payslips[9].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)


class test_rest_br_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases('tests/hmrc/2026/rest/BR_monthly.csv', 2026, 'BR_Monthly')

    def test_period_01(self):
        hmrc_tax_due = self.payslips[0].income_tax
        paye_tax_due = paye.tax_due(self.payslips[0], Decimal('0.0'))
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_02(self):
        hmrc_tax_due = self.payslips[1].income_tax
        paye_tax_due = paye.tax_due(self.payslips[1], self.payslips[0].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)

    def test_period_03(self):
        hmrc_tax_due = self.payslips[2].income_tax
        paye_tax_due = paye.tax_due(self.payslips[2], self.payslips[1].tax_to_date)
        self.assertEqual(paye_tax_due, hmrc_tax_due)


if __name__ == "__main__":
    unittest.main()
