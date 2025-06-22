# Batch script to run Altman Z-Score CLI for multiple sets of companies
# Usage: pwsh.exe -File run_batch_examples.ps1
# Expanded portfolio with 60+ well-known companies across diverse industries
# Groups are ordered to test extremes first (distressed -> growth -> established -> mega-caps)

# Group 1: Distressed/Cyclical Companies (Test extreme cases)
# These should show distress or grey zone Z-Scores
$distressed = @(
    'T', # AT&T (High debt, telecom)
    'UAL', # United Airlines (High leverage)
    'AAL', # American Airlines (High leverage)
    'AMC', # AMC Entertainment (Volatile, meme stock)
    'GME', # GameStop (Volatile, meme stock)
    'CCL', # Carnival Corp (Travel, high leverage)
    'NCLH', # Norwegian Cruise Line (Travel recovery)
    'GE', # General Electric (Turnaround story)
    'F', # Ford Motor (Cyclical, EV transition)
    'GM', # General Motors (Auto, EV transition)
    'X', # United States Steel (Cyclical commodity)
    'FCX', # Freeport-McMoRan (Mining, commodity cycles)
    'BBY', # Best Buy (Retail challenges)
    'M', # Macy's (Department store decline)
    'SONO'    # Sonos (Tech hardware challenges)
)

# Group 2: High-Growth Tech & SaaS Companies
# Test growth companies with varied profitability patterns
$high_growth_tech = @(
    'SNOW', # Snowflake (Data cloud)
    'PLTR', # Palantir (Big data analytics)
    'UBER', # Uber (Gig economy)
    'LYFT', # Lyft (Ride sharing)
    'DASH', # DoorDash (Food delivery)
    'ROKU', # Roku (Streaming platform)
    'DOCU', # DocuSign (Digital transactions)
    'ZM', # Zoom Video (Video communications)
    'DDOG', # Datadog (Cloud monitoring)
    'NET', # Cloudflare (Edge computing)
    'CRWD', # CrowdStrike (Cybersecurity)
    'MDB', # MongoDB (Database)
    'SHOP', # Shopify (E-commerce platform)
    'SQ', # Block (Fintech payments)
    'AFRM', # Affirm (Buy now, pay later)
    'COIN', # Coinbase (Crypto exchange)
    'RBLX', # Roblox (Gaming platform)
    'U', # Unity Software (Gaming engine)
    'TWLO', # Twilio (Communications API)
    'OKTA'  # Okta (Identity management)
)

# Group 3: Established Growth & Consumer Companies
# Mix of consumer brands and established growth companies
$consumer_growth = @(
    'NFLX', # Netflix (Streaming leader)
    'DIS', # Disney (Entertainment)
    'SBUX', # Starbucks (Coffee chain)
    'NKE', # Nike (Athletic apparel)
    'LULU', # Lululemon (Athletic apparel)
    'HD', # Home Depot (Home improvement)
    'LOW', # Lowe's (Home improvement)
    'TGT', # Target (Retail)
    'COST', # Costco (Warehouse retail)
    'WMT', # Walmart (Retail giant)
    'AMGN', # Amgen (Biotech)
    'GILD', # Gilead Sciences (Biotech)
    'MRNA', # Moderna (mRNA vaccines)
    'PFE', # Pfizer (Pharmaceuticals)
    'ABBV', # AbbVie (Pharmaceuticals)
    'TMO', # Thermo Fisher Scientific (Life sciences)
    'DHR', # Danaher (Healthcare/tech)
    'CRM', # Salesforce (CRM software)
    'ADBE', # Adobe (Creative software)
    'PYPL'  # PayPal (Digital payments)
)

