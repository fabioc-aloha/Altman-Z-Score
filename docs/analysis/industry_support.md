# Industry-Specific Support Plan

This document outlines the plan to enhance the Altman Z-Score Analysis tool with proper industry-specific considerations, focusing on adapting the model for different business sectors within the U.S. market.

## Current Limitations

1. **Model Application Issues**
   - Single model applied across all industries
   - Manufacturing-centric financial ratios
   - No consideration of industry-specific capital structures
   - Limited handling of regulated industries

2. **Industry-Specific Metrics Missing**
   - No regulatory metrics for utilities
   - No risk-based capital for financial institutions
   - No R&D consideration for technology companies
   - No real estate metrics for REITs

3. **Validation Gaps**
   - Lack of industry-specific thresholds
   - No peer comparison framework
   - Missing industry-standard ratios
   - Limited regulatory compliance checks

## Implementation Plan

### Phase 1: Utility Company Support

1. Utility-Specific Model:
   ```python
   class UtilityZScoreModel:
       def __init__(self):
           # Modified weights based on utility characteristics
           self.weights = {
               'X1': 0.5,    # Reduced working capital importance
               'X2': 1.2,    # Increased retained earnings weight
               'X3': 3.3,    # Maintained EBIT importance
               'X4': 2.4,    # Increased market value weight
               'X5': 0.3     # Reduced sales turnover importance
           }
           
           # Adjusted thresholds for utilities
           self.thresholds = {
               'safe': 2.6,
               'grey': 1.1,
               'distress': 1.1
           }
   ```

2. Additional Utility Metrics:
   - Rate base return calculation
   - Regulatory asset coverage
   - Capital expenditure ratio
   - Allowed return metrics
   - Debt service coverage ratio

3. Utility-Specific Validation:
   - Peer utility comparison
   - Regulatory compliance checks
   - Rate case impact analysis
   - Capital structure requirements

### Phase 2: Financial Institution Support

1. Financial Institution Classification:
   ```python
   class FinancialInstitutionClassifier:
       def __init__(self):
           self.institution_types = {
               'commercial_bank': ['6020', '6022'],     # SIC codes
               'investment_bank': ['6211', '6282'],
               'insurance': ['6311', '6321'],
               'asset_manager': ['6282', '6221'],
               'broker_dealer': ['6211']
           }
           
       def classify_institution(self, company_data: dict) -> str:
           sic_code = company_data.get('sic_code')
           for type_name, codes in self.institution_types.items():
               if sic_code in codes:
                   return type_name
           return 'other_financial'
   ```

2. Investment Bank Model:
   ```python
   class InvestmentBankModel:
       def __init__(self):
           self.capital_metrics = {
               'tier1': 0.08,          # Higher than commercial banks
               'leverage_max': 0.25,    # Investment bank specific
               'risk_weighted': 0.10    # Trading book focus
           }
           
           self.trading_metrics = {
               'var_limit': 0.02,      # Value at Risk
               'trading_capital': 0.15, # Trading to capital ratio
               'position_limit': 0.20   # Single position limit
           }
           
           self.revenue_metrics = {
               'trading_revenue': 0.40,    # Trading revenue max %
               'advisory_revenue': 0.30,   # Advisory revenue min %
               'asset_mgmt': 0.20         # Asset management min %
           }
   ```

3. Investment Bank Specific Metrics:
   - Trading book risk measures
   - Deal pipeline analysis
   - Fee-based revenue stability
   - Market making capacity
   - Prime brokerage metrics
   - Capital markets activity
   - Advisory revenue quality

4. Trading Risk Framework:
   ```python
   class TradingRiskAnalyzer:
       def analyze_trading_risk(self, data: dict) -> dict:
           return {
               'var_exposure': self._calculate_var(),
               'position_concentration': self._assess_concentration(),
               'market_liquidity': self._evaluate_liquidity(),
               'counterparty_exposure': self._assess_counterparty_risk()
           }
   ```

5. Investment Bank Validation Rules:
   - Trading limit compliance
   - Position concentration checks
   - Counterparty exposure limits
   - Liquidity buffer requirements
   - Capital adequacy rules
   - Risk weighted asset limits
   - Market risk controls

6. Additional Risk Considerations:
   ```python
   class InvestmentBankRiskManager:
       def assess_risks(self, company_data: dict) -> dict:
           return {
               'market_risk': self._evaluate_market_risk(),
               'operational_risk': self._assess_operational_risk(),
               'reputational_risk': self._evaluate_reputation(),
               'regulatory_risk': self._assess_compliance(),
               'model_risk': self._evaluate_model_risk()
           }
   ```

