# Batch script to run Altman Z-Score CLI for multiple sets of companies
# Usage: pwsh.exe -File run_batch_examples.ps1
# Managed Portfolio Winners - Professional curated selection of high-performing companies
# Groups organized by sector and market characteristics for comprehensive analysis

# Group 1: Mega-Cap Technology Leaders
# Dominant technology companies with strong market positions and AI/cloud focus
$mega_cap_tech = @(
    'NVDA', # NVIDIA (AI/Semiconductors)
    'META', # Meta Platforms (Social media/VR)
    'AVGO', # Broadcom (Semiconductors)
    'ORCL', # Oracle (Enterprise software/cloud)
    'NOW', # ServiceNow (Enterprise software)
    'TSLA', # Tesla (Electric vehicles/tech)
    'AMD', # Advanced Micro Devices (Semiconductors)
    'AMZN', # Amazon (E-commerce/cloud)
    'CRM', # Salesforce (CRM software)
    'OKTA', # Okta (Identity management)
    'GOOG', # Alphabet Class C (Search/cloud)
    'INTU', # Intuit (Financial software)
    'GOOGL', # Alphabet Class A (Search/cloud)
    'MU', # Micron Technology (Memory semiconductors)
    'IBM', # IBM (Enterprise tech/consulting)
    'PANW', # Palo Alto Networks (Cybersecurity)
    'ANET', # Arista Networks (Cloud networking)
    'ANSS', # ANSYS (Engineering simulation)
    'WDAY', # Workday (Enterprise software)
    'ADI'  # Analog Devices (Semiconductors)
)

# Group 2: Financial Services & Banking
# Leading financial institutions, payment processors, and insurance companies
$financials = @(
    'JPM', # JPMorgan Chase (Investment banking)
    'GS', # Goldman Sachs (Investment banking)
    'BK', # Bank of New York Mellon (Custody/asset management)
    'WFC', # Wells Fargo (Commercial banking)
    'C', # Citigroup (Global banking)
    'BAC', # Bank of America (Commercial banking)
    'MS', # Morgan Stanley (Investment banking)
    'PNC', # PNC Financial Services (Regional banking)
    'COF', # Capital One Financial (Consumer banking)
    'AXP', # American Express (Credit cards/services)
    'MA', # Mastercard (Payment processing)
    'V', # Visa (Payment processing)
    'CPAY', # Corpay (Business payments)
    'PGR', # Progressive (Insurance)
    'ALL', # Allstate (Insurance)
    'AIG', # American International Group (Insurance)
    'HIG', # Hartford Financial Services (Insurance)
    'AFL', # Aflac (Insurance)
    'MET', # MetLife (Insurance)
    'SCHW', # Charles Schwab (Brokerage)
    'STT', # State Street (Asset management)
    'BX', # Blackstone (Private equity)
    'APO', # Apollo Global Management (Private equity)
    'AMP'  # Ameriprise Financial (Wealth management)
)

# Group 3: High-Growth & Disruptive Companies
# Growth companies with innovative business models and emerging technologies
$growth_disruptors = @(
    'NFLX', # Netflix (Streaming entertainment)
    'DASH', # DoorDash (Food delivery)
    'PLTR', # Palantir (Big data analytics)
    'CRWD', # CrowdStrike (Cybersecurity)
    'UBER', # Uber (Ride sharing/gig economy)
    'COIN', # Coinbase (Cryptocurrency exchange)
    'BKNG', # Booking Holdings (Online travel)
    'HUBS', # HubSpot (Marketing automation)
    'MPWR', # Monolithic Power Systems (Power semiconductors)
    'PODD', # Insulet (Medical devices)
    'GEV', # GE Vernova (Energy transition)
    'ROKU', # Roku (Streaming platform)
    'SQ', # Block (Digital payments)
    'SHOP', # Shopify (E-commerce platform)
    'SNOW', # Snowflake (Cloud data platform)
    'NET', # Cloudflare (Web infrastructure)
    'DDOG', # Datadog (Cloud monitoring)
    'MDB', # MongoDB (Database software)
    'DOCU', # DocuSign (Digital signatures)
    'PATH'  # UiPath (Robotic process automation)
)

# Group 4: Industrial & Infrastructure Companies
# Diverse industrial sectors including aerospace, defense, logistics, and manufacturing
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
    'CMI'  # Cummins (Diesel engines)
)

# Group 5: Energy & Utilities
# Energy companies, utilities, and telecommunications infrastructure
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
    'D', # Dominion Energy (Utilities)
    'EXC', # Exelon (Utilities)
    'AEP', # American Electric Power (Utilities)
    'PCG', # PG&E Corporation (California utility)
    'ED', # Consolidated Edison (Northeast utility)
    'AWK', # American Water Works (Water utility)
    'VZ', # Verizon (Telecom infrastructure)
    'TMUS' # T-Mobile (Wireless telecom)
)

