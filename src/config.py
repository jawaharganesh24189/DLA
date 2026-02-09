"""
Configuration file for DLA (Dialogue Learning Algorithm) model training.
Centralized hyperparameters and settings for easy modification without code changes.
"""

import os


class Config:
    """
    Configuration class containing all hyperparameters and settings for the DLA model.
    
    Sections:
    - Data Configuration: Paths and data processing settings
    - Model Architecture: Generator and Discriminator parameters
    - Training Configuration: Training loop and optimization settings
    - Generation Configuration: Inference and sampling settings
    """
    
    # ====================
    # Data Configuration
    # ====================
    
    # Path to directory containing multiple .txt dialogue files
    # Each .txt file should contain dialogues in one of these formats:
    #   1. context: <text> response: <text>
    #   2. Speaker: dialogue text (line by line)
    DATA_DIR = "data"
    
    # File pattern to match (e.g., "*.txt" for all txt files, "train-*.txt" for training files)
    DATA_PATTERN = "*.txt"
    
    # Maximum sequence length (number of words per dialogue turn)
    # Longer sequences = more context but slower training
    MAX_SEQUENCE_LENGTH = 50
    
    # Vocabulary size - number of unique words to keep
    # Larger vocab = more expressive but more memory
    VOCAB_SIZE = 10000
    
    # Minimum word frequency to include in vocabulary
    # Words appearing less than this will be replaced with <UNK>
    MIN_WORD_FREQ = 2
    
    # ====================
    # Model Architecture
    # ====================
    
    # Embedding dimension - size of word embeddings
    # Higher = more expressive but slower training
    EMBEDDING_DIM = 128
    
    # Hidden dimension for LSTM layers
    # Higher = more model capacity but more memory
    HIDDEN_DIM = 256
    
    # Number of LSTM layers in Generator
    GENERATOR_LSTM_LAYERS = 2
    
    # Dropout rate for regularization (0.0 to 1.0)
    # Higher = more regularization but may underfit
    DROPOUT_RATE = 0.3
    
    # Discriminator CNN kernel sizes
    # Multiple kernel sizes capture different n-gram patterns
    DISCRIMINATOR_KERNEL_SIZES = [3, 4, 5]
    
    # Number of filters per kernel size
    DISCRIMINATOR_NUM_FILTERS = 128
    
    # ====================
    # Training Configuration
    # ====================
    
    # Batch size for training
    # Larger = faster but more memory, smaller = more stable updates
    BATCH_SIZE = 64
    
    # Pre-training epochs for Generator (MLE training before adversarial)
    # More epochs = better initialization but longer training
    GENERATOR_PRETRAIN_EPOCHS = 10
    
    # Pre-training epochs for Discriminator
    DISCRIMINATOR_PRETRAIN_EPOCHS = 5
    
    # Adversarial training epochs
    # This is the main GAN training phase
    ADVERSARIAL_EPOCHS = 30
    
    # Generator training steps per adversarial epoch
    # Higher = Generator gets more updates relative to Discriminator
    G_STEPS = 1
    
    # Discriminator training steps per adversarial epoch
    # Higher = Discriminator gets stronger, may stabilize training
    D_STEPS = 5
    
    # Learning rate for Generator (MLE pre-training)
    GENERATOR_LR_PRETRAIN = 0.001
    
    # Learning rate for Generator (adversarial training)
    # Typically lower than pre-training to stabilize GAN
    GENERATOR_LR_ADVERSARIAL = 0.0001
    
    # Learning rate for Discriminator
    DISCRIMINATOR_LR = 0.0001
    
    # Monte Carlo rollout samples for policy gradient
    # More rollouts = more accurate gradient estimate but slower
    MC_ROLLOUT_NUM = 16
    
    # Reward discount factor (gamma) for future rewards
    # 0.0 = only immediate reward, 1.0 = all future rewards equally
    REWARD_GAMMA = 0.99
    
    # ====================
    # Generation Configuration
    # ====================
    
    # Sampling temperature for text generation
    # Higher = more diverse but less coherent, lower = more conservative
    TEMPERATURE = 1.0
    
    # Top-k sampling - only consider top k most likely next words
    # Smaller = more focused sampling, larger = more diverse
    TOP_K = 50
    
    # Top-p (nucleus) sampling - sample from smallest set with cumulative prob >= p
    # Higher = more diverse, lower = more focused
    TOP_P = 0.95
    
    # Maximum generation length (in words)
    MAX_GENERATION_LENGTH = 50
    
    # ====================
    # System Configuration
    # ====================
    
    # Random seed for reproducibility
    RANDOM_SEED = 42
    
    # Number of training examples to display during training
    DISPLAY_EXAMPLES = 5
    
    # Save checkpoint every N epochs
    CHECKPOINT_EVERY = 5
    
    # Output directory for saved models
    OUTPUT_DIR = "outputs"
    
    # Model checkpoint directory
    MODEL_DIR = os.path.join(OUTPUT_DIR, "models")
    
    # Logs directory
    LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")
    
    # Use GPU if available (TensorFlow will auto-detect)
    USE_GPU = True
    
    # Mixed precision training for faster computation on modern GPUs
    # Set to False if you encounter numerical instability
    USE_MIXED_PRECISION = False
    
    @classmethod
    def display_config(cls):
        """Display all configuration parameters in a formatted way."""
        print("\n" + "="*60)
        print("DLA Model Configuration")
        print("="*60)
        
        sections = {
            "Data Configuration": [
                "DATA_DIR", "DATA_PATTERN", "MAX_SEQUENCE_LENGTH", 
                "VOCAB_SIZE", "MIN_WORD_FREQ"
            ],
            "Model Architecture": [
                "EMBEDDING_DIM", "HIDDEN_DIM", "GENERATOR_LSTM_LAYERS",
                "DROPOUT_RATE", "DISCRIMINATOR_KERNEL_SIZES", "DISCRIMINATOR_NUM_FILTERS"
            ],
            "Training Configuration": [
                "BATCH_SIZE", "GENERATOR_PRETRAIN_EPOCHS", "DISCRIMINATOR_PRETRAIN_EPOCHS",
                "ADVERSARIAL_EPOCHS", "G_STEPS", "D_STEPS", 
                "GENERATOR_LR_PRETRAIN", "GENERATOR_LR_ADVERSARIAL", "DISCRIMINATOR_LR",
                "MC_ROLLOUT_NUM", "REWARD_GAMMA"
            ],
            "Generation Configuration": [
                "TEMPERATURE", "TOP_K", "TOP_P", "MAX_GENERATION_LENGTH"
            ],
            "System Configuration": [
                "RANDOM_SEED", "CHECKPOINT_EVERY", "OUTPUT_DIR", 
                "USE_GPU", "USE_MIXED_PRECISION"
            ]
        }
        
        for section, params in sections.items():
            print(f"\n{section}:")
            print("-" * 60)
            for param in params:
                value = getattr(cls, param)
                print(f"  {param:.<40} {value}")
        
        print("\n" + "="*60 + "\n")
    
    @classmethod
    def create_directories(cls):
        """Create necessary output directories if they don't exist."""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.MODEL_DIR, exist_ok=True)
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
        os.makedirs(cls.DATA_DIR, exist_ok=True)


# Display configuration when module is imported
if __name__ == "__main__":
    Config.display_config()
    Config.create_directories()
    print("✓ Configuration loaded successfully!")
    print(f"✓ Output directories created at: {Config.OUTPUT_DIR}")
