# Batch script to run Altman Z-Score CLI for multiple sets of companies
# Usage: pwsh.exe -File run_batch_examples.ps1

# Group 1: 10 well-known US large-cap companies (diverse industries)
$large_caps = @(
    'AAPL',  # Apple
    'MSFT',  # Microsoft
    'GOOGL', # Alphabet
    'AMZN',  # Amazon
    'META',  # Meta Platforms
    'JPM',   # JPMorgan Chase
    'JNJ',   # Johnson & Johnson
    'TSLA',  # Tesla
    'NVDA',  # Nvidia
    'PG'     # Procter & Gamble
)

# Group 2: 10 companies currently struggling or distressed (as of 2025)
$distressed = @(
    'CVNA',  # Carvana
    'RIDEQ', # Lordstown Motors (bankrupt)
    'BBBYQ', # Bed Bath & Beyond (bankrupt)
    'NKLA',  # Nikola
    'FRCB',  # First Republic Bank (failed)
    'TUP',   # Tupperware
    'AMC',   # AMC Entertainment
    'CLOV',  # Clover Health
    'GME',   # GameStop
    'AAL'    # American Airlines (high leverage)
)

# Group 3: 10 tech/AI/EM/early-stage/foreign tickers (to flex mapping and model selection)
$tech_em = @(
    'SNOW',  # Snowflake (tech, high R&D)
    'PLTR',  # Palantir (tech, gov contracts)
    'BIDU',  # Baidu (China, EM)
    'MELI',  # MercadoLibre (LatAm, EM)
    'SHOP',  # Shopify (Canada, tech)
    'ASML',  # ASML (Netherlands, tech)
    'UBER',  # Uber (tech, high growth)
    'SQ',    # Block/Square (fintech)
    'NIO',   # NIO (China, EV, EM)
    'SE'     # Sea Ltd (Singapore, EM)
)

# Group 4: 10 Latin American and Brazilian companies (to flex international/EM/IFRS mapping)
$latam_br = @(
    'VALE',   # Vale S.A. (Brazil)
    'PBR',    # Petrobras (Brazil)
    'ITUB',   # Itaú Unibanco (Brazil)
    'BBD',    # Banco Bradesco (Brazil)
    'GGB',    # Gerdau (Brazil)
    'CRESY',  # Cresud (Argentina)
    'SBS',    # Companhia de Saneamento Basico (Brazil)
    'TAM',    # TAM Linhas Aereas (Brazil, may be delisted)
    'AMX',    # América Móvil (Mexico)
    'EC'      # Ecopetrol (Colombia)
)

# Group 5: 10 European companies (to flex EU/IFRS/region logic)
$europe = @(
    'SAP',    # SAP SE (Germany)
    'SIEGY',  # Siemens AG (Germany)
    'NESN',   # Nestle (Switzerland)
    'RDS.A',  # Shell (UK/Netherlands)
    'SAN',    # Sanofi (France)
    'OR',     # L'Oreal (France)
    'AZN',    # AstraZeneca (UK/Sweden)
    'VOD',    # Vodafone (UK)
    'CS',     # Credit Suisse (Switzerland)
    'BASFY'   # BASF (Germany)
)

# Group 6: 10 Asian companies (to flex Asia/region logic)
$asia = @(
    'TM',     # Toyota Motor (Japan)
    'SONY',   # Sony Group (Japan)
    'HMC',    # Honda Motor (Japan)
    'BABA',   # Alibaba (China)
    'TSM',    # Taiwan Semiconductor (Taiwan)
    'SFTBY',  # SoftBank Group (Japan)
    'INFY',   # Infosys (India)
    'JD',     # JD.com (China)
    'NTES',   # NetEase (China)
    'SAMSUNG' # Samsung Electronics (Korea, GDR/OTC)
)

# Group 7: 10 edge case companies (dual-listed, ADR, recent IPO, delisted, SPAC, etc.)
$edge_cases = @(
    'BRK.A',   # Berkshire Hathaway A (expensive ticker, special handling)
    'GOOG',    # Alphabet Class C (dual class)
    'TCEHY',   # Tencent Holdings (ADR, OTC)
    'ARM',     # Arm Holdings (recent IPO)
    'DWAC',    # Digital World Acquisition Corp (SPAC)
    'LUMN',    # Lumen Technologies (recently delisted)
    'YNDX',    # Yandex (Russian, trading halted)
    'BABA',    # Alibaba (dual listed, HK/US)
    'VIE',     # Veolia Environnement (foreign, Euronext)
    'GME'     # GameStop (meme stock, high volatility)
)

