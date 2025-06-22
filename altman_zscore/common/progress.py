"""
Progress tracking framework for the Altman Z-Score pipeline.

This module provides unified progress tracking across all layers with support for nested
progress tracking, logging integration, and optional UI progress indicators.
"""

import threading
import time
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from contextlib import contextmanager
from enum import Enum

from .logging_config import get_logger
from .exceptions import AltmanZScoreError

logger = get_logger(__name__)


class ProgressStatus(Enum):
    """Progress status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressInfo:
    """Progress information for a task."""
    task_id: str
    description: str
    current: int = 0
    total: int = 100
    status: ProgressStatus = ProgressStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total <= 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100.0)
    
    @property
    def elapsed_time(self) -> Optional[float]:
        """Calculate elapsed time in seconds."""
        if self.start_time is None:
            return None
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def estimated_remaining(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        elapsed = self.elapsed_time
        if elapsed is None or self.current <= 0:
            return None
        
        if self.percentage >= 100:
            return 0.0
        
        rate = self.current / elapsed
        remaining_items = max(0, self.total - self.current)
        return remaining_items / rate if rate > 0 else None


class ProgressTracker:
    """
    Thread-safe progress tracker with support for nested progress tracking.
    
    Features:
    - Hierarchical progress tracking (parent/child relationships)
    - Thread-safe operations
    - Integration with logging framework
    - Optional callback for UI updates
    - Automatic cleanup of completed tasks
    """
    
    def __init__(self, 
                 log_interval: float = 5.0,
                 ui_callback: Optional[Callable[[ProgressInfo], None]] = None,
                 auto_cleanup: bool = True):
        """
        Initialize progress tracker.
        
        Args:
            log_interval: Seconds between automatic progress log messages
            ui_callback: Optional callback for UI progress updates
            auto_cleanup: Whether to automatically cleanup completed tasks
        """
        self._tasks: Dict[str, ProgressInfo] = {}
        self._lock = threading.RLock()
        self._log_interval = log_interval
        self._ui_callback = ui_callback
        self._auto_cleanup = auto_cleanup
        self._last_log_time: Dict[str, float] = {}
    
    def create_task(self, 
                   task_id: str, 
                   description: str, 
                   total: int = 100,
                   parent_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> ProgressInfo:
        """
        Create a new progress task.
        
        Args:
            task_id: Unique identifier for the task
            description: Human-readable description
            total: Total number of items to process
            parent_id: Optional parent task ID for nested tracking
            metadata: Optional metadata dictionary
            
        Returns:
            ProgressInfo object for the created task
            
        Raises:
            AltmanZScoreError: If task ID already exists
        """
        with self._lock:
            if task_id in self._tasks:
                raise AltmanZScoreError(f"Task ID '{task_id}' already exists")
            
            # Validate parent exists if specified
            if parent_id is not None and parent_id not in self._tasks:
                raise AltmanZScoreError(f"Parent task '{parent_id}' does not exist")
            
            task = ProgressInfo(
                task_id=task_id,
                description=description,
                total=total,
                parent_id=parent_id,
                metadata=metadata or {}
            )
            
            self._tasks[task_id] = task
            logger.info(f"Created progress task '{task_id}': {description}")
            
            return task
    
    def start_task(self, task_id: str) -> None:
        """
        Start a progress task.
        
        Args:
            task_id: Task identifier
            
        Raises:
            AltmanZScoreError: If task doesn't exist
        """
        with self._lock:
            if task_id not in self._tasks:
                raise AltmanZScoreError(f"Task '{task_id}' does not exist")
            
            task = self._tasks[task_id]
            task.status = ProgressStatus.RUNNING
            task.start_time = time.time()
            
            logger.info(f"Started task '{task_id}': {task.description}")
            self._notify_ui(task)
    
    def update_progress(self, 
                       task_id: str, 
                       current: int, 
                       message: Optional[str] = None) -> None:
        """
        Update task progress.
        
        Args:
            task_id: Task identifier
            current: Current progress value
            message: Optional progress message
        """
        with self._lock:
            if task_id not in self._tasks:
                logger.warning(f"Attempted to update non-existent task '{task_id}'")
                return
            
            task = self._tasks[task_id]
            task.current = current
            
            if message:
                task.metadata['last_message'] = message
            
            # Log progress at intervals
            current_time = time.time()
            last_log = self._last_log_time.get(task_id, 0)
            
            if current_time - last_log >= self._log_interval:
                logger.info(f"Task '{task_id}' progress: {task.percentage:.1f}% "
                           f"({current}/{task.total})")
                self._last_log_time[task_id] = current_time
            
            self._notify_ui(task)
    
    def complete_task(self, 
                     task_id: str, 
                     success: bool = True,
                     message: Optional[str] = None) -> None:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task identifier
            success: Whether task completed successfully
            message: Optional completion message
        """
        with self._lock:
            if task_id not in self._tasks:
                logger.warning(f"Attempted to complete non-existent task '{task_id}'")
                return
            
            task = self._tasks[task_id]
            task.status = ProgressStatus.COMPLETED if success else ProgressStatus.FAILED
            task.end_time = time.time()
            task.current = task.total if success else task.current
            
            if message:
                task.metadata['completion_message'] = message
            
            elapsed = task.elapsed_time
            elapsed_str = f" in {elapsed:.2f}s" if elapsed else ""
            
            if success:
                logger.info(f"Completed task '{task_id}'{elapsed_str}")
            else:
                logger.error(f"Failed task '{task_id}'{elapsed_str}")
            
            self._notify_ui(task)
            
            # Auto-cleanup if enabled
            if self._auto_cleanup and success:
                # Don't cleanup immediately - give UI time to update
                threading.Timer(1.0, self._cleanup_task, args=[task_id]).start()
    
    def cancel_task(self, task_id: str, message: Optional[str] = None) -> None:
        """
        Cancel a task.
        
        Args:
            task_id: Task identifier
            message: Optional cancellation message
        """
        with self._lock:
            if task_id not in self._tasks:
                logger.warning(f"Attempted to cancel non-existent task '{task_id}'")
                return
            
            task = self._tasks[task_id]
            task.status = ProgressStatus.CANCELLED
            task.end_time = time.time()
            
            if message:
                task.metadata['cancellation_message'] = message
            
            logger.info(f"Cancelled task '{task_id}': {message or 'No reason provided'}")
            self._notify_ui(task)
    
    def get_task(self, task_id: str) -> Optional[ProgressInfo]:
        """Get task information."""
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_active_tasks(self) -> List[ProgressInfo]:
        """Get all active (running) tasks."""
        with self._lock:
            return [task for task in self._tasks.values() 
                   if task.status == ProgressStatus.RUNNING]
    
    def get_child_tasks(self, parent_id: str) -> List[ProgressInfo]:
        """Get all child tasks for a parent."""
        with self._lock:
            return [task for task in self._tasks.values() 
                   if task.parent_id == parent_id]
    
    def _notify_ui(self, task: ProgressInfo) -> None:
        """Notify UI callback if configured."""
        if self._ui_callback:
            try:
                self._ui_callback(task)
            except Exception as e:
                logger.warning(f"UI callback error for task '{task.task_id}': {e}")
    
    def _cleanup_task(self, task_id: str) -> None:
        """Remove completed task from tracking."""
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                self._last_log_time.pop(task_id, None)
    
    @contextmanager
    def track_task(self, 
                   task_id: str, 
                   description: str, 
                   total: int = 100,
                   parent_id: Optional[str] = None):
        """
        Context manager for automatic task lifecycle management.
        
        Usage:
            with tracker.track_task("my_task", "Processing data", 100):
                for i in range(100):
                    # Do work
                    tracker.update_progress("my_task", i + 1)
        """
        self.create_task(task_id, description, total, parent_id)
        self.start_task(task_id)
        
        try:
            yield self.get_task(task_id)
            self.complete_task(task_id, success=True)
        except Exception as e:
            self.complete_task(task_id, success=False, 
                             message=f"Exception: {str(e)}")
            raise


