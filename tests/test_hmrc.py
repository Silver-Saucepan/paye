import csv
from decimal import Decimal
import os
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


def get_tax_due(payslips, i):
    hmrc_tax_due = payslips[i].income_tax
    paye_tax_due = paye.tax_due(
        payslips[i],
        Decimal('0.0') if payslips[i].period == 1 else payslips[i - 1].tax_to_date,
    )
    return paye_tax_due, hmrc_tax_due


class test_rest_gen_cumul_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Gen_cumul_mthly.csv', 2026, 'Gen_cumul_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_gen_cumul_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Gen_cumul_wkly.csv', 2026, 'Gen_cumul_wkly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_gen_w1m1_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Gen_W1M1_mthly.csv', 2026, 'Gen_W1M1_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_gen_w1m1_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Gen_W1M1_wkly.csv', 2026, 'Gen_W1M1_wkly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_br_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases('tests/hmrc/2026/rest/BR_monthly.csv', 2026, 'BR_Monthly')

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_br_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases('tests/hmrc/2026/rest/BR_weekly.csv', 2026, 'BR_Weekly')

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_k_cumul_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/K_cumul_mthly.csv', 2026, 'K_cumul_Mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_k_cumul_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/K_cumul_wkly.csv', 2026, 'K_cumul_Wkly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_k_w1m1_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/K_W1M1_mthly.csv', 2026, 'K_W1M1_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_k_w1m1_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases('tests/hmrc/2026/rest/K_W1M1_wkly.csv', 2026, 'K_W1M1_wkly')

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_large_code_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Large_code_mthly.csv', 2026, 'Large_code_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_rest_large_code_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/rest/Large_code_wkly.csv', 2026, 'Large_code_wkly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


################ SCOTTISH TAX CODES #########################


class test_scottish_gen_cumul_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Scottish/Gen_cumul_mthly.csv', 2026, 'Gen_cumul_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_scottish_gen_cumul_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Scottish/Gen_cumul_wkly.csv', 2026, 'Gen_cumul_wkly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_scottish_gen_w1m1_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Scottish/Gen_W1M1_mthly.csv', 2026, 'Gen_W1M1_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_scottish_gen_w1m1_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Scottish/Gen_W1M1_wkly.csv', 2026, 'Gen_W1M1_wkly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_scottish_k_cumul_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Scottish/K_cumul_mthly.csv', 2026, 'K_cumul_Mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_scottish_k_cumul_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Scottish/K_cumul_wkly.csv', 2026, 'K_cumul_Wkly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


################ WELSH TAX CODES #########################


class test_welsh_gen_cumul_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Welsh/Gen_cumul_mthly.csv', 2026, 'Gen_cumul_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_welsh_gen_cumul_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Welsh/Gen_cumul_wkly.csv', 2026, 'Gen_cumul_wkly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_welsh_gen_w1m1_mthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Welsh/Gen_W1M1_mthly.csv', 2026, 'Gen_W1M1_mthly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class test_welsh_gen_w1m1_wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases(
            'tests/hmrc/2026/Welsh/Gen_W1M1_wkly.csv', 2026, 'Gen_W1M1_wkly'
        )

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


def monthly():
    suite = unittest.TestSuite()
    suite.addTest(test_rest_gen_cumul_mthly('test_periods'))
    suite.addTest(test_rest_gen_w1m1_mthly('test_periods'))
    suite.addTest(test_rest_br_mthly('test_periods'))
    suite.addTest(test_rest_k_cumul_mthly('test_periods'))
    suite.addTest(test_rest_k_w1m1_mthly('test_periods'))
    suite.addTest(test_rest_large_code_mthly('test_periods'))
    suite.addTest(test_scottish_gen_cumul_mthly('test_periods'))
    suite.addTest(test_scottish_gen_w1m1_mthly('test_periods'))
    suite.addTest(test_scottish_k_cumul_mthly('test_periods'))
    suite.addTest(test_welsh_gen_cumul_mthly('test_periods'))
    suite.addTest(test_welsh_gen_w1m1_mthly('test_periods'))
    return suite


def weekly():
    suite = unittest.TestSuite()
    suite.addTest(test_rest_gen_cumul_wkly('test_periods'))
    suite.addTest(test_rest_gen_w1m1_wkly('test_periods'))
    suite.addTest(test_rest_br_wkly('test_periods'))
    suite.addTest(test_rest_k_cumul_wkly('test_periods'))
    suite.addTest(test_rest_k_w1m1_wkly('test_periods'))
    suite.addTest(test_rest_large_code_wkly('test_periods'))
    suite.addTest(test_scottish_gen_cumul_wkly('test_periods'))
    suite.addTest(test_scottish_gen_w1m1_wkly('test_periods'))
    suite.addTest(test_scottish_k_cumul_wkly('test_periods'))
    suite.addTest(test_welsh_gen_cumul_wkly('test_periods'))
    suite.addTest(test_welsh_gen_w1m1_wkly('test_periods'))
    return suite


if __name__ == "__main__":
    """Run these tests like this:

    PAYE_PERIOD=monthly python tests/test_hmrc.py
    or
    PAYE_PERIOD=weekly python tests/test_hmrc.py
    """
    runner = unittest.TextTestRunner()
    if os.environ.get('PAYE_PERIOD', 'monthly').lower() == 'monthly':
        runner.run(monthly())
    else:
        runner.run(weekly())