# Group 8: 10 companies for industry mix (manufacturing, services, finance, utilities, retail, healthcare, energy, telecom, real estate, consumer goods)
$industry_mix = @(
    'CAT',    # Caterpillar (Manufacturing)
    'UNH',    # UnitedHealth Group (Healthcare)
    'DUK',    # Duke Energy (Utilities)
    'WMT',    # Walmart (Retail)
    'GS',     # Goldman Sachs (Finance)
    'VZ',     # Verizon (Telecom)
    'O',      # Realty Income (Real Estate REIT)
    'KO',     # Coca-Cola (Consumer Goods)
    'SLB',    # Schlumberger (Energy)
    'ADP'     # Automatic Data Processing (Services)
)

# Remove duplicates across all groups

# Helper to run the CLI for a group
function Invoke-ZScoreBatch($tickers, $groupName) {
    $tickersStr = $tickers -join ','
    $outDir = "output/batch_$groupName"
    if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
    Write-Host "Running Z-Score batch for ${groupName}: ${tickersStr}"
    python main.py --tickers $tickersStr --output $outDir --full-report
}

# Run all groups with true deduplication (each ticker only in its first group)
$seen = @{}
function Get-UniqueGroupTickers($tickers) {
    $result = @()
    foreach ($t in $tickers) {
        if (-not $seen.ContainsKey($t)) {
            $seen[$t] = $true
            $result += $t
        }
    }
    return $result
}

Invoke-ZScoreBatch (Get-UniqueGroupTickers $large_caps) 'large_caps'
Invoke-ZScoreBatch (Get-UniqueGroupTickers $distressed) 'distressed'
Invoke-ZScoreBatch (Get-UniqueGroupTickers $tech_em) 'tech_em'
Invoke-ZScoreBatch (Get-UniqueGroupTickers $latam_br) 'latam_br'
Invoke-ZScoreBatch (Get-UniqueGroupTickers $europe) 'europe'
Invoke-ZScoreBatch (Get-UniqueGroupTickers $asia) 'asia'
Invoke-ZScoreBatch (Get-UniqueGroupTickers $edge_cases) 'edge_cases'
Invoke-ZScoreBatch (Get-UniqueGroupTickers $industry_mix) 'industry_mix'

Write-Host "Batch processing complete. Check the output directories for reports."

# Summarize results for all tickers
$summaryPath = "output/batch_summary.md"
$summaryLines = @()
$summaryLines += "# Batch Run Summary"
$summaryLines += "| Group | Ticker | Success | Model Used | Z-Score | Notes |"
$summaryLines += "|-------|--------|---------|------------|---------|-------|"

$groups = @(
    @{name='large_caps'; tickers=$large_caps},
    @{name='distressed'; tickers=$distressed},
    @{name='tech_em'; tickers=$tech_em},
    @{name='latam_br'; tickers=$latam_br},
    @{name='europe'; tickers=$europe},
    @{name='asia'; tickers=$asia},
    @{name='edge_cases'; tickers=$edge_cases},
    @{name='industry_mix'; tickers=$industry_mix}
)

foreach ($group in $groups) {
    $gname = $group.name
    foreach ($ticker in $group.tickers | Select-Object -Unique) {
        $outDir = "output/batch_$gname"
        $jsonPath = Join-Path $outDir "zscore_${ticker}.json"
        $mdPath = Join-Path $outDir "zscore_${ticker}_zscore_full_report.md"
        $success = $false
        $model = ''
        $zscore = ''
        $notes = ''
        if (Test-Path $jsonPath) {
            try {
                $data = Get-Content $jsonPath | ConvertFrom-Json
                $success = $true
                $model = $data.model_used
                $zscore = $data.zscore
                if ($data.warnings) { $notes = $data.warnings -join '; ' }
            } catch {
                $notes = 'JSON parse error'
            }
        } elseif (Test-Path $mdPath) {
            $notes = 'No JSON, but Markdown report exists'
        } else {
            $notes = 'No output file found'
        }
        $summaryLines += "| $gname | $ticker | $success | $model | $zscore | $notes |"
    }
}
$summaryLines | Set-Content $summaryPath
Write-Host "Summary written to $summaryPath"
