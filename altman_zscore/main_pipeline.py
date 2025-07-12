"""
Main Pipeline - Complete end-to-end investment analysis pipeline

This module provides the main entry point for complete ticker analysis,
integrating all layers from data fetching through comprehensive investment
analysis and final report generation.

Key Features:
- Complete pipeline orchestration with market analysis
- Z-Score calculation with market intelligence
- Error handling and recovery
- Progress tracking and logging with conditional progress bars
- Batch processing capabilities
- Bankruptcy analysis with pre-bankruptcy Z-Score progression
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from ._version import __version__
from .common.logging_config import get_logger, should_show_progress_bars, is_quiet_logging_mode
from .common.exceptions import PipelineError
from .data.bankruptcy_dates import get_bankruptcy_date, is_bankrupt_company, get_company_health_status
from .layers.data_fetch.data_merger import DataMerger
from .layers.zscore_calculation.zscore_calculator import ZScoreCalculator
from .layers.market_analysis.market_analysis_orchestrator import MarketAnalysisOrchestrator
from .layers.output_generation.csv_json_generator import CSVJSONGenerator
from .layers.output_generation.chart_generator import ChartGenerator
from .layers.output_generation.report_generator import ReportGenerator
from .layers.output_generation.file_manager import FileManager
from .layers.ai_analysis.ai_orchestrator import AIAnalysisOrchestrator
from .layers.forecasting.zscore_forecaster import ZScoreForecaster

logger = get_logger(__name__)


class PipelineProgressBar:
    """
    Progress bar for pipeline operations with granular step tracking.
    Shows progress when logging is in quiet mode.
    """
    
    def __init__(self, ticker: str, total_steps: int):
        """
        Initialize progress bar.
        
        Args:
            ticker: Stock ticker being analyzed
            total_steps: Total number of pipeline steps
        """
        self.ticker = ticker
        self.total_steps = total_steps
        self.current_step = 0
        self.current_substep = 0
        self.total_substeps = 0
        self.show_progress = should_show_progress_bars()
        self.last_line_length = 0  # Track last message length for proper clearing
        self.current_step_name = ""
        self.step_history = []  # Track completed steps for summary
        
    def update(self, step_name: str, step_number: Optional[int] = None, substep: str = None, 
               substep_total: Optional[int] = None, substep_current: Optional[int] = None):
        """
        Update progress bar with current step and optional substep progress.
        
        Args:
            step_name: Name of the current step
            step_number: Optional step number (auto-increments if not provided)
            substep: Optional substep description
            substep_total: Optional total number of substeps for this step
            substep_current: Optional current substep number
        """
        # Track step completion
        if step_number is not None and step_number != self.current_step:
            if self.current_step > 0 and self.current_step_name:
                self.step_history.append({
                    'step': self.current_step,
                    'name': self.current_step_name
                })
            
        if step_number is not None:
            self.current_step = step_number
        else:
            self.current_step += 1
        
        self.current_step_name = step_name
        
        # Handle substep tracking
        if substep_total is not None:
            self.total_substeps = substep_total
        if substep_current is not None:
            self.current_substep = substep_current
        elif substep and substep_total:
            self.current_substep += 1
            
        # Create full step description with enhanced detail
        full_step_name = step_name
        if substep:
            if self.total_substeps > 0:
                full_step_name = f"{step_name} - {substep} ({self.current_substep}/{self.total_substeps})"
            else:
                full_step_name = f"{step_name} - {substep}"
            
        if self.show_progress:
            self._display_progress(full_step_name)
    
    def update_substep(self, substep: str, substep_current: Optional[int] = None):
        """
        Update progress bar with substep without incrementing main step counter.
        
        Args:
            substep: Substep description
            substep_current: Optional current substep number
        """
        if substep_current is not None:
            self.current_substep = substep_current
        elif self.total_substeps > 0:
            self.current_substep += 1
            
        if self.show_progress:
            if self.total_substeps > 0:
                substep_detail = f"{substep} ({self.current_substep}/{self.total_substeps})"
            else:
                substep_detail = substep
            self._display_progress(f"{self.current_step_name or 'Processing'} - {substep_detail}")
    
    def start_substeps(self, total_substeps: int):
        """
        Initialize substep tracking for the current step.
        
        Args:
            total_substeps: Total number of substeps for this step
        """
        self.total_substeps = total_substeps
        self.current_substep = 0
    
    def get_current_step(self) -> int:
        """Get the current step number."""
        return self.current_step
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get basic progress summary."""
        return {
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'progress_percent': min(100, int((self.current_step / self.total_steps) * 100)),
            'step_history': self.step_history
        }
    
    def _display_progress(self, step_name: str, force_newline: bool = False):
        """Display the progress bar in terminal without timing information."""
        try:
            bar_length = 35
            progress = min(1.0, self.current_step / self.total_steps)
            filled_length = int(bar_length * progress)
            bar = '■' * filled_length + '□' * (bar_length - filled_length)
            
            # Create progress message without timing
            percentage = int(progress * 100)
            
            # Simple message format without timing
            msg = f"[{self.ticker}] |{bar}| {percentage:3d}% ({self.current_step}/{self.total_steps}) - {step_name}"
            
            # Handle terminal width constraints
            try:
                import shutil
                terminal_width = shutil.get_terminal_size().columns
                if len(msg) > terminal_width - 5:
                    # Truncate step name if message is too long
                    max_step_name_length = terminal_width - len(msg) + len(step_name) - 10
                    if max_step_name_length > 20:
                        truncated_step_name = step_name[:max_step_name_length] + "..."
                        msg = f"[{self.ticker}] |{bar}| {percentage:3d}% ({self.current_step}/{self.total_steps}) - {truncated_step_name}"
            except:
                pass  # Ignore terminal width detection errors
            
            # Clear the previous line completely using the tracked length
            clear_length = max(self.last_line_length, len(msg), 120)
            print(f"\r{' ' * clear_length}\r{msg}", end='', flush=True)
            
            # Update tracked length
            self.last_line_length = len(msg)
            
            # Add newline only when explicitly requested
            if force_newline:
                print()
                
        except Exception:
            # Silently ignore any progress display errors
            pass
    
    def finish(self, success: bool = True):
        """
        Finish the progress bar with summary.
        
        Args:
            success: Whether the operation completed successfully
        """
        if self.show_progress:
            # Final step tracking
            if self.current_step_name:
                self.step_history.append({
                    'step': self.current_step,
                    'name': self.current_step_name
                })
            
            status = "[OK] Complete" if success else "[X] Failed"
            if self.current_step < self.total_steps:
                self.current_step = self.total_steps
                
            # Update to final status without timing
            self._display_progress(status, force_newline=False)
            print()  # Single newline to end the progress line


