# International Company Support Plan

This document outlines the plan to add support for international companies in the Altman Z-Score Analysis tool, with a focus on handling different accounting standards, currencies, and company types.

## Current Scope Limitation (June 2025)

**IMPORTANT**: Currently, this tool is limited to U.S.-based companies only. International companies (including ADRs) are not supported in the current version. This includes companies like INFY (Infosys) which, although listed on NYSE, require additional handling for:
- Form 20-F filings
- IFRS to US GAAP conversion
- ADR ratio calculations
- Emerging market considerations

## Current Limitations

1. **Data Source Limitations**
   - Only supports U.S. GAAP XBRL tags from SEC filings
   - No support for IFRS taxonomy
   - Limited handling of Form 20-F filings
   - No currency conversion support
   - Incomplete handling of API authentication failures
   - Limited support for historical SEC data retrieval

2. **Regional Standards Limitations**
   - Different regional accounting standards not handled
   - No special handling for country-specific reporting requirements
   - Lack of support for country-specific fiscal year conventions
   - Limited understanding of local market contexts

3. **Currency and Economic Limitations**
   - No support for hyperinflationary economies
   - Missing inflation adjustment calculations
   - Limited handling of volatile exchange rates
   - No support for multiple exchange rates (official vs. market rates)
   - Historical currency conversion not implemented

4. **Dual Listing Challenges**
   - No support for primary vs. secondary market listings
   - Missing ADR ratio calculations
   - Limited handling of cross-exchange data
   - Incomplete market data aggregation across exchanges
   - No reconciliation between local and ADR share prices

5. **State-Owned Enterprise Limitations**
   - No support for government ownership structures
   - Missing assessment of strategic importance
   - Limited handling of public service obligations
   - No evaluation of sovereign support or political risks
   - Incomplete integration of SOE-specific reporting standards

## Implementation Plan

### Phase 1: Form 20-F Support (Required for ADRs)

1. Form 20-F Detection and Processing:
   ```python
   FORM_20F_INDICATORS = {
       "form_type": ["20-F", "20F", "20FR12B", "20FR12G"],
       "filing_category": "F-series",
       "company_category": "Foreign Private Issuer"
   }
   ```

2. Required Features:
   - Detect Form 20-F filings vs. standard 10-K/10-Q
   - Handle different filing periods and deadlines
   - Process foreign private issuer status
   - Support longer filing windows
   - Handle different fiscal year conventions

3. Implementation Priority:
   - High: Form 20-F detection and basic processing
   - Medium: Fiscal year alignment
   - Low: Full international filing support

### Phase 2: IFRS Support

1. Add IFRS Taxonomy Support:
   ```python
   IFRS_TO_GAAP_MAPPING = {
       # Balance Sheet
       "ifrs-full:Assets": "us-gaap:Assets",
       "ifrs-full:CurrentAssets": "us-gaap:AssetsCurrent",
       "ifrs-full:CurrentLiabilities": "us-gaap:LiabilitiesCurrent",
       "ifrs-full:Equity": "us-gaap:StockholdersEquity",
       # Income Statement
       "ifrs-full:Revenue": "us-gaap:Revenues",
       "ifrs-full:ProfitLoss": "us-gaap:NetIncomeLoss",
       # Add more mappings...
   }
   ```

2. Required Features:
   - Map IFRS concepts to US GAAP equivalents
   - Handle IFRS-specific calculations
   - Support IFRS disclosure requirements
   - Process IFRS footnotes and annotations
   - Convert between standards where needed

3. Implementation Priority:
   - High: Basic IFRS taxonomy mapping
   - Medium: Advanced IFRS calculations
   - Low: Full standards reconciliation

### Phase 3: ADR and Dual Listing Support

1. ADR Processing Requirements:
   - Handle ADR ratios (e.g., 1 ADR = X ordinary shares)
   - Support different ADR levels (Level I, II, III)
   - Process sponsored vs. unsponsored ADRs
   - Calculate proper market values
   - Reconcile home market and U.S. market data

