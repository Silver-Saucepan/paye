import os

collect_ignore = []
if os.environ.get('PAYE_PERIOD', 'monthly').lower() != 'monthly':
    collect_ignore.append('test_payslip.py')