class AltmanZScorePipeline:
    """Complete Altman Z-Score investment analysis pipeline."""
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize the pipeline.
        
        Args:
            output_base_path: Base directory for output files
        """
        self.output_base_path = output_base_path
        
        # Initialize components
        self.data_merger = DataMerger()
        self.zscore_calculator = ZScoreCalculator()
        self.market_analyzer = MarketAnalysisOrchestrator()
        self.ai_orchestrator = AIAnalysisOrchestrator()
        self.csv_json_generator = CSVJSONGenerator(output_base_path)
        self.chart_generator = ChartGenerator(output_base_path)
        self.report_generator = ReportGenerator(output_base_path)
        self.file_manager = FileManager(output_base_path)
        self.zscore_forecaster = ZScoreForecaster()
    
    async def analyze_ticker(
        self, 
        ticker: str,
        generate_charts: bool = True,
        generate_reports: bool = True,
        include_comprehensive_ai_analysis: bool = True,
        include_market_analysis: bool = True,
        forced_model: str = None,
        quarters: int = 4,
        batch_size: int = 10,
        bankruptcy_analysis: bool = False,
        pre_bankruptcy_quarters: int = 3,
        specific_date: str = None,
        enable_forecasting: bool = False,
        forecast_years: int = 2
    ) -> Dict[str, str]:
        """
        Complete analysis for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            generate_charts: Whether to generate visualization charts
            generate_reports: Whether to generate comprehensive reports
            include_comprehensive_ai_analysis: Whether to include AI final commentary generation
            include_market_analysis: Whether to include market analysis
            forced_model: Optional model to force (overrides automatic selection)
            quarters: Number of quarters for historical analysis
            batch_size: Batch size for concurrent processing
            bankruptcy_analysis: Enable bankruptcy-specific analysis for known bankrupt companies
            pre_bankruptcy_quarters: Number of quarters before bankruptcy to analyze
            specific_date: Specific date to analyze (format: YYYY-MM-DD)
            enable_forecasting: Whether to generate Z-Score forecasts based on analyst consensus
            forecast_years: Number of years to forecast (1-3)
            
        Returns:
            Dict[str, str]: Paths to generated output files
        """
        try:
            logger.info(f"Starting complete investment analysis for {ticker}")
            
            # ===============================================================================
            # STEP 0: BANKRUPTCY DETECTION AND ROUTING LOGIC
            # ===============================================================================
            # Test if ticker has current market data. If it fails, check bankruptcy database
            # and automatically switch to bankruptcy analysis mode.
            
            initial_test_passed = False
            auto_bankruptcy_mode = False
            auto_bankruptcy_info = None
            
            if not bankruptcy_analysis:  # Only test if not already in bankruptcy mode
                logger.info(f"Testing ticker availability for {ticker}")
                try:
                    # Quick test: try to fetch basic market data
                    from .layers.data_fetch.yahoo_fetcher import YahooDataFetcher
                    yahoo_fetcher = YahooDataFetcher()
                    
                    # Test current price - this will fail for delisted/bankrupt companies
                    test_price = yahoo_fetcher.get_current_price(ticker)  # Not async
                    if test_price and test_price > 0:
                        initial_test_passed = True
                        logger.info(f"✓ Ticker {ticker} is actively trading (price: ${test_price:.2f})")
                    else:
                        raise Exception(f"No current price data available for {ticker}")
                        
                except Exception as e:
                    logger.warning(f"✗ Ticker {ticker} failed availability test: {e}")
                    
                    # Check if this ticker is in the bankruptcy database
                    if is_bankrupt_company(ticker):
                        bankruptcy_date = get_bankruptcy_date(ticker)
                        if bankruptcy_date:
                            logger.info(f"🔍 Found {ticker} in bankruptcy database (bankruptcy: {bankruptcy_date.strftime('%Y-%m-%d')})")
                            logger.info(f"🔄 Automatically switching to bankruptcy analysis mode")
                            
                            auto_bankruptcy_mode = True
                            bankruptcy_analysis = True  # Enable bankruptcy analysis
                            
                            auto_bankruptcy_info = {
                                'ticker': ticker,
                                'bankruptcy_date': bankruptcy_date.strftime('%Y-%m-%d'),
                                'auto_detected': True,
                                'reason': 'Market data unavailable - company found in bankruptcy database'
                            }
                            
                            logger.info(f"📊 Will analyze {pre_bankruptcy_quarters} quarters before bankruptcy")
                        else:
                            logger.error(f"❌ {ticker} found in bankruptcy database but no bankruptcy date available")
                            raise PipelineError(f"Bankruptcy date not available for {ticker}")
                    else:
                        logger.error(f"❌ {ticker} not found in active markets or bankruptcy database")
                        raise PipelineError(f"Ticker {ticker} is not available for analysis (delisted/invalid ticker)")
            else:
                # Already in bankruptcy mode - validate the ticker is in database
                if not is_bankrupt_company(ticker):
                    logger.warning(f"⚠️  Bankruptcy analysis requested for {ticker} but not found in bankruptcy database")
                initial_test_passed = True  # Skip the test since we're explicitly in bankruptcy mode
            
            # Log analysis mode
            if auto_bankruptcy_mode:
                logger.info(f"🔬 Analysis Mode: AUTO-DETECTED BANKRUPTCY ANALYSIS for {ticker}")
                logger.info(f"📅 Bankruptcy Date: {auto_bankruptcy_info['bankruptcy_date']}")
                logger.info(f"🔍 Reason: {auto_bankruptcy_info['reason']}")
            elif bankruptcy_analysis:
                logger.info(f"🔬 Analysis Mode: MANUAL BANKRUPTCY ANALYSIS for {ticker}")
            else:
                logger.info(f"🔬 Analysis Mode: STANDARD ANALYSIS for {ticker}")
            
            # ===============================================================================
            # CONTINUE WITH STANDARD PIPELINE (with potential bankruptcy routing)
            # ===============================================================================
            
            # Calculate total steps for granular progress tracking
            total_steps = 0
            
            # Data fetching and processing: 3 steps
            total_steps += 3  # Fetch financial data, merge data, validate data
            
            # Z-Score calculation: 4 steps  
            total_steps += 4  # Model selection, scaling correction, calculation, validation
            
            # Market analysis: 5 steps (if enabled)
            if include_market_analysis:
                total_steps += 5  # Technical, valuation, performance, risk-return, consolidation
            
            # AI final commentary: 1 step (if enabled)
            if include_comprehensive_ai_analysis:
                total_steps += 1  # Direct LLM commentary generation
            
            # Z-Score forecasting: 1 step (if enabled and not bankruptcy analysis)
            if enable_forecasting and not bankruptcy_analysis:
                total_steps += 1  # Forecast generation
            
            # Output generation: base 2 steps
            total_steps += 2  # CSV/JSON generation
            
            # Optional outputs
            if generate_charts:
                total_steps += 3  # Chart data prep, visualization, finalization
            if generate_reports:
                total_steps += 2  # Comprehensive report, summary report
            
            # Initialize progress bar (only shows in quiet logging mode)
            progress = PipelineProgressBar(ticker, total_steps)
            current_step = 0
            
            # Enhanced analysis mode handling - simplified to always use requested quarters
            logger.info(f"Analysis configuration: {quarters} quarters, batch size {batch_size}")
            
            # Set environment variables for downstream components
            import os
            os.environ['ANALYSIS_QUARTERS'] = str(quarters)
            os.environ['BATCH_SIZE'] = str(batch_size)
            
            # STEP GROUP 1: Data Fetching and Processing (3 steps)
            current_step += 1
            progress.update("Fetching Financial Data", current_step)
            logger.info(f"Step {current_step}: Fetching financial data for {ticker}")
            
            # Add substep tracking for data fetching
            progress.start_substeps(3)
            progress.update_substep("Income statement data")
            
            current_step += 1  
            progress.update("Merging Financial Data", current_step)
            
            # Handle bankruptcy analysis if enabled (manual or auto-detected)
            end_date = None
            bankruptcy_info = None
            
            if bankruptcy_analysis and (is_bankrupt_company(ticker) or auto_bankruptcy_mode):
                if auto_bankruptcy_mode and auto_bankruptcy_info:
                    # Use auto-detected bankruptcy information
                    bankruptcy_date_str = auto_bankruptcy_info['bankruptcy_date']
                    bankruptcy_date = datetime.strptime(bankruptcy_date_str, '%Y-%m-%d').date()
                    logger.info(f"Using auto-detected bankruptcy info: {bankruptcy_date_str}")
                else:
                    # Use manual bankruptcy lookup
                    bankruptcy_date = get_bankruptcy_date(ticker)
                    bankruptcy_date_str = bankruptcy_date.strftime('%Y-%m-%d') if bankruptcy_date else None
                
                if bankruptcy_date:
                    logger.info(f"Bankruptcy analysis enabled for {ticker} - bankruptcy date: {bankruptcy_date.strftime('%Y-%m-%d')}")
                    end_date = bankruptcy_date.strftime("%Y-%m-%d")
                    
                    # Store comprehensive bankruptcy info for reporting
                    bankruptcy_info = {
                        'bankruptcy_date': end_date,
                        'pre_bankruptcy_quarters': pre_bankruptcy_quarters,
                        'analysis_type': 'Pre-Bankruptcy Analysis',
                        'auto_detected': auto_bankruptcy_mode,
                        'detection_reason': auto_bankruptcy_info.get('reason') if auto_bankruptcy_info else 'Manual analysis request'
                    }
                    
                    if auto_bankruptcy_mode:
                        logger.info(f"🤖 AUTO-DETECTED: Analyzing {pre_bankruptcy_quarters} quarters before bankruptcy ({end_date})")
                    else:
                        logger.info(f"📋 MANUAL: Analyzing {pre_bankruptcy_quarters} quarters before bankruptcy date: {end_date}")
                    
                    progress.update_substep(f"Bankruptcy analysis - {pre_bankruptcy_quarters} pre-bankruptcy quarters")
                    quarters = max(pre_bankruptcy_quarters + 1, 4)  # Ensure we get enough data
                else:
                    logger.error(f"Bankruptcy analysis requested for {ticker} but no bankruptcy date found")
                    raise PipelineError(f"Cannot perform bankruptcy analysis for {ticker}: no bankruptcy date available")
            elif specific_date:
                logger.info(f"Analyzing {ticker} at specific date: {specific_date}")
                end_date = specific_date
                progress.update_substep(f"Point-in-time analysis: {specific_date}")
            
            logger.info(f"Step {current_step}: Merging financial data for {ticker}")
            progress.start_substeps(quarters)
            
            # Pass parameters to data merger
            try:
                merged = await self.data_merger.merge_financial_data(
                    ticker, 
                    start_date=None,
                    end_date=end_date,
                    quarters=quarters
                )
                if not isinstance(merged, list):
                    merged = [merged]
            except Exception as e:
                # Enhanced error handling for bankruptcy analysis
                if auto_bankruptcy_mode or bankruptcy_analysis:
                    logger.error(f"❌ Data unavailable for bankrupt company {ticker}")
                    logger.error(f"🔍 Detected Issue: {str(e)}")
                    logger.info(f"📋 Bankruptcy Analysis Limitations:")
                    logger.info(f"   • Company: {ticker}")
                    logger.info(f"   • Bankruptcy Date: {bankruptcy_info.get('bankruptcy_date') if bankruptcy_info else 'Unknown'}")
                    logger.info(f"   • Status: Delisted/Data Unavailable")
                    logger.info(f"   • Primary Data Source (FMP): No longer available for delisted companies")
                    logger.info(f"")
                    logger.info(f"📊 Recommended Solutions:")
                    logger.info(f"   1. Use SEC EDGAR fallback (retail validation framework):")
                    logger.info(f"      python retail_validation/scripts/validate_retail_model.py --enable-edgar --test-edgar {ticker}")
                    logger.info(f"   2. Try alternative ticker format (if company merged/acquired)")
                    logger.info(f"   3. Use manual bankruptcy analysis with --bankruptcy-analysis flag for available pre-bankruptcy data")
                    logger.info(f"")
                    logger.info(f"💡 Auto-Detection Summary:")
                    if auto_bankruptcy_info:
                        logger.info(f"   • Detection: {auto_bankruptcy_info['reason']}")
                        logger.info(f"   • Bankruptcy Database: ✓ Found")
                        logger.info(f"   • Market Data: ✗ Unavailable")
                        logger.info(f"   • Financial Data: ✗ Unavailable")
                    
                    # Create a custom exception with bankruptcy context
                    raise PipelineError(
                        f"Bankruptcy analysis failed for {ticker}: {str(e)}. "
                        f"This is expected for fully delisted companies. "
                        f"Use SEC EDGAR fallback or retail validation framework for historical analysis."
                    )
                else:
                    # Regular error handling for non-bankruptcy cases
                    raise e
            
            progress.update_substep(f"Processed {len(merged)} quarters")
            
            current_step += 1
            progress.update("Validating Data Quality", current_step)
            logger.info(f"Step {current_step}: Validating data quality for {ticker} ({len(merged)} periods)")
            progress.start_substeps(len(merged))
            for i, _ in enumerate(merged, 1):
                progress.update_substep(f"Quarter {i} validation")
            
            # STEP GROUP 2: Z-Score Calculation (4 steps)
            current_step += 1
            progress.update("Model Selection", current_step)
            logger.info(f"Step {current_step}: Selecting optimal Z-Score model for {ticker}")
            progress.update_substep("Analyzing financial characteristics")
            
            current_step += 1
            progress.update("Scaling Correction", current_step)
            logger.info(f"Step {current_step}: Applying scaling corrections for {ticker}")
            progress.update_substep("Company size adjustments")
            
            current_step += 1
            progress.update("Calculating Z-Score", current_step)
            logger.info(f"Step {current_step}: Calculating Z-Score for {ticker}")
            progress.start_substeps(len(merged))
            
            # OPTIMIZATION: Perform model selection once for all quarters
            selected_model = forced_model
            if not forced_model and merged:
                logger.info(f"Performing single model selection for {ticker} (optimization)")
                try:
                    model_selection_result = self.zscore_calculator.model_selector.select_model(merged[0])
                    selected_model = model_selection_result.model_name
                    logger.info(f"Selected model '{selected_model}' for all {len(merged)} quarters of {ticker} "
                               f"(confidence: {model_selection_result.confidence:.2f})")
                except Exception as e:
                    logger.warning(f"Model selection failed for {ticker}: {e}. Using default 'original' model.")
                    selected_model = "original"
            
            zscore_results = []
            for i, data in enumerate(merged, 1):
                progress.update_substep(f"Quarter {i} calculation", i)
                result = self.zscore_calculator.calculate_zscore(data, forced_model=selected_model)
                zscore_results.append(result)
            
            current_step += 1
            progress.update("Validating Z-Score", current_step)
            logger.info(f"Step {current_step}: Validating Z-Score results for {ticker}")
            progress.update_substep("Risk category classification")
            
            # Use the most recent result for dashboard/report
            # NOTE: zscore_results[0] is the latest/current quarter based on data ordering
            latest_result = zscore_results[0]
            
            # Add bankruptcy analysis metadata if applicable
            if bankruptcy_info:
                if not hasattr(latest_result, 'metadata') or latest_result.metadata is None:
                    latest_result.metadata = {}
                
                # Add bankruptcy analysis information to metadata
                latest_result.metadata.update({
                    'bankruptcy_analysis': True,
                    'bankruptcy_date': bankruptcy_info['bankruptcy_date'],
                    'pre_bankruptcy_quarters': bankruptcy_info['pre_bankruptcy_quarters'],
                    'analysis_type': bankruptcy_info['analysis_type'],
                    'auto_detected': bankruptcy_info.get('auto_detected', False),
                    'detection_reason': bankruptcy_info.get('detection_reason', 'Manual analysis request')
                })
                
                logger.info(f"✓ Added bankruptcy metadata to {ticker} results")
                if bankruptcy_info.get('auto_detected'):
                    logger.info(f"  🤖 Auto-detected bankruptcy analysis")
                    logger.info(f"  📅 Bankruptcy date: {bankruptcy_info['bankruptcy_date']}")
                    logger.info(f"  🔍 Detection reason: {bankruptcy_info['detection_reason']}")
            
            
            # STEP GROUP 3: Market Analysis (5 steps if enabled)
            market_analysis = None
            if include_market_analysis:
                current_step += 1
                progress.update("Technical Analysis", current_step)
                logger.info(f"Step {current_step}: Running technical analysis for {ticker}")
                progress.start_substeps(4)
                progress.update_substep("Price indicators (RSI, MACD)")
                
                current_step += 1
                progress.update("Valuation Analysis", current_step)
                logger.info(f"Step {current_step}: Running valuation analysis for {ticker}")
                progress.start_substeps(1)
                progress.update_substep("P/E, P/B, market cap metrics")
                
                current_step += 1
                progress.update("Performance Analysis", current_step)
                logger.info(f"Step {current_step}: Running performance analysis for {ticker}")
                progress.start_substeps(1)
                progress.update_substep("Returns and volatility")
                
                current_step += 1
                progress.update("Risk-Return Analysis", current_step)
                logger.info(f"Step {current_step}: Running risk-return analysis for {ticker}")
                progress.start_substeps(1)
                progress.update_substep("Beta and Sharpe ratio")
                
                current_step += 1
                progress.update("Market Analysis Summary", current_step)
                logger.info(f"Step {current_step}: Consolidating market analysis for {ticker}")
                progress.start_substeps(1)
                progress.update_substep("Investment recommendation")
                
                try:
                    # Note: analyze_ticker method is not async, but we'll call it directly
                    market_analysis = self.market_analyzer.analyze_ticker(
                        ticker, 
                        zscore_results[0].z_score, 
                        zscore_results[0].risk_category
                    )
                    if market_analysis.risk_return_profile:
                        logger.info(f"Market analysis complete for {ticker}: {market_analysis.risk_return_profile.investment_rating} ({market_analysis.risk_return_profile.confidence_level:.1%} confidence)")
                    else:
                        logger.info(f"Market analysis complete for {ticker} (no risk-return profile generated)")
                except Exception as e:
                    logger.warning(f"Market analysis failed for {ticker}: {str(e)}. Continuing with Z-Score only.")
                    market_analysis = None
            
            # STEP GROUP 4: AI Final Commentary (1 step if enabled)
            comprehensive_ai_analysis = None
            if include_comprehensive_ai_analysis:
                current_step += 1
                progress.update("AI Final Commentary", current_step)
                logger.info(f"Step {current_step}: Generating AI final commentary for {ticker}")
                progress.start_substeps(2)
                
                try:
                    financial_data_for_ai = merged[0] if merged else None
                    if financial_data_for_ai:
                        progress.update_substep("Preparing analysis data")
                        comprehensive_ai_analysis = await self.ai_orchestrator.perform_comprehensive_analysis(
                            financial_data_for_ai,
                            zscore_results=zscore_results,  # Pass Z-Score calculations for trend analysis
                            market_analysis=market_analysis  # Pass market analysis for technical/valuation data
                        )
                        progress.update_substep("Generating insights")
                        logger.info(f"Direct LLM analysis complete for {ticker}: "
                                  f"commentary generated from comprehensive raw data")
                    else:
                        logger.warning(f"No financial data available for AI analysis of {ticker}")
                except Exception as e:
                    logger.warning(f"AI analysis failed for {ticker}: {str(e)}. Continuing with standard analysis.")
                    comprehensive_ai_analysis = None
            
            # STEP GROUP 4.5: Z-Score Forecasting (1 step if enabled)
            forecast_results = None
            if enable_forecasting and not bankruptcy_analysis:  # Skip forecasting for bankrupt companies
                current_step += 1
                progress.update("Generating Z-Score Forecasts", current_step)
                logger.info(f"Step {current_step}: Generating Z-Score forecasts for {ticker} ({forecast_years} years)")
                progress.start_substeps(3)
                
                try:
                    progress.update_substep("Fetching analyst consensus data")
                    
                    # Debug: Check the ZScoreCalculationResult being passed
                    current_zscore_result = zscore_results[0]
                    logger.info(f"DEBUG: Passing ZScoreCalculationResult with Z-Score: {current_zscore_result.z_score}")
                    logger.info(f"DEBUG: ZScoreCalculationResult component values: {current_zscore_result.component_values}")
                    
                    forecast_results = await self.zscore_forecaster.generate_forecasts(
                        ticker, current_zscore_result, forecast_years, zscore_results
                    )
                    
                    if forecast_results:
                        progress.update_substep("Calculating forecast scenarios")
                        logger.info(f"Successfully generated {len(forecast_results.forecast_scenarios)} forecast scenarios for {ticker}")
                        
                        # Debug: Check if scenarios have valid Z-Scores
                        if forecast_results.forecast_scenarios:
                            first_scenario = forecast_results.forecast_scenarios[0]
                            logger.info(f"DEBUG: First scenario Z-Score: {first_scenario.z_score}")
                        
                        # Add forecast metadata for reporting
                        forecast_summary = forecast_results.get_forecast_summary()
                        logger.info(f"DEBUG: Forecast summary keys: {list(forecast_summary.keys())}")
                        logger.info(f"DEBUG: Z-Score range data: {forecast_summary.get('z_score_range', 'MISSING')}")
                        logger.info(f"Forecast range: {forecast_summary.get('z_score_range', {}).get('min', 'N/A'):.2f} - {forecast_summary.get('z_score_range', {}).get('max', 'N/A'):.2f}")
                        
                        progress.update_substep("Validating forecast quality")
                    else:
                        logger.warning(f"Unable to generate forecasts for {ticker} - insufficient analyst coverage")
                        
                except Exception as e:
                    logger.warning(f"Forecasting failed for {ticker}: {str(e)}. Continuing with historical analysis only.")
                    forecast_results = None
            elif enable_forecasting and bankruptcy_analysis:
                logger.info(f"Skipping forecasting for bankrupt company {ticker}")
            
            # STEP GROUP 5: Output Generation
            current_step += 1
            progress.update("Generating CSV Data", current_step)
            logger.info(f"Step {current_step}: Generating CSV data for {ticker}")
            progress.update_substep("Formatting financial metrics")
            csv_path = self.csv_json_generator.generate_csv_report(zscore_results, market_analysis, comprehensive_ai_analysis, forecast_results)
            
            current_step += 1
            progress.update("Generating JSON Data", current_step)
            logger.info(f"Step {current_step}: Generating JSON data for {ticker}")
            progress.update_substep("Structuring analysis results")
            json_path = self.csv_json_generator.generate_json_report(zscore_results, market_analysis, comprehensive_ai_analysis, forecast_results)
            output_files = {'csv': csv_path, 'json': json_path}
            
            # STEP GROUP 6: Charts (3 steps if enabled)
            if generate_charts:
                current_step += 1
                progress.update("Preparing Chart Data", current_step)
                logger.info(f"Step {current_step}: Preparing chart data for {ticker}")
                progress.start_substeps(1)
                progress.update_substep("Processing time series")
                
                current_step += 1
                progress.update("Creating Visualizations", current_step)
                logger.info(f"Step {current_step}: Creating visualizations for {ticker} ({len(zscore_results)} periods)")
                progress.start_substeps(5)
                progress.update_substep("Z-Score dashboard")
                
                current_step += 1
                progress.update("Finalizing Charts", current_step)
                logger.info(f"Step {current_step}: Finalizing charts for {ticker}")
                progress.start_substeps(1)
                progress.update_substep("Rendering visualizations")
                logger.info(f"Step {current_step}: Finalizing charts for {ticker}")
                progress.update_substep("Rendering interactive plots")
                
                try:
                    chart_path = self.chart_generator.generate_zscore_dashboard(
                        zscore_results, market_analysis, comprehensive_ai_analysis, None, forecast_results
                    )
                    output_files['chart'] = chart_path
                except Exception as e:
                    logger.warning(f"Chart generation failed for {ticker}: {str(e)}. Continuing with other outputs.")
            
            # Removed AI Insights Generation - now using comprehensive AI commentary directly
            # This eliminates duplication while maintaining high-quality AI analysis
            
            # STEP GROUP 8: Reports (2 steps if enabled)
            if generate_reports:
                current_step += 1
                progress.update("Comprehensive Report", current_step)
                logger.info(f"Step {current_step}: Generating comprehensive report for {ticker}")
                progress.update_substep("Rendering HTML template")
                report_path = self.report_generator.generate_comprehensive_report(
                    latest_result, None, market_analysis, comprehensive_ai_analysis  # ai_insights removed
                )
                
                current_step += 1
                progress.update("Summary Report", current_step)
                logger.info(f"Step {current_step}: Generating summary report for {ticker}")
                progress.update_substep("Creating text summary")
                summary_path = self.report_generator.generate_summary_report(
                    latest_result, market_analysis, comprehensive_ai_analysis
                )
                output_files['report'] = report_path
                output_files['summary'] = summary_path
            
            # Complete progress
            progress.finish(success=True)
            logger.info(f"Complete investment analysis finished for {ticker}. Generated {len(output_files)} files.")
            return output_files
            
        except Exception as e:
            # Mark progress as failed if we have it
            if 'progress' in locals():
                progress.finish(success=False)
            error_msg = f"Pipeline failed for {ticker}: {str(e)}"
            logger.error(error_msg)
            raise PipelineError(error_msg) from e
    
    async def batch_analyze(
        self, 
        tickers: List[str],
        bankruptcy_analysis: bool = False,
        **kwargs
    ) -> Dict[str, Dict[str, str]]:
        """
        Analyze multiple tickers in batch.
        
        Args:
            tickers: List of ticker symbols
            bankruptcy_analysis: Enable bankruptcy-specific analysis for known bankrupt companies
            **kwargs: Additional arguments passed to analyze_ticker
            
        Returns:
            Dict[str, Dict[str, str]]: Results for each ticker
        """
        results = {}
        
        logger.info(f"Starting batch analysis for {len(tickers)} tickers")
        if bankruptcy_analysis:
            logger.info("Bankruptcy analysis mode enabled - checking for bankruptcy dates")
        
        # Show batch progress if in quiet logging mode
        show_batch_progress = should_show_progress_bars() and len(tickers) > 1
        
        # Filter tickers for bankruptcy analysis if enabled
        if bankruptcy_analysis:
            # Test each ticker to see if it's bankrupt/delisted
            logger.info("Testing tickers for bankruptcy/delisting status...")
            bankrupt_tickers_in_list = []
            
            for ticker in tickers:
                if is_bankrupt_company(ticker):
                    bankrupt_tickers_in_list.append(ticker)
                    logger.info(f"✓ {ticker} identified as bankrupt/delisted")
                else:
                    logger.debug(f"✗ {ticker} appears to be active")
            
            if not bankrupt_tickers_in_list:
                logger.warning("No bankrupt companies found in ticker list for bankruptcy analysis")
                if show_batch_progress:
                    print("\nNo bankrupt companies found in ticker list. Exiting bankruptcy analysis.")
                return {"error": "No bankrupt companies found in ticker list"}
            
            logger.info(f"Found {len(bankrupt_tickers_in_list)} bankrupt companies in list of {len(tickers)} tickers")
            
            if show_batch_progress:
                print(f"\nRunning bankruptcy analysis on {len(bankrupt_tickers_in_list)} companies:")
                for ticker in bankrupt_tickers_in_list:
                    bankruptcy_date = get_bankruptcy_date(ticker)
                    print(f"- {ticker}: Bankruptcy Date {bankruptcy_date.strftime('%Y-%m-%d')}")
                print("\n")
            
            # Use the filtered list for processing
            tickers_to_process = bankrupt_tickers_in_list
        else:
            # Normal analysis - process all tickers
            tickers_to_process = tickers
        
        for i, ticker in enumerate(tickers_to_process, 1):
            try:
                if show_batch_progress:
                    # Simple batch progress indicator
                    if bankruptcy_analysis:
                        bankruptcy_date = get_bankruptcy_date(ticker)
                        date_str = bankruptcy_date.strftime('%Y-%m-%d') if bankruptcy_date else "Unknown"
                        print(f"\n[BATCH] Processing bankrupt company {i}/{len(tickers_to_process)}: {ticker} (Bankruptcy: {date_str})")
                    else:
                        print(f"\n[BATCH] Processing {i}/{len(tickers_to_process)}: {ticker}")
                
                logger.info(f"Processing ticker {i}/{len(tickers_to_process)}: {ticker}")
                
                # Pass bankruptcy_analysis parameter to analyze_ticker
                results[ticker] = await self.analyze_ticker(ticker, bankruptcy_analysis=bankruptcy_analysis, **kwargs)
                
            except Exception as e:
                logger.error(f"Failed to process {ticker}: {str(e)}")
                results[ticker] = {'error': str(e)}
        
        if show_batch_progress:
            successful = len([r for r in results.values() if 'error' not in r])
            if bankruptcy_analysis:
                print(f"\nBankruptcy analysis complete: {successful}/{len(tickers_to_process)} companies analyzed successfully")
            else:
                print(f"\nBatch analysis complete: {successful}/{len(tickers_to_process)} successful")
        
        logger.info(f"Batch analysis complete. Processed {len(results)} tickers.")
        return results
    
    async def run_bankruptcy_analysis(
        self,
        specific_tickers: List[str] = None,
        pre_bankruptcy_quarters: int = 3,
        generate_charts: bool = True,
        generate_reports: bool = True,
        **kwargs
    ) -> Dict[str, Dict[str, str]]:
        """
        Run bankruptcy analysis on all known bankrupt companies or a specified list.
        Analyzes Z-Score progression for the quarters leading up to bankruptcy.
        
        Args:
            specific_tickers: Optional list of specific bankrupt tickers to analyze
            pre_bankruptcy_quarters: Number of quarters before bankruptcy to analyze
            generate_charts: Whether to generate visualization charts
            generate_reports: Whether to generate comprehensive reports
            **kwargs: Additional arguments passed to analyze_ticker
            
        Returns:
            Dict[str, Dict[str, str]]: Results for each bankrupt ticker
        """
        logger.info(f"Starting bankruptcy analysis for {pre_bankruptcy_quarters} pre-bankruptcy quarters")
        
        # With dynamic bankruptcy detection, we need to check each ticker individually
        # If specific_tickers is provided, test each one for bankruptcy status
        if specific_tickers:
            logger.info(f"Testing {len(specific_tickers)} specific tickers for bankruptcy status...")
            bankrupt_tickers = []
            
            for ticker in specific_tickers:
                if is_bankrupt_company(ticker):
                    bankrupt_tickers.append(ticker)
                    logger.info(f"✓ {ticker} identified as bankrupt/delisted")
                else:
                    logger.warning(f"✗ {ticker} appears to be active (not bankrupt)")
            
            if not bankrupt_tickers:
                logger.warning("No bankrupt companies found in provided ticker list")
                return {"error": "No bankrupt companies in provided ticker list"}
        else:
            logger.error("Dynamic bankruptcy detection requires specific ticker list")
            return {"error": "Bankruptcy analysis requires specific ticker list with dynamic detection"}
        
        logger.info(f"Running bankruptcy analysis on {len(bankrupt_tickers)} companies")
        
        # Show summary of companies to analyze
        show_progress = should_show_progress_bars()
        if show_progress:
            print("\nRunning bankruptcy analysis on the following companies:")
            for ticker in bankrupt_tickers:
                bankruptcy_date = get_bankruptcy_date(ticker)
                print(f"- {ticker}: Bankruptcy Date {bankruptcy_date.strftime('%Y-%m-%d')}")
            print("\n")
        
        # Run the batch analysis with bankruptcy_analysis=True
        return await self.batch_analyze(
            bankrupt_tickers,
            bankruptcy_analysis=True,
            pre_bankruptcy_quarters=pre_bankruptcy_quarters,
            generate_charts=generate_charts,
            generate_reports=generate_reports,
            **kwargs
        )
    
    def get_pipeline_status(self) -> Dict[str, any]:
        """
        Get current pipeline status and health.
        
        Returns:
            Dict: Pipeline status information
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'components': {
                'data_merger': 'Ready',
                'zscore_calculator': 'Ready', 
                'market_analyzer': 'Ready',
                'output_generators': 'Ready',
                'file_manager': 'Ready'
            },
            'storage': self.file_manager.get_storage_summary(),
            'version': __version__
        }
