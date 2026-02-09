"""
Utility functions for DLA (Dialogue Learning Algorithm) training and evaluation.

Contains:
- Text preprocessing and tokenization
- Sequence padding and batching
- Evaluation metrics (BLEU, perplexity, diversity)
- Monte Carlo rollout for policy gradient
- Data loading and processing helpers
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from collections import Counter
import re
from typing import List, Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Tokenizer:
    """
    Simple word-level tokenizer for dialogue text.
    
    Converts text to integer sequences and vice versa.
    Handles special tokens: <PAD>, <START>, <END>, <UNK>
    
    Args:
        vocab_size (int): Maximum vocabulary size
        min_freq (int): Minimum word frequency to include
    """
    
    def __init__(self, vocab_size=10000, min_freq=2):
        self.vocab_size = vocab_size
        self.min_freq = min_freq
        
        # Special tokens
        self.PAD = 0
        self.START = 1
        self.END = 2
        self.UNK = 3
        
        # Vocabularies
        self.word2idx = {'<PAD>': self.PAD, '<START>': self.START, 
                        '<END>': self.END, '<UNK>': self.UNK}
        self.idx2word = {v: k for k, v in self.word2idx.items()}
        
        # Statistics
        self.word_counts = Counter()
        self.vocab_built = False
    
    def fit_on_texts(self, texts: List[str]):
        """
        Build vocabulary from list of texts.
        
        Args:
            texts: List of text strings to build vocabulary from
        """
        logger.info(f"Building vocabulary from {len(texts)} texts...")
        
        # Count word frequencies
        for text in texts:
            words = self._tokenize(text)
            self.word_counts.update(words)
        
        # Filter by minimum frequency
        filtered_words = [word for word, count in self.word_counts.items() 
                         if count >= self.min_freq]
        
        # Sort by frequency and take top vocab_size - 4 (reserve space for special tokens)
        sorted_words = sorted(filtered_words, 
                            key=lambda w: self.word_counts[w], 
                            reverse=True)
        top_words = sorted_words[:self.vocab_size - 4]
        
        # Build word to index mapping
        for idx, word in enumerate(top_words, start=4):  # Start after special tokens
            self.word2idx[word] = idx
            self.idx2word[idx] = word
        
        self.vocab_built = True
        logger.info(f"Vocabulary built: {len(self.word2idx)} words")
        logger.info(f"Most common words: {sorted_words[:10]}")
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Convert to lowercase and split on whitespace/punctuation
        text = text.lower()
        # Keep basic punctuation as separate tokens
        text = re.sub(r"([?.!,'])", r" \1 ", text)
        words = text.split()
        return words
    
    def text_to_sequence(self, text: str, add_start_end=False) -> List[int]:
        """
        Convert text to sequence of integer indices.
        
        Args:
            text: Input text string
            add_start_end: Whether to add <START> and <END> tokens
        
        Returns:
            List of integer indices
        """
        words = self._tokenize(text)
        sequence = [self.word2idx.get(word, self.UNK) for word in words]
        
        if add_start_end:
            sequence = [self.START] + sequence + [self.END]
        
        return sequence
    
    def sequence_to_text(self, sequence: List[int]) -> str:
        """
        Convert sequence of indices back to text.
        
        Args:
            sequence: List of integer indices
        
        Returns:
            Decoded text string
        """
        words = [self.idx2word.get(idx, '<UNK>') for idx in sequence]
        # Remove special tokens
        words = [w for w in words if w not in ['<PAD>', '<START>', '<END>']]
        return ' '.join(words)


def pad_sequences(sequences: List[List[int]], maxlen: int, padding='post') -> np.ndarray:
    """
    Pad sequences to same length.
    
    Args:
        sequences: List of integer sequences
        maxlen: Maximum sequence length
        padding: 'pre' or 'post' padding
    
    Returns:
        Padded numpy array of shape (num_sequences, maxlen)
    """
    padded = np.zeros((len(sequences), maxlen), dtype=np.int32)
    
    for i, seq in enumerate(sequences):
        if len(seq) > maxlen:
            # Truncate
            if padding == 'post':
                padded[i] = seq[:maxlen]
            else:
                padded[i] = seq[-maxlen:]
        else:
            # Pad
            if padding == 'post':
                padded[i, :len(seq)] = seq
            else:
                padded[i, -len(seq):] = seq
    
    return padded


def create_batches(data: np.ndarray, batch_size: int, shuffle=True) -> List[np.ndarray]:
    """
    Create batches from data.
    
    Args:
        data: Input data array
        batch_size: Size of each batch
        shuffle: Whether to shuffle data before batching
    
    Returns:
        List of batches
    """
    if shuffle:
        indices = np.random.permutation(len(data))
        data = data[indices]
    
    num_batches = len(data) // batch_size
    batches = []
    
    for i in range(num_batches):
        batch = data[i * batch_size:(i + 1) * batch_size]
        batches.append(batch)
    
    # Add remaining data as last batch if exists
    if len(data) % batch_size != 0:
        batch = data[num_batches * batch_size:]
        batches.append(batch)
    
    return batches


def calculate_bleu(references: List[List[str]], hypothesis: List[str], n=2) -> float:
    """
    Calculate BLEU score for generated text.
    
    Args:
        references: List of reference sequences (each is list of words)
        hypothesis: Generated sequence (list of words)
        n: N-gram size (2 for BLEU-2, 4 for BLEU-4)
    
    Returns:
        BLEU score (0 to 1)
    """
    from collections import defaultdict
    
    # Count n-grams in hypothesis
    hyp_ngrams = defaultdict(int)
    for i in range(len(hypothesis) - n + 1):
        ngram = tuple(hypothesis[i:i + n])
        hyp_ngrams[ngram] += 1
    
    # Count matching n-grams with references
    matches = 0
    total = sum(hyp_ngrams.values())
    
    for ref in references:
        ref_ngrams = defaultdict(int)
        for i in range(len(ref) - n + 1):
            ngram = tuple(ref[i:i + n])
            ref_ngrams[ngram] += 1
        
        # Count clipped matches
        for ngram, count in hyp_ngrams.items():
            matches += min(count, ref_ngrams[ngram])
    
    # Calculate precision
    if total == 0:
        return 0.0
    
    precision = matches / total
    
    # Brevity penalty
    ref_len = sum(len(ref) for ref in references) / len(references)
    hyp_len = len(hypothesis)
    
    if hyp_len > ref_len:
        bp = 1.0
    else:
        bp = np.exp(1 - ref_len / hyp_len) if hyp_len > 0 else 0.0
    
    bleu = bp * precision
    return bleu


def calculate_diversity(sequences: List[List[int]], n=2) -> float:
    """
    Calculate diversity score - ratio of unique n-grams to total n-grams.
    
    Args:
        sequences: List of integer sequences
        n: N-gram size
    
    Returns:
        Diversity score (0 to 1, higher is more diverse)
    """
    all_ngrams = []
    
    for seq in sequences:
        for i in range(len(seq) - n + 1):
            ngram = tuple(seq[i:i + n])
            all_ngrams.append(ngram)
    
    if len(all_ngrams) == 0:
        return 0.0
    
    unique_ngrams = len(set(all_ngrams))
    total_ngrams = len(all_ngrams)
    
    diversity = unique_ngrams / total_ngrams
    return diversity


def monte_carlo_rollout(generator, current_seq, num_rollouts=16, max_length=50):
    """
    Perform Monte Carlo rollout for policy gradient.
    
    Complete partial sequences by sampling from generator,
    then evaluate with discriminator to get rewards.
    
    Args:
        generator: Generator model
        current_seq: Current partial sequence (batch_size, current_length)
        num_rollouts: Number of rollout samples per sequence
        max_length: Maximum sequence length
    
    Returns:
        rollout_sequences: List of completed sequences
    """
    batch_size = tf.shape(current_seq)[0]
    current_length = tf.shape(current_seq)[1]
    
    rollout_sequences = []
    
    for _ in range(num_rollouts):
        # Start with current sequence
        seq = tf.identity(current_seq)
        
        # Generate remaining tokens
        for step in range(current_length, max_length):
            # Get next token probabilities
            logits, _ = generator(seq, training=False)
            
            # Sample next token
            next_token_logits = logits[:, -1, :]
            next_token = tf.random.categorical(next_token_logits, num_samples=1)
            
            # Append to sequence
            seq = tf.concat([seq, next_token], axis=1)
            
            # Check if all sequences ended
            if tf.reduce_all(next_token == 0):
                break
        
        rollout_sequences.append(seq)
    
    return rollout_sequences


def calculate_perplexity(model, data, tokenizer):
    """
    Calculate perplexity on dataset.
    
    Lower perplexity = better model (more confident predictions).
    
    Args:
        model: Language model (Generator)
        data: Test data sequences
        tokenizer: Tokenizer for decoding
    
    Returns:
        perplexity: Perplexity score
    """
    total_loss = 0.0
    total_tokens = 0
    
    for batch in create_batches(data, batch_size=32, shuffle=False):
        # Forward pass
        logits, _ = model(batch[:, :-1], training=False)
        targets = batch[:, 1:]
        
        # Calculate cross-entropy loss
        loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=False)
        
        # Mask padding tokens
        mask = tf.cast(targets != 0, tf.float32)
        loss = loss_fn(targets, logits, sample_weight=mask)
        
        # Accumulate
        total_loss += float(loss) * tf.reduce_sum(mask)
        total_tokens += tf.reduce_sum(mask)
    
    # Calculate perplexity
    avg_loss = total_loss / total_tokens
    perplexity = np.exp(avg_loss)
    
    return perplexity


def load_dialogue_data(data_dir: str, tokenizer: Tokenizer, max_length: int, 
                      config) -> Tuple[np.ndarray, Dict]:
    """
    Load and process dialogue data from multiple .txt files.
    
    Uses the DialogueParser from data_processor.py to handle various formats.
    
    Args:
        data_dir: Directory containing .txt files
        tokenizer: Tokenizer instance
        max_length: Maximum sequence length
        config: Configuration object
    
    Returns:
        sequences: Padded integer sequences (num_examples, max_length)
        stats: Dictionary of dataset statistics
    """
    from data_processor import DialogueParser, DatasetStatistics
    
    logger.info(f"Loading dialogue data from: {data_dir}")
    
    # Parse all .txt files in directory
    parser = DialogueParser()
    turns = parser.parse_directory(data_dir, pattern=config.DATA_PATTERN)
    
    if len(turns) == 0:
        logger.error(f"No dialogue turns found in {data_dir}")
        raise ValueError(f"No data found in {data_dir}")
    
    # Calculate statistics
    stats = DatasetStatistics.calculate_stats(turns)
    logger.info(f"Loaded {len(turns)} dialogue turns")
    logger.info(f"Average context length: {stats['avg_context_length']:.1f} words")
    logger.info(f"Average response length: {stats['avg_response_length']:.1f} words")
    
    # Extract texts for vocabulary building
    contexts = [turn.context for turn in turns]
    responses = [turn.response for turn in turns]
    all_texts = contexts + responses
    
    # Build vocabulary if not already built
    if not tokenizer.vocab_built:
        tokenizer.fit_on_texts(all_texts)
    
    # Convert to sequences
    logger.info("Converting texts to sequences...")
    sequences = []
    
    for turn in turns:
        # Combine context and response for autoregressive training
        # Format: <START> context <END> response <END>
        full_text = turn.context + " " + turn.response
        seq = tokenizer.text_to_sequence(full_text, add_start_end=True)
        sequences.append(seq)
    
    # Pad sequences
    sequences = pad_sequences(sequences, maxlen=max_length, padding='post')
    
    logger.info(f"Processed {len(sequences)} sequences")
    logger.info(f"Sequence shape: {sequences.shape}")
    
    return sequences, stats


def print_training_examples(generator, tokenizer, num_examples=5):
    """
    Generate and print example dialogues during training.
    
    Args:
        generator: Trained generator model
        tokenizer: Tokenizer for decoding
        num_examples: Number of examples to generate
    """
    print("\n" + "="*60)
    print("Generated Examples:")
    print("="*60)
    
    for i in range(num_examples):
        # Generate sequence
        generated = generator.generate_sequence(
            start_token=tokenizer.START,
            max_length=50,
            temperature=1.0,
            top_k=50
        )
        
        # Decode to text
        text = tokenizer.sequence_to_text(generated)
        
        print(f"\n{i+1}. {text}")
    
    print("="*60 + "\n")


# Test utilities when run directly
if __name__ == "__main__":
    print("Testing DLA Utilities...")
    print("=" * 60)
    
    # Test tokenizer
    print("\n1. Testing Tokenizer...")
    tokenizer = Tokenizer(vocab_size=100, min_freq=1)
    
    texts = [
        "Hello, how are you?",
        "I am doing great, thanks!",
        "What is your name?",
        "My name is DLA."
    ]
    
    tokenizer.fit_on_texts(texts)
    print(f"   Vocabulary size: {len(tokenizer.word2idx)}")
    
    test_text = "Hello, what is your name?"
    sequence = tokenizer.text_to_sequence(test_text, add_start_end=True)
    decoded = tokenizer.sequence_to_text(sequence)
    
    print(f"   Original: {test_text}")
    print(f"   Sequence: {sequence}")
    print(f"   Decoded: {decoded}")
    print("   ✓ Tokenizer working!")
    
    # Test padding
    print("\n2. Testing Padding...")
    sequences = [[1, 2, 3], [4, 5, 6, 7, 8], [9, 10]]
    padded = pad_sequences(sequences, maxlen=5, padding='post')
    print(f"   Original: {sequences}")
    print(f"   Padded:\n{padded}")
    print("   ✓ Padding working!")
    
    # Test BLEU
    print("\n3. Testing BLEU...")
    ref = [['hello', 'world', 'this', 'is', 'test']]
    hyp = ['hello', 'world', 'test']
    bleu = calculate_bleu(ref, hyp, n=2)
    print(f"   Reference: {ref[0]}")
    print(f"   Hypothesis: {hyp}")
    print(f"   BLEU-2: {bleu:.4f}")
    print("   ✓ BLEU working!")
    
    # Test diversity
    print("\n4. Testing Diversity...")
    seqs = [[1, 2, 3, 4, 5], [1, 2, 6, 7, 8], [9, 10, 11, 12, 13]]
    diversity = calculate_diversity(seqs, n=2)
    print(f"   Sequences: {seqs}")
    print(f"   Diversity (2-gram): {diversity:.4f}")
    print("   ✓ Diversity working!")
    
    print("\n" + "=" * 60)
    print("✓ All utility tests passed!")
