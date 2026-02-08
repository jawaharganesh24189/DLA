"""
Enhanced data processor for multi-file dialogue processing
Extends the base DialogueParser with advanced features for large-scale processing
"""

import os
import json
import csv
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml

# Import existing components
from .data_processor import DialogueParser, DialogueTurn, DatasetStatistics
from .drive_data_loader import DriveDataLoader
from .data_cache import DataCache
from .processing_monitor import ProcessingMonitor

logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """Configuration for dialogue processing"""
    # Quality filters
    min_dialogue_length: int = 5
    max_dialogue_length: int = 150
    min_char_occurrence: int = 3
    min_word_count: int = 2
    max_word_count: int = 100
    remove_duplicates: bool = True
    
    # Tokenizer
    max_vocab_size: int = 5000
    min_word_freq: int = 2
    oov_token: str = "<UNK>"
    pad_token: str = "<PAD>"
    start_token: str = "<START>"
    end_token: str = "<END>"
    
    # Augmentation
    augmentation_enabled: bool = False
    augment_ratio: float = 0.3
    synonym_replace_prob: float = 0.3
    
    # Processing
    batch_size: int = 100
    parallel_workers: int = 4
    show_progress: bool = True


class EnhancedDialogueProcessor:
    """
    Advanced dialogue processor with multi-file support and quality controls
    
    Features:
    - Multi-format support (txt, json, jsonl, csv)
    - Quality filtering and validation
    - Duplicate detection
    - Data augmentation
    - Parallel processing
    - Progress tracking
    - Caching
    """
    
    def __init__(
        self,
        tokenizer_config: Optional[Dict] = None,
        quality_filters: Optional[Dict] = None,
        augmentation: Optional[Dict] = None,
        cache_dir: str = "./cache",
        log_dir: str = "./logs"
    ):
        """
        Initialize enhanced processor
        
        Args:
            tokenizer_config: Tokenizer configuration dictionary
            quality_filters: Quality filter configuration dictionary
            augmentation: Augmentation configuration dictionary
            cache_dir: Directory for caching
            log_dir: Directory for logs
        """
        # Create config from provided parameters
        self.config = ProcessingConfig()
        
        if tokenizer_config:
            for key, value in tokenizer_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        
        if quality_filters:
            for key, value in quality_filters.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        
        if augmentation:
            enabled = augmentation.get('enabled', False)
            self.config.augmentation_enabled = enabled
            if 'augment_ratio' in augmentation:
                self.config.augment_ratio = augmentation['augment_ratio']
        
        # Initialize components
        self.parser = DialogueParser()
        self.cache = DataCache(cache_dir=cache_dir)
        self.monitor = ProcessingMonitor(log_dir=log_dir, enable_tqdm=self.config.show_progress)
        
        # Storage
        self.vocabulary: Set[str] = set()
        self.word_frequencies: Dict[str, int] = {}
        self.seen_dialogues: Set[str] = set()
        
        logger.info("EnhancedDialogueProcessor initialized")
    
    @classmethod
    def from_config_file(cls, config_path: str) -> 'EnhancedDialogueProcessor':
        """
        Create processor from YAML config file
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            EnhancedDialogueProcessor instance
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return cls(
            tokenizer_config=config.get('tokenizer', {}),
            quality_filters=config.get('quality', {}),
            augmentation=config.get('augmentation', {}),
            cache_dir=config.get('cache', {}).get('cache_dir', './cache'),
            log_dir=config.get('monitoring', {}).get('log_dir', './logs')
        )
    
    def process_drive_files(
        self,
        file_list: List[str],
        batch_size: Optional[int] = None,
        show_progress: bool = True,
        use_cache: bool = True,
        checkpoint_interval: int = 500
    ) -> List[DialogueTurn]:
        """
        Process multiple files from Google Drive
        
        Args:
            file_list: List of file paths to process
            batch_size: Batch size for processing
            show_progress: Show progress bars
            use_cache: Use cached results if available
            checkpoint_interval: Create checkpoint every N files
            
        Returns:
            List of DialogueTurn objects
        """
        if batch_size is None:
            batch_size = self.config.batch_size
        
        # Check cache
        cache_key = f"processed_files_{hashlib.md5(str(sorted(file_list)).encode()).hexdigest()}"
        
        if use_cache:
            cached_data = self.cache.load_cached_data(cache_key)
            if cached_data is not None:
                logger.info(f"Loaded {len(cached_data)} dialogues from cache")
                return cached_data
        
        # Start monitoring
        self.monitor.start_processing(total_files=len(file_list))
        
        all_turns = []
        
        # Process files
        for i, filepath in enumerate(file_list):
            try:
                # Process single file
                turns = self._process_single_file(filepath)
                
                # Apply quality filters
                filtered_turns = self._apply_quality_filters(turns)
                all_turns.extend(filtered_turns)
                
                # Update monitor
                self.monitor.update_progress(
                    current_file=filepath,
                    dialogues_extracted=len(filtered_turns),
                    success=True
                )
                
                # Create checkpoint periodically
                if (i + 1) % checkpoint_interval == 0:
                    checkpoint_state = {
                        'files_processed': i + 1,
                        'dialogues_collected': len(all_turns),
                        'cache_key': cache_key
                    }
                    self.cache.create_checkpoint(checkpoint_state, f"processing_{i+1}")
                
            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")
                self.monitor.update_progress(
                    current_file=filepath,
                    success=False,
                    error=e
                )
                continue
        
        # Remove duplicates if configured
        if self.config.remove_duplicates:
            original_count = len(all_turns)
            all_turns = self._remove_duplicates(all_turns)
            removed = original_count - len(all_turns)
            self.monitor.update_quality_metrics(duplicates_removed=removed)
        
        # Finish monitoring
        self.monitor.finish_processing()
        self.monitor.print_summary()
        self.monitor.save_stats_report()
        self.monitor.save_error_log()
        
        # Cache results
        if use_cache:
            self.cache.save_processed_data(all_turns, cache_key)
        
        return all_turns
    
    def _process_single_file(self, filepath: str) -> List[DialogueTurn]:
        """
        Process a single file with format detection
        
        Args:
            filepath: Path to file
            
        Returns:
            List of DialogueTurn objects
        """
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.json':
            return self._parse_json_file(filepath)
        elif ext == '.jsonl':
            return self._parse_jsonl_file(filepath)
        elif ext == '.csv':
            return self._parse_csv_file(filepath)
        else:  # .txt or other
            return self.parser.parse_file(filepath)
    
    def _parse_json_file(self, filepath: str) -> List[DialogueTurn]:
        """Parse JSON file with dialogue structure"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            turns = []
            
            # Handle different JSON structures
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        context = item.get('context', item.get('prompt', ''))
                        response = item.get('response', item.get('completion', ''))
                        if context and response:
                            turns.append(DialogueTurn(
                                context=str(context),
                                response=str(response),
                                metadata={'format': 'json', 'source': filepath}
                            ))
            elif isinstance(data, dict):
                # Single dialogue or nested structure
                if 'dialogues' in data:
                    return self._parse_json_file_from_list(data['dialogues'])
                elif 'context' in data and 'response' in data:
                    turns.append(DialogueTurn(
                        context=str(data['context']),
                        response=str(data['response']),
                        metadata={'format': 'json', 'source': filepath}
                    ))
            
            return turns
            
        except Exception as e:
            logger.error(f"Error parsing JSON file {filepath}: {e}")
            return []
    
    def _parse_json_file_from_list(self, data_list: List) -> List[DialogueTurn]:
        """Parse dialogues from a list structure"""
        turns = []
        for item in data_list:
            if isinstance(item, dict):
                context = item.get('context', item.get('prompt', ''))
                response = item.get('response', item.get('completion', ''))
                if context and response:
                    turns.append(DialogueTurn(
                        context=str(context),
                        response=str(response),
                        metadata={'format': 'json'}
                    ))
        return turns
    
    def _parse_jsonl_file(self, filepath: str) -> List[DialogueTurn]:
        """Parse JSONL file (one JSON object per line)"""
        turns = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        obj = json.loads(line)
                        context = obj.get('context', obj.get('prompt', ''))
                        response = obj.get('response', obj.get('completion', ''))
                        
                        if context and response:
                            turns.append(DialogueTurn(
                                context=str(context),
                                response=str(response),
                                metadata={'format': 'jsonl', 'line': line_num}
                            ))
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON on line {line_num} of {filepath}")
                        continue
            
            return turns
            
        except Exception as e:
            logger.error(f"Error parsing JSONL file {filepath}: {e}")
            return []
    
    def _parse_csv_file(self, filepath: str) -> List[DialogueTurn]:
        """Parse CSV file with context and response columns"""
        turns = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                sniffer = csv.Sniffer()
                try:
                    delimiter = sniffer.sniff(sample).delimiter
                except:
                    delimiter = ','
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    # Try common column names
                    context = (row.get('context') or row.get('prompt') or 
                              row.get('Context') or row.get('Prompt') or '')
                    response = (row.get('response') or row.get('completion') or
                               row.get('Response') or row.get('Completion') or '')
                    
                    if context and response:
                        turns.append(DialogueTurn(
                            context=str(context),
                            response=str(response),
                            metadata={'format': 'csv', 'row': row_num}
                        ))
            
            return turns
            
        except Exception as e:
            logger.error(f"Error parsing CSV file {filepath}: {e}")
            return []
    
    def _apply_quality_filters(self, turns: List[DialogueTurn]) -> List[DialogueTurn]:
        """
        Apply quality filters to dialogue turns
        
        Args:
            turns: List of DialogueTurn objects
            
        Returns:
            Filtered list of DialogueTurn objects
        """
        filtered = []
        
        for turn in turns:
            # Length filters
            context_len = len(turn.context)
            response_len = len(turn.response)
            
            if context_len < self.config.min_dialogue_length:
                continue
            if response_len < self.config.min_dialogue_length:
                continue
            if context_len > self.config.max_dialogue_length:
                continue
            if response_len > self.config.max_dialogue_length:
                continue
            
            # Word count filters
            context_words = len(turn.context.split())
            response_words = len(turn.response.split())
            
            if context_words < self.config.min_word_count:
                continue
            if response_words < self.config.min_word_count:
                continue
            if context_words > self.config.max_word_count:
                continue
            if response_words > self.config.max_word_count:
                continue
            
            filtered.append(turn)
        
        return filtered
    
    def _remove_duplicates(self, turns: List[DialogueTurn]) -> List[DialogueTurn]:
        """
        Remove duplicate dialogues based on content hash
        
        Args:
            turns: List of DialogueTurn objects
            
        Returns:
            De-duplicated list
        """
        unique_turns = []
        seen = set()
        
        for turn in turns:
            # Create hash of context + response
            content_hash = hashlib.md5(
                f"{turn.context}|{turn.response}".encode()
            ).hexdigest()
            
            if content_hash not in seen:
                seen.add(content_hash)
                unique_turns.append(turn)
        
        logger.info(f"Removed {len(turns) - len(unique_turns)} duplicate dialogues")
        return unique_turns
    
    def build_vocabulary(self, turns: List[DialogueTurn]) -> Dict[str, int]:
        """
        Build vocabulary from dialogues
        
        Args:
            turns: List of DialogueTurn objects
            
        Returns:
            Word to index mapping
        """
        # Count word frequencies
        word_freq = {}
        
        for turn in turns:
            for text in [turn.context, turn.response]:
                words = text.lower().split()
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Filter by minimum frequency
        filtered_words = {
            word: freq for word, freq in word_freq.items()
            if freq >= self.config.min_word_freq
        }
        
        # Sort by frequency and take top N
        sorted_words = sorted(
            filtered_words.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.config.max_vocab_size - 4]  # Reserve space for special tokens
        
        # Build vocabulary
        vocab = {
            self.config.pad_token: 0,
            self.config.start_token: 1,
            self.config.end_token: 2,
            self.config.oov_token: 3
        }
        
        for idx, (word, _) in enumerate(sorted_words, start=4):
            vocab[word] = idx
        
        logger.info(f"Built vocabulary with {len(vocab)} tokens")
        self.vocabulary = set(vocab.keys())
        self.word_frequencies = dict(sorted_words)
        
        return vocab
    
    def augment_dialogues(
        self,
        turns: List[DialogueTurn],
        techniques: Optional[List[str]] = None
    ) -> List[DialogueTurn]:
        """
        Augment dialogues using various techniques
        
        Args:
            turns: List of DialogueTurn objects
            techniques: List of augmentation techniques to apply
            
        Returns:
            Augmented list including original dialogues
        """
        if not self.config.augmentation_enabled:
            return turns
        
        if techniques is None:
            techniques = ['context_shuffle']
        
        augmented = list(turns)  # Start with originals
        num_to_augment = int(len(turns) * self.config.augment_ratio)
        
        logger.info(f"Augmenting {num_to_augment} dialogues")
        
        # Randomly select dialogues to augment
        to_augment = random.sample(turns, min(num_to_augment, len(turns)))
        
        for turn in to_augment:
            if 'context_shuffle' in techniques:
                # Shuffle words in context (simple augmentation)
                words = turn.context.split()
                if len(words) > 3:
                    # Shuffle middle words, keep first and last
                    middle = words[1:-1]
                    random.shuffle(middle)
                    shuffled_context = ' '.join([words[0]] + middle + [words[-1]])
                    
                    augmented.append(DialogueTurn(
                        context=shuffled_context,
                        response=turn.response,
                        metadata={'augmented': True, 'technique': 'context_shuffle'}
                    ))
        
        logger.info(f"Created {len(augmented)} total dialogues (including augmented)")
        return augmented
    
    def get_processing_stats(self) -> Dict:
        """Get current processing statistics"""
        return self.monitor.get_current_stats()
    
    def export_to_format(
        self,
        turns: List[DialogueTurn],
        output_path: str,
        format_type: str = 'jsonl'
    ) -> bool:
        """
        Export processed dialogues to file
        
        Args:
            turns: List of DialogueTurn objects
            output_path: Path to save file
            format_type: Format type ('jsonl', 'csv', 'txt')
            
        Returns:
            True if successful
        """
        try:
            if format_type == 'jsonl':
                with open(output_path, 'w') as f:
                    for turn in turns:
                        obj = {
                            'context': turn.context,
                            'response': turn.response,
                            'metadata': turn.metadata
                        }
                        f.write(json.dumps(obj) + '\n')
            
            elif format_type == 'csv':
                with open(output_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['context', 'response'])
                    for turn in turns:
                        writer.writerow([turn.context, turn.response])
            
            elif format_type == 'txt':
                with open(output_path, 'w') as f:
                    for turn in turns:
                        f.write(f"Context: {turn.context}\n")
                        f.write(f"Response: {turn.response}\n")
                        f.write("\n")
            
            else:
                raise ValueError(f"Unknown format: {format_type}")
            
            logger.info(f"Exported {len(turns)} dialogues to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to {format_type}: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create processor from config
    processor = EnhancedDialogueProcessor.from_config_file("config/data_config.yaml")
    
    # Or create with custom config
    processor = EnhancedDialogueProcessor(
        tokenizer_config={'max_vocab_size': 5000, 'min_word_freq': 2},
        quality_filters={'min_dialogue_length': 5, 'max_dialogue_length': 100},
        augmentation={'enabled': True, 'augment_ratio': 0.3}
    )
    
    # Process files
    file_list = ['file1.txt', 'file2.json', 'file3.csv']
    dialogues = processor.process_drive_files(file_list)
    
    print(f"Processed {len(dialogues)} dialogues")
