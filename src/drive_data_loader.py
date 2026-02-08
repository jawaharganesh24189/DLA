"""
Google Drive Data Loader for Colab Environment
Handles mounting, scanning, and batch loading of dialogue files from Google Drive
"""

import os
import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    """Metadata for a dialogue file"""
    path: str
    size_bytes: int
    modified_time: float
    file_type: str
    

class DriveDataLoader:
    """
    Handles Google Drive integration for Colab environments
    
    Features:
    - Auto-mount with retry logic
    - Recursive folder scanning
    - Batch file processing
    - Rate limit handling
    - Metadata caching
    """
    
    def __init__(self, mount_path: str = "/content/drive", force_remount: bool = False):
        """
        Initialize Drive Data Loader
        
        Args:
            mount_path: Base path for Google Drive mount
            force_remount: If True, force remount even if already mounted
        """
        self.mount_path = mount_path
        self.force_remount = force_remount
        self.is_mounted = False
        self._file_cache: Dict[str, List[FileMetadata]] = {}
        
    def mount_drive(self, max_retries: int = 3, timeout: int = 300) -> bool:
        """
        Mount Google Drive with retry logic
        
        Args:
            max_retries: Maximum number of mount attempts
            timeout: Timeout in seconds for each attempt
            
        Returns:
            True if successful, False otherwise
        """
        # Check if already mounted
        if not self.force_remount and os.path.exists(self.mount_path) and os.path.ismount(self.mount_path):
            logger.info(f"Google Drive already mounted at {self.mount_path}")
            self.is_mounted = True
            return True
        
        # Try to import google.colab
        try:
            from google.colab import drive
        except ImportError:
            logger.warning("google.colab not available. Assuming local/non-Colab environment.")
            # In non-Colab environments, check if the path exists
            if os.path.exists(self.mount_path):
                logger.info(f"Using existing path {self.mount_path}")
                self.is_mounted = True
                return True
            else:
                logger.error(f"Path {self.mount_path} does not exist and not in Colab environment")
                return False
        
        # Mount with retries
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Mounting Google Drive (attempt {attempt}/{max_retries})...")
                drive.mount(self.mount_path, force_remount=self.force_remount)
                
                # Verify mount
                if os.path.exists(self.mount_path) and os.path.ismount(self.mount_path):
                    logger.info("Google Drive mounted successfully!")
                    self.is_mounted = True
                    return True
                else:
                    logger.warning(f"Mount path exists but is not a mount point")
                    
            except Exception as e:
                logger.error(f"Mount attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        logger.error("Failed to mount Google Drive after all attempts")
        return False
    
    def scan_folder(
        self, 
        drive_path: str, 
        recursive: bool = False,
        file_extensions: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> List[str]:
        """
        Scan a Drive folder for dialogue files
        
        Args:
            drive_path: Path to folder in Google Drive
            recursive: If True, scan subdirectories
            file_extensions: List of extensions to include (e.g., ['.txt', '.json'])
            use_cache: If True, use cached results if available
            
        Returns:
            List of file paths
        """
        if not self.is_mounted:
            logger.warning("Drive not mounted. Call mount_drive() first.")
            if not self.mount_drive():
                return []
        
        # Check cache
        cache_key = f"{drive_path}:{recursive}:{file_extensions}"
        if use_cache and cache_key in self._file_cache:
            logger.info(f"Using cached file list for {drive_path}")
            return [fm.path for fm in self._file_cache[cache_key]]
        
        # Default extensions
        if file_extensions is None:
            file_extensions = ['.txt', '.json', '.jsonl', '.csv']
        
        # Validate path
        if not os.path.exists(drive_path):
            logger.error(f"Path does not exist: {drive_path}")
            return []
        
        logger.info(f"Scanning folder: {drive_path} (recursive={recursive})")
        
        files = []
        file_metadata_list = []
        
        try:
            if recursive:
                # Recursive scan
                for root, dirs, filenames in os.walk(drive_path):
                    for filename in filenames:
                        filepath = os.path.join(root, filename)
                        if any(filename.lower().endswith(ext) for ext in file_extensions):
                            files.append(filepath)
                            file_metadata_list.append(self._get_file_metadata(filepath))
            else:
                # Non-recursive scan
                for item in os.listdir(drive_path):
                    filepath = os.path.join(drive_path, item)
                    if os.path.isfile(filepath):
                        if any(item.lower().endswith(ext) for ext in file_extensions):
                            files.append(filepath)
                            file_metadata_list.append(self._get_file_metadata(filepath))
            
            # Cache results
            self._file_cache[cache_key] = file_metadata_list
            
            logger.info(f"Found {len(files)} files")
            return sorted(files)
            
        except Exception as e:
            logger.error(f"Error scanning folder: {e}")
            return []
    
    def _get_file_metadata(self, filepath: str) -> FileMetadata:
        """Get metadata for a file"""
        stat = os.stat(filepath)
        ext = os.path.splitext(filepath)[1].lower()
        
        return FileMetadata(
            path=filepath,
            size_bytes=stat.st_size,
            modified_time=stat.st_mtime,
            file_type=ext
        )
    
    def load_files_batch(
        self, 
        file_list: List[str], 
        batch_size: int = 100,
        start_index: int = 0
    ) -> List[Tuple[str, str]]:
        """
        Load files in batches with content
        
        Args:
            file_list: List of file paths
            batch_size: Number of files per batch
            start_index: Index to start from (for resuming)
            
        Returns:
            List of (filepath, content) tuples
        """
        batch_files = []
        end_index = min(start_index + batch_size, len(file_list))
        
        logger.info(f"Loading batch: files {start_index} to {end_index}")
        
        for filepath in file_list[start_index:end_index]:
            try:
                content = self._read_file_safe(filepath)
                if content:
                    batch_files.append((filepath, content))
            except Exception as e:
                logger.warning(f"Could not read {filepath}: {e}")
                continue
        
        return batch_files
    
    def _read_file_safe(self, filepath: str) -> Optional[str]:
        """
        Safely read file with multiple encoding attempts
        
        Args:
            filepath: Path to file
            
        Returns:
            File content or None if failed
        """
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                logger.error(f"Error reading {filepath}: {e}")
                return None
        
        logger.warning(f"Could not decode {filepath} with any encoding")
        return None
    
    def get_folder_stats(self, drive_path: str) -> Dict:
        """
        Get quick statistics about a folder without loading all files
        
        Args:
            drive_path: Path to folder
            
        Returns:
            Dictionary with statistics
        """
        if not os.path.exists(drive_path):
            logger.error(f"Path does not exist: {drive_path}")
            return {}
        
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'file_types': {},
            'largest_file': None,
            'largest_file_size_mb': 0
        }
        
        try:
            for root, dirs, files in os.walk(drive_path):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        size = os.path.getsize(filepath)
                        stats['total_files'] += 1
                        stats['total_size_mb'] += size / (1024 * 1024)
                        
                        # Track file types
                        ext = os.path.splitext(filename)[1].lower()
                        stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                        
                        # Track largest file
                        size_mb = size / (1024 * 1024)
                        if size_mb > stats['largest_file_size_mb']:
                            stats['largest_file_size_mb'] = size_mb
                            stats['largest_file'] = filepath
                            
                    except Exception as e:
                        logger.debug(f"Could not stat {filepath}: {e}")
                        continue
            
            logger.info(f"Folder stats: {stats['total_files']} files, "
                       f"{stats['total_size_mb']:.2f} MB total")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating folder stats: {e}")
            return stats
    
    def save_file_list(self, files: List[str], output_path: str) -> None:
        """
        Save file list to JSON for later use
        
        Args:
            files: List of file paths
            output_path: Path to save JSON file
        """
        try:
            with open(output_path, 'w') as f:
                json.dump({'files': files, 'count': len(files)}, f, indent=2)
            logger.info(f"Saved {len(files)} file paths to {output_path}")
        except Exception as e:
            logger.error(f"Error saving file list: {e}")
    
    def load_file_list(self, input_path: str) -> List[str]:
        """
        Load file list from JSON
        
        Args:
            input_path: Path to JSON file
            
        Returns:
            List of file paths
        """
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded {data.get('count', 0)} file paths from {input_path}")
            return data.get('files', [])
        except Exception as e:
            logger.error(f"Error loading file list: {e}")
            return []


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize loader
    loader = DriveDataLoader()
    
    # Mount drive
    if loader.mount_drive():
        # Scan folder
        files = loader.scan_folder(
            '/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/Dataset',
            recursive=True
        )
        
        print(f"Found {len(files)} dialogue files")
        
        # Get stats
        stats = loader.get_folder_stats('/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/Dataset')
        print(f"Stats: {stats}")
