import pytest
from altman_zscore.company_profile import CompanyProfile

def test_apple():
    profile = CompanyProfile.from_ticker('AAPL')
    assert profile.industry is not None
    assert profile.is_public is True
    assert profile.is_emerging_market is False
    assert 'tech' in profile.industry.lower() or 'computer' in profile.industry.lower()

def test_sonos():
    profile = CompanyProfile.from_ticker('SONO')
    assert profile.industry is not None
    assert profile.is_public is True
    assert profile.is_emerging_market is False
    assert 'consumer' in profile.industry.lower() or 'electronics' in profile.industry.lower()

def test_baba():
    profile = CompanyProfile.from_ticker('BABA')
    assert profile.industry is not None
    assert profile.is_public is True
    assert profile.is_emerging_market is True
    assert 'e-commerce' in profile.industry.lower() or 'retail' in profile.industry.lower()

def test_tcs():
    profile = CompanyProfile.from_ticker('TCS')
    assert profile.industry is not None
    assert profile.is_public is True
    assert profile.is_emerging_market is True
    assert 'tech' in profile.industry.lower() or 'consult' in profile.industry.lower()

def test_jpm():
    profile = CompanyProfile.from_ticker('JPM')
    assert profile.industry is not None
    assert profile.is_public is True
    assert profile.is_emerging_market is False
    assert 'bank' in profile.industry.lower() or 'financial' in profile.industry.lower()

def test_nio():
    profile = CompanyProfile.from_ticker('NIO')
    assert profile.industry is not None
    assert profile.is_public is True
    assert profile.is_emerging_market is True
    assert 'auto' in profile.industry.lower() or 'vehicle' in profile.industry.lower()