7. False Positive Prevention:
   ```python
   class BankruptcyDetector:
       def __init__(self):
           self.false_positive_keywords = {
               'advisory': ['restructuring', 'reorganization'],
               'services': ['bankruptcy services', 'workout'],
               'business_lines': ['distressed assets', 'special situations']
           }
           
       def is_actually_bankrupt(self, description: str, financials: dict) -> bool:
           # Check if bankruptcy keywords refer to services rather than status
           if self._has_service_context(description):
               return False
           return self._check_actual_bankruptcy_indicators(financials)
   ```

### Phase 3: Technology Company Support

1. Tech-Specific Model:
   ```python
   class TechnologyZScoreModel:
       def __init__(self):
           self.rd_metrics = {
               'rd_to_revenue_min': 0.10,
               'rd_growth_rate_min': 0.05
           }
           
           self.digital_metrics = {
               'recurring_revenue_min': 0.40,
               'customer_churn_max': 0.15
           }
   ```

2. Technology Metrics:
   - R&D investment ratios
   - Recurring revenue metrics
   - Customer acquisition costs
   - Churn rates
   - Growth metrics

3. Tech-Specific Validation:
   - Innovation metrics
   - Market penetration rates
   - Platform scalability
   - IP portfolio value

### Phase 4: REIT Support

1. REIT-Specific Model:
   - Funds from operations (FFO)
   - Net operating income (NOI)
   - Property type considerations
   - Geographic diversification

2. Real Estate Metrics:
   - Occupancy rates
   - Lease renewal rates
   - Property value appreciation
   - Maintenance cost ratio

### Phase 5: Oil & Gas Industry Support

1. Oil & Gas Specific Model:
   ```python
   class OilGasZScoreModel:
       def __init__(self):
           self.weights = {
               'X1': 0.6,    # Working capital importance adjusted for commodity cycles
               'X2': 1.4,    # Higher retained earnings weight for reinvestment needs
               'X3': 3.3,    # EBIT importance maintained but volatile
               'X4': 2.8,    # Increased market value weight for resource base
               'X5': 0.6     # Sales importance adjusted for price volatility
           }
           
           self.thresholds = {
               'safe': 2.9,      # Higher threshold due to industry volatility
               'grey': 1.8,      # Wider grey zone for commodity cycles
               'distress': 1.8
           }
           
           self.commodity_factors = {
               'oil_price_threshold': 40.0,  # USD per barrel
               'price_cycle_period': 365,    # days
               'hedge_effectiveness': 0.7
           }
   ```

2. Resource-Based Metrics:
   - Reserve replacement ratio
   - Production costs per barrel
   - Reserve life index
   - Finding & development costs
   - Production efficiency
   - Resource base valuation
   - Proven reserves ratio

3. Commodity-Specific Adjustments:
   ```python
   class CommodityAdjuster:
       def adjust_metrics(self, base_metrics: dict, market_data: dict) -> dict:
           return {
               'price_cycle_position': self._calculate_cycle_position(),
               'commodity_price_impact': self._assess_price_sensitivity(),
               'hedge_effectiveness': self._evaluate_hedging_program(),
               'breakeven_analysis': self._calculate_breakeven_prices()
           }
   ```

4. Operational Metrics:
   - Lifting costs
   - Drilling success rate
   - Reserve replacement costs
   - Operating margin per barrel
   - Field decline rates
   - Capital efficiency
   - Exploration success rate

5. Industry-Specific Risk Factors:
   - Commodity price exposure
   - Reserve quality assessment
   - Regulatory compliance
   - Environmental liabilities
   - Political risk exposure
   - Infrastructure access
   - License to operate

6. ESG Considerations:
   ```python
   class OilGasESGMetrics:
       def calculate_esg_impact(self, company_data: dict) -> dict:
           return {
               'carbon_intensity': self._calc_emissions_per_barrel(),
               'water_management': self._assess_water_usage(),
               'environmental_liabilities': self._evaluate_cleanup_obligations(),
               'community_relations': self._assess_social_license()
           }
   ```

7. Validation Framework:
   - Peer group comparison
   - Commodity cycle position
   - Resource base quality
   - Cost structure analysis
   - Capital intensity metrics
   - Environmental compliance
   - Safety performance

