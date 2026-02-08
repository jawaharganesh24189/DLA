# Data Processing Guide

Complete guide for using the Enhanced Multi-File Google Drive Data Processing System with the GAN Dialogue Model.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Components](#components)
4. [Configuration](#configuration)
5. [Processing Pipeline](#processing-pipeline)
6. [File Formats](#file-formats)
7. [Quality Filters](#quality-filters)
8. [Data Augmentation](#data-augmentation)
9. [Caching](#caching)
10. [Monitoring](#monitoring)
11. [Troubleshooting](#troubleshooting)

## Overview

The enhanced data processing system provides a complete pipeline for loading, processing, and preparing dialogue datasets from Google Drive for the GAN dialogue generation model.

### Key Features

- **Multi-format support**: TXT, JSON, JSONL, CSV
- **Quality filtering**: Length, word count, character frequency filters
- **Duplicate detection**: Automatic removal of duplicate dialogues
- **Data augmentation**: Synonym replacement, context shuffling
- **Caching**: Avoid reprocessing with intelligent caching
- **Progress tracking**: Real-time progress bars and statistics
- **Error handling**: Graceful error handling with detailed logging

## Quick Start

### In Google Colab

```python
# Install dependencies (if needed)
!pip install -r requirements.txt

# Import components
from src.drive_data_loader import DriveDataLoader
from src.enhanced_data_processor import EnhancedDialogueProcessor

# Mount Drive and scan files
loader = DriveDataLoader()
loader.mount_drive()
files = loader.scan_folder('/content/drive/MyDrive/YourFolder', recursive=True)

# Process files
processor = EnhancedDialogueProcessor.from_config_file('config/data_config.yaml')
dialogues = processor.process_drive_files(files)

print(f"Processed {len(dialogues)} dialogues")
```

### Standalone Script

```bash
python examples/process_drive_folder.py
```

## Components

### 1. DriveDataLoader (`src/drive_data_loader.py`)

Handles Google Drive integration:

```python
loader = DriveDataLoader(mount_path="/content/drive")

# Mount drive with retry logic
loader.mount_drive(max_retries=3, timeout=300)

# Scan folder
files = loader.scan_folder(
    drive_path='/content/drive/MyDrive/Dataset',
    recursive=True,
    file_extensions=['.txt', '.json']
)

# Get folder statistics
stats = loader.get_folder_stats(drive_path)
print(f"Total files: {stats['total_files']}")
```

### 2. EnhancedDialogueProcessor (`src/enhanced_data_processor.py`)

Main processing engine:

```python
processor = EnhancedDialogueProcessor(
    tokenizer_config={
        'max_vocab_size': 5000,
        'min_word_freq': 2
    },
    quality_filters={
        'min_dialogue_length': 5,
        'max_dialogue_length': 150
    }
)

# Process files
dialogues = processor.process_drive_files(files)

# Build vocabulary
vocab = processor.build_vocabulary(dialogues)

# Export results
processor.export_to_format(dialogues, 'output.jsonl', 'jsonl')
```

### 3. DataCache (`src/data_cache.py`)

Caching and checkpointing:

```python
cache = DataCache(cache_dir="./cache", expiry_hours=168)

# Save processed data
cache.save_processed_data(dialogues, cache_key="my_dataset")

# Load cached data
cached_dialogues = cache.load_cached_data("my_dataset")

# Create checkpoint
state = {'files_processed': 500}
cache.create_checkpoint(state, "checkpoint_500")

# Restore checkpoint
state = cache.restore_from_checkpoint("checkpoint_500")
```

### 4. ProcessingMonitor (`src/processing_monitor.py`)

Track processing metrics:

```python
monitor = ProcessingMonitor(log_dir="./logs")

monitor.start_processing(total_files=1000)

for file in files:
    # Process file...
    monitor.update_progress(
        current_file=file,
        dialogues_extracted=10,
        success=True
    )

stats = monitor.finish_processing()
monitor.print_summary()
```

## Configuration

Configuration is managed via YAML files. See `config/data_config.yaml` for the main config and `examples/sample_config.yaml` for a template.

### Key Configuration Sections

**Drive Settings:**
```yaml
drive:
  base_path: "/content/drive/MyDrive/YourFolder"
  data_folder: "Dataset"
  cache_folder: "cache"
```

**Processing Settings:**
```yaml
processing:
  batch_size: 100
  parallel_workers: 4
  show_progress: true
```

**Quality Filters:**
```yaml
quality:
  min_dialogue_length: 5
  max_dialogue_length: 150
  remove_duplicates: true
```

## Processing Pipeline

The typical processing pipeline:

```python
# 1. Initialize components
loader = DriveDataLoader()
processor = EnhancedDialogueProcessor.from_config_file('config/data_config.yaml')

# 2. Mount and scan
loader.mount_drive()
files = loader.scan_folder(DRIVE_PATH, recursive=True)

# 3. Process files
dialogues = processor.process_drive_files(
    file_list=files,
    batch_size=100,
    use_cache=True
)

# 4. Build vocabulary
vocab = processor.build_vocabulary(dialogues)

# 5. Augment (optional)
dialogues = processor.augment_dialogues(dialogues)

# 6. Export
processor.export_to_format(dialogues, 'output.jsonl', 'jsonl')
```

## File Formats

### TXT Files

Supports two formats:

**Context-Response Format:**
```
context: What is your name?
response: I'm an AI assistant.

context: How are you?
response: I'm doing well, thank you!
```

**Speaker Format:**
```
Alice: Hello, how are you?
Bob: I'm fine, thanks for asking.
Alice: That's great to hear.
```

### JSON Files

```json
[
  {
    "context": "What is your name?",
    "response": "I'm an AI assistant."
  },
  {
    "context": "How are you?",
    "response": "I'm doing well!"
  }
]
```

Or nested:
```json
{
  "dialogues": [
    {"context": "...", "response": "..."}
  ]
}
```

### JSONL Files

One JSON object per line:
```jsonl
{"context": "What is your name?", "response": "I'm an AI assistant."}
{"context": "How are you?", "response": "I'm doing well!"}
```

### CSV Files

```csv
context,response
"What is your name?","I'm an AI assistant."
"How are you?","I'm doing well!"
```

## Quality Filters

Quality filters ensure high-quality training data:

- **Length filters**: Min/max character length
- **Word count filters**: Min/max word count
- **Duplicate removal**: Hash-based deduplication
- **Character frequency**: Minimum occurrence threshold

Configure in `config/data_config.yaml`:
```yaml
quality:
  min_dialogue_length: 5
  max_dialogue_length: 150
  min_word_count: 2
  max_word_count: 100
  remove_duplicates: true
```

## Data Augmentation

Increase dataset size and diversity:

### Supported Techniques

1. **Context Shuffle**: Shuffle words in context while preserving meaning
2. **Synonym Replace**: Replace words with synonyms (requires NLTK)

### Configuration

```yaml
augmentation:
  enabled: true
  techniques: ["context_shuffle"]
  augment_ratio: 0.3  # 30% more data
```

### Usage

```python
# Automatic during processing
dialogues = processor.process_drive_files(files)

# Or manual
augmented = processor.augment_dialogues(dialogues)
```

## Caching

Caching avoids reprocessing and speeds up development:

### Cache Structure

- Processed data cached by file list hash
- Metadata tracks creation time, file count
- Automatic expiration after configured time
- Checkpoints for resumable processing

### Usage

```python
# Automatic with processor
dialogues = processor.process_drive_files(files, use_cache=True)

# Manual cache management
cache = DataCache()
cache.save_processed_data(data, "my_key")
data = cache.load_cached_data("my_key")

# Clear cache
cache.clear_cache(keep_checkpoints=True)
```

## Monitoring

### Real-time Progress

Progress bars show:
- Files processed
- Dialogues extracted
- Error count
- Memory usage

### Statistics

After processing:
- Total files/dialogues
- Success/failure rates
- Processing time and rate
- Memory usage
- Error summary

### Logs

Logs are saved to `./logs/`:
- `processing_TIMESTAMP.log`: Detailed processing log
- `stats_TIMESTAMP.json`: Statistics report
- `errors_TIMESTAMP.csv`: Failed files with error messages

## Troubleshooting

### Drive Mount Issues

**Problem**: Drive won't mount
**Solution**: 
- Check internet connection
- Restart Colab runtime
- Use `force_remount=True`

### Memory Issues

**Problem**: Out of memory errors
**Solution**:
- Reduce `batch_size` in config
- Process fewer files at once
- Disable augmentation temporarily
- Clear cache

### Encoding Errors

**Problem**: Cannot read some files
**Solution**:
- Files are automatically tried with multiple encodings
- Check error log for specific files
- Manually specify encoding if needed

### Slow Processing

**Problem**: Processing takes too long
**Solution**:
- Enable caching
- Reduce quality filter strictness
- Process in smaller batches
- Use checkpoints for resumability

### Cache Issues

**Problem**: Stale cache data
**Solution**:
```python
# Clear cache
cache = DataCache()
cache.clear_cache(keep_checkpoints=False)

# Or disable cache
dialogues = processor.process_drive_files(files, use_cache=False)
```

## Performance Tips

1. **Use caching**: Enables instant reloading on reruns
2. **Batch processing**: Optimal batch_size is 50-100
3. **Checkpoints**: Resume from interruptions
4. **Quality filters**: Filter early to reduce memory
5. **Monitor memory**: Track usage and adjust batch size

## Integration with GAN Model

After processing, use dialogues with the GAN model:

```python
# Process dialogues
processor = EnhancedDialogueProcessor.from_config_file('config/data_config.yaml')
dialogues = processor.process_drive_files(files)

# Build vocabulary
vocab = processor.build_vocabulary(dialogues)

# Prepare for GAN training
contexts = [d.context for d in dialogues]
responses = [d.response for d in dialogues]

# Continue with GAN training...
```

## Additional Resources

- [Drive Setup Guide](DRIVE_SETUP.md): Google Drive configuration
- [Configuration Reference](../config/data_config.yaml): Full config options
- [Example Script](../examples/process_drive_folder.py): Complete example
- [README](../README.md): Project overview