# Group 4: Industrial & Infrastructure Companies
# Diverse industrial sectors avoiding financial services
$industrials = @(
    'CAT', # Caterpillar (Heavy machinery)
    'DE', # John Deere (Agricultural equipment)
    'MMM', # 3M (Industrial conglomerate)
    'HON', # Honeywell (Aerospace/industrial tech)
    'GD', # General Dynamics (Defense)
    'LMT', # Lockheed Martin (Defense/aerospace)
    'RTX', # Raytheon Technologies (Aerospace/defense)
    'BA', # Boeing (Aerospace)
    'UPS', # United Parcel Service (Logistics)
    'FDX', # FedEx (Logistics)
    'CSX', # CSX Corporation (Rail transport)
    'UNP', # Union Pacific (Rail transport)
    'WM', # Waste Management (Environmental services)
    'RSG', # Republic Services (Waste management)
    'EMR', # Emerson Electric (Industrial automation)
    'ETN', # Eaton Corporation (Power management)
    'PH', # Parker-Hannifin (Motion/control technologies)
    'ITW', # Illinois Tool Works (Industrial)
    'ROK', # Rockwell Automation (Industrial automation)
    'ADP'  # Automatic Data Processing (Business services)
)

# Group 5: Energy & Utilities (Non-Financial Infrastructure)
# Energy companies and utilities with stable cash flows
$energy_utilities = @(
    'XOM', # Exxon Mobil (Integrated oil)
    'CVX', # Chevron (Integrated oil)
    'COP', # ConocoPhillips (Oil & gas)
    'EOG', # EOG Resources (Oil & gas)
    'PXD', # Pioneer Natural Resources (Shale oil)
    'SLB', # Schlumberger (Oilfield services)
    'HAL', # Halliburton (Oilfield services)
    'KMI', # Kinder Morgan (Pipeline)
    'WMB', # Williams Companies (Pipeline)
    'NEE', # NextEra Energy (Renewable utilities)
    'DUK', # Duke Energy (Utilities)
    'SO', # Southern Company (Utilities)
    'D' # Dominion Energy (Utilities)
    'EXC', # Exelon (Utilities)
    'AEP', # American Electric Power (Utilities)
    'PCG', # PG&E Corporation (California utility)
    'ED', # Consolidated Edison (Northeast utility)
    'AWK', # American Water Works (Water utility)
    'VZ', # Verizon (Telecom infrastructure)
    'TMUS' # T-Mobile (Wireless telecom)
)

# Group 6: Consumer Staples & Healthcare
# Defensive companies with stable demand
$staples_healthcare = @(
    'KO', # Coca-Cola (Beverages)
    'PEP', # PepsiCo (Beverages/snacks)
    'PG', # Procter & Gamble (Consumer goods)
    'UL', # Unilever (Consumer goods)
    'CL', # Colgate-Palmolive (Consumer goods)
    'KMB', # Kimberly-Clark (Consumer products)
    'GIS', # General Mills (Food)
    'K', # Kellogg (Food)
    'HSY', # Hershey (Confectionery)
    'MO', # Altria (Tobacco)
    'PM', # Philip Morris Intl (Tobacco)
    'JNJ', # Johnson & Johnson (Healthcare)
    'UNH', # UnitedHealth Group (Healthcare)
    'CVS', # CVS Health (Healthcare services)
    'WBA', # Walgreens Boots Alliance (Pharmacy)
    'MCK', # McKesson (Healthcare distribution)
    'ABC', # AmerisourceBergen (Healthcare distribution)
    'CAH'  # Cardinal Health
)

