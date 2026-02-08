"""
Example script for processing Google Drive dialogue files
Demonstrates standalone usage of the enhanced data processing system
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.drive_data_loader import DriveDataLoader
from src.enhanced_data_processor import EnhancedDialogueProcessor
from src.data_cache import DataCache


def main():
    """Main processing pipeline"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("Google Drive Dialogue Processing Pipeline")
    logger.info("="*60)
    
    # Configuration
    DRIVE_PATH = "/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/Dataset"
    OUTPUT_DIR = "./output"
    CACHE_DIR = "./cache"
    
    # Step 1: Initialize Drive Loader
    logger.info("\n[Step 1] Initializing Drive Loader...")
    drive_loader = DriveDataLoader()
    
    # Step 2: Mount Google Drive
    logger.info("\n[Step 2] Mounting Google Drive...")
    if not drive_loader.mount_drive():
        logger.error("Failed to mount Google Drive. Exiting.")
        return
    
    # Step 3: Scan folder for dialogue files
    logger.info("\n[Step 3] Scanning folder for dialogue files...")
    files = drive_loader.scan_folder(
        DRIVE_PATH,
        recursive=True,
        file_extensions=['.txt', '.json', '.jsonl', '.csv']
    )
    
    logger.info(f"Found {len(files)} dialogue files")
    
    # Step 4: Get folder statistics
    logger.info("\n[Step 4] Calculating folder statistics...")
    stats = drive_loader.get_folder_stats(DRIVE_PATH)
    logger.info(f"Total files: {stats.get('total_files', 0)}")
    logger.info(f"Total size: {stats.get('total_size_mb', 0):.2f} MB")
    logger.info(f"File types: {stats.get('file_types', {})}")
    
    # Step 5: Initialize Enhanced Processor
    logger.info("\n[Step 5] Initializing Enhanced Processor...")
    processor = EnhancedDialogueProcessor(
        tokenizer_config={
            'max_vocab_size': 5000,
            'min_word_freq': 2,
            'oov_token': '<UNK>'
        },
        quality_filters={
            'min_dialogue_length': 5,
            'max_dialogue_length': 150,
            'min_word_count': 2,
            'remove_duplicates': True
        },
        augmentation={
            'enabled': True,
            'techniques': ['context_shuffle'],
            'augment_ratio': 0.3
        },
        cache_dir=CACHE_DIR
    )
    
    # Step 6: Process all files
    logger.info("\n[Step 6] Processing dialogue files...")
    logger.info("This may take several minutes depending on the number of files...")
    
    dialogues = processor.process_drive_files(
        file_list=files[:100],  # Process first 100 files for demo
        batch_size=50,
        show_progress=True,
        use_cache=True,
        checkpoint_interval=25
    )
    
    logger.info(f"\nProcessed {len(dialogues)} dialogues")
    
    # Step 7: Build vocabulary
    logger.info("\n[Step 7] Building vocabulary...")
    vocab = processor.build_vocabulary(dialogues)
    logger.info(f"Vocabulary size: {len(vocab)} tokens")
    
    # Step 8: Apply augmentation (if enabled)
    if processor.config.augmentation_enabled:
        logger.info("\n[Step 8] Applying data augmentation...")
        dialogues = processor.augment_dialogues(dialogues)
        logger.info(f"Total dialogues after augmentation: {len(dialogues)}")
    
    # Step 9: Export processed data
    logger.info("\n[Step 9] Exporting processed data...")
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Export in multiple formats
    processor.export_to_format(
        dialogues,
        f"{OUTPUT_DIR}/processed_dialogues.jsonl",
        format_type='jsonl'
    )
    
    processor.export_to_format(
        dialogues,
        f"{OUTPUT_DIR}/processed_dialogues.csv",
        format_type='csv'
    )
    
    # Step 10: Save vocabulary
    logger.info("\n[Step 10] Saving vocabulary...")
    import json
    with open(f"{OUTPUT_DIR}/vocabulary.json", 'w') as f:
        json.dump(vocab, f, indent=2)
    
    # Step 11: Print final statistics
    logger.info("\n[Step 11] Final Statistics")
    logger.info("="*60)
    stats = processor.get_processing_stats()
    logger.info(f"Files processed: {stats['processed_files']}")
    logger.info(f"Failed files: {stats['failed_files']}")
    logger.info(f"Total dialogues: {stats['total_dialogues']}")
    logger.info(f"Duplicates removed: {stats['total_duplicates_removed']}")
    logger.info(f"Processing time: {stats.get('end_time', 0) - stats['start_time']:.2f}s")
    logger.info(f"Memory usage: {stats['memory_usage_mb']:.2f} MB")
    logger.info("="*60)
    
    logger.info("\n✅ Processing complete!")
    logger.info(f"Output files saved to: {OUTPUT_DIR}/")
    logger.info(f"Cache saved to: {CACHE_DIR}/")


if __name__ == "__main__":
    main()