2. Implementation Example:
   ```python
   ADR_CONFIGURATION = {
       "adr_ratio": float,  # e.g., 5.0 for 1 ADR = 5 ordinary shares
       "adr_level": str,    # I, II, or III
       "sponsored": bool,   # True/False
       "home_market": str,  # Primary listing exchange
       "home_currency": str # Primary listing currency
   }
   ```

3. Priority Features:
   - High: ADR ratio handling
   - Medium: Dual market data reconciliation
   - Low: Full cross-exchange support

### Phase 4: Enhanced Model Selection

1. Update Model Selection Logic:
   ```python
   def select_zscore_model(company_data: dict) -> str:
       if company_data["is_bank"]:
           if company_data["region"] == "emerging":
               return "emerging_bank"
           return "bank"
       elif company_data["is_international"]:
           if company_data["accounting_standard"] == "IFRS":
               return "international"
       return "original"
   ```

2. Add New Z-Score Variants:
   - International company adaptations
   - Bank-specific models
   - Regional adjustments

### Phase 5: Quality Assurance and Monitoring

1. Data Quality Metrics:
   - Track field mapping success rates
   - Monitor currency conversion accuracy
   - Measure data completeness by company type
   - Report validation failure patterns

2. Automated Testing:
   ```python
   class InternationalTestSuite:
       def test_currency_conversion(self):
           # Test currency detection and conversion
           assert self.converter.detect_currency("20-F filing") == "CNY"
           assert abs(self.converter.convert(100, "CNY", "2023-12-31") - 15.5) < 0.01

       def test_field_mapping(self):
           # Test IFRS to GAAP mapping
           assert self.mapper.map_field("ifrs-full:Assets") == "us-gaap:Assets"
           assert self.mapper.get_alternatives("RetainedEarnings") == ["RE", "AccumulatedDeficit"]
   ```

3. Validation Framework:
   - Implement cross-validation checks
   - Add reconciliation with local filings
   - Create benchmark comparisons
   - Monitor temporal consistency

4. Performance Monitoring:
   - Track processing times by company type
   - Monitor API rate limits and usage
   - Measure cache effectiveness
   - Report system resource usage

5. Documentation and Reporting:
   - Generate quality assurance reports
   - Document validation procedures
   - Create troubleshooting guides
   - Maintain change log for mappings

### Phase 6: Hyperinflationary Economy Support

1. Inflation Detection and Classification:
   ```python
   class InflationHandler:
       def __init__(self):
           self.hyperinflation_threshold = 100  # 100% over 3 years
           self.high_inflation_countries = {
               "AR": "Argentina",
               "VE": "Venezuela",
               "ZW": "Zimbabwe",
               # Add more as needed
           }

       def needs_inflation_adjustment(self, country_code: str, data_period: str) -> bool:
           return (
               country_code in self.high_inflation_countries or
               self.calculate_inflation_rate(country_code, data_period) > self.hyperinflation_threshold
           )
   ```

2. Inflation Adjustment Framework:
   - Implement IAS 29 guidelines for financial reporting
   - Apply price index adjustments to historical data
   - Handle different price indices by country
   - Track adjustment factors in metadata

3. Data Validation for Hyperinflationary Economies:
   - Verify price index data availability
   - Validate adjustment calculations
   - Check for temporal consistency
   - Monitor for economic status changes

4. Reporting Enhancements:
   - Add inflation-adjusted metrics
   - Show original and adjusted values
   - Document adjustment methodologies
   - Provide economic context warnings

### Phase 7: Dual Listing and ADR Support

1. Multi-Exchange Data Management:
   ```python
   class DualListingHandler:
       def reconcile_market_data(self, ticker: str) -> dict:
           primary_data = self.get_primary_market_data(ticker)
           adr_data = self.get_adr_data(ticker)
           return {
               "primary": self.normalize_data(primary_data),
               "adr": self.normalize_data(adr_data),
               "conversion_ratio": self.get_adr_ratio(ticker),
               "price_difference": self.calculate_price_difference()
           }

       def get_adr_ratio(self, ticker: str) -> float:
           # Implement ADR ratio lookup and calculation
           pass
   ```

