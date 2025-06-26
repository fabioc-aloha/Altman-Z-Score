"""
Z-Score Calculator - Direct calculation from MergedFinancialData

Strategic Advantages:
- Direct calculation from FMP standardized financial data
- No field mapping complexity 
- No legacy module dependencies
- Automatic model selection based on company characteristics
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import asyncio

from altman_zscore.common.logging_config import get_logger
from altman_zscore.common.exceptions import CalculationError
from altman_zscore.common.constants import ZSCORE_MODELS
from altman_zscore.models.data_models import MergedFinancialData
from altman_zscore.layers.zscore_calculation.model_selector import ModelSelector, CompanyType


logger = get_logger(__name__)


@dataclass
class ZScoreCalculationResult:
    """Result of Z-Score calculation."""
    ticker: str
    z_score: float
    model_used: str
    risk_category: str
    component_values: Dict[str, float]
    calculation_timestamp: str
    data_quality_score: float
    warnings: List[str]
    metadata: Dict[str, Any]


class ZScoreCalculator:
    """
    Direct Z-Score calculator using MergedFinancialData.
    
    This implementation calculates Z-Scores directly from the standardized
    financial data structure, eliminating the need for complex field mapping.
    """
    
    def __init__(self):
        """Initialize the Z-Score calculator."""
        self.logger = get_logger(self.__class__.__name__)
        self.model_selector = ModelSelector()
        
        # Load Z-Score thresholds from constants
        self.risk_thresholds = {
            model_name: {
                "safe": model_data["thresholds"]["safe"],
                "gray": model_data["thresholds"]["grey_lower"]
            }
            for model_name, model_data in ZSCORE_MODELS.items()
        }
    
    def _calculate_original_zscore(self, data: MergedFinancialData) -> Dict[str, float]:
        """
        Calculate original Altman Z-Score for manufacturing companies.
        
        Z = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
        
        Where:
        A = Working Capital / Total Assets
        B = Retained Earnings / Total Assets  
        C = EBIT / Total Assets
        D = Market Value Equity / Total Liabilities
        E = Sales / Total Assets
        """
        # Use enhanced component calculation
        components = self._calculate_component_ratios(data)
        
        # Extract metadata and warnings
        metadata = components.pop('_metadata', {})
        component_warnings = metadata.get('warnings', [])
        
        # Log any calculation warnings
        for warning in component_warnings:
            self.logger.warning(f"{data.ticker}: {warning}")
        
        # Calculate Z-Score using coefficients from constants
        coeffs = ZSCORE_MODELS["original"]["coefficients"]
        z_score = (
            coeffs["X1"] * components.get('working_capital_ratio', 0) +
            coeffs["X2"] * components.get('retained_earnings_ratio', 0) +
            coeffs["X3"] * components.get('ebit_ratio', 0) +
            coeffs["X4"] * components.get('market_equity_ratio', 0) +
            coeffs["X5"] * components.get('asset_turnover', 0)
        )
        
        components['z_score'] = z_score
        
        # Store calculation metadata separately, not in component_values
        if metadata:
            components['_calculation_metadata'] = metadata
        
        return components
    
    def _calculate_service_zscore(self, data: MergedFinancialData) -> Dict[str, float]:
        """
        Calculate Z''-Score for service/non-manufacturing companies.
        
        Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4 (NO constant)
        
        Where:
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets  
        X3 = EBIT / Total Assets
        X4 = Book Value of Equity / Total Liabilities (NOT market value)
        """
        components = {}
        
        # Component X1: Working Capital / Total Assets
        if data.working_capital_ratio is not None:
            components['working_capital_ratio'] = data.working_capital_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            balance_sheet = raw_data.get('balance_sheet', {})
            current_assets = balance_sheet.get('totalCurrentAssets', 0)
            current_liabilities = balance_sheet.get('totalCurrentLiabilities', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - working capital ratio will be 0")
            components['working_capital_ratio'] = (current_assets - current_liabilities) / total_assets if total_assets > 0 else 0
        
        # Component X2: Retained Earnings / Total Assets
        if data.retained_earnings_ratio is not None:
            components['retained_earnings_ratio'] = data.retained_earnings_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            balance_sheet = raw_data.get('balance_sheet', {})
            retained_earnings = balance_sheet.get('retainedEarnings', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - retained earnings ratio will be 0")
            components['retained_earnings_ratio'] = retained_earnings / total_assets if total_assets > 0 else 0
        
        # Component X3: EBIT / Total Assets
        if data.ebit_ratio is not None:
            components['ebit_ratio'] = data.ebit_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            income_statement = raw_data.get('income_statement', {})
            balance_sheet = raw_data.get('balance_sheet', {})
            ebit = income_statement.get('operatingIncome', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - EBIT ratio will be 0")
            components['ebit_ratio'] = ebit / total_assets if total_assets > 0 else 0
        
        # Component X4: Book Value of Equity / Total Liabilities (CORRECTED)
        if data.raw_fmp_data:
            balance_sheet = data.raw_fmp_data.get('balance_sheet', {})
            book_value = balance_sheet.get('totalStockholdersEquity', 0)
            total_liabilities = balance_sheet.get('totalLiabilities', 0)
            if total_liabilities == 0:
                self.logger.warning(f"Total liabilities missing for {data.ticker} - book equity ratio will be 0")
            components['book_equity_ratio'] = book_value / total_liabilities if total_liabilities > 0 else 0
        else:
            components['book_equity_ratio'] = 0.0
        
        # Calculate service Z''-Score using SERVICE coefficients (NO constant)
        coeffs = ZSCORE_MODELS["service"]["coefficients"]  # Use service model, not emerging
        z_score = (
            coeffs["X1"] * components.get('working_capital_ratio', 0) +
            coeffs["X2"] * components.get('retained_earnings_ratio', 0) +
            coeffs["X3"] * components.get('ebit_ratio', 0) +
            coeffs["X4"] * components.get('book_equity_ratio', 0)  # Use book equity ratio
        )
        # Service model does NOT include a constant (unlike emerging market model)
        
        components['z_score'] = z_score
        return components
    
    def _calculate_private_zscore(self, data: MergedFinancialData) -> Dict[str, float]:
        """
        Calculate Z-Score for private companies (no market data).
        
        Z = 0.717*A + 0.847*B + 3.107*C + 0.420*D + 0.998*E
        """
        components = {}
        
        # Use book values instead of market values
        if data.working_capital_ratio is not None:
            components['working_capital_ratio'] = data.working_capital_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            balance_sheet = raw_data.get('balance_sheet', {})
            current_assets = balance_sheet.get('totalCurrentAssets', 0)
            current_liabilities = balance_sheet.get('totalCurrentLiabilities', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - working capital ratio will be 0")
            components['working_capital_ratio'] = (current_assets - current_liabilities) / total_assets if total_assets > 0 else 0
        
        if data.retained_earnings_ratio is not None:
            components['retained_earnings_ratio'] = data.retained_earnings_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            balance_sheet = raw_data.get('balance_sheet', {})
            retained_earnings = balance_sheet.get('retainedEarnings', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - retained earnings ratio will be 0")
            components['retained_earnings_ratio'] = retained_earnings / total_assets if total_assets > 0 else 0
        
        if data.ebit_ratio is not None:
            components['ebit_ratio'] = data.ebit_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            income_statement = raw_data.get('income_statement', {})
            balance_sheet = raw_data.get('balance_sheet', {})
            ebit = income_statement.get('operatingIncome', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - EBIT ratio will be 0")
            components['ebit_ratio'] = ebit / total_assets if total_assets > 0 else 0
        
        # Book value equity / Total Liabilities (instead of market value)
        if data.raw_fmp_data:
            balance_sheet = data.raw_fmp_data.get('balance_sheet', {})
            book_value = balance_sheet.get('totalStockholdersEquity', 0)
            total_liabilities = balance_sheet.get('totalLiabilities', 0)
            if total_liabilities == 0:
                self.logger.warning(f"Total liabilities missing for {data.ticker} - book equity ratio will be 0")
            components['book_equity_ratio'] = book_value / total_liabilities if total_liabilities > 0 else 0
        else:
            components['book_equity_ratio'] = 0.0
        
        if data.asset_turnover is not None:
            components['asset_turnover'] = data.asset_turnover
        else:
            raw_data = data.raw_fmp_data or {}
            income_statement = raw_data.get('income_statement', {})
            balance_sheet = raw_data.get('balance_sheet', {})
            revenue = income_statement.get('revenue', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - asset turnover will be 0")
            components['asset_turnover'] = revenue / total_assets if total_assets > 0 else 0
        
        # Calculate private Z-Score using coefficients from constants
        coeffs = ZSCORE_MODELS["private"]["coefficients"]
        z_score = (
            coeffs["X1"] * components.get('working_capital_ratio', 0) +
            coeffs["X2"] * components.get('retained_earnings_ratio', 0) +
            coeffs["X3"] * components.get('ebit_ratio', 0) +
            coeffs["X4"] * components.get('book_equity_ratio', 0) +
            coeffs["X5"] * components.get('asset_turnover', 0)
        )
        
        components['z_score'] = z_score
        return components
    
    def _calculate_emerging_zscore(self, data: MergedFinancialData) -> Dict[str, float]:
        """
        Calculate Z''-Score for emerging market companies.
        
        Z'' = 3.25 + 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4 (WITH constant)
        
        Where:
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets  
        X3 = EBIT / Total Assets
        X4 = Book Value of Equity / Total Liabilities
        """
        components = {}
        
        # Component X1: Working Capital / Total Assets
        if data.working_capital_ratio is not None:
            components['working_capital_ratio'] = data.working_capital_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            balance_sheet = raw_data.get('balance_sheet', {})
            current_assets = balance_sheet.get('totalCurrentAssets', 0)
            current_liabilities = balance_sheet.get('totalCurrentLiabilities', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - working capital ratio will be 0")
            components['working_capital_ratio'] = (current_assets - current_liabilities) / total_assets if total_assets > 0 else 0
        
        # Component X2: Retained Earnings / Total Assets
        if data.retained_earnings_ratio is not None:
            components['retained_earnings_ratio'] = data.retained_earnings_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            balance_sheet = raw_data.get('balance_sheet', {})
            retained_earnings = balance_sheet.get('retainedEarnings', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - retained earnings ratio will be 0")
            components['retained_earnings_ratio'] = retained_earnings / total_assets if total_assets > 0 else 0
        
        # Component X3: EBIT / Total Assets
        if data.ebit_ratio is not None:
            components['ebit_ratio'] = data.ebit_ratio
        else:
            raw_data = data.raw_fmp_data or {}
            income_statement = raw_data.get('income_statement', {})
            balance_sheet = raw_data.get('balance_sheet', {})
            ebit = income_statement.get('operatingIncome', 0)
            total_assets = balance_sheet.get('totalAssets', 0)
            if total_assets == 0:
                self.logger.warning(f"Total assets missing for {data.ticker} - EBIT ratio will be 0")
            components['ebit_ratio'] = ebit / total_assets if total_assets > 0 else 0
        
        # Component X4: Book Value of Equity / Total Liabilities
        if data.raw_fmp_data:
            balance_sheet = data.raw_fmp_data.get('balance_sheet', {})
            book_value = balance_sheet.get('totalStockholdersEquity', 0)
            total_liabilities = balance_sheet.get('totalLiabilities', 0)
            if total_liabilities == 0:
                self.logger.warning(f"Total liabilities missing for {data.ticker} - book equity ratio will be 0")
            components['book_equity_ratio'] = book_value / total_liabilities if total_liabilities > 0 else 0
        else:
            components['book_equity_ratio'] = 0.0
        
        # Calculate emerging market Z''-Score with constant
        coeffs = ZSCORE_MODELS["emerging"]["coefficients"]
        z_score = (
            coeffs["X1"] * components.get('working_capital_ratio', 0) +
            coeffs["X2"] * components.get('retained_earnings_ratio', 0) +
            coeffs["X3"] * components.get('ebit_ratio', 0) +
            coeffs["X4"] * components.get('book_equity_ratio', 0)
        )
        # Emerging market model INCLUDES the +3.25 constant
        if "constant" in coeffs:
            z_score += coeffs["constant"]
        
        components['z_score'] = z_score
        return components
    
    def _categorize_risk(self, z_score: float, model: str) -> str:
        """Categorize bankruptcy risk based on Z-Score and model."""
        thresholds = self.risk_thresholds.get(model, self.risk_thresholds["original"])
        
        if z_score >= thresholds["safe"]:
            return "Safe"
        elif z_score >= thresholds["gray"]:
            return "Gray Zone"
        else:
            return "Distress"
    
    def _validate_calculation_data(self, data: MergedFinancialData) -> List[str]:
        """Validate input data and return list of warnings."""
        warnings = []
        
        if not data.raw_fmp_data:
            warnings.append("No raw financial data available - calculation may be incomplete")
            return warnings
        
        # Check for critical balance sheet data
        balance_sheet = data.raw_fmp_data.get('balance_sheet', {})
        income_statement = data.raw_fmp_data.get('income_statement', {})
        
        # Critical fields validation
        if not balance_sheet.get('totalAssets'):
            warnings.append("Total assets missing - ratios cannot be calculated reliably")
        
        if not balance_sheet.get('totalLiabilities'):
            warnings.append("Total liabilities missing - equity ratios may be inaccurate")
        
        if not income_statement.get('revenue'):
            warnings.append("Revenue missing - asset turnover cannot be calculated")
        
        if not income_statement.get('operatingIncome'):
            warnings.append("Operating income (EBIT) missing - profitability ratios unavailable")
        
        # Check for pre-calculated ratios
        if data.working_capital_ratio is None and not balance_sheet.get('totalCurrentAssets'):
            warnings.append("Working capital components not available")
            
        if data.ebit_ratio is None and not income_statement.get('operatingIncome'):
            warnings.append("EBIT ratio not available")
        
        # Market data validation
        if data.market_cap is None or data.market_cap <= 0:
            warnings.append("Market data not available - may affect model selection")
        
        return warnings
    
    def _detect_and_fix_scaling(self, data: MergedFinancialData) -> MergedFinancialData:
        """
        Detect and fix scaling issues between market data and financial statement data.
        
        Both Yahoo Finance market cap and FMP financial data are now in dollars,
        so we need to check if there are any actual scaling mismatches by examining
        the reasonableness of calculated ratios.
        """
        if not data.market_cap or not data.raw_fmp_data:
            return data
        
        # Check if we have balance sheet data to validate scaling
        balance_sheet = data.raw_fmp_data.get('balance_sheet', {})
        total_liabilities = balance_sheet.get('totalLiabilities', 0)
        
        if total_liabilities == 0:
            self.logger.warning(f"No total liabilities data for {data.ticker} - cannot validate scaling")
            return data
        
        # Calculate market cap to total liabilities ratio
        market_equity_ratio = data.market_cap / total_liabilities
        
        # For most companies, market cap to total liabilities should be reasonable (0.1 to 100)
        # If it's extremely high (>1000), there might be a scaling issue
        if market_equity_ratio > 1000:
            self.logger.info(f"Detected potential scaling issue for {data.ticker}: Market cap to liabilities ratio is {market_equity_ratio:.2f}")
            
            # Apply scaling correction: assume market cap needs to be scaled down
            scaling_factor = 1000
            corrected_market_cap = data.market_cap / scaling_factor
            
            self.logger.info(f"Applying scaling correction for {data.ticker}: Market cap from ${data.market_cap:,.0f} to ${corrected_market_cap:,.0f}")
            
            # Create corrected data
            corrected_data = MergedFinancialData(
                ticker=data.ticker,
                timestamp=data.timestamp,
                working_capital_ratio=data.working_capital_ratio,
                retained_earnings_ratio=data.retained_earnings_ratio,
                ebit_ratio=data.ebit_ratio,
                asset_turnover=data.asset_turnover,
                market_cap=corrected_market_cap,
                shares_outstanding=data.shares_outstanding,
                current_price=data.current_price,
                current_ratio=data.current_ratio,
                debt_to_equity=data.debt_to_equity,
                inventory_ratio=data.inventory_ratio,
                data_quality_score=data.data_quality_score,
                raw_fmp_data=data.raw_fmp_data,
                raw_yahoo_data=data.raw_yahoo_data,
                quarters=data.quarters,
                company_profile=data.company_profile,
                metadata=data.metadata
            )
            
            return corrected_data
        else:
            self.logger.info(f"Market cap scaling appears correct for {data.ticker}: Market cap to liabilities ratio is {market_equity_ratio:.2f}")
            return data

    def _calculate_ebit_enhanced(self, data: MergedFinancialData) -> tuple[float, str, list[str]]:
        """
        Calculate EBIT using multiple approaches for validation.
        
        Returns:
            tuple: (ebit_value, method_used, warnings)
        """
        warnings = []
        raw_data = data.raw_fmp_data or {}
        income_statement = raw_data.get('income_statement', {})
        
        # Method 1: Operating Income (most direct)
        operating_income = income_statement.get('operatingIncome', 0)
        
        # Method 2: Net Income + Interest Expense + Tax Expense
        net_income = income_statement.get('netIncome', 0)
        interest_expense = income_statement.get('interestExpense', 0)
        tax_expense = income_statement.get('incomeTaxExpense', 0)
        calculated_ebit = net_income + interest_expense + tax_expense
        
        # Method 3: Revenue - Operating Expenses
        revenue = income_statement.get('revenue', 0)
        operating_expenses = income_statement.get('operatingExpenses', 0)
        revenue_based_ebit = revenue - operating_expenses if operating_expenses > 0 else 0
        
        # Choose best method and validate
        if operating_income > 0:
            ebit_value = operating_income
            method = "operating_income"
            
            # Validate against calculated EBIT if available
            if calculated_ebit > 0 and abs(operating_income - calculated_ebit) / max(operating_income, calculated_ebit) > 0.1:
                warnings.append(f"EBIT methods differ significantly: Operating Income {operating_income:,.0f} vs Calculated {calculated_ebit:,.0f}")
                
        elif calculated_ebit > 0:
            ebit_value = calculated_ebit
            method = "calculated_ebit"
            warnings.append("Using calculated EBIT (Net Income + Interest + Tax)")
            
        elif revenue_based_ebit > 0:
            ebit_value = revenue_based_ebit
            method = "revenue_based"
            warnings.append("Using revenue-based EBIT estimation")
            
        else:
            ebit_value = 0
            method = "unavailable"
            warnings.append("EBIT calculation failed - all methods returned zero or negative")
        
        return ebit_value, method, warnings

    def _calculate_component_ratios(self, data: MergedFinancialData) -> Dict[str, Any]:
        """
        Calculate all component ratios with enhanced validation.
        
        Returns:
            Dict with component values and metadata
        """
        components = {}
        warnings = []
        raw_data = data.raw_fmp_data or {}
        balance_sheet = raw_data.get('balance_sheet', {})
        income_statement = raw_data.get('income_statement', {})
        
        total_assets = balance_sheet.get('totalAssets', 0)
        if total_assets <= 0:
            warnings.append("Total assets missing or zero - all ratios will be zero")
            
        # X1: Working Capital / Total Assets
        if data.working_capital_ratio is not None:
            components['working_capital_ratio'] = data.working_capital_ratio
        else:
            current_assets = balance_sheet.get('totalCurrentAssets', 0)
            current_liabilities = balance_sheet.get('totalCurrentLiabilities', 0)
            working_capital = current_assets - current_liabilities
            components['working_capital_ratio'] = working_capital / total_assets if total_assets > 0 else 0
            
            # Validate reasonableness
            if abs(components['working_capital_ratio']) > 1.0:
                warnings.append(f"Working capital ratio unusually high: {components['working_capital_ratio']:.3f}")
        
        # X2: Retained Earnings / Total Assets
        if data.retained_earnings_ratio is not None:
            components['retained_earnings_ratio'] = data.retained_earnings_ratio
        else:
            retained_earnings = balance_sheet.get('retainedEarnings', 0)
            components['retained_earnings_ratio'] = retained_earnings / total_assets if total_assets > 0 else 0
            
            # Validate reasonableness
            if abs(components['retained_earnings_ratio']) > 2.0:
                warnings.append(f"Retained earnings ratio unusually high: {components['retained_earnings_ratio']:.3f}")
        
        # X3: EBIT / Total Assets (Enhanced)
        if data.ebit_ratio is not None:
            components['ebit_ratio'] = data.ebit_ratio
            ebit_method = "pre_calculated"
            ebit_warnings = []
        else:
            ebit_value, ebit_method, ebit_warnings = self._calculate_ebit_enhanced(data)
            components['ebit_ratio'] = ebit_value / total_assets if total_assets > 0 else 0
            warnings.extend(ebit_warnings)
        
        # X4: Market Value or Book Value Equity / Total Liabilities
        total_liabilities = balance_sheet.get('totalLiabilities', 0)
        if total_liabilities <= 0:
            warnings.append("Total liabilities missing or zero - equity ratio will be zero")
            
        # Market value for original model
        if data.market_cap and data.market_cap > 0:
            components['market_equity_ratio'] = data.market_cap / total_liabilities if total_liabilities > 0 else 0
        else:
            components['market_equity_ratio'] = 0.0
            
        # Book value for other models
        book_value = balance_sheet.get('totalStockholdersEquity', 0)
        components['book_equity_ratio'] = book_value / total_liabilities if total_liabilities > 0 else 0
        
        # X5: Sales / Total Assets
        if data.asset_turnover is not None:
            components['asset_turnover'] = data.asset_turnover
        else:
            revenue = income_statement.get('revenue', 0)
            components['asset_turnover'] = revenue / total_assets if total_assets > 0 else 0
            
            # Validate reasonableness
            if components['asset_turnover'] > 5.0:
                warnings.append(f"Asset turnover unusually high: {components['asset_turnover']:.3f}")
        
        components['_metadata'] = {
            'ebit_method': ebit_method,
            'warnings': warnings,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities
        }
        
        return components

    def calculate_zscore(self, data: MergedFinancialData, forced_model: Optional[str] = None) -> ZScoreCalculationResult:
        """
        Calculate Z-Score from MergedFinancialData.
        
        Args:
            data: Merged financial data structure
            forced_model: Optional model to force (overrides automatic selection)
            
        Returns:
            ZScoreCalculationResult with calculation details
        """
        self.logger.info(f"Calculating Z-Score for {data.ticker}")
        
        # Detect and fix any scaling issues
        corrected_data = self._detect_and_fix_scaling(data)
        
        # Validate input data
        warnings = self._validate_calculation_data(corrected_data)
        
        # Select appropriate model
        try:
            if forced_model:
                # Use forced model if provided
                model_name = forced_model
                self.logger.info(f"Using forced model '{model_name}' for {data.ticker}")
            else:
                # Use automatic model selection
                model_selection = self.model_selector.select_model(corrected_data)
                model_name = model_selection.model_name
                self.logger.info(f"Selected {model_name} model for {data.ticker}")
            
        except Exception as e:
            self.logger.warning(f"Model selection failed for {data.ticker}: {e}")
            model_name = "original"  # Default fallback
            warnings.append(f"Using default model due to selection error: {e}")
        
        # Calculate Z-Score based on selected model
        try:
            if model_name == "original":
                components = self._calculate_original_zscore(corrected_data)
            elif model_name in ["public_service", "service"]:
                # Handle both "public_service" (from model selector) and "service" (from constants)
                components = self._calculate_service_zscore(corrected_data)
                model_name = "service"  # Normalize to constants key
            elif model_name == "private":
                components = self._calculate_private_zscore(corrected_data)
            elif model_name == "emerging":
                components = self._calculate_emerging_zscore(corrected_data)
            elif model_name == "retail":
                # Retail model - documented as proprietary extension
                self.logger.warning(f"Using proprietary retail model for {corrected_data.ticker}")
                components = self._calculate_original_zscore(corrected_data)  # Fallback to original
                warnings.append("Retail model not fully validated - using original model instead")
                model_name = "original"
            elif model_name == "financial":
                # Financial institutions - typically excluded from Altman Z-Score
                self.logger.warning(f"Financial company detected: {corrected_data.ticker} - Z-Score may not be applicable")
                components = self._calculate_emerging_zscore(corrected_data)  # Use current implementation
                warnings.append("Financial institutions may not be suitable for Z-Score analysis")
            else:
                # Default to original for unimplemented models
                self.logger.warning(f"Model {model_name} not fully implemented, using original")
                components = self._calculate_original_zscore(corrected_data)
                model_name = "original"
                warnings.append(f"Model {model_name} not implemented, used original instead")
            
            z_score = components['z_score']
            risk_category = self._categorize_risk(z_score, model_name)
            
            # Calculate data quality score
            data_quality = corrected_data.data_quality_score if corrected_data.data_quality_score is not None else 1.0
            
            # Preserve original metadata (like company_name) and add calculation metadata
            result_metadata = corrected_data.metadata.copy() if corrected_data.metadata else {}
            result_metadata.update({
                "calculation_method": "direct_from_merged_data",
                "components_calculated": len(components),
                "model_selection_confidence": getattr(model_selection, 'confidence', 0.8) if 'model_selection' in locals() else 0.8
            })
            
            result = ZScoreCalculationResult(
                ticker=corrected_data.ticker,
                z_score=z_score,
                model_used=model_name,
                risk_category=risk_category,
                component_values=components,
                calculation_timestamp=corrected_data.timestamp,  # Use period date from financial data
                data_quality_score=data_quality,
                warnings=warnings,
                metadata=result_metadata
            )
            
            self.logger.info(f"Z-Score calculation completed for {corrected_data.ticker}: {z_score:.3f} ({risk_category})")
            return result
            
        except Exception as e:
            error_msg = f"Z-Score calculation failed for {corrected_data.ticker}: {e}"
            self.logger.error(error_msg)
            raise CalculationError(error_msg) from e


async def calculate_zscore_from_merged_data(data: MergedFinancialData) -> ZScoreCalculationResult:
    """
    Async interface for Z-Score calculation.
    
    Args:
        data: Merged financial data structure
        
    Returns:
        ZScoreCalculationResult
    """
    calculator = ZScoreCalculator()
    
    # Run calculation in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, calculator.calculate_zscore, data)