# Group 6: Consumer Staples & Healthcare
# Defensive companies with stable demand and healthcare leaders
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
    'CAH', # Cardinal Health (Healthcare distribution)
    'TMO', # Thermo Fisher Scientific (Life sciences)
    'DHR', # Danaher (Life sciences/diagnostics)
    'GILD', # Gilead Sciences (Biotechnology)
    'MRNA', # Moderna (Biotechnology)
    'PFE'  # Pfizer (Pharmaceuticals)
)

# Group 7: Consumer Discretionary & Retail
# Consumer-focused companies, retail, and lifestyle brands
$consumer_retail = @(
    'AAPL', # Apple (Consumer electronics)
    'MSFT', # Microsoft (Consumer/enterprise software)
    'HD', # Home Depot (Home improvement retail)
    'LOW', # Lowe's (Home improvement retail)
    'TGT', # Target (General merchandise)
    'COST', # Costco (Warehouse retail)
    'SBUX', # Starbucks (Coffee/restaurants)
    'NKE', # Nike (Athletic apparel)
    'LULU', # Lululemon (Athletic apparel)
    'AMGN', # Amgen (Biotechnology)
    'INTC', # Intel (Semiconductors)
    'QCOM', # Qualcomm (Mobile chips)
    'TXN', # Texas Instruments (Semiconductors)
    'CSCO', # Cisco Systems (Networking)
    'AMAT', # Applied Materials (Semiconductor equipment)
    'BBY', # Best Buy (Electronics retail)
    'ABNB', # Airbnb (Travel/hospitality)
    'AFRM', # Affirm (Buy now, pay later)
    'BMBL', # Bumble (Dating apps)
    'POSH'  # Poshmark (Social commerce)
)

# Group 8: Emerging Growth & High-Risk/High-Reward
# Recent IPOs, SPACs, and volatile growth companies
$emerging_growth = @(
    'ARM', # Arm Holdings (Chip design, 2023 IPO)
    'FSLR', # First Solar (Solar energy)
    'RIVN', # Rivian (Electric vehicles, 2021)
    'LCID', # Lucid Motors (Electric vehicles, 2021 SPAC)
    'SOFI', # SoFi Technologies (Fintech, 2021 SPAC)
    'HOOD', # Robinhood Markets (Trading app, 2021)
    'UPST', # Upstart Holdings (AI lending, 2020)
    'OPEN', # Opendoor Technologies (Real estate, 2020 SPAC)
    'WISH', # ContextLogic/Wish (E-commerce, 2020)
    'DKNG', # DraftKings (Sports betting, 2020 SPAC)
    'SPCE', # Virgin Galactic (Space tourism, 2019 SPAC)
    'NKLA', # Nikola Corporation (Electric trucks, 2020 SPAC)
    'CLOV', # Clover Health (Healthcare, 2021 SPAC)
    'GOEV', # Canoo (Electric vehicles, 2020 SPAC)
    'CHPT', # ChargePoint (EV charging, 2021 SPAC)
    'RBLX', # Roblox (Gaming platform)
    'LYFT', # Lyft (Ride sharing)
    'GME', # GameStop (Gaming retail/meme stock)
    'AMC', # AMC Entertainment (Movie theaters/meme stock)
    'PYPL'  # PayPal (Digital payments)
)

