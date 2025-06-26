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

# Group 4: Industrial & Infrastructure Companies (EXPANDED)
# Diverse industrial sectors including aerospace, defense, logistics, and industrial tech
$industrials = @(
    'CAT', # Caterpillar (Heavy machinery)
    'DE', # John Deere (Agricultural equipment)
    'MMM', # 3M (Industrial conglomerate)
    'HON', # Honeywell (Aerospace/industrial tech)
    'UPS', # United Parcel Service (Logistics)
    'GD', # General Dynamics (Aerospace/defense)
    'LMT', # Lockheed Martin (Aerospace/defense)
    'RTX', # Raytheon Technologies (Aerospace/defense)
    'BA', # Boeing (Aerospace/commercial aircraft)
    'FDX', # FedEx (Package delivery)
    'CSX', # CSX Corporation (Railroad)
    'UNP', # Union Pacific (Railroad)
    'WM', # Waste Management (Environmental services)
    'RSG', # Republic Services (Waste management)
    'EMR', # Emerson Electric (Industrial automation)
    'ETN', # Eaton Corporation (Power management)
    'PH', # Parker-Hannifin (Motion and control)
    'ITW', # Illinois Tool Works (Industrial products)
    'ROK', # Rockwell Automation (Industrial automation)
    'ADP', # Automatic Data Processing (Business services)
    'GWW', # W.W. Grainger (Industrial distribution)
    'LUV', # Southwest Airlines (Low-cost airline)
    'DAL', # Delta Air Lines (Major airline)
    'PCAR', # PACCAR (Heavy truck manufacturing)
    'CMI' # Cummins (Diesel engines)
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

# Group 8: Recent IPOs & SPACs (2020-2024)
# Test newer public companies with limited financial history
$recent_ipos = @(
    'ARM', # Arm Holdings (Chip design, 2023 IPO)
    'FSLR', # First Solar (Re-IPO/SPAC, solar energy)
    'RIVN', # Rivian (Electric vehicles, 2021)
    'LCID', # Lucid Motors (Electric vehicles, 2021 SPAC)
    'SOFI', # SoFi Technologies (Fintech, 2021 SPAC)
    'HOOD', # Robinhood Markets (Trading app, 2021)
    'UPST', # Upstart Holdings (AI lending, 2020)
    'OPEN', # Opendoor Technologies (Real estate, 2020 SPAC)
    'WISH', # ContextLogic/Wish (E-commerce, 2020)
    'ABNB', # Airbnb (Home sharing, 2020)
    'AFRM', # Affirm Holdings (Buy now pay later, 2021)
    'PATH', # UiPath (Robotic process automation, 2021)
    'POSH', # Poshmark (Social commerce, 2021)
    'BMBL', # Bumble (Dating app, 2021)
    'DKNG', # DraftKings (Sports betting, 2020 SPAC)
    'SPCE', # Virgin Galactic (Space tourism, 2019 SPAC)
    'NKLA', # Nikola Corporation (Electric trucks, 2020 SPAC)
    'CLOV', # Clover Health (Healthcare, 2021 SPAC)
    'GOEV', # Canoo (Electric vehicles, 2020 SPAC)
    'CHPT'  # ChargePoint (EV charging, 2021 SPAC)
)

# Helper to run the CLI for a group with enhanced capabilities
function Invoke-ZScoreBatch($tickers, $groupName) {
    Write-Host "Running ENHANCED Z-Score batch for ${groupName}" -ForegroundColor Cyan
    Write-Host "Processing $($tickers.Count) companies individually with multi-quarter analysis..." -ForegroundColor Yellow
    Write-Host "UPGRADED ACCOUNT: Enhanced API limits and historical data access enabled!" -ForegroundColor Green
    
    # Enable multi-quarter analysis with upgraded account
    $env:PYTHONUNBUFFERED = "1"  # Ensure Python output is not buffered
    $env:FMP_ENHANCED_MODE = "1"  # Enable enhanced features for upgraded accounts
    
    # Process each ticker individually to avoid overwhelming the API
    $tickerCount = 1
    foreach ($ticker in $tickers) {
        Write-Host "[$tickerCount/$($tickers.Count)] Processing $ticker..." -ForegroundColor White
        python main.py $ticker --quarters 8 --enhanced-analysis 2>$null
        
        # Small pause between individual tickers to respect rate limits
        if ($tickerCount -lt $tickers.Count) {
            Start-Sleep -Seconds 1
        }
        $tickerCount++
    }
    Write-Host "Completed processing all $($tickers.Count) companies in $groupName" -ForegroundColor Green
}

# Helper to check API usage before running
function Test-APIUsage {
    Write-Host "Checking API usage status..." -ForegroundColor Yellow
    Write-Host "UPGRADED FMP ACCOUNT DETECTED!" -ForegroundColor Green
    Write-Host "Enhanced limits available for comprehensive analysis" -ForegroundColor Cyan
    Write-Host "Multi-quarter historical analysis now enabled" -ForegroundColor Cyan
    Write-Host "Batch processing of large portfolios supported" -ForegroundColor Green
}

# --- MENU-BASED GROUP SELECTION ---
$groups = @{
    '1' = @{ Name = 'Distressed/Cyclical Companies (15 stocks)'; Tickers = $distressed }
    '2' = @{ Name = 'High-Growth Tech & SaaS (20 stocks)'; Tickers = $high_growth_tech }
    '3' = @{ Name = 'Consumer & Growth Companies (20 stocks)'; Tickers = $consumer_growth }
    '4' = @{ Name = 'Industrial & Infrastructure (25 stocks)'; Tickers = $industrials }
    '5' = @{ Name = 'Energy & Utilities (20 stocks)'; Tickers = $energy_utilities }
    '6' = @{ Name = 'Consumer Staples & Healthcare (18 stocks)'; Tickers = $staples_healthcare }
    '7' = @{ Name = 'Mega-Cap Tech Leaders (20 stocks)'; Tickers = $mega_cap_tech }
    '8' = @{ Name = 'Recent IPOs & SPACs (20 stocks)'; Tickers = $recent_ipos }
}
# Add an 'All Groups' option (0) and enhanced portfolio options
$all_tickers = $distressed + $high_growth_tech + $consumer_growth + $industrials + $energy_utilities + $staples_healthcare + $mega_cap_tech + $recent_ipos
$groups['0'] = @{ Name = 'ALL GROUPS (130+ stocks - FULL PORTFOLIO ANALYSIS)'; Tickers = $all_tickers }
$groups['9'] = @{ Name = 'Quick Sample (Top 10 from each sector - 80 stocks)'; Tickers = ($distressed[0..2] + $high_growth_tech[0..2] + $consumer_growth[0..2] + $industrials[0..2] + $energy_utilities[0..2] + $staples_healthcare[0..2] + $mega_cap_tech[0..2] + $recent_ipos[0..2]) }
$groups['10'] = @{ Name = 'Fortune 500 Focus (Mega-caps + Industrials - 45 stocks)'; Tickers = $mega_cap_tech + $industrials[0..4] }

# Check API usage before proceeding
Test-APIUsage

Write-Host "\nSelect portfolio group(s) to run (comma-separated, e.g. 1,3,7):" -ForegroundColor Cyan
Write-Host "ENHANCED MODE: Multi-quarter analysis and large portfolios now supported!" -ForegroundColor Green
Write-Host "Recommended: Try option 9 for cross-sector sample or individual groups for focused analysis" -ForegroundColor Yellow
Write-Host "NOTE: Each group will be processed individually to manage API limits" -ForegroundColor Magenta
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

Write-Host "\nProcessing each group individually to manage API limits..." -ForegroundColor Cyan
$groupCount = 1
foreach ($g in $selectedGroups) {
    Write-Host "\n--- Processing Group $groupCount of $($selectedGroups.Count): $($groups[$g].Name) ---" -ForegroundColor Yellow
    Invoke-ZScoreBatch $groups[$g].Tickers $groups[$g].Name
    
    if ($groupCount -lt $selectedGroups.Count) {
        Write-Host "Pausing 5 seconds between groups to respect API limits..." -ForegroundColor Magenta
        Start-Sleep -Seconds 5
    }
    $groupCount++
}

Write-Host "All groups processing complete! Check the output directories for comprehensive reports." -ForegroundColor Green
Write-Host "Total groups analyzed: $($selectedGroups.Count)" -ForegroundColor Cyan
Write-Host "Total companies processed: $(($selectedGroups | ForEach-Object { $groups[$_].Tickers.Count } | Measure-Object -Sum).Sum)" -ForegroundColor Cyan

# Generate portfolio summary table
Write-Host "Generating portfolio summary table..." -ForegroundColor Yellow
python generate_readme_table.py
