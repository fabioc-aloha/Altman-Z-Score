# Batch script to run Altman Z-Score CLI for multiple sets of companies
# Usage: pwsh.exe -File run_batch_examples.ps1

# Group 1: 10 Well-Known US Large-Cap Companies (Diverse Industries)
$large_caps = @(
    'AAPL', # Apple
    'MSFT', # Microsoft
    'GOOGL', # Alphabet
    'AMZN', # Amazon
    'META', # Meta Platforms
    'JPM', # JPMorgan Chase
    'JNJ', # Johnson & Johnson
    'TSLA', # Tesla
    'NVDA', # Nvidia
    'PG'     # Procter & Gamble
)

# Group 2: 11 Notable US Companies With Recent Financial Challenges (But Still Active)
$distressed = @(
    'T', # AT&T (High debt)
    'UAL', # United Airlines (High leverage)
    'AMC', # AMC Entertainment (Volatile, but active)
    'C', # Citigroup (Historically challenged)
    'GE', # General Electric (Turnaround)
    'F', # Ford Motor (Cyclical, high debt)
    'TUP', # Tupperware (Struggling, but not bankrupt)
    'CCL', # Carnival Corp (Travel, high leverage)
    'AAL', # American Airlines (High leverage)
    'GME', # GameStop (Volatile, meme stock)
    'SONO'   # Sonos (Tech, recent financial challenges)
)

# Group 3: 10 Tech/AI/EM/Early-Stage/Foreign Tickers (To Flex Mapping and Model Selection)
$tech_em = @(
    'SNOW', # Snowflake (Tech, high R&D)
    'PLTR', # Palantir (Tech, gov contracts)
    'BIDU', # Baidu (China, EM)
    'MELI', # MercadoLibre (LatAm, EM)
    'SHOP', # Shopify (Canada, tech)
    'ASML', # ASML (Netherlands, tech)
    'UBER', # Uber (Tech, high growth)
    'SQ', # Block/Square (Fintech)
    'NIO', # NIO (China, EV, EM)
    'SE'     # Sea Ltd (Singapore, EM)
)

# Group 4: 10 Latin American and Brazilian Companies (To Flex International/EM/IFRS Mapping)
$latam_br = @(
    'VALE', # Vale S.A. (Brazil)
    'PBR', # Petrobras (Brazil)
    'ITUB', # Itaú Unibanco (Brazil)
    'BBD', # Banco Bradesco (Brazil)
    'GGB', # Gerdau (Brazil)
    'CRESY', # Cresud (Argentina)
    'SBS', # Companhia de Saneamento Basico (Brazil)
    'AMX', # América Móvil (Mexico)
    'EC', # Ecopetrol (Colombia)
    'SID'    # Companhia Siderúrgica Nacional (Brazil)
)

# Group 5: 10 European Companies (To Flex EU/IFRS/Region Logic)
$europe = @(
    'SAP', # SAP SE (Germany)
    'SIEGY', # Siemens AG (Germany)
    'NESN', # Nestle (Switzerland)
    'SHEL', # Shell (UK/Netherlands)
    'SAN', # Sanofi (France)
    'OR', # L'Oreal (France)
    'AZN', # AstraZeneca (UK/Sweden)
    'VOD', # Vodafone (UK)
    'BASFY', # BASF (Germany)
    'UL'      # Unilever (UK/Netherlands)
)

# Group 6: 10 Asian Companies (To Flex Asia/Region Logic)
$asia = @(
    'TM', # Toyota Motor (Japan)
    'SONY', # Sony Group (Japan)
    'HMC', # Honda Motor (Japan)
    'BABA', # Alibaba (China)
    'TSM', # Taiwan Semiconductor (Taiwan)
    'SFTBY', # SoftBank Group (Japan)
    'INFY', # Infosys (India)
    'JD', # JD.com (China)
    'NTES', # NetEase (China)
    'SAMSUNG' # Samsung Electronics (Korea, GDR/OTC)
)

# Group 7: 10 Companies for Industry Mix (Manufacturing, Services, Finance, Utilities, Retail, Healthcare, Energy, Telecom, Real Estate, Consumer Goods)
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
Invoke-ZScoreBatch $europe 'europe'
Invoke-ZScoreBatch $asia 'asia'
Invoke-ZScoreBatch $industry_mix 'industry_mix'

Write-Host "Batch processing complete. Check the output directories for reports."
