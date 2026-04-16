import paye
from datetime import date

def test_period_start_dates():
    START_DATES_2026 = (
        date(2026, 4, 6),
        date(2026, 5, 6),
        date(2026, 6, 6),
        date(2026, 7, 6),
        date(2026, 8, 6),
        date(2026, 9, 6),
        date(2026, 10, 6),
        date(2026, 11, 6),
        date(2026, 12, 6),
        date(2027, 1, 6),
        date(2027, 2, 6),
        date(2027, 3, 6),
    )
    for period in range(1, 13):
        assert paye.uk_tax_period_start_date(2026, period) == START_DATES_2026[period-1]
