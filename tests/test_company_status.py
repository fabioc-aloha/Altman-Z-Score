import pytest
from altman_zscore.company_status_helpers import check_company_status, handle_special_status, detect_company_region
from altman_zscore.company_status import CompanyStatus


def test_check_company_status_known_bankruptcy():
    status = check_company_status("LEHMQ", CompanyStatusClass=CompanyStatus)
    assert status.is_bankrupt
    assert not status.is_active
    assert status.exists
    assert status.bankruptcy_date == "2008-09-15"
    assert status.status_reason and "bankruptcy" in status.status_reason.lower()

def test_detect_company_region_us():
    info = {"country": "United States"}
    assert detect_company_region(info) == "US"

def test_detect_company_region_em():
    info = {"country": "Brazil"}
    assert detect_company_region(info) == "EM"

def test_handle_special_status_bankrupt(tmp_path, monkeypatch):
    # Patch get_output_dir and write_ticker_not_available to use tmp_path
    monkeypatch.setattr("altman_zscore.utils.paths.get_output_dir", lambda *args, **kwargs: str(tmp_path))
    monkeypatch.setattr("altman_zscore.utils.paths.write_ticker_not_available", lambda ticker, reason=None: None)
    status = CompanyStatus(
        ticker="LEHMQ",
        exists=True,
        is_active=False,
        is_bankrupt=True,
        is_delisted=False,
        last_trading_date=None,
        error_message=None,
        bankruptcy_date="2008-09-15",
        status_reason="Known bankruptcy case (filed on 2008-09-15)",
    )
    should_stop = handle_special_status(status)
    assert should_stop
    # Debug: list files in tmp_path
    print("Files in tmp_path:", list(tmp_path.iterdir()))
    # Check that status.json and error files are created
    import os, json
    assert os.path.exists(str(tmp_path / "status.json"))
    with open(str(tmp_path / "status.json")) as f:
        data = json.load(f)
        assert data["is_bankrupt"]