2. Cross-Exchange Reconciliation:
   - Handle different trading hours
   - Account for market holidays
   - Track currency basis spreads
   - Monitor arbitrage opportunities

3. ADR-Specific Features:
   - Calculate and apply ADR ratios
   - Handle sponsored vs. unsponsored ADRs
   - Support different ADR levels
   - Track depositary bank relationships

4. Market Data Integration:
   - Aggregate data across exchanges
   - Handle time zone differences
   - Support multiple price sources
   - Implement cross-validation checks

5. Authentication and API Management:
   - Implement robust API error handling
   - Add automatic retry logic
   - Support multiple API keys
   - Monitor rate limits across providers

### Phase 8: Regional Model Adaptation

1. Regional Model Framework:
   ```python
   class RegionalModelAdapter:
       def __init__(self, region: str):
           self.region = region
           self.local_standards = self.load_regional_standards(region)
           self.reporting_requirements = self.load_reporting_requirements(region)
           
       def adapt_model(self, base_model: BaseModel) -> RegionalModel:
           return RegionalModel(
               base_model=base_model,
               local_standards=self.local_standards,
               reporting_requirements=self.reporting_requirements
           )
   ```

2. Regional Standards Integration:
   - Local accounting principles
   - Regional reporting requirements
   - Market-specific adjustments
   - Local regulatory compliance

3. Regional Validation Rules:
   - Country-specific thresholds
   - Local market benchmarks
   - Regional peer comparisons
   - Market maturity factors

4. Regional Context Support:
   - Local market indicators
   - Regional economic factors
   - Market development stage
   - Local business practices

5. Reporting Adaptations:
   - Regional benchmark inclusion
   - Local context annotations
   - Market-specific risk factors
   - Regional compliance status

### Phase 9: State-Owned Enterprise Support

1. SOE Classification Framework:
   ```python
   class StateOwnedEnterpriseHandler:
       def __init__(self):
           self.soe_characteristics = {
               'ownership_threshold': 0.50,  # Government ownership percentage
               'strategic_sectors': [
                   'oil_and_gas',
                   'utilities',
                   'transportation',
                   'telecommunications'
               ],
               'governance_models': [
                   'direct_control',
                   'sovereign_wealth_fund',
                   'holding_company'
               ]
           }

       def assess_soe_status(self, company_data: dict) -> dict:
           return {
               'is_soe': self._check_soe_criteria(company_data),
               'ownership_type': self._determine_ownership_type(company_data),
               'governance_model': self._identify_governance_model(company_data),
               'strategic_importance': self._assess_strategic_importance(company_data)
           }
   ```

2. SOE-Specific Considerations:
   - Government ownership percentage
   - Strategic sector classification
   - Policy-driven mandates
   - Public service obligations
   - Sovereign support assessment
   - Political risk factors
   - Regulatory relationships

3. Mixed Ownership Adjustments:
   - Public-private partnership structures
   - Minority shareholder rights
   - Government guarantee assessment
   - Commercial vs. policy objectives
   - Subsidy impact analysis
   - Cross-border considerations
   - Transparency requirements

4. SOE Reporting Framework:
   - Government reporting requirements
   - International transparency standards
   - Public accountability measures
   - Policy objective tracking
   - Sovereign rating impact
   - Special disclosure requirements
   - Related party transactions

5. Risk Assessment Modifications:
   ```python
   class SOERiskAdjuster:
       def adjust_risk_metrics(self, base_metrics: dict, soe_data: dict) -> dict:
           return {
               'sovereign_support': self._calculate_support_probability(soe_data),
               'policy_burden': self._assess_policy_obligations(soe_data),
               'political_risk': self._evaluate_political_exposure(soe_data),
               'commercial_viability': self._assess_standalone_strength(base_metrics)
           }
   ```

6. Validation Rules:
   - Government ownership verification
   - Policy mandate compliance
   - Public service obligations
   - Subsidy dependence assessment
   - Political independence metrics
   - Governance structure review
   - International compliance checks

