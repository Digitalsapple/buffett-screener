#test 1
from scoring import score_ROE

def test_roe_scoring():
    assert score_ROE(0.15) == 20
    assert score_ROE(0.10) == 10
    assert score_ROE(0.099) == 0
    assert score_ROE(None) is None

#test 2
from financials import get_unique_periods

def test_latest_filing_selected():
    older = {
        "start": "2023-01-01",
        "end": "2023-12-31",
        "filed": "2024-02-01",
        "val": 100,
    }
    newer = {
        "start": "2023-01-01",
        "end": "2023-12-31",
        "filed": "2024-03-01",
        "val": 120,
    }

    period = ("2023-01-01", "2023-12-31")
    result = get_unique_periods([older, newer])
    assert len(result) == 1
    assert result[period]["val"] == 120
    result_reversed = get_unique_periods([newer, older])
    assert result_reversed[period]["val"] == 120

#test 3
from financials import filter_dates
def test_date_filing():
    original = {
        "start": "2023-01-01",
        "end": "2023-12-31",
        "filed": "2024-02-01",
        "val": 100,
    }

    future_revision = {
        "start": "2023-01-01",
        "end": "2023-12-31",
        "filed": "2024-05-01",
        "val": 999999,
    }

    records = [original, future_revision]
    eligible = filter_dates(records, "2024-04-01")
    unique = get_unique_periods(eligible)
    period = ("2023-01-01", "2023-12-31")
    assert len(eligible) == 1 
    assert unique[period]["val"] == 100