# Global progress tracker instance
_global_tracker: Optional[ProgressTracker] = None


def get_global_tracker() -> ProgressTracker:
    """Get or create the global progress tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ProgressTracker()
    return _global_tracker


def set_global_tracker(tracker: ProgressTracker) -> None:
    """Set the global progress tracker."""
    global _global_tracker
    _global_tracker = tracker


# Convenience functions for common usage patterns
def create_progress_task(task_id: str, 
                        description: str, 
                        total: int = 100,
                        parent_id: Optional[str] = None) -> ProgressInfo:
    """Create a progress task using the global tracker."""
    return get_global_tracker().create_task(task_id, description, total, parent_id)


def start_progress_task(task_id: str) -> None:
    """Start a progress task using the global tracker."""
    get_global_tracker().start_task(task_id)


def update_progress(task_id: str, current: int, message: Optional[str] = None) -> None:
    """Update progress using the global tracker."""
    get_global_tracker().update_progress(task_id, current, message)


def complete_progress_task(task_id: str, success: bool = True, message: Optional[str] = None) -> None:
    """Complete a progress task using the global tracker."""
    get_global_tracker().complete_task(task_id, success, message)


@contextmanager
def track_progress(task_id: str, 
                  description: str, 
                  total: int = 100,
                  parent_id: Optional[str] = None):
    """Context manager for progress tracking using the global tracker."""
    with get_global_tracker().track_task(task_id, description, total, parent_id) as task:
        yield task
