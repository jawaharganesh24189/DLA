# DLA Training Notebook

## 📓 Overview

**DLA_Training_Notebook.ipynb** is a comprehensive, self-contained Jupyter notebook for training a dialogue generation model using Generative Adversarial Networks (GANs).

## ✨ Key Features

- **🔋 Self-Contained**: No external Python files needed - all code is in the notebook
- **📁 Multi-File Support**: Automatically loads and trains on multiple .txt dialogue files from `data/` directory
- **⚡ Fast Training**: Optimized with `@tf.function` decorators for maximum speed
- **📝 Well-Commented**: Clear explanations and documentation throughout
- **🎯 Production-Ready**: Complete training pipeline from data loading to model generation

## 🏗️ Architecture

### Generator (LSTM-based)
- 2-layer LSTM with 256 hidden units
- 128-dimensional word embeddings
- Autoregressive sequence generation

### Discriminator (CNN-based)
- Multi-kernel CNN (3-gram, 4-gram, 5-gram patterns)
- 128 filters per kernel size
- Binary classification (real/fake dialogues)

## 📋 Notebook Structure

1. **Setup & Imports** - All necessary dependencies
2. **Configuration** - Centralized hyperparameters for easy tuning
3. **Data Loading & Processing** - Multi-file .txt parser and tokenizer
4. **Model Architecture** - Generator and Discriminator classes
5. **Training Functions** - Pre-training and adversarial training
6. **Evaluation & Metrics** - BLEU, diversity, perplexity
7. **Main Training Loop** - Complete training pipeline
8. **Generation & Testing** - Generate and test dialogues

## 🚀 Quick Start

### 1. Prepare Your Data

Add dialogue .txt files to the `data/` directory in one of these formats:

**Format 1: Context-Response pairs**
```
context: Hello, how are you?
response: I'm doing great, thanks for asking!

context: What's your favorite color?
response: I really like blue.
```

**Format 2: Speaker dialogues**
```
Alice: Hello, how are you?
Bob: I'm doing great, thanks!
Alice: That's wonderful to hear.
```

### 2. Open and Run the Notebook

```bash
jupyter notebook DLA_Training_Notebook.ipynb
```

### 3. Execute All Cells

Simply run all cells in order. The notebook will:
- ✅ Load all .txt files from `data/` directory
- ✅ Build vocabulary and preprocess text
- ✅ Pre-train Generator (5 epochs, ~2-3 min)
- ✅ Pre-train Discriminator (3 epochs, ~1-2 min)
- ✅ Perform adversarial training (5 epochs, ~3-4 min)
- ✅ Generate sample dialogues
- ✅ Save trained models to `outputs/models/`

**Total training time: ~6-9 minutes** (with default settings)

## ⚙️ Configuration

All hyperparameters are centralized in the `Config` class:

```python
class Config:
    # Data
    DATA_DIR = "data"
    MAX_SEQUENCE_LENGTH = 50
    VOCAB_SIZE = 10000
    
    # Model
    EMBEDDING_DIM = 128
    HIDDEN_DIM = 256
    GENERATOR_LSTM_LAYERS = 2
    
    # Training (optimized for speed)
    BATCH_SIZE = 64
    GENERATOR_PRETRAIN_EPOCHS = 5      # Fast pre-training
    DISCRIMINATOR_PRETRAIN_EPOCHS = 3  # Fast pre-training
    ADVERSARIAL_EPOCHS = 5             # Fast adversarial training
```

### For Longer/Better Training

Increase epochs for better results (will take longer):

```python
GENERATOR_PRETRAIN_EPOCHS = 10-20
DISCRIMINATOR_PRETRAIN_EPOCHS = 5-10
ADVERSARIAL_EPOCHS = 10-30
```

## 📊 Training Output

The notebook displays:
- ✅ Training progress with loss/accuracy metrics
- ✅ Generated example dialogues during training
- ✅ Diversity scores (measures generation variety)
- ✅ Final evaluation metrics

Example output:
```
Epoch 5/5 - G_Loss: 2.3451 - D_Loss: 0.4523 - D_Acc: 0.7845 - Time: 45.2s

Generated Examples:
==========================================================
1. hello how are you doing today ?
2. i love reading books and learning new things .
3. what is your favorite type of music ?
==========================================================

Diversity (2-gram): 0.8234
```

## 💬 Generation

After training, generate dialogues with different creativity levels:

```python
# Conservative generation (temperature=0.7)
generate_dialogues(generator, tokenizer, num_samples=5, temperature=0.7)

# Balanced generation (temperature=1.0)
generate_dialogues(generator, tokenizer, num_samples=5, temperature=1.0)

# Creative generation (temperature=1.3)
generate_dialogues(generator, tokenizer, num_samples=5, temperature=1.3)
```

### Interactive Mode

Try interactive dialogue generation:

```python
interactive_generation(generator, tokenizer)
```

Then type prompts and get responses!

## 📦 Output Files

After training, models are saved to:

```
outputs/
└── models/
    └── checkpoint_final/
        ├── generator.weights.h5      # Trained generator weights
        ├── discriminator.weights.h5  # Trained discriminator weights
        └── tokenizer.pkl              # Vocabulary and tokenizer
```

## 🔧 Requirements

```
tensorflow>=2.0
numpy
```

Install with:
```bash
pip install tensorflow numpy
```

## 📈 Performance Tips

1. **GPU Acceleration**: Automatically uses GPU if available for 3-5x speedup
2. **Batch Size**: Increase `BATCH_SIZE` if you have more memory (64 → 128)
3. **Sequence Length**: Reduce `MAX_SEQUENCE_LENGTH` for faster training (50 → 30)
4. **Data Size**: More training data = better results

## 🎯 Use Cases

- **Chatbot Training**: Train conversational AI models
- **Dialogue Systems**: Build context-aware response generators
- **Text Generation**: Generate creative dialogue text
- **Research**: Experiment with GAN-based text generation

## 🐛 Troubleshooting

### No training data found
```
⚠️ ERROR: No dialogue data found in data/
```
**Solution**: Add .txt dialogue files to the `data/` directory

### Out of memory
```
ResourceExhaustedError: OOM when allocating tensor
```
**Solution**: Reduce `BATCH_SIZE` or `MAX_SEQUENCE_LENGTH`

### Poor generation quality
**Solution**: 
- Increase training epochs
- Add more training data
- Adjust temperature (0.7-1.3 range)

## 📚 Additional Resources

- **Original Source Code**: See `src/` directory for modular implementation
- **Sample Data**: Check `data/` directory for example dialogue files
- **Training Script**: `src/train.py` for command-line training

## 🤝 Contributing

To improve the notebook:
1. Add more training data to `data/`
2. Experiment with hyperparameters in `Config` class
3. Try different generation strategies (temperature, top-k)

## 📝 License

This notebook is part of the DLA (Dialogue Learning Algorithm) project.

## 🎉 Happy Training!

For questions or issues, refer to the main README.md or check the inline documentation in the notebook.
