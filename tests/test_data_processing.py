import pytest
from datetime import datetime
from altman_zscore.core.data_processing import extract_sic_code_from_industry, filter_valid_quarters

@pytest.mark.parametrize(
    "industry,expected",
    [
        ("Tech - SIC 3571", "3571"),
        ("SIC 1234", "1234"),
        ("Industry SIC 5678 something", "5678"),
        ("No SIC here", None),
        ("", None),
        (None, None),
        ("SIC", None),
        ("SIC ", None),
        ("SIC1234", None),
    ],
)
def test_extract_sic_code_from_industry_cases(industry, expected):
    assert extract_sic_code_from_industry(industry) == expected

def test_filter_valid_quarters_valid():
    fin_info = {
        "quarters": [
            {"period_end": "2024-01-01", "value": 1},
            {"period_end": "2023-01-01", "value": 2},
            {"period_end": "2022-01-01", "value": 3},
        ]
    }
    # Should filter out quarters before 2023-01-01
    result = filter_valid_quarters(fin_info, "2023-01-01")
    assert len(result) == 2
    assert all(datetime.strptime(q["period_end"], "%Y-%m-%d") >= datetime(2023, 1, 1) for q in result)

def test_filter_valid_quarters_invalid_structure():
    # Not a dict
    assert filter_valid_quarters([], "2023-01-01") == []
    # Missing 'quarters' key
    assert filter_valid_quarters({}, "2023-01-01") == []
    # 'quarters' not a list
    assert filter_valid_quarters({"quarters": None}, "2023-01-01") == []
    # 'quarters' is an empty list
    assert filter_valid_quarters({"quarters": []}, "2023-01-01") == []

def test_filter_valid_quarters_missing_period_end():
    fin_info = {
        "quarters": [
            {"value": 1},  # No period_end
            {"period_end": "2024-01-01", "value": 2},
        ]
    }
    result = filter_valid_quarters(fin_info, "2023-01-01")
    assert len(result) == 1
    assert result[0]["period_end"] == "2024-01-01"

def test_filter_valid_quarters_malformed_date():
    fin_info = {
        "quarters": [
            {"period_end": "not-a-date", "value": 1},
            {"period_end": "2024-01-01", "value": 2},
        ]
    }
    # Should skip the malformed date and not raise
    result = filter_valid_quarters(fin_info, "2023-01-01")
    assert len(result) == 1
    assert result[0]["period_end"] == "2024-01-01"

def test_filter_valid_quarters_no_start_date():
    fin_info = {
        "quarters": [
            {"period_end": "2024-01-01", "value": 1},
            {"period_end": "2023-01-01", "value": 2},
        ]
    }
    # Should return all valid quarters if no start_date is given
    result = filter_valid_quarters(fin_info, "")
    assert len(result) == 2
    result = filter_valid_quarters(fin_info, None)
    assert len(result) == 2

def test_filter_valid_quarters_all_invalid():
    fin_info = {
        "quarters": [
            {"period_end": None, "value": None},
            {"period_end": "", "value": 0.0},
            {"period_end": None, "value": ""},
        ]
    }
    result = filter_valid_quarters(fin_info, "2023-01-01")
    assert result == []

def test_filter_valid_quarters_extra_fields():
    fin_info = {
        "quarters": [
            {"period_end": "2024-01-01", "value": 1, "raw_payload": None, "extra": 123},
            {"period_end": "2023-01-01", "value": 2, "raw_payload": None},
        ]
    }
    result = filter_valid_quarters(fin_info, "2023-01-01")
    assert len(result) == 2
    assert all("extra" in q or "raw_payload" in q for q in result)