7. SOE-Specific Thresholds:
   ```python
   class SOEThresholdAdjuster:
       def __init__(self):
           self.threshold_modifiers = {
               'strategic_importance': {
                   'high': {'safe': -0.5, 'distress': -0.8},  # More lenient
                   'medium': {'safe': -0.3, 'distress': -0.5},
                   'low': {'safe': -0.1, 'distress': -0.2}
               },
               'sovereign_rating': {
                   'investment_grade': {'multiplier': 0.9},
                   'speculative': {'multiplier': 1.1},
                   'unrated': {'multiplier': 1.2}
               }
           }
   ```

### Phase 10: Regional Accounting Standards

1. Japanese Accounting Framework:
   ```python
   class JapaneseAccountingHandler:
       def __init__(self):
           self.fiscal_year_end = '03-31'  # Common in Japan
           self.accounting_standards = {
               'j_gaap': 'Japanese GAAP',
               'ifrs': 'IFRS',
               'sec': 'SEC Standards'
           }
           
           # Japanese accounting specificities
           self.special_items = {
               'keiretsu_relationships': True,
               'cross_shareholdings': True,
               'lifetime_employment': True
           }
   ```

2. Japanese Market Characteristics:
   - Keiretsu relationships
   - Cross-shareholding impact
   - Long-term employment costs
   - Corporate governance structure
   - Bank-centered financing
   - Group company relationships
   - Interlocking ownership

3. Japanese Financial Adjustments:
   ```python
   class JapaneseFinancialAdjuster:
       def adjust_financials(self, data: dict) -> dict:
           return {
               'adjusted_assets': self._adjust_cross_holdings(),
               'employment_obligations': self._calculate_lifetime_employment(),
               'group_relationships': self._assess_keiretsu_impact(),
               'bank_relationships': self._evaluate_main_bank()
           }
   ```

4. Japan-Specific Validation:
   - Cross-shareholding verification
   - Group company relationships
   - Main bank system impact
   - Employment obligations
   - Corporate governance
   - Regulatory compliance
   - Market practice alignment

## Technical Requirements

1. New Dependencies:
   - Forex data provider
   - IFRS taxonomy parser
   - International financial data sources

2. Database Updates:
   - Currency conversion history
   - IFRS mapping tables
   - Regional regulation metadata

3. Code Structure:
   - New modules for IFRS support
   - Currency conversion service
   - Industry-specific calculators
   - Enhanced model selection

## Testing Strategy

1. Test Cases:
   - U.S. ADRs (e.g., ASML, BBD)
   - International banks
   - Different accounting standards
   - Currency conversion accuracy

2. Validation:
   - Compare with manual calculations
   - Cross-reference with Bloomberg/CapIQ
   - Historical accuracy testing

## Success Metrics

1. Coverage Metrics:
   - Support for >95% of Form 20-F filers
   - Successful processing of all major currencies
   - Complete field mapping for IFRS standards
   - Handling of all major banking systems
   - Support for all hyperinflationary economies
   - Coverage of major dual-listed companies

2. Quality Metrics:
   - <1% currency conversion errors
   - >98% field mapping accuracy
   - <5% missing critical fields
   - Zero unhandled validation errors
   - <2% inflation adjustment deviation
   - >99% ADR ratio accuracy

3. Performance Metrics:
   - Processing time within 2x of US companies
   - Cache hit rate >90%
   - API usage within rate limits
   - Resource usage within budget
   - <1% API authentication failures
   - >99.9% data provider availability

4. Validation Metrics:
   - Cross-exchange price correlation >95%
   - Inflation adjustment validation >98%
   - Currency conversion accuracy >99%
   - Data freshness <24 hours
   - Market data completeness >95%

## Implementation Priorities

1. Critical Path Items:
   - Currency conversion framework
   - IFRS taxonomy support
   - API authentication resilience
   - Basic ADR handling

2. High Impact Features:
   - Hyperinflationary adjustments
   - Dual listing support
   - Market data aggregation
   - Enhanced error handling

3. Quality Improvements:
   - Validation framework
   - Testing infrastructure
   - Documentation updates
   - Performance optimization
