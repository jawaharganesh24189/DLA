# Google Drive Setup Guide

Complete guide for setting up Google Drive integration with the dialogue processing system in Google Colab.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Organizing Your Data](#organizing-your-data)
4. [Mounting Drive in Colab](#mounting-drive-in-colab)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

## Prerequisites

- Google account with Google Drive access
- Google Colab account (free tier is sufficient)
- Dialogue dataset files in supported formats (TXT, JSON, JSONL, CSV)

## Initial Setup

### 1. Create Folder Structure

In your Google Drive, create the following folder structure:

```
MyDrive/
└── DLA_Notebooks_Data_PGPM/
    ├── Dataset/              # Your dialogue files
    ├── cache/                # Processed data cache
    ├── output/               # Processed output files
    └── logs/                 # Processing logs
```

### 2. Upload Your Data

Upload your dialogue files to the `Dataset` folder:

1. Open Google Drive (drive.google.com)
2. Navigate to `DLA_Notebooks_Data_PGPM/Dataset`
3. Click "New" → "File upload" or "Folder upload"
4. Select your dialogue files

**Supported file formats:**
- `.txt` - Text files with dialogues
- `.json` - JSON formatted dialogues
- `.jsonl` - JSON Lines format
- `.csv` - CSV with context/response columns

### 3. Verify Folder Path

Note the exact path to your data folder. In Colab, it will typically be:
```
/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/Dataset
```

## Organizing Your Data

### Recommended Structure

For better organization, especially with many files:

```
Dataset/
├── training/
│   ├── conversations/
│   │   ├── conv_001.txt
│   │   ├── conv_002.txt
│   │   └── ...
│   ├── scripts/
│   │   ├── script_001.json
│   │   └── ...
│   └── metadata.json
├── validation/
│   └── ...
└── test/
    └── ...
```

### File Naming Conventions

Use consistent naming:
- `dialogue_001.txt`, `dialogue_002.txt`, etc.
- `conversation_2024_01_01.json`
- Include metadata in filenames if helpful

### Large Datasets

For very large datasets (>1000 files):

1. **Split into subdirectories**: Group by category, date, or source
2. **Use compression**: Upload as .zip and extract in Colab
3. **Incremental uploads**: Upload in batches to avoid timeouts

## Mounting Drive in Colab

### Method 1: Using DriveDataLoader (Recommended)

```python
from src.drive_data_loader import DriveDataLoader

# Initialize loader
loader = DriveDataLoader()

# Mount with automatic retry
success = loader.mount_drive(max_retries=3, timeout=300)

if success:
    print("✅ Drive mounted successfully!")
else:
    print("❌ Failed to mount Drive")
```

### Method 2: Manual Mount

```python
from google.colab import drive

# Mount Drive
drive.mount('/content/drive', force_remount=False)

# Verify mount
import os
if os.path.exists('/content/drive/MyDrive'):
    print("✅ Drive mounted successfully!")
else:
    print("❌ Drive not mounted")
```

### First-Time Mount

When mounting for the first time:

1. A link will appear in the output
2. Click the link (opens Google auth page)
3. Select your Google account
4. Click "Allow" to grant permissions
5. Copy the authorization code
6. Paste it in the Colab input field
7. Press Enter

**Note**: You only need to do this once per Colab session.

## Accessing Your Data

### Verify Data Location

```python
import os

# Check if folder exists
data_path = '/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/Dataset'
if os.path.exists(data_path):
    file_count = len(os.listdir(data_path))
    print(f"✅ Found {file_count} items in dataset folder")
else:
    print("❌ Dataset folder not found")
    print("Please check the path and ensure folder exists in Drive")
```

### List Files

```python
# List all files
files = os.listdir(data_path)
print("Files in dataset:")
for f in files[:10]:  # Show first 10
    print(f"  - {f}")
```

### Get File Statistics

```python
from src.drive_data_loader import DriveDataLoader

loader = DriveDataLoader()
loader.mount_drive()

# Get detailed stats
stats = loader.get_folder_stats(data_path)
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_mb']:.2f} MB")
print(f"File types: {stats['file_types']}")
```

## Troubleshooting

### Issue: "Drive not mounted"

**Symptoms**: Code can't find Drive files

**Solutions**:
1. Check if Drive is mounted: `ls /content/drive`
2. Remount: `loader.mount_drive(force_remount=True)`
3. Restart Colab runtime: Runtime → Restart runtime

### Issue: "Permission denied"

**Symptoms**: Can't read/write files

**Solutions**:
1. Check file permissions in Google Drive
2. Ensure you're logged into correct Google account
3. Re-authorize: Unmount and mount again

### Issue: "Path not found"

**Symptoms**: Can't find data folder

**Solutions**:
1. Verify exact folder path in Drive
2. Check for typos in path string
3. Ensure folder is in "My Drive" not "Shared with me"
4. Use absolute path: `/content/drive/MyDrive/...`

### Issue: "Mount timeout"

**Symptoms**: Mount operation times out

**Solutions**:
1. Check internet connection
2. Increase timeout: `loader.mount_drive(timeout=600)`
3. Try again after a few minutes
4. Close other Drive connections

### Issue: "Files not showing"

**Symptoms**: Folder appears empty but has files in web interface

**Solutions**:
1. Refresh Drive: Click refresh icon in Files panel
2. Wait a few seconds for sync
3. Check if files are in "Trash" in Drive
4. Ensure files finished uploading

### Issue: "Slow file access"

**Symptoms**: Reading files takes very long

**Solutions**:
1. Drive I/O can be slow for many small files
2. Consider uploading a compressed archive
3. Use caching to avoid re-reading
4. Process in smaller batches

## Best Practices

### 1. Use Caching

Enable caching to avoid re-downloading:

```python
processor = EnhancedDialogueProcessor(cache_dir='/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/cache')
```

### 2. Organize by Purpose

Separate data by purpose:
- Training data
- Validation data
- Test data
- Processed outputs

### 3. Keep Backups

- Don't rely solely on Drive
- Keep local backups of important data
- Version your datasets

### 4. Monitor Storage

Check Drive storage:
```python
import shutil

usage = shutil.disk_usage('/content/drive')
print(f"Drive space: {usage.free / (1024**3):.2f} GB free")
```

### 5. Clean Up

Regularly remove:
- Old cache files
- Temporary processing files
- Outdated logs

```python
# Clean cache
from src.data_cache import DataCache
cache = DataCache(cache_dir='/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/cache')
cache.clear_cache(keep_checkpoints=True)
```

### 6. Use Checkpoints

For large processing jobs:

```python
processor = EnhancedDialogueProcessor()
dialogues = processor.process_drive_files(
    files,
    checkpoint_interval=500  # Checkpoint every 500 files
)
```

If interrupted, restore from checkpoint:

```python
from src.data_cache import DataCache
cache = DataCache()
state = cache.restore_from_checkpoint('processing_500')
```

### 7. Batch Processing

Process large datasets in batches:

```python
# Process in chunks
BATCH_SIZE = 100
for i in range(0, len(files), BATCH_SIZE):
    batch = files[i:i+BATCH_SIZE]
    dialogues = processor.process_drive_files(batch)
    # Save intermediate results
    processor.export_to_format(dialogues, f'batch_{i}.jsonl', 'jsonl')
```

### 8. Monitor Resources

Watch memory and disk usage:

```python
import psutil

# Memory
mem = psutil.virtual_memory()
print(f"Memory: {mem.percent}% used")

# Disk
disk = psutil.disk_usage('/content')
print(f"Disk: {disk.percent}% used")
```

## Security Considerations

### 1. Access Control

- Don't share Drive folders publicly
- Use specific sharing for collaborators
- Review folder permissions regularly

### 2. Sensitive Data

- Don't store passwords or API keys in Drive
- Use environment variables in Colab
- Consider encryption for sensitive datasets

### 3. Session Management

- Disconnect when done: Runtime → Disconnect
- Clear outputs before sharing notebooks
- Don't leave sessions running unattended

## Performance Tips

### 1. Co-locate Cache

Store cache in Drive for persistence:
```python
cache_dir = '/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/cache'
```

### 2. Parallel Processing

Use parallel workers for faster processing:
```yaml
processing:
  parallel_workers: 4
```

### 3. Reduce I/O

- Process multiple files per read
- Use batch operations
- Enable compression for large outputs

### 4. Local Staging

For very large datasets, copy to local storage first:

```python
import shutil

# Copy to local /content for faster access
shutil.copytree(
    '/content/drive/MyDrive/Dataset',
    '/content/local_dataset'
)

# Process from local
files = loader.scan_folder('/content/local_dataset')
```

## Additional Resources

- [Google Colab Guide](https://colab.research.google.com/notebooks/intro.ipynb)
- [Google Drive for Colab](https://colab.research.google.com/notebooks/io.ipynb)
- [Data Processing Guide](DATA_PROCESSING_GUIDE.md)
- [Project README](../README.md)

## Support

If you encounter issues:

1. Check this guide for solutions
2. Review error logs in `./logs/`
3. Check GitHub issues
4. Open a new issue with:
   - Error message
   - Steps to reproduce
   - Colab runtime info
