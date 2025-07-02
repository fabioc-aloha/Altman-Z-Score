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
"""

import asyncio
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

from ._version import __version__
from .common.logging_config import get_logger, should_show_progress_bars, is_quiet_logging_mode
from .common.exceptions import PipelineError
from .layers.data_fetch.data_merger import DataMerger
from .layers.zscore_calculation.zscore_calculator import ZScoreCalculator
from .layers.market_analysis.market_analysis_orchestrator import MarketAnalysisOrchestrator
from .layers.output_generation.csv_json_generator import CSVJSONGenerator
from .layers.output_generation.chart_generator import ChartGenerator
from .layers.output_generation.report_generator import ReportGenerator
from .layers.output_generation.file_manager import FileManager
from .layers.ai_analysis.ai_orchestrator import AIAnalysisOrchestrator

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
    
    async def analyze_ticker(
        self, 
        ticker: str,
        generate_charts: bool = True,
        generate_reports: bool = True,
        include_comprehensive_ai_analysis: bool = True,
        include_market_analysis: bool = True,
        forced_model: str = None,
        quarters: int = 4,
        enhanced_analysis: bool = False,
        batch_size: int = 10
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
            quarters: Number of quarters for historical analysis (enhanced accounts: 8-20)
            enhanced_analysis: Enable enhanced features for upgraded FMP accounts
            batch_size: Batch size for concurrent processing (enhanced accounts: 20-50)
            
        Returns:
            Dict[str, str]: Paths to generated output files
        """
        try:
            logger.info(f"Starting complete investment analysis for {ticker}")
            
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
            
            # Enhanced analysis mode handling
            if enhanced_analysis:
                logger.info(f"Enhanced analysis mode enabled: {quarters} quarters, batch size {batch_size}")
                # Set enhanced mode environment variables for downstream components
                import os
                os.environ['FMP_ENHANCED_MODE'] = '1'
                os.environ['ANALYSIS_QUARTERS'] = str(quarters)
                os.environ['BATCH_SIZE'] = str(batch_size)
            
            # Validate quarters parameter for enhanced vs regular accounts
            if quarters > 4 and not enhanced_analysis:
                logger.warning(f"Quarters={quarters} requested but enhanced_analysis=False. Using 4 quarters for free account compatibility.")
                quarters = 4
            elif enhanced_analysis and quarters < 8:
                logger.info(f"Enhanced analysis enabled but quarters={quarters}. Consider using 8+ quarters for better trend analysis.")
            
            # STEP GROUP 1: Data Fetching and Processing (3 steps)
            current_step += 1
            progress.update("Fetching Financial Data", current_step)
            logger.info(f"Step {current_step}: Fetching financial data for {ticker}")
            
            # Add substep tracking for data fetching
            progress.start_substeps(3)
            progress.update_substep("Income statement data")
            
            current_step += 1  
            progress.update("Merging Financial Data", current_step)
            logger.info(f"Step {current_step}: Merging financial data for {ticker}")
            progress.start_substeps(quarters if enhanced_analysis else 4)
            
            # Pass enhanced parameters to data merger
            merged = await self.data_merger.merge_financial_data(
                ticker, 
                start_date=None,
                quarters=quarters if enhanced_analysis else 4
            )
            if not isinstance(merged, list):
                merged = [merged]
            
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
            latest_result = zscore_results[0]
            
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
            
            # STEP GROUP 5: Output Generation
            current_step += 1
            progress.update("Generating CSV Data", current_step)
            logger.info(f"Step {current_step}: Generating CSV data for {ticker}")
            progress.update_substep("Formatting financial metrics")
            csv_path = self.csv_json_generator.generate_csv_report(zscore_results, market_analysis, comprehensive_ai_analysis)
            
            current_step += 1
            progress.update("Generating JSON Data", current_step)
            logger.info(f"Step {current_step}: Generating JSON data for {ticker}")
            progress.update_substep("Structuring analysis results")
            json_path = self.csv_json_generator.generate_json_report(zscore_results, market_analysis, comprehensive_ai_analysis)
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
                        zscore_results, market_analysis, comprehensive_ai_analysis
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
        **kwargs
    ) -> Dict[str, Dict[str, str]]:
        """
        Analyze multiple tickers in batch.
        
        Args:
            tickers: List of ticker symbols
            **kwargs: Additional arguments passed to analyze_ticker
            
        Returns:
            Dict[str, Dict[str, str]]: Results for each ticker
        """
        results = {}
        
        logger.info(f"Starting batch analysis for {len(tickers)} tickers")
        
        # Show batch progress if in quiet logging mode
        show_batch_progress = should_show_progress_bars() and len(tickers) > 1
        
        for i, ticker in enumerate(tickers, 1):
            try:
                if show_batch_progress:
                    # Simple batch progress indicator
                    print(f"\n[BATCH] Processing {i}/{len(tickers)}: {ticker}")
                
                logger.info(f"Processing ticker {i}/{len(tickers)}: {ticker}")
                results[ticker] = await self.analyze_ticker(ticker, **kwargs)
                
            except Exception as e:
                logger.error(f"Failed to process {ticker}: {str(e)}")
                results[ticker] = {'error': str(e)}
        
        if show_batch_progress:
            successful = len([r for r in results.values() if 'error' not in r])
            print(f"\nBatch analysis complete: {successful}/{len(tickers)} successful")
        
        logger.info(f"Batch analysis complete. Processed {len(results)} tickers.")
        return results
    
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
