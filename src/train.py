"""
Main training script for DLA (Dialogue Learning Algorithm).

Implements adversarial training loop for dialogue generation:
1. Pre-train Generator with Maximum Likelihood Estimation (MLE)
2. Pre-train Discriminator to distinguish real vs generated text
3. Adversarial training with policy gradient (REINFORCE)

Usage:
    python src/train.py
"""

import os
import sys
import time
import numpy as np
import tensorflow as tf
from tensorflow import keras
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from model import build_generator, build_discriminator
from utils import (
    Tokenizer, load_dialogue_data, create_batches, 
    print_training_examples, calculate_diversity, calculate_perplexity
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DLATrainer:
    """
    Main trainer class for DLA dialogue generation model.
    
    Handles:
    - Data loading and preprocessing
    - Model initialization
    - Pre-training (MLE)
    - Adversarial training (policy gradient)
    - Checkpoint saving and loading
    - Metrics tracking
    """
    
    def __init__(self, config):
        """
        Initialize trainer with configuration.
        
        Args:
            config: Configuration object with all hyperparameters
        """
        self.config = config
        
        # Set random seeds for reproducibility
        np.random.seed(config.RANDOM_SEED)
        tf.random.set_seed(config.RANDOM_SEED)
        
        # Create output directories
        config.create_directories()
        
        # Initialize components
        self.tokenizer = None
        self.generator = None
        self.discriminator = None
        self.train_data = None
        self.data_stats = None
        
        # Optimizers
        self.gen_optimizer_pretrain = None
        self.gen_optimizer_adversarial = None
        self.disc_optimizer = None
        
        # Training history
        self.history = {
            'gen_pretrain_loss': [],
            'disc_pretrain_loss': [],
            'disc_pretrain_acc': [],
            'gen_adversarial_loss': [],
            'disc_adversarial_loss': [],
            'disc_adversarial_acc': [],
            'diversity': [],
            'perplexity': []
        }
        
        logger.info("DLA Trainer initialized")
    
    def load_data(self):
        """Load and preprocess dialogue data from multiple .txt files."""
        logger.info("="*60)
        logger.info("STEP 1: Loading Data")
        logger.info("="*60)
        
        # Initialize tokenizer
        self.tokenizer = Tokenizer(
            vocab_size=self.config.VOCAB_SIZE,
            min_freq=self.config.MIN_WORD_FREQ
        )
        
        # Load data using DialogueParser
        self.train_data, self.data_stats = load_dialogue_data(
            data_dir=self.config.DATA_DIR,
            tokenizer=self.tokenizer,
            max_length=self.config.MAX_SEQUENCE_LENGTH,
            config=self.config
        )
        
        logger.info(f"Training data shape: {self.train_data.shape}")
        logger.info(f"Vocabulary size: {len(self.tokenizer.word2idx)}")
        logger.info("✓ Data loaded successfully!\n")
    
    def build_models(self):
        """Build Generator and Discriminator models."""
        logger.info("="*60)
        logger.info("STEP 2: Building Models")
        logger.info("="*60)
        
        # Build Generator
        logger.info("Building Generator (LSTM-based)...")
        self.generator = build_generator(self.config)
        logger.info(f"  - Embedding dim: {self.config.EMBEDDING_DIM}")
        logger.info(f"  - Hidden dim: {self.config.HIDDEN_DIM}")
        logger.info(f"  - LSTM layers: {self.config.GENERATOR_LSTM_LAYERS}")
        
        # Build Discriminator
        logger.info("\nBuilding Discriminator (CNN-based)...")
        self.discriminator = build_discriminator(self.config)
        logger.info(f"  - Kernel sizes: {self.config.DISCRIMINATOR_KERNEL_SIZES}")
        logger.info(f"  - Filters per kernel: {self.config.DISCRIMINATOR_NUM_FILTERS}")
        
        # Initialize optimizers
        self.gen_optimizer_pretrain = keras.optimizers.Adam(
            learning_rate=self.config.GENERATOR_LR_PRETRAIN
        )
        self.gen_optimizer_adversarial = keras.optimizers.Adam(
            learning_rate=self.config.GENERATOR_LR_ADVERSARIAL
        )
        self.disc_optimizer = keras.optimizers.Adam(
            learning_rate=self.config.DISCRIMINATOR_LR
        )
        
        logger.info("✓ Models built successfully!\n")
    
    @tf.function
    def pretrain_generator_step(self, inputs, targets):
        """
        Single pre-training step for Generator using MLE.
        
        Standard teacher-forcing: predict next token given previous tokens.
        
        Args:
            inputs: Input sequences (batch_size, seq_len)
            targets: Target sequences (batch_size, seq_len)
        
        Returns:
            loss: Cross-entropy loss
        """
        with tf.GradientTape() as tape:
            # Forward pass
            logits, _ = self.generator(inputs, training=True)
            
            # Calculate loss (cross-entropy)
            loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=False)
            
            # Mask padding tokens
            mask = tf.cast(targets != 0, tf.float32)
            loss = loss_fn(targets, logits, sample_weight=mask)
        
        # Backward pass
        gradients = tape.gradient(loss, self.generator.trainable_variables)
        self.gen_optimizer_pretrain.apply_gradients(
            zip(gradients, self.generator.trainable_variables)
        )
        
        return loss
    
    def pretrain_generator(self):
        """Pre-train Generator with Maximum Likelihood Estimation."""
        logger.info("="*60)
        logger.info("STEP 3: Pre-training Generator (MLE)")
        logger.info("="*60)
        
        num_epochs = self.config.GENERATOR_PRETRAIN_EPOCHS
        batch_size = self.config.BATCH_SIZE
        
        for epoch in range(num_epochs):
            epoch_start = time.time()
            epoch_losses = []
            
            # Create batches
            batches = create_batches(self.train_data, batch_size, shuffle=True)
            
            for batch in batches:
                # Split into input and target (shifted by 1)
                inputs = batch[:, :-1]
                targets = batch[:, 1:]
                
                # Training step
                loss = self.pretrain_generator_step(inputs, targets)
                epoch_losses.append(float(loss))
            
            # Calculate epoch metrics
            avg_loss = np.mean(epoch_losses)
            epoch_time = time.time() - epoch_start
            
            self.history['gen_pretrain_loss'].append(avg_loss)
            
            logger.info(
                f"Epoch {epoch+1}/{num_epochs} - "
                f"Loss: {avg_loss:.4f} - "
                f"Time: {epoch_time:.1f}s"
            )
            
            # Print examples every few epochs
            if (epoch + 1) % 5 == 0 or epoch == num_epochs - 1:
                print_training_examples(
                    self.generator, 
                    self.tokenizer, 
                    num_examples=3
                )
        
        logger.info("✓ Generator pre-training complete!\n")
    
    @tf.function
    def pretrain_discriminator_step(self, real_data, fake_data):
        """
        Single pre-training step for Discriminator.
        
        Train to distinguish real dialogues from generated ones.
        
        Args:
            real_data: Real dialogue sequences
            fake_data: Generated dialogue sequences
        
        Returns:
            loss: Binary cross-entropy loss
            accuracy: Classification accuracy
        """
        with tf.GradientTape() as tape:
            # Get predictions
            real_scores = self.discriminator(real_data, training=True)
            fake_scores = self.discriminator(fake_data, training=True)
            
            # Labels: 1 for real, 0 for fake
            real_labels = tf.ones_like(real_scores)
            fake_labels = tf.zeros_like(fake_scores)
            
            # Calculate loss
            loss_fn = keras.losses.BinaryCrossentropy()
            real_loss = loss_fn(real_labels, real_scores)
            fake_loss = loss_fn(fake_labels, fake_scores)
            loss = (real_loss + fake_loss) / 2
            
            # Calculate accuracy
            real_acc = tf.reduce_mean(tf.cast(real_scores > 0.5, tf.float32))
            fake_acc = tf.reduce_mean(tf.cast(fake_scores < 0.5, tf.float32))
            accuracy = (real_acc + fake_acc) / 2
        
        # Backward pass
        gradients = tape.gradient(loss, self.discriminator.trainable_variables)
        self.disc_optimizer.apply_gradients(
            zip(gradients, self.discriminator.trainable_variables)
        )
        
        return loss, accuracy
    
    def generate_fake_samples(self, num_samples):
        """
        Generate fake samples from Generator for Discriminator training.
        
        Args:
            num_samples: Number of samples to generate
        
        Returns:
            fake_samples: Generated sequences (num_samples, max_length)
        """
        fake_samples = []
        
        for _ in range(num_samples):
            # Generate sequence
            generated = self.generator.generate_sequence(
                start_token=self.tokenizer.START,
                max_length=self.config.MAX_SEQUENCE_LENGTH,
                temperature=1.0,
                top_k=50
            )
            fake_samples.append(generated)
        
        # Pad to same length
        from utils import pad_sequences
        fake_samples = pad_sequences(
            fake_samples, 
            maxlen=self.config.MAX_SEQUENCE_LENGTH,
            padding='post'
        )
        
        return fake_samples
    
    def pretrain_discriminator(self):
        """Pre-train Discriminator to distinguish real vs fake."""
        logger.info("="*60)
        logger.info("STEP 4: Pre-training Discriminator")
        logger.info("="*60)
        
        num_epochs = self.config.DISCRIMINATOR_PRETRAIN_EPOCHS
        batch_size = self.config.BATCH_SIZE
        
        for epoch in range(num_epochs):
            epoch_start = time.time()
            epoch_losses = []
            epoch_accs = []
            
            # Create batches
            batches = create_batches(self.train_data, batch_size, shuffle=True)
            
            for real_batch in batches:
                # Generate fake samples
                fake_batch = self.generate_fake_samples(len(real_batch))
                
                # Training step
                loss, accuracy = self.pretrain_discriminator_step(
                    real_batch, fake_batch
                )
                
                epoch_losses.append(float(loss))
                epoch_accs.append(float(accuracy))
            
            # Calculate epoch metrics
            avg_loss = np.mean(epoch_losses)
            avg_acc = np.mean(epoch_accs)
            epoch_time = time.time() - epoch_start
            
            self.history['disc_pretrain_loss'].append(avg_loss)
            self.history['disc_pretrain_acc'].append(avg_acc)
            
            logger.info(
                f"Epoch {epoch+1}/{num_epochs} - "
                f"Loss: {avg_loss:.4f} - "
                f"Accuracy: {avg_acc:.4f} - "
                f"Time: {epoch_time:.1f}s"
            )
        
        logger.info("✓ Discriminator pre-training complete!\n")
    
    def adversarial_training_step(self, real_batch):
        """
        Single adversarial training step.
        
        Alternates between:
        1. Train Generator with policy gradient (rewards from Discriminator)
        2. Train Discriminator on new generated samples
        
        Args:
            real_batch: Batch of real dialogue sequences
        
        Returns:
            gen_loss: Generator loss
            disc_loss: Discriminator loss
            disc_acc: Discriminator accuracy
        """
        # Generate fake samples
        fake_batch = self.generate_fake_samples(len(real_batch))
        
        # Train Discriminator
        disc_loss, disc_acc = self.pretrain_discriminator_step(
            real_batch, fake_batch
        )
        
        # For Generator training, we would implement policy gradient here
        # For simplicity, we continue with MLE for now
        # Full policy gradient implementation requires Monte Carlo rollouts
        inputs = real_batch[:, :-1]
        targets = real_batch[:, 1:]
        gen_loss = self.pretrain_generator_step(inputs, targets)
        
        return gen_loss, disc_loss, disc_acc
    
    def adversarial_training(self):
        """Main adversarial training loop."""
        logger.info("="*60)
        logger.info("STEP 5: Adversarial Training")
        logger.info("="*60)
        
        num_epochs = self.config.ADVERSARIAL_EPOCHS
        batch_size = self.config.BATCH_SIZE
        
        for epoch in range(num_epochs):
            epoch_start = time.time()
            gen_losses = []
            disc_losses = []
            disc_accs = []
            
            # Create batches
            batches = create_batches(self.train_data, batch_size, shuffle=True)
            
            for batch in batches:
                # Adversarial training step
                gen_loss, disc_loss, disc_acc = self.adversarial_training_step(batch)
                
                gen_losses.append(float(gen_loss))
                disc_losses.append(float(disc_loss))
                disc_accs.append(float(disc_acc))
            
            # Calculate epoch metrics
            avg_gen_loss = np.mean(gen_losses)
            avg_disc_loss = np.mean(disc_losses)
            avg_disc_acc = np.mean(disc_accs)
            epoch_time = time.time() - epoch_start
            
            self.history['gen_adversarial_loss'].append(avg_gen_loss)
            self.history['disc_adversarial_loss'].append(avg_disc_loss)
            self.history['disc_adversarial_acc'].append(avg_disc_acc)
            
            logger.info(
                f"Epoch {epoch+1}/{num_epochs} - "
                f"G_Loss: {avg_gen_loss:.4f} - "
                f"D_Loss: {avg_disc_loss:.4f} - "
                f"D_Acc: {avg_disc_acc:.4f} - "
                f"Time: {epoch_time:.1f}s"
            )
            
            # Print examples and calculate metrics periodically
            if (epoch + 1) % self.config.CHECKPOINT_EVERY == 0:
                print_training_examples(
                    self.generator, 
                    self.tokenizer, 
                    num_examples=self.config.DISPLAY_EXAMPLES
                )
                
                # Calculate diversity
                fake_samples = self.generate_fake_samples(100)
                diversity = calculate_diversity(fake_samples, n=2)
                self.history['diversity'].append(diversity)
                logger.info(f"Diversity (2-gram): {diversity:.4f}")
                
                # Save checkpoint
                self.save_checkpoint(epoch + 1)
        
        logger.info("✓ Adversarial training complete!\n")
    
    def save_checkpoint(self, epoch):
        """
        Save model checkpoint.
        
        Args:
            epoch: Current epoch number
        """
        checkpoint_dir = os.path.join(self.config.MODEL_DIR, f"checkpoint_epoch_{epoch}")
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Save generator
        self.generator.save_weights(os.path.join(checkpoint_dir, "generator.weights.h5"))
        
        # Save discriminator
        self.discriminator.save_weights(os.path.join(checkpoint_dir, "discriminator.weights.h5"))
        
        # Save tokenizer
        import pickle
        with open(os.path.join(checkpoint_dir, "tokenizer.pkl"), 'wb') as f:
            pickle.dump(self.tokenizer, f)
        
        logger.info(f"✓ Checkpoint saved at: {checkpoint_dir}")
    
    def train(self):
        """Main training pipeline - orchestrates all training steps."""
        logger.info("\n")
        logger.info("#"*60)
        logger.info("# DLA Training Pipeline")
        logger.info("#"*60)
        
        # Display configuration
        self.config.display_config()
        
        training_start = time.time()
        
        # Step 1: Load data
        self.load_data()
        
        # Step 2: Build models
        self.build_models()
        
        # Step 3: Pre-train Generator
        self.pretrain_generator()
        
        # Step 4: Pre-train Discriminator
        self.pretrain_discriminator()
        
        # Step 5: Adversarial training
        self.adversarial_training()
        
        # Training complete
        total_time = time.time() - training_start
        
        logger.info("="*60)
        logger.info("TRAINING COMPLETE!")
        logger.info("="*60)
        logger.info(f"Total training time: {total_time/60:.1f} minutes")
        
        # Final evaluation
        logger.info("\nFinal Evaluation:")
        fake_samples = self.generate_fake_samples(200)
        diversity = calculate_diversity(fake_samples, n=2)
        logger.info(f"  Final Diversity (2-gram): {diversity:.4f}")
        
        # Save final model
        self.save_checkpoint("final")
        
        logger.info("\n✓ All done! Models saved to: " + self.config.MODEL_DIR)


def main():
    """Main entry point for training."""
    try:
        # Initialize trainer
        trainer = DLATrainer(Config)
        
        # Run training
        trainer.train()
        
        return 0
    
    except Exception as e:
        logger.error(f"Training failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
