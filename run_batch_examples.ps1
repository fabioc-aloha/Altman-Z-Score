# Batch script to run Altman Z-Score CLI for multiple sets of companies
# Usage: pwsh.exe -File run_batch_examples.ps1
# Groups are ordered to test extremes first (distressed -> tech -> mixed -> healthy)

# Group 1: 11 Notable US Companies With Recent Financial Challenges (But Still Active)
# Test extreme cases first - these should show distress or grey zone Z-Scores
$distressed = @(
    # 'T', # AT&T (High debt)
    # 'UAL', # United Airlines (High leverage)
    # 'AMC', # AMC Entertainment (Volatile, but active)
    # 'GE', # General Electric (Turnaround)
    'F', # Ford Motor (Cyclical, high debt)
    'TUP', # Tupperware (Struggling, but not bankrupt)
    'CCL', # Carnival Corp (Travel, high leverage)
    'AAL', # American Airlines (High leverage)
    'GME', # GameStop (Volatile, meme stock)
    'SONO'   # Sonos (Tech, recent financial challenges)
)

# Group 2: 15 Notable US Tech/Fintech/Early-Stage Companies (Diverse maturities)
# Test growth companies with varied profitability patterns
$tech_us = @(
    'SNOW', # Snowflake (Tech, growth)
    'PLTR', # Palantir (Tech, gov contracts)
    'UBER', # Uber (Tech, high growth)
    'SQ', # Block/Square (Fintech)
    'ROKU', # Roku (Tech, consumer streaming)
    'DOCU', # DocuSign (Tech, SaaS)
    'ZM', # Zoom Video (Tech, SaaS)
    'DDOG', # Datadog (Cloud monitoring)
    'NET', # Cloudflare (Cloud infra)
    'CRWD', # CrowdStrike (Cybersecurity)
    'MDB', # MongoDB (Database, SaaS)
    'SHOP', # Shopify (US-listed, e-commerce)
    'AFRM', # Affirm (Fintech, lending)
    'COIN', # Coinbase (Fintech, crypto)
    'RBLX'  # Roblox (Gaming platform)
)

# Group 3: 10 Companies for Industry Mix (Manufacturing, Services, Finance, Utilities, Retail, Healthcare, Energy, Telecom, Real Estate, Consumer Goods)
# Test diverse industry patterns and model selection
$industry_mix = @(
    'CAT', # Caterpillar (Manufacturing)
    'UNH', # UnitedHealth Group (Healthcare)
    'DUK', # Duke Energy (Utilities)
    'WMT', # Walmart (Retail)
    'GS', # Goldman Sachs (Finance)
    'VZ', # Verizon (Telecom)
    'O', # Realty Income (Real Estate REIT)
    'KO', # Coca-Cola (Consumer Goods)
    'SLB', # Schlumberger (Energy)
    'ADP'  # Automatic Data Processing (Services)
)

# Group 4: 11 Well-Known US Large-Cap Companies (Diverse Industries)
# Test healthy, established companies last - these should show safe zone Z-Scores
$large_caps = @(
    'AAPL', # Apple
    'MSFT', # Microsoft
    'GOOGL', # Alphabet
    'GOOG', # Alphabet (Class C)
    'AMZN', # Amazon
    'META', # Meta Platforms
    'JPM', # JPMorgan Chase
    'JNJ', # Johnson & Johnson
    'TSLA', # Tesla
    'NVDA', # Nvidia
    'PG'     # Procter & Gamble
)

# Helper to run the CLI for a group
function Invoke-ZScoreBatch($tickers, $groupName) {
    Write-Host "Running Z-Score batch for ${groupName}: $($tickers -join ' ')"
    python main.py @tickers
}

# Run all groups (no deduplication) - ordered to test extremes first
Invoke-ZScoreBatch $distressed 'distressed'
# Invoke-ZScoreBatch $tech_us 'tech_us'
Invoke-ZScoreBatch $industry_mix 'industry_mix'
# Invoke-ZScoreBatch $large_caps 'large_caps'

Write-Host "Batch processing complete. Check the output directories for reports."
