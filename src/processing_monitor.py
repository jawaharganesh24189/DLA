"""
Processing monitor with real-time statistics and logging
Tracks processing metrics, memory usage, and errors
"""

import os
import time
import json
import csv
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
import logging
from datetime import datetime

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """Statistics for dialogue processing"""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_dialogues: int = 0
    total_duplicates_removed: int = 0
    total_filtered_out: int = 0
    current_file: Optional[str] = None
    memory_usage_mb: float = 0
    processing_rate_files_per_sec: float = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class FileError:
    """Record of a file processing error"""
    filepath: str
    error_type: str
    error_message: str
    timestamp: float = field(default_factory=time.time)


class ProcessingMonitor:
    """
    Comprehensive monitoring for dialogue processing
    
    Features:
    - Real-time progress bars
    - Memory usage tracking
    - Error logging
    - Statistics collection
    - Report generation
    """
    
    def __init__(
        self, 
        log_dir: str = "./logs",
        enable_tqdm: bool = True,
        update_interval: int = 10
    ):
        """
        Initialize processing monitor
        
        Args:
            log_dir: Directory for log files
            enable_tqdm: If True, show progress bars
            update_interval: Update interval for progress (files)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_tqdm = enable_tqdm and tqdm is not None
        self.update_interval = update_interval
        
        # Initialize stats
        self.stats = ProcessingStats()
        self.errors: List[FileError] = []
        
        # Progress bar
        self.pbar = None
        
        # Process for memory monitoring
        self.process = psutil.Process(os.getpid())
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup file logging"""
        log_file = self.log_dir / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add to root logger
        logging.getLogger().addHandler(file_handler)
        
        logger.info(f"Logging to: {log_file}")
    
    def start_processing(self, total_files: int) -> None:
        """
        Start monitoring a processing job
        
        Args:
            total_files: Total number of files to process
        """
        self.stats = ProcessingStats(total_files=total_files)
        self.errors = []
        
        logger.info(f"Starting processing: {total_files} files")
        
        if self.enable_tqdm:
            self.pbar = tqdm(
                total=total_files,
                desc="Processing files",
                unit="file",
                dynamic_ncols=True
            )
    
    def update_progress(
        self, 
        current_file: Optional[str] = None,
        dialogues_extracted: int = 0,
        success: bool = True,
        error: Optional[Exception] = None
    ) -> None:
        """
        Update processing progress
        
        Args:
            current_file: Current file being processed
            dialogues_extracted: Number of dialogues extracted from current file
            success: Whether processing was successful
            error: Exception if processing failed
        """
        if success:
            self.stats.processed_files += 1
            self.stats.total_dialogues += dialogues_extracted
        else:
            self.stats.failed_files += 1
            if error and current_file:
                self.errors.append(FileError(
                    filepath=current_file,
                    error_type=type(error).__name__,
                    error_message=str(error)
                ))
        
        self.stats.current_file = current_file
        
        # Update memory usage periodically
        if self.stats.processed_files % self.update_interval == 0:
            self.stats.memory_usage_mb = self.process.memory_info().rss / (1024 * 1024)
        
        # Update progress bar
        if self.pbar:
            self.pbar.update(1)
            self.pbar.set_postfix({
                'dialogues': self.stats.total_dialogues,
                'errors': self.stats.failed_files,
                'mem_mb': f"{self.stats.memory_usage_mb:.0f}"
            })
    
    def log_error(self, filepath: str, error: Exception) -> None:
        """
        Log a file processing error
        
        Args:
            filepath: Path to file that failed
            error: Exception that occurred
        """
        self.errors.append(FileError(
            filepath=filepath,
            error_type=type(error).__name__,
            error_message=str(error)
        ))
        logger.error(f"Error processing {filepath}: {error}")
    
    def update_quality_metrics(
        self, 
        duplicates_removed: int = 0,
        filtered_out: int = 0
    ) -> None:
        """
        Update data quality metrics
        
        Args:
            duplicates_removed: Number of duplicate dialogues removed
            filtered_out: Number of dialogues filtered by quality rules
        """
        self.stats.total_duplicates_removed += duplicates_removed
        self.stats.total_filtered_out += filtered_out
    
    def finish_processing(self) -> ProcessingStats:
        """
        Finish processing and finalize stats
        
        Returns:
            Final statistics
        """
        self.stats.end_time = time.time()
        
        # Calculate processing rate
        elapsed = self.stats.end_time - self.stats.start_time
        if elapsed > 0:
            self.stats.processing_rate_files_per_sec = self.stats.processed_files / elapsed
        
        # Close progress bar
        if self.pbar:
            self.pbar.close()
        
        # Log summary
        logger.info("="*60)
        logger.info("PROCESSING COMPLETE")
        logger.info("="*60)
        logger.info(f"Total files: {self.stats.total_files}")
        logger.info(f"Processed: {self.stats.processed_files}")
        logger.info(f"Failed: {self.stats.failed_files}")
        logger.info(f"Total dialogues: {self.stats.total_dialogues}")
        logger.info(f"Duplicates removed: {self.stats.total_duplicates_removed}")
        logger.info(f"Filtered out: {self.stats.total_filtered_out}")
        logger.info(f"Processing time: {elapsed:.2f}s")
        logger.info(f"Rate: {self.stats.processing_rate_files_per_sec:.2f} files/sec")
        logger.info(f"Peak memory: {self.stats.memory_usage_mb:.2f} MB")
        logger.info("="*60)
        
        return self.stats
    
    def get_current_stats(self) -> Dict:
        """Get current processing statistics"""
        # Update memory
        self.stats.memory_usage_mb = self.process.memory_info().rss / (1024 * 1024)
        
        # Calculate current rate
        elapsed = time.time() - self.stats.start_time
        if elapsed > 0:
            self.stats.processing_rate_files_per_sec = self.stats.processed_files / elapsed
        
        return self.stats.to_dict()
    
    def save_stats_report(self, output_path: Optional[str] = None) -> str:
        """
        Save statistics report to JSON
        
        Args:
            output_path: Path to save report (optional)
            
        Returns:
            Path where report was saved
        """
        if output_path is None:
            output_path = self.log_dir / f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'stats': self.stats.to_dict(),
            'errors': [asdict(err) for err in self.errors],
            'error_summary': self._get_error_summary()
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Saved statistics report to: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving stats report: {e}")
            return ""
    
    def save_error_log(self, output_path: Optional[str] = None) -> str:
        """
        Save error log to CSV
        
        Args:
            output_path: Path to save error log (optional)
            
        Returns:
            Path where log was saved
        """
        if output_path is None:
            output_path = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.errors:
            logger.info("No errors to log")
            return ""
        
        try:
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(
                    f, 
                    fieldnames=['filepath', 'error_type', 'error_message', 'timestamp']
                )
                writer.writeheader()
                for error in self.errors:
                    writer.writerow(asdict(error))
            
            logger.info(f"Saved error log to: {output_path} ({len(self.errors)} errors)")
            return str(output_path)
        except Exception as e:
            logger.error(f"Error saving error log: {e}")
            return ""
    
    def _get_error_summary(self) -> Dict[str, int]:
        """Get summary of errors by type"""
        summary = {}
        for error in self.errors:
            summary[error.error_type] = summary.get(error.error_type, 0) + 1
        return summary
    
    def print_summary(self) -> None:
        """Print a human-readable summary"""
        stats = self.get_current_stats()
        
        print("\n" + "="*60)
        print("PROCESSING SUMMARY")
        print("="*60)
        print(f"Files processed: {stats['processed_files']}/{stats['total_files']}")
        print(f"Success rate: {(stats['processed_files']/max(stats['total_files'],1)*100):.1f}%")
        print(f"Total dialogues: {stats['total_dialogues']}")
        print(f"Duplicates removed: {stats['total_duplicates_removed']}")
        print(f"Filtered out: {stats['total_filtered_out']}")
        print(f"Failed files: {stats['failed_files']}")
        
        elapsed = time.time() - stats['start_time']
        print(f"Processing time: {elapsed:.2f}s")
        print(f"Processing rate: {stats['processing_rate_files_per_sec']:.2f} files/sec")
        print(f"Memory usage: {stats['memory_usage_mb']:.2f} MB")
        
        if self.errors:
            print(f"\nError summary:")
            for error_type, count in self._get_error_summary().items():
                print(f"  {error_type}: {count}")
        
        print("="*60 + "\n")
    
    def get_eta_seconds(self) -> Optional[float]:
        """
        Calculate estimated time to completion
        
        Returns:
            Estimated seconds remaining, or None if cannot calculate
        """
        if self.stats.processed_files == 0:
            return None
        
        elapsed = time.time() - self.stats.start_time
        rate = self.stats.processed_files / elapsed
        
        remaining_files = self.stats.total_files - self.stats.processed_files
        if rate > 0:
            return remaining_files / rate
        return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize monitor
    monitor = ProcessingMonitor()
    
    # Simulate processing
    monitor.start_processing(total_files=100)
    
    for i in range(100):
        time.sleep(0.01)  # Simulate work
        
        # Simulate some failures
        if i % 10 == 0 and i > 0:
            monitor.update_progress(
                current_file=f"file_{i}.txt",
                success=False,
                error=Exception("Sample error")
            )
        else:
            monitor.update_progress(
                current_file=f"file_{i}.txt",
                dialogues_extracted=5,
                success=True
            )
    
    # Finish and get stats
    final_stats = monitor.finish_processing()
    monitor.print_summary()
    
    # Save reports
    monitor.save_stats_report()
    monitor.save_error_log()