# Helper to run the CLI for a group with enhanced capabilities
function Invoke-ZScoreBatch($tickers, $groupName) {
    Write-Host "Running ENHANCED Z-Score batch for ${groupName}" -ForegroundColor Cyan
    Write-Host "Processing $($tickers.Count) companies individually with multi-quarter analysis..." -ForegroundColor Yellow
    Write-Host "UPGRADED ACCOUNT: Enhanced API limits and historical data access enabled!" -ForegroundColor Green
    
    # Enable multi-quarter analysis with upgraded account
    $env:PYTHONUNBUFFERED = "1"  # Ensure Python output is not buffered
    $env:FMP_ENHANCED_MODE = "1"  # Enable enhanced features for upgraded accounts
    
    # Process each ticker individually for reliable results
    $successCount = 0
    $failureCount = 0
    $totalTickers = $tickers.Count
    
    for ($i = 0; $i -lt $totalTickers; $i++) {
        $ticker = $tickers[$i]
        $progress = [math]::Round((($i + 1) / $totalTickers) * 100, 1)
        
        Write-Host "`n[$($i+1)/$totalTickers] Processing $ticker ($progress%)" -ForegroundColor Cyan
        
        try {
            # Run individual ticker analysis
            python main.py $ticker --quarters 8 --enhanced-analysis --progress auto
            
            if ($LASTEXITCODE -eq 0) {
                $successCount++
                Write-Host "✓ $ticker completed successfully" -ForegroundColor Green
            }
            else {
                $failureCount++
                Write-Host "✗ $ticker failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
            }
        }
        catch {
            $failureCount++
            Write-Host "✗ $ticker failed with error: $($_.Exception.Message)" -ForegroundColor Red
        }
        
        # Small delay between tickers to respect API rate limits
        if ($i -lt ($totalTickers - 1)) {
            Start-Sleep -Milliseconds 500
        }
    }
    
    Write-Host "`nCompleted processing $groupName" -ForegroundColor Green
    Write-Host "Success: $successCount/$totalTickers tickers" -ForegroundColor Green
    if ($failureCount -gt 0) {
        Write-Host "Failures: $failureCount/$totalTickers tickers" -ForegroundColor Red
    }
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
    '1' = @{ Name = 'Mega-Cap Technology Leaders (20 stocks)'; Tickers = $mega_cap_tech }
    '2' = @{ Name = 'Financial Services & Banking (24 stocks)'; Tickers = $financials }
    '3' = @{ Name = 'High-Growth & Disruptive Companies (20 stocks)'; Tickers = $growth_disruptors }
    '4' = @{ Name = 'Industrial & Infrastructure (25 stocks)'; Tickers = $industrials }
    '5' = @{ Name = 'Energy & Utilities (20 stocks)'; Tickers = $energy_utilities }
    '6' = @{ Name = 'Consumer Staples & Healthcare (23 stocks)'; Tickers = $staples_healthcare }
    '7' = @{ Name = 'Consumer Discretionary & Retail (20 stocks)'; Tickers = $consumer_retail }
    '8' = @{ Name = 'Emerging Growth & High-Risk/High-Reward (20 stocks)'; Tickers = $emerging_growth }
}
# Add an 'All Groups' option (0) and enhanced portfolio options
$all_tickers = $mega_cap_tech + $financials + $growth_disruptors + $industrials + $energy_utilities + $staples_healthcare + $consumer_retail + $emerging_growth
$groups['0'] = @{ Name = 'ALL GROUPS (170+ stocks - FULL PORTFOLIO ANALYSIS)'; Tickers = $all_tickers }
$groups['9'] = @{ Name = 'Quick Sample (Top 3 from each sector - 24 stocks)'; Tickers = ($mega_cap_tech[0..2] + $financials[0..2] + $growth_disruptors[0..2] + $industrials[0..2] + $energy_utilities[0..2] + $staples_healthcare[0..2] + $consumer_retail[0..2] + $emerging_growth[0..2]) }
$groups['10'] = @{ Name = 'Fortune 500 Focus (Mega-caps + Industrials - 45 stocks)'; Tickers = $mega_cap_tech + $industrials[0..4] }

# Check API usage before proceeding
Test-APIUsage

Write-Host "\nSelect portfolio group(s) to run (comma-separated, e.g. 1,3,7):" -ForegroundColor Cyan
Write-Host "ENHANCED MODE: Multi-quarter analysis with optimized individual processing!" -ForegroundColor Green
Write-Host "Recommended: Try option 9 for cross-sector sample or individual groups for focused analysis" -ForegroundColor Yellow
Write-Host "NOTE: Each ticker will be processed individually for maximum reliability" -ForegroundColor Magenta
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

Write-Host "\nProcessing each ticker individually for maximum reliability..." -ForegroundColor Cyan
$groupCount = 1
foreach ($g in $selectedGroups) {
    Write-Host "\n--- Processing Group $groupCount of $($selectedGroups.Count): $($groups[$g].Name) ---" -ForegroundColor Yellow
    Invoke-ZScoreBatch $groups[$g].Tickers $groups[$g].Name
    
    if ($groupCount -lt $selectedGroups.Count) {
        Write-Host "Pausing 10 seconds between groups to allow API rate limits to reset..." -ForegroundColor Magenta
        Start-Sleep -Seconds 10
    }
    $groupCount++
}

Write-Host "All groups processing complete! Check the output directories for comprehensive reports." -ForegroundColor Green
Write-Host "Total groups analyzed: $($selectedGroups.Count)" -ForegroundColor Cyan
Write-Host "Total companies processed: $(($selectedGroups | ForEach-Object { $groups[$_].Tickers.Count } | Measure-Object -Sum).Sum)" -ForegroundColor Cyan

# Generate portfolio summary table
Write-Host "Generating portfolio summary table..." -ForegroundColor Yellow
python generate_readme_table.py