# Group 7: Mega-Cap Tech Leaders (FAANG+ and established giants)
# Well-established tech companies - should show safe zone Z-Scores
$mega_cap_tech = @(
    'AAPL', # Apple (Consumer electronics)
    'MSFT', # Microsoft (Software/cloud)
    'GOOGL', # Alphabet Class A (Search/cloud)
    'GOOG', # Alphabet Class C (Search/cloud)
    'AMZN', # Amazon (E-commerce/cloud)
    'META', # Meta Platforms (Social media)
    'TSLA', # Tesla (Electric vehicles)
    'NVDA', # NVIDIA (Semiconductors/AI)
    'AVGO', # Broadcom (Semiconductors)
    'ORCL', # Oracle (Enterprise software)
    'INTC', # Intel (Semiconductors)
    'AMD', # Advanced Micro Devices (Semiconductors)
    'QCOM', # Qualcomm (Mobile chips)
    'TXN', # Texas Instruments (Semiconductors)
    'CSCO', # Cisco Systems (Networking)
    'IBM', # IBM (Enterprise tech/consulting)
    'INTU', # Intuit (Financial software)
    'NOW', # ServiceNow (Enterprise software)
    'PANW', # Palo Alto Networks (Cybersecurity)
    'AMAT'  # Applied Materials (Semiconductor equipment)
)

# Helper to run the CLI for a group with rate limiting
function Invoke-ZScoreBatch($tickers, $groupName) {
    Write-Host "Running Z-Score batch for ${groupName}: $($tickers -join ' ')" -ForegroundColor Cyan
    Write-Host "Processing $($tickers.Count) companies..." -ForegroundColor Yellow
    
    # Redirect stderr to null to suppress 401 errors while keeping progress bars visible
    $env:PYTHONUNBUFFERED = "1"  # Ensure Python output is not buffered
    python build_field_database.py @tickers 2>$null
    python main.py @tickers 2>$null
    
    # Add delay between batches to prevent rate limiting
    Write-Host "Waiting 45 seconds before next batch to prevent rate limiting..." -ForegroundColor Green
    Start-Sleep -Seconds 45
}

# --- MENU-BASED GROUP SELECTION ---
$groups = @{
    '1' = @{ Name = 'Distressed/Cyclical Companies'; Tickers = $distressed }
    '2' = @{ Name = 'High-Growth Tech & SaaS'; Tickers = $high_growth_tech }
    '3' = @{ Name = 'Consumer & Growth Companies'; Tickers = $consumer_growth }
    '4' = @{ Name = 'Industrial & Infrastructure'; Tickers = $industrials }
    '5' = @{ Name = 'Energy & Utilities'; Tickers = $energy_utilities }
    '6' = @{ Name = 'Consumer Staples & Healthcare'; Tickers = $staples_healthcare }
    '7' = @{ Name = 'Mega-Cap Tech Leaders'; Tickers = $mega_cap_tech }
}
# Add an 'All Groups' option (0) combining all tickers
$all_tickers = $distressed + $high_growth_tech + $consumer_growth + $industrials + $energy_utilities + $staples_healthcare + $mega_cap_tech
$groups['0'] = @{ Name = 'All Groups'; Tickers = $all_tickers }

Write-Host "\nSelect portfolio group(s) to run (comma-separated, e.g. 1,3,7):" -ForegroundColor Cyan
foreach ($key in ($groups.Keys | Sort-Object { [int]$_ })) {
    Write-Host ("  $key. " + $groups[$key].Name) -ForegroundColor Yellow
}
$selection = Read-Host "Enter group numbers"
$selectedGroups = $selection -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $groups.ContainsKey($_) }

if ($selectedGroups.Count -eq 0) {
    Write-Host "No valid group selected. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "\nYou selected:" -ForegroundColor Green
foreach ($g in $selectedGroups) {
    Write-Host ("  " + $groups[$g].Name) -ForegroundColor White
}

foreach ($g in $selectedGroups) {
    Invoke-ZScoreBatch $groups[$g].Tickers $groups[$g].Name
}

Write-Host "Batch processing complete! Check the output directories for comprehensive reports." -ForegroundColor Green
Write-Host "Total companies analyzed: $($selectedGroups.Count) group(s)" -ForegroundColor Cyan

# Generate portfolio summary table
Write-Host "Generating portfolio summary table..." -ForegroundColor Yellow
python generate_readme_table.py