8. Additional Risk Factors:
   ```python
   class OilGasRiskAdjuster:
       def adjust_risk_profile(self, base_risk: float, company_data: dict) -> float:
           risk_factors = {
               'reserve_risk': self._assess_reserve_uncertainty(),
               'price_risk': self._evaluate_price_exposure(),
               'regulatory_risk': self._assess_regulatory_exposure(),
               'operational_risk': self._evaluate_operational_complexity()
           }
           return self._combine_risk_factors(base_risk, risk_factors)
   ```

### Phase 6: Manufacturing Conglomerate Support

1. Conglomerate Model Framework:
   ```python
   class ManufacturingConglomerateModel:
       def __init__(self):
           self.segment_weights = {
               'manufacturing': 0.50,
               'financial_services': 0.25,
               'r_and_d': 0.15,
               'other': 0.10
           }
           
           # Modified Z-Score weights for manufacturing focus
           self.manufacturing_weights = {
               'X1': 1.2,    # Working capital importance for manufacturing
               'X2': 1.4,    # Retained earnings for R&D and capital investment
               'X3': 3.3,    # EBIT remains key
               'X4': 0.6,    # Market value consideration
               'X5': 1.0     # Asset turnover for manufacturing
           }
           
           # Specific thresholds for manufacturing conglomerates
           self.thresholds = {
               'safe': 2.99,
               'grey': 1.81,
               'distress': 1.81
           }
   ```

2. Segment Analysis:
   ```python
   class SegmentAnalyzer:
       def analyze_segments(self, company_data: dict) -> dict:
           return {
               'manufacturing': self._analyze_manufacturing_ops(),
               'financial': self._analyze_financial_services(),
               'r_and_d': self._analyze_research_development(),
               'other': self._analyze_other_segments()
           }
   ```

3. Manufacturing Metrics:
   - Production efficiency
   - Capacity utilization
   - Inventory turnover
   - Supply chain metrics
   - Product development cycle
   - Quality indicators
   - Factory automation level

4. R&D Effectiveness:
   - R&D to revenue ratio
   - Patent portfolio value
   - New product pipeline
   - Innovation metrics
   - Development cycle time
   - Technology adoption rate
   - Research effectiveness

5. Operational Excellence:
   ```python
   class OperationalMetrics:
       def calculate_metrics(self, data: dict) -> dict:
           return {
               'production_efficiency': self._calc_efficiency(),
               'quality_metrics': self._assess_quality(),
               'cycle_time': self._calculate_cycle_time(),
               'automation_level': self._assess_automation()
           }
   ```

6. Capital Investment Framework:
   - Capital expenditure ratio
   - Equipment modernization
   - Factory automation
   - Technology investment
   - Maintenance capital
   - Expansion projects
   - Environmental compliance

7. Segment-Specific Validation:
   ```python
   class ConglomerateValidator:
       def validate_segments(self, company_data: dict) -> dict:
           return {
               'manufacturing': self._validate_manufacturing(),
               'financial': self._validate_financial_services(),
               'r_and_d': self._validate_research_dev(),
               'other': self._validate_other_segments()
           }
   ```

8. Global Operations Framework:
   - Regional performance
   - Currency exposure
   - Market share analysis
   - Geographic diversification
   - Local content requirements
   - Trade compliance
   - Supply chain resilience

## Implementation Strategy

1. Model Selection Framework:
   ```python
   def select_model(company_data: dict) -> BaseModel:
       sic_code = company_data.get('sic_code')
       if is_utility(sic_code):           # 4900-4999
           return UtilityZScoreModel()
       elif is_bank(sic_code):            # 6000-6199
           return BankZScoreModel()
       elif is_tech_company(sic_code):    # 7370-7379
           return TechnologyZScoreModel()
       elif is_reit(sic_code):            # 6798
           return REITZScoreModel()
       elif is_oil_gas_company(sic_code): # 1300-1399
           return OilGasZScoreModel()
       return OriginalZScoreModel()
   ```

2. Data Requirements:
   - Industry-specific financial ratios
   - Regulatory compliance data
   - Peer comparison metrics
   - Industry benchmark data

3. Validation Framework:
   - Industry-specific thresholds
   - Peer group analytics
   - Regulatory compliance checks
   - Time series validation

## Success Metrics

1. Accuracy Metrics:
   - >95% model selection accuracy
   - <5% false positive rate
   - <3% false negative rate
   - >90% peer group correlation

2. Validation Metrics:
   - 100% regulatory metric coverage
   - >95% industry-specific ratio coverage
   - >98% data quality score
   - <1% missing critical metrics

3. Performance Goals:
   - Support for top 10 industries by market cap
   - Coverage of all regulated sectors
   - Industry-specific reporting for all supported sectors
   - Real-time peer comparison capabilities
