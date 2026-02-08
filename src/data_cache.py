"""
Data caching and checkpointing system for dialogue processing
Implements efficient caching to avoid reprocessing and supports resume functionality
"""

import os
import pickle
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class CacheMetadata:
    """Metadata for cached data"""
    cache_key: str
    created_time: float
    file_count: int
    data_hash: str
    version: str = "1.0"
    

class DataCache:
    """
    Caching system for processed dialogue data
    
    Features:
    - Pickle and JSON serialization
    - Cache validation with hashing
    - Checkpoint management for long-running processes
    - Automatic cache expiration
    """
    
    def __init__(self, cache_dir: str = "./cache", expiry_hours: int = 168):
        """
        Initialize data cache
        
        Args:
            cache_dir: Directory to store cache files
            expiry_hours: Cache expiration time in hours (default: 1 week)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.expiry_seconds = expiry_hours * 3600
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load cache metadata from disk"""
        self.metadata: Dict[str, CacheMetadata] = {}
        
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    for key, meta_dict in data.items():
                        self.metadata[key] = CacheMetadata(**meta_dict)
                logger.info(f"Loaded metadata for {len(self.metadata)} cached items")
            except Exception as e:
                logger.warning(f"Could not load cache metadata: {e}")
    
    def _save_metadata(self) -> None:
        """Save cache metadata to disk"""
        try:
            data = {key: asdict(meta) for key, meta in self.metadata.items()}
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save cache metadata: {e}")
    
    def _generate_cache_key(self, identifier: str) -> str:
        """Generate a cache key from an identifier"""
        return hashlib.md5(identifier.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str, format: str = 'pickle') -> Path:
        """Get the file path for a cache key"""
        ext = 'pkl' if format == 'pickle' else 'json'
        return self.cache_dir / f"{cache_key}.{ext}"
    
    def _compute_data_hash(self, data: Any) -> str:
        """Compute hash of data for validation"""
        try:
            data_str = str(data)
            return hashlib.md5(data_str.encode()).hexdigest()[:16]
        except:
            return "unknown"
    
    def save_processed_data(
        self, 
        data: Any, 
        cache_key: str,
        metadata: Optional[Dict] = None,
        format: str = 'pickle'
    ) -> bool:
        """
        Save processed data to cache
        
        Args:
            data: Data to cache
            cache_key: Unique identifier for this cache entry
            metadata: Optional metadata dictionary
            format: 'pickle' or 'json'
            
        Returns:
            True if successful
        """
        try:
            hashed_key = self._generate_cache_key(cache_key)
            cache_path = self._get_cache_path(hashed_key, format)
            
            # Save data
            if format == 'pickle':
                with open(cache_path, 'wb') as f:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            else:  # json
                with open(cache_path, 'w') as f:
                    json.dump(data, f, indent=2)
            
            # Update metadata
            file_count = len(data) if isinstance(data, (list, dict)) else 1
            self.metadata[hashed_key] = CacheMetadata(
                cache_key=cache_key,
                created_time=time.time(),
                file_count=file_count,
                data_hash=self._compute_data_hash(data)
            )
            self._save_metadata()
            
            logger.info(f"Cached data for key '{cache_key}' ({cache_path.stat().st_size / 1024:.2f} KB)")
            return True
            
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            return False
    
    def load_cached_data(
        self, 
        cache_key: str,
        validate: bool = True,
        format: str = 'pickle'
    ) -> Optional[Any]:
        """
        Load data from cache
        
        Args:
            cache_key: Unique identifier for cache entry
            validate: If True, check cache expiration
            format: 'pickle' or 'json'
            
        Returns:
            Cached data or None if not found/expired
        """
        try:
            hashed_key = self._generate_cache_key(cache_key)
            cache_path = self._get_cache_path(hashed_key, format)
            
            # Check if cache exists
            if not cache_path.exists():
                logger.debug(f"Cache miss for key '{cache_key}'")
                return None
            
            # Check metadata
            if hashed_key not in self.metadata:
                logger.warning(f"Cache file exists but no metadata for key '{cache_key}'")
                return None
            
            meta = self.metadata[hashed_key]
            
            # Validate expiration
            if validate:
                age_seconds = time.time() - meta.created_time
                if age_seconds > self.expiry_seconds:
                    logger.info(f"Cache expired for key '{cache_key}' (age: {age_seconds/3600:.1f} hours)")
                    return None
            
            # Load data
            if format == 'pickle':
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
            else:  # json
                with open(cache_path, 'r') as f:
                    data = json.load(f)
            
            logger.info(f"Cache hit for key '{cache_key}' ({cache_path.stat().st_size / 1024:.2f} KB)")
            return data
            
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return None
    
    def create_checkpoint(
        self, 
        state: Dict,
        checkpoint_id: str
    ) -> bool:
        """
        Create a checkpoint for resumable processing
        
        Args:
            state: Dictionary containing processing state
            checkpoint_id: Unique identifier for checkpoint
            
        Returns:
            True if successful
        """
        try:
            checkpoint_path = self.cache_dir / f"checkpoint_{checkpoint_id}.pkl"
            
            checkpoint_data = {
                'state': state,
                'timestamp': time.time(),
                'checkpoint_id': checkpoint_id
            }
            
            with open(checkpoint_path, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            
            logger.info(f"Created checkpoint: {checkpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating checkpoint: {e}")
            return False
    
    def restore_from_checkpoint(
        self, 
        checkpoint_id: str
    ) -> Optional[Dict]:
        """
        Restore processing state from checkpoint
        
        Args:
            checkpoint_id: Unique identifier for checkpoint
            
        Returns:
            State dictionary or None if not found
        """
        try:
            checkpoint_path = self.cache_dir / f"checkpoint_{checkpoint_id}.pkl"
            
            if not checkpoint_path.exists():
                logger.warning(f"Checkpoint not found: {checkpoint_id}")
                return None
            
            with open(checkpoint_path, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            age = time.time() - checkpoint_data['timestamp']
            logger.info(f"Restored checkpoint: {checkpoint_id} (age: {age/60:.1f} minutes)")
            
            return checkpoint_data['state']
            
        except Exception as e:
            logger.error(f"Error restoring checkpoint: {e}")
            return None
    
    def list_checkpoints(self) -> List[str]:
        """List all available checkpoints"""
        checkpoints = []
        for path in self.cache_dir.glob("checkpoint_*.pkl"):
            checkpoint_id = path.stem.replace("checkpoint_", "")
            checkpoints.append(checkpoint_id)
        return sorted(checkpoints)
    
    def clear_cache(self, keep_checkpoints: bool = True) -> int:
        """
        Clear all cached data
        
        Args:
            keep_checkpoints: If True, preserve checkpoints
            
        Returns:
            Number of files removed
        """
        removed = 0
        try:
            for path in self.cache_dir.glob("*"):
                if path.is_file():
                    # Skip checkpoints if requested
                    if keep_checkpoints and path.stem.startswith("checkpoint_"):
                        continue
                    
                    # Skip metadata file
                    if path == self.metadata_file:
                        continue
                    
                    path.unlink()
                    removed += 1
            
            # Clear metadata
            self.metadata.clear()
            self._save_metadata()
            
            logger.info(f"Cleared cache: removed {removed} files")
            return removed
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return removed
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the cache"""
        stats = {
            'total_entries': len(self.metadata),
            'total_size_mb': 0,
            'oldest_entry': None,
            'newest_entry': None,
            'expired_entries': 0
        }
        
        try:
            current_time = time.time()
            oldest_time = float('inf')
            newest_time = 0
            
            for hashed_key, meta in self.metadata.items():
                # Calculate size
                for ext in ['pkl', 'json']:
                    cache_path = self.cache_dir / f"{hashed_key}.{ext}"
                    if cache_path.exists():
                        stats['total_size_mb'] += cache_path.stat().st_size / (1024 * 1024)
                
                # Track oldest/newest
                if meta.created_time < oldest_time:
                    oldest_time = meta.created_time
                    stats['oldest_entry'] = meta.cache_key
                
                if meta.created_time > newest_time:
                    newest_time = meta.created_time
                    stats['newest_entry'] = meta.cache_key
                
                # Count expired
                if (current_time - meta.created_time) > self.expiry_seconds:
                    stats['expired_entries'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating cache stats: {e}")
            return stats
    
    def validate_cache_integrity(self) -> Tuple[int, int]:
        """
        Validate cache integrity
        
        Returns:
            Tuple of (valid_entries, invalid_entries)
        """
        valid = 0
        invalid = 0
        
        for hashed_key, meta in self.metadata.items():
            found = False
            for ext in ['pkl', 'json']:
                cache_path = self.cache_dir / f"{hashed_key}.{ext}"
                if cache_path.exists():
                    found = True
                    valid += 1
                    break
            
            if not found:
                logger.warning(f"Cache file missing for key: {meta.cache_key}")
                invalid += 1
        
        logger.info(f"Cache integrity: {valid} valid, {invalid} invalid entries")
        return valid, invalid


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize cache
    cache = DataCache(cache_dir="./cache")
    
    # Save some data
    sample_data = {"dialogues": ["Hello", "Hi there", "How are you?"]}
    cache.save_processed_data(sample_data, "test_data_v1")
    
    # Load data
    loaded = cache.load_cached_data("test_data_v1")
    print(f"Loaded: {loaded}")
    
    # Create checkpoint
    state = {"files_processed": 100, "current_file": "file_100.txt"}
    cache.create_checkpoint(state, "processing_run_1")
    
    # Restore checkpoint
    restored_state = cache.restore_from_checkpoint("processing_run_1")
    print(f"Restored state: {restored_state}")
    
    # Get stats
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats}")
