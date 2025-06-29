"""
Pipeline Progress Tracking - Modular progress bar and step management

This module provides comprehensive progress tracking for the main pipeline,
separating progress bar logic from the core pipeline orchestration.

Key Features:
- Granular step tracking with substeps
- Conditional progress display based on logging mode
- Step timing and performance metrics
- Pipeline status reporting
- Error handling and recovery tracking
"""

import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..common.logging_config import get_logger, should_show_progress_bars, is_quiet_logging_mode

logger = get_logger(__name__)


@dataclass
class StepTiming:
    """Timing information for a pipeline step."""
    step_number: int
    step_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    substeps_completed: int = 0
    substeps_total: int = 0


class PipelineProgressTracker:
    """
    Advanced progress tracker for pipeline operations with granular step tracking.
    Shows detailed progress when logging is in quiet mode.
    """
    
    def __init__(self, ticker: str, total_steps: int, show_timing: bool = True):
        """
        Initialize progress tracker.
        
        Args:
            ticker: Stock ticker being analyzed
            total_steps: Total number of pipeline steps
            show_timing: Whether to track and display timing information
        """
        self.ticker = ticker
        self.total_steps = total_steps
        self.current_step = 0
        self.current_substep = 0
        self.total_substeps = 0
        self.show_progress = should_show_progress_bars()
        self.show_timing = show_timing
        self.last_line_length = 0  # Track last message length for proper clearing
        
        # Timing tracking
        self.pipeline_start_time = datetime.now()
        self.current_step_start_time = datetime.now()
        self.step_history: List[StepTiming] = []
        self.current_step_name = ""
        
        # Status tracking
        self.failed_steps: List[str] = []
        self.warnings: List[str] = []
        self.completed_successfully = False
        
        if self.show_progress:
            self._clear_line()
            print(f"🚀 Starting analysis for {ticker} ({total_steps} steps)")
        
    def start_step(self, step_name: str, step_number: Optional[int] = None, substeps_total: int = 0):
        """
        Start a new pipeline step.
        
        Args:
            step_name: Name of the step
            step_number: Optional step number (auto-increments if not provided)
            substeps_total: Total number of substeps for this step
        """
        # Complete previous step if it exists
        if self.current_step > 0 and self.current_step_name:
            self._complete_current_step()
        
        # Start new step
        if step_number is not None:
            self.current_step = step_number
        else:
            self.current_step += 1
            
        self.current_step_name = step_name
        self.current_substep = 0
        self.total_substeps = substeps_total
        self.current_step_start_time = datetime.now()
        
        self._update_display()
        
    def update_substep(self, substep_description: str, substep_number: Optional[int] = None):
        """
        Update current substep progress.
        
        Args:
            substep_description: Description of current substep
            substep_number: Optional substep number (auto-increments if not provided)
        """
        if substep_number is not None:
            self.current_substep = substep_number
        else:
            self.current_substep += 1
            
        if self.show_progress:
            substep_text = f" • {substep_description}"
            if self.total_substeps > 0:
                substep_text += f" ({self.current_substep}/{self.total_substeps})"
            self._display_progress(additional_text=substep_text)
    
    def add_warning(self, warning: str):
        """Add a warning message to the step."""
        self.warnings.append(f"Step {self.current_step}: {warning}")
        
    def mark_step_failed(self, error_message: str):
        """Mark the current step as failed."""
        self.failed_steps.append(f"Step {self.current_step} ({self.current_step_name}): {error_message}")
        
    def finish(self, success: bool = True):
        """
        Finish the pipeline progress tracking.
        
        Args:
            success: Whether the pipeline completed successfully
        """
        # Complete final step
        if self.current_step > 0 and self.current_step_name:
            self._complete_current_step()
            
        self.completed_successfully = success
        total_duration = (datetime.now() - self.pipeline_start_time).total_seconds()
        
        if self.show_progress:
            self._clear_line()
            if success:
                print(f"✅ {self.ticker} analysis completed successfully in {total_duration:.1f}s")
                if self.warnings:
                    print(f"⚠️  {len(self.warnings)} warnings occurred")
            else:
                print(f"❌ {self.ticker} analysis failed after {total_duration:.1f}s")
                if self.failed_steps:
                    print(f"💥 {len(self.failed_steps)} steps failed")
                    
        if self.show_timing and self.step_history:
            self._display_timing_summary()
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        total_duration = (datetime.now() - self.pipeline_start_time).total_seconds()
        
        return {
            'ticker': self.ticker,
            'total_steps': self.total_steps,
            'completed_steps': len(self.step_history),
            'current_step': self.current_step,
            'pipeline_duration_seconds': total_duration,
            'completed_successfully': self.completed_successfully,
            'warnings_count': len(self.warnings),
            'failed_steps_count': len(self.failed_steps),
            'warnings': self.warnings,
            'failed_steps': self.failed_steps,
            'step_timings': [
                {
                    'step': timing.step_number,
                    'name': timing.step_name,
                    'duration': timing.duration_seconds,
                    'substeps': f"{timing.substeps_completed}/{timing.substeps_total}"
                }
                for timing in self.step_history
            ]
        }
    
    def _complete_current_step(self):
        """Complete the current step and record timing."""
        end_time = datetime.now()
        duration = (end_time - self.current_step_start_time).total_seconds()
        
        step_timing = StepTiming(
            step_number=self.current_step,
            step_name=self.current_step_name,
            start_time=self.current_step_start_time,
            end_time=end_time,
            duration_seconds=duration,
            substeps_completed=self.current_substep,
            substeps_total=self.total_substeps
        )
        
        self.step_history.append(step_timing)
        
    def _update_display(self):
        """Update the progress display."""
        if self.show_progress:
            self._display_progress()
            
    def _display_progress(self, additional_text: str = ""):
        """Display current progress with optional additional text."""
        progress_percent = (self.current_step / self.total_steps) * 100
        
        # Create progress bar
        bar_length = 20
        filled_length = int(bar_length * self.current_step // self.total_steps)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Main progress text
        progress_text = f"[{bar}] {progress_percent:.0f}% | Step {self.current_step}/{self.total_steps}: {self.current_step_name}"
        
        # Add timing if enabled
        if self.show_timing and self.step_history:
            avg_step_time = sum(s.duration_seconds for s in self.step_history) / len(self.step_history)
            remaining_steps = self.total_steps - self.current_step
            eta_seconds = avg_step_time * remaining_steps
            progress_text += f" | ETA: {eta_seconds:.0f}s"
        
        # Add additional text (like substep info)
        if additional_text:
            progress_text += additional_text
            
        # Clear previous line and print new progress
        self._clear_line()
        print(f"\r{progress_text}", end="", flush=True)
        self.last_line_length = len(progress_text)
        
    def _clear_line(self):
        """Clear the current line."""
        if self.last_line_length > 0:
            print(f"\r{' ' * self.last_line_length}\r", end="", flush=True)
            
    def _display_timing_summary(self):
        """Display timing summary for completed steps."""
        if not self.step_history:
            return
            
        print("\n📊 Step Timing Summary:")
        print("=" * 60)
        
        total_time = sum(s.duration_seconds for s in self.step_history)
        
        for timing in self.step_history:
            percentage = (timing.duration_seconds / total_time) * 100
            print(f"  {timing.step_number:2d}. {timing.step_name:<30} {timing.duration_seconds:6.2f}s ({percentage:5.1f}%)")
            
        print("=" * 60)
        print(f"  Total Pipeline Time: {total_time:.2f}s")
        
        # Find slowest steps
        slowest_steps = sorted(self.step_history, key=lambda x: x.duration_seconds, reverse=True)[:3]
        print(f"\n🐌 Slowest Steps:")
        for i, timing in enumerate(slowest_steps, 1):
            print(f"  {i}. {timing.step_name} ({timing.duration_seconds:.2f}s)")


class PipelineStepManager:
    """
    Manages pipeline step definitions and execution order.
    Provides a centralized way to define and modify pipeline steps.
    """
    
    def __init__(self):
        """Initialize step manager."""
        self.logger = get_logger(self.__class__.__name__)
        
    def get_pipeline_steps(
        self, 
        include_market_analysis: bool = True,
        include_ai_analysis: bool = True,
        generate_charts: bool = True,
        generate_reports: bool = True,
        include_ai_insights: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get the complete list of pipeline steps based on configuration.
        
        Args:
            include_market_analysis: Whether to include market analysis steps
            include_ai_analysis: Whether to include comprehensive AI analysis
            generate_charts: Whether to include chart generation steps
            generate_reports: Whether to include report generation steps
            include_ai_insights: Whether to include AI insights generation
            
        Returns:
            List of step definitions with metadata
        """
        steps = []
        
        # Core data processing steps (always included)
        steps.extend([
            {
                'name': 'Fetching Financial Data',
                'category': 'data_processing',
                'substeps': 3,
                'description': 'Retrieve financial statements and market data'
            },
            {
                'name': 'Merging Financial Data', 
                'category': 'data_processing',
                'substeps': 2,
                'description': 'Combine and validate financial data sources'
            },
            {
                'name': 'Validating Data Quality',
                'category': 'data_processing', 
                'substeps': 1,
                'description': 'Check data completeness and accuracy'
            }
        ])
        
        # Z-Score calculation steps (always included)
        steps.extend([
            {
                'name': 'Model Selection',
                'category': 'zscore_calculation',
                'substeps': 1,
                'description': 'Select optimal Z-Score model for company'
            },
            {
                'name': 'Scaling Correction',
                'category': 'zscore_calculation',
                'substeps': 1,
                'description': 'Apply company size adjustments'
            },
            {
                'name': 'Calculating Z-Score',
                'category': 'zscore_calculation',
                'substeps': 1,
                'description': 'Compute final Z-Score and risk category'
            },
            {
                'name': 'Validating Z-Score',
                'category': 'zscore_calculation',
                'substeps': 1,
                'description': 'Verify calculation accuracy'
            }
        ])
        
        # Market analysis steps (optional)
        if include_market_analysis:
            steps.extend([
                {
                    'name': 'Technical Analysis',
                    'category': 'market_analysis',
                    'substeps': 4,
                    'description': 'Analyze price indicators and trends'
                },
                {
                    'name': 'Valuation Analysis',
                    'category': 'market_analysis',
                    'substeps': 3,
                    'description': 'Evaluate market valuation metrics'
                },
                {
                    'name': 'Performance Analysis',
                    'category': 'market_analysis',
                    'substeps': 2,
                    'description': 'Assess returns and volatility'
                },
                {
                    'name': 'Risk-Return Analysis',
                    'category': 'market_analysis',
                    'substeps': 2,
                    'description': 'Calculate risk-adjusted metrics'
                },
                {
                    'name': 'Market Analysis Summary',
                    'category': 'market_analysis',
                    'substeps': 1,
                    'description': 'Consolidate market insights'
                }
            ])
        
        # Comprehensive AI analysis steps (optional)
        if include_ai_analysis:
            steps.extend([
                {
                    'name': 'AI Data Quality Check',
                    'category': 'ai_analysis',
                    'substeps': 2,
                    'description': 'AI-powered data quality assessment'
                },
                {
                    'name': 'AI Peer Analysis',
                    'category': 'ai_analysis',
                    'substeps': 3,
                    'description': 'Industry comparison and ranking'
                },
                {
                    'name': 'AI Sentiment Analysis',
                    'category': 'ai_analysis',
                    'substeps': 2,
                    'description': 'Market sentiment evaluation'
                },
                {
                    'name': 'AI Risk Analysis',
                    'category': 'ai_analysis',
                    'substeps': 2,
                    'description': 'Comprehensive risk assessment'
                },
                {
                    'name': 'AI Final Commentary',
                    'category': 'ai_analysis',
                    'substeps': 2,
                    'description': 'Generate final AI insights'
                }
            ])
        
        # Output generation steps (always included)
        steps.extend([
            {
                'name': 'Generating CSV Data',
                'category': 'output_generation',
                'substeps': 1,
                'description': 'Export structured data to CSV'
            },
            {
                'name': 'Generating JSON Data',
                'category': 'output_generation',
                'substeps': 1,
                'description': 'Export structured data to JSON'
            }
        ])
        
        # Chart generation steps (optional)
        if generate_charts:
            steps.extend([
                {
                    'name': 'Preparing Chart Data',
                    'category': 'chart_generation',
                    'substeps': 2,
                    'description': 'Process data for visualization'
                },
                {
                    'name': 'Creating Visualizations',
                    'category': 'chart_generation',
                    'substeps': 5,
                    'description': 'Generate interactive charts'
                },
                {
                    'name': 'Finalizing Charts',
                    'category': 'chart_generation',
                    'substeps': 1,
                    'description': 'Render and save visualizations'
                }
            ])
        
        # AI insights generation (optional)
        if include_ai_insights:
            steps.extend([
                {
                    'name': 'AI Insights Generation',
                    'category': 'ai_insights',
                    'substeps': 2,
                    'description': 'Generate investment insights'
                },
                {
                    'name': 'AI Insights Formatting',
                    'category': 'ai_insights',
                    'substeps': 1,
                    'description': 'Format insights for output'
                }
            ])
        
        # Report generation steps (optional)
        if generate_reports:
            steps.extend([
                {
                    'name': 'Comprehensive Report',
                    'category': 'report_generation',
                    'substeps': 2,
                    'description': 'Generate detailed HTML report'
                },
                {
                    'name': 'Summary Report',
                    'category': 'report_generation',
                    'substeps': 1,
                    'description': 'Create concise text summary'
                }
            ])
        
        return steps
    
    def get_total_steps(self, **kwargs) -> int:
        """Get total number of steps for given configuration."""
        steps = self.get_pipeline_steps(**kwargs)
        return len(steps)
    
    def get_steps_by_category(self, category: str, **kwargs) -> List[Dict[str, Any]]:
        """Get steps filtered by category."""
        steps = self.get_pipeline_steps(**kwargs)
        return [step for step in steps if step['category'] == category]
