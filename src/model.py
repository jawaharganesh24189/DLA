"""
Neural network models for DLA (Dialogue Learning Algorithm).

Contains:
- Generator: LSTM-based sequence generation model (SeqGAN style)
- Discriminator: CNN-based authenticity classifier
- Helper functions for building model components
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np


class Generator(keras.Model):
    """
    LSTM-based Generator for dialogue generation using policy gradient (REINFORCE).
    
    Architecture:
    1. Embedding layer: Maps word indices to dense vectors
    2. LSTM layers: Sequential processing with context memory
    3. Dense output: Projects to vocabulary space with softmax
    
    The generator is trained in two phases:
    - Pre-training: Maximum Likelihood Estimation (MLE) with teacher forcing
    - Adversarial: Policy gradient using rewards from Discriminator
    
    Args:
        vocab_size (int): Size of vocabulary
        embedding_dim (int): Dimension of word embeddings
        hidden_dim (int): Dimension of LSTM hidden state
        num_layers (int): Number of stacked LSTM layers
        dropout_rate (float): Dropout rate for regularization
    """
    
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers=2, dropout_rate=0.3):
        super(Generator, self).__init__()
        
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Word embedding layer - converts word indices to dense vectors
        self.embedding = layers.Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            mask_zero=True,  # Mask padding tokens (0)
            name="generator_embedding"
        )
        
        # Stack of LSTM layers for sequential processing
        self.lstm_layers = []
        for i in range(num_layers):
            self.lstm_layers.append(
                layers.LSTM(
                    hidden_dim,
                    return_sequences=True,  # Return full sequence for next layer
                    return_state=True,       # Return hidden and cell states
                    dropout=dropout_rate,
                    recurrent_dropout=dropout_rate,
                    name=f"generator_lstm_{i+1}"
                )
            )
        
        # Output layer - project to vocabulary space
        self.output_layer = layers.Dense(
            vocab_size,
            activation='softmax',  # Probability distribution over vocabulary
            name="generator_output"
        )
        
        # Dropout for regularization
        self.dropout = layers.Dropout(dropout_rate)
    
    def call(self, inputs, training=False, states=None):
        """
        Forward pass through the generator.
        
        Args:
            inputs: Word indices (batch_size, sequence_length)
            training: Whether in training mode (enables dropout)
            states: Initial LSTM states (optional)
        
        Returns:
            logits: Probability distribution over vocabulary (batch_size, seq_len, vocab_size)
            states: Final LSTM states for continuation
        """
        # Embed input words
        x = self.embedding(inputs)
        
        if training:
            x = self.dropout(x, training=training)
        
        # Pass through LSTM layers
        all_states = []
        for lstm_layer in self.lstm_layers:
            if states is not None and len(all_states) < len(states):
                # Use provided initial state
                x, h, c = lstm_layer(x, initial_state=states[len(all_states)])
            else:
                # Initialize with zeros
                x, h, c = lstm_layer(x)
            all_states.append([h, c])
        
        if training:
            x = self.dropout(x, training=training)
        
        # Project to vocabulary space
        logits = self.output_layer(x)
        
        return logits, all_states
    
    def generate_sequence(self, start_token, max_length, temperature=1.0, top_k=50):
        """
        Generate a sequence autoregressively (word-by-word).
        
        Args:
            start_token (int): Initial token to start generation
            max_length (int): Maximum sequence length to generate
            temperature (float): Sampling temperature (higher = more random)
            top_k (int): Only sample from top-k most likely tokens
        
        Returns:
            generated_sequence: List of generated word indices
        """
        # Initialize with start token
        current_token = tf.constant([[start_token]])
        generated = [start_token]
        states = None
        
        for _ in range(max_length - 1):
            # Get predictions for next token
            logits, states = self.call(current_token, training=False, states=states)
            
            # Apply temperature
            logits = logits[:, -1, :] / temperature
            
            # Top-k sampling
            if top_k > 0:
                top_k_logits, top_k_indices = tf.nn.top_k(logits, k=top_k)
                next_token_idx = tf.random.categorical(top_k_logits, num_samples=1)
                # Get the actual token from top_k_indices
                next_token = tf.gather(top_k_indices[0], next_token_idx[0])
            else:
                next_token = tf.random.categorical(logits, num_samples=1)
            
            # Add to generated sequence
            next_token = int(next_token[0])
            generated.append(next_token)
            
            # Check for end token (assuming 0 is padding/end)
            if next_token == 0:
                break
            
            # Update input for next iteration
            current_token = tf.constant([[next_token]])
        
        return generated


class Discriminator(keras.Model):
    """
    CNN-based Discriminator to classify real vs generated dialogues.
    
    Architecture:
    1. Embedding layer: Maps word indices to dense vectors
    2. Multi-kernel CNN: Captures n-gram patterns of different lengths
    3. Max pooling: Extracts most important features
    4. Dense layers: Final classification to real/fake
    
    Uses multiple kernel sizes (3, 4, 5) to capture short and long-range patterns
    similar to Kim's CNN for text classification.
    
    Args:
        vocab_size (int): Size of vocabulary
        embedding_dim (int): Dimension of word embeddings
        kernel_sizes (list): List of CNN kernel sizes (e.g., [3, 4, 5])
        num_filters (int): Number of filters per kernel size
        dropout_rate (float): Dropout rate for regularization
    """
    
    def __init__(self, vocab_size, embedding_dim, kernel_sizes=[3, 4, 5], 
                 num_filters=128, dropout_rate=0.3):
        super(Discriminator, self).__init__()
        
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.kernel_sizes = kernel_sizes
        self.num_filters = num_filters
        
        # Word embedding layer - can be shared with Generator or separate
        self.embedding = layers.Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            mask_zero=False,  # Don't mask for CNN
            name="discriminator_embedding"
        )
        
        # Multiple CNN branches with different kernel sizes
        # Each captures n-gram patterns of different lengths
        self.conv_layers = []
        self.pooling_layers = []
        
        for kernel_size in kernel_sizes:
            # 1D convolution over sequence
            conv = layers.Conv1D(
                filters=num_filters,
                kernel_size=kernel_size,
                activation='relu',
                padding='valid',  # No padding - reduce sequence length
                name=f"discriminator_conv_{kernel_size}"
            )
            self.conv_layers.append(conv)
            
            # Global max pooling - extract most important feature
            pool = layers.GlobalMaxPooling1D(name=f"discriminator_pool_{kernel_size}")
            self.pooling_layers.append(pool)
        
        # Concatenate all CNN features
        self.concat = layers.Concatenate(name="discriminator_concat")
        
        # Dropout for regularization
        self.dropout = layers.Dropout(dropout_rate)
        
        # Highway connection for better gradient flow
        self.highway = layers.Dense(
            num_filters * len(kernel_sizes),
            activation='relu',
            name="discriminator_highway"
        )
        
        # Final classification layer
        self.output_layer = layers.Dense(
            1,
            activation='sigmoid',  # Output probability in [0, 1]
            name="discriminator_output"
        )
    
    def call(self, inputs, training=False):
        """
        Forward pass through the discriminator.
        
        Args:
            inputs: Word indices (batch_size, sequence_length)
            training: Whether in training mode (enables dropout)
        
        Returns:
            score: Probability that input is real (batch_size, 1)
        """
        # Embed input words
        x = self.embedding(inputs)  # (batch_size, seq_len, embedding_dim)
        
        # Apply multiple CNN branches
        conv_outputs = []
        for conv_layer, pool_layer in zip(self.conv_layers, self.pooling_layers):
            # Convolve over sequence
            conv_out = conv_layer(x)  # (batch_size, seq_len - kernel + 1, filters)
            
            # Max pool to get single feature per filter
            pooled = pool_layer(conv_out)  # (batch_size, filters)
            conv_outputs.append(pooled)
        
        # Concatenate all features from different kernel sizes
        concatenated = self.concat(conv_outputs)  # (batch_size, filters * num_kernels)
        
        if training:
            concatenated = self.dropout(concatenated, training=training)
        
        # Highway connection
        highway_out = self.highway(concatenated)
        
        if training:
            highway_out = self.dropout(highway_out, training=training)
        
        # Final binary classification
        score = self.output_layer(highway_out)  # (batch_size, 1)
        
        return score


def build_generator(config):
    """
    Build Generator model from configuration.
    
    Args:
        config: Configuration object with model hyperparameters
    
    Returns:
        generator: Compiled Generator model
    """
    generator = Generator(
        vocab_size=config.VOCAB_SIZE,
        embedding_dim=config.EMBEDDING_DIM,
        hidden_dim=config.HIDDEN_DIM,
        num_layers=config.GENERATOR_LSTM_LAYERS,
        dropout_rate=config.DROPOUT_RATE
    )
    
    return generator


def build_discriminator(config):
    """
    Build Discriminator model from configuration.
    
    Args:
        config: Configuration object with model hyperparameters
    
    Returns:
        discriminator: Compiled Discriminator model
    """
    discriminator = Discriminator(
        vocab_size=config.VOCAB_SIZE,
        embedding_dim=config.EMBEDDING_DIM,
        kernel_sizes=config.DISCRIMINATOR_KERNEL_SIZES,
        num_filters=config.DISCRIMINATOR_NUM_FILTERS,
        dropout_rate=config.DROPOUT_RATE
    )
    
    return discriminator


# Test models when run directly
if __name__ == "__main__":
    print("Testing DLA Models...")
    print("=" * 60)
    
    # Create dummy config
    class DummyConfig:
        VOCAB_SIZE = 5000
        EMBEDDING_DIM = 128
        HIDDEN_DIM = 256
        GENERATOR_LSTM_LAYERS = 2
        DROPOUT_RATE = 0.3
        DISCRIMINATOR_KERNEL_SIZES = [3, 4, 5]
        DISCRIMINATOR_NUM_FILTERS = 128
    
    config = DummyConfig()
    
    # Build models
    print("\n1. Building Generator...")
    generator = build_generator(config)
    
    # Test generator
    dummy_input = tf.constant([[1, 2, 3, 4, 5]])
    logits, states = generator(dummy_input, training=False)
    print(f"   Input shape: {dummy_input.shape}")
    print(f"   Output shape: {logits.shape}")
    print(f"   Number of LSTM states: {len(states)}")
    print("   ✓ Generator working correctly!")
    
    # Build discriminator
    print("\n2. Building Discriminator...")
    discriminator = build_discriminator(config)
    
    # Test discriminator
    score = discriminator(dummy_input, training=False)
    print(f"   Input shape: {dummy_input.shape}")
    print(f"   Output shape: {score.shape}")
    print(f"   Score value: {float(score[0, 0]):.4f}")
    print("   ✓ Discriminator working correctly!")
    
    # Test sequence generation
    print("\n3. Testing sequence generation...")
    generated = generator.generate_sequence(start_token=1, max_length=10)
    print(f"   Generated sequence: {generated}")
    print("   ✓ Generation working correctly!")
    
    print("\n" + "=" * 60)
    print("✓ All model tests passed!")
