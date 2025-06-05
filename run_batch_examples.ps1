# Batch script to run Altman Z-Score CLI for multiple sets of companies
# Usage: pwsh.exe -File run_batch_examples.ps1

# Group 1: 10 well-known US large-cap companies (diverse industries)
$large_caps = @(
    'AAPL',  # Apple
    'MSFT',  # Microsoft
    'SONO',  # Sonos (tech, high R&D)
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

# Helper to run the CLI for a group
function Invoke-ZScoreBatch($tickers, $groupName) {
    Write-Host "Running Z-Score batch for ${groupName}: $($tickers -join ' ')"
    python main.py --start 2024-01-01 @tickers
}

# Run all groups (no deduplication)
Invoke-ZScoreBatch $large_caps 'large_caps'
Invoke-ZScoreBatch $distressed 'distressed'
Invoke-ZScoreBatch $tech_em 'tech_em'
Invoke-ZScoreBatch $latam_br 'latam_br'
# Invoke-ZScoreBatch $europe 'europe'
# Invoke-ZScoreBatch $asia 'asia'
# Invoke-ZScoreBatch $edge_cases 'edge_cases'
# Invoke-ZScoreBatch $industry_mix 'industry_mix'

Write-Host "Batch processing complete. Check the output directories for reports."
