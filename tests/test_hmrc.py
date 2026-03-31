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
    """Load period test data from csv file file_name and return it as a list of Payslips

    The Payslips contain the required result in their income_tax attribute
    """

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


def get_tax_due(payslips: list[paye.Payslip], i: int) -> tuple[Decimal, Decimal]:
    """For the i'th Payslip,  return the calculated tax and the required answer"""
    hmrc_tax_due = payslips[i].income_tax
    paye_tax_due = paye.tax_due(
        payslips[i],
        Decimal('0.0') if payslips[i].period == 1 else payslips[i - 1].tax_to_date,
    )
    return paye_tax_due, hmrc_tax_due


class TestRestGenCumulMthly(unittest.TestCase):
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


class TestRestGenCumulWkly(unittest.TestCase):
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


class TestRestGenW1m1Mthly(unittest.TestCase):
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


class TestRestGenW1m1Wkly(unittest.TestCase):
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


class TestRestBrMthly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases('tests/hmrc/2026/rest/BR_monthly.csv', 2026, 'BR_Monthly')

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class TestRestBrWkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases('tests/hmrc/2026/rest/BR_weekly.csv', 2026, 'BR_Weekly')

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class TestRestKCumulMthly(unittest.TestCase):
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


class TestRestKCumulWkly(unittest.TestCase):
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


class TestRestKW1m1Mthly(unittest.TestCase):
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


class TestRestKW1m1Wkly(unittest.TestCase):
    payslips = []

    def setUp(self) -> None:
        self.payslips = load_test_cases('tests/hmrc/2026/rest/K_W1M1_wkly.csv', 2026, 'K_W1M1_wkly')

    def test_periods(self):
        for i in range(0, len(self.payslips)):
            with self.subTest(i=i):
                paye, hmrc = get_tax_due(self.payslips, i)
                self.assertEqual(paye, hmrc)


class TestRestLargeCodeMthly(unittest.TestCase):
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


class TestRestLargeCodeWkly(unittest.TestCase):
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


class TestScottishGenCumulMthly(unittest.TestCase):
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


class TestScottishGenCumulWkly(unittest.TestCase):
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


class TestScottishGenW1m1Mthly(unittest.TestCase):
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


class TestScottishGenW1m1Wkly(unittest.TestCase):
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


class TestScottishKCumulMthly(unittest.TestCase):
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


class TestScottishKCumulWkly(unittest.TestCase):
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


class TestWelshGenCumulMthly(unittest.TestCase):
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


class TestWelshGenCumulWkly(unittest.TestCase):
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


class TestWelshGenW1m1Mthly(unittest.TestCase):
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


class TestWelshGenW1m1Wkly(unittest.TestCase):
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
    suite.addTest(TestRestGenCumulMthly('test_periods'))
    suite.addTest(TestRestGenW1m1Mthly('test_periods'))
    suite.addTest(TestRestBrMthly('test_periods'))
    suite.addTest(TestRestKCumulMthly('test_periods'))
    suite.addTest(TestRestKW1m1Mthly('test_periods'))
    suite.addTest(TestRestLargeCodeMthly('test_periods'))
    suite.addTest(TestScottishGenCumulMthly('test_periods'))
    suite.addTest(TestScottishGenW1m1Mthly('test_periods'))
    suite.addTest(TestScottishKCumulMthly('test_periods'))
    suite.addTest(TestWelshGenCumulMthly('test_periods'))
    suite.addTest(TestWelshGenW1m1Mthly('test_periods'))
    return suite


def weekly():
    suite = unittest.TestSuite()
    suite.addTest(TestRestGenCumulWkly('test_periods'))
    suite.addTest(TestRestGenW1m1Wkly('test_periods'))
    suite.addTest(TestRestBrWkly('test_periods'))
    suite.addTest(TestRestKCumulWkly('test_periods'))
    suite.addTest(TestRestKW1m1Wkly('test_periods'))
    suite.addTest(TestRestLargeCodeWkly('test_periods'))
    suite.addTest(TestScottishGenCumulWkly('test_periods'))
    suite.addTest(TestScottishGenW1m1Wkly('test_periods'))
    suite.addTest(TestScottishKCumulWkly('test_periods'))
    suite.addTest(TestWelshGenCumulWkly('test_periods'))
    suite.addTest(TestWelshGenW1m1Wkly('test_periods'))
    return suite


if __name__ == "__main__":
    """Run these tests like this:

    PAYE_PERIOD=monthly python tests/test_hmrc.py
    or
    PAYE_PERIOD=weekly python tests/test_hmrc.py
    """
    period = os.environ.get('PAYE_PERIOD', 'monthly').lower()
    runner = unittest.TextTestRunner()
    if period == 'monthly':
        print("Running tests for montly pay, set PAYE_PERIOD=weekly to test weekly pay")
        runner.run(monthly())
    elif period == 'weekly':
        print ("Running tests for weekly pay, set PAYE_PERIOD=monthly to test weekly pay")
        runner.run(weekly())
    else:
        print("PAYE_PERIOD must be weekly or monthly")
