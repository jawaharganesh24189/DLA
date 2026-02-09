"""
Quick test script to verify DLA training works end-to-end.
Uses minimal settings for fast execution.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from train import DLATrainer

# Modify config for quick test
Config.GENERATOR_PRETRAIN_EPOCHS = 2
Config.DISCRIMINATOR_PRETRAIN_EPOCHS = 1
Config.ADVERSARIAL_EPOCHS = 2
Config.BATCH_SIZE = 16
Config.VOCAB_SIZE = 500
Config.MAX_SEQUENCE_LENGTH = 30
Config.EMBEDDING_DIM = 64
Config.HIDDEN_DIM = 128
Config.CHECKPOINT_EVERY = 2

print("="*60)
print("Quick Test: DLA Training Pipeline")
print("="*60)
print("\nThis is a minimal test with reduced parameters:")
print(f"  - Generator pretrain: {Config.GENERATOR_PRETRAIN_EPOCHS} epochs")
print(f"  - Discriminator pretrain: {Config.DISCRIMINATOR_PRETRAIN_EPOCHS} epoch")
print(f"  - Adversarial training: {Config.ADVERSARIAL_EPOCHS} epochs")
print(f"  - Batch size: {Config.BATCH_SIZE}")
print(f"  - Vocab size: {Config.VOCAB_SIZE}")
print("="*60)

try:
    # Initialize trainer
    trainer = DLATrainer(Config)
    
    # Run training
    trainer.train()
    
    print("\n" + "="*60)
    print("✓ Quick test completed successfully!")
    print("="*60)
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
