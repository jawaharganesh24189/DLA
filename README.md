# DLA - Deep Learning Applications

## Overview
This repository contains Jupyter notebooks for various deep learning applications, focusing on natural language processing and language modeling.

## Notebooks

### 8D - Attack on Titan Language Model
**File**: `8D_AoT_Language_Model.ipynb`

A complete implementation of a character-level language model trained on Attack on Titan Season 1 scripts with **enhanced preprocessing for improved accuracy**. This notebook demonstrates:

- **Advanced Text Preprocessing**: Stop word removal, whitespace normalization, and context optimization
- **Data Loading & Parsing**: Loading and cleaning the AoTS1.txt script dataset
- **Character-Level Tokenization**: Creating vocabulary and character mappings
- **Deep LSTM Architecture**: 3-layer LSTM model with batch normalization and recurrent dropout
- **Optimized Training**: Enhanced callbacks and training parameters for better convergence
- **Text Generation**: Temperature-based sampling for creative text generation
- **Model Persistence**: Saving and loading models to/from Google Drive

#### Key Features:
- ✅ **Enhanced preprocessing** - removes stop words, normalizes whitespace (18.7% text reduction)
- ✅ **Deep LSTM architecture** - 3 LSTM layers + dense layer for better learning
- ✅ **Batch Normalization** - for training stability
- ✅ **Recurrent Dropout** (0.2) - prevents overfitting
- ✅ Character-level tokenization (80-character sequences, optimized for context)
- ✅ Temperature-controlled text generation
- ✅ Training visualization (loss and accuracy plots)
- ✅ **Optimized training** - 50 epochs, batch size 64
- ✅ Google Colab compatible with GPU support (T4)
- ✅ Model and vocabulary persistence
- ✅ Interactive text generation examples

#### Dataset:
**File**: `AoTS1.txt`
- Contains dialogue and narration from Attack on Titan Season 1
- 8,129 characters across 375 lines
- 161 dialogue lines from various characters
- 72 unique characters in vocabulary

#### Requirements:
```python
tensorflow >= 2.0
numpy
matplotlib
```

#### Usage:
1. Open the notebook in Google Colab
2. Enable GPU acceleration (Runtime > Change runtime type > T4 GPU)
3. Upload or ensure AoTS1.txt is available
4. Run all cells in sequence
5. Experiment with text generation using different seeds and temperatures

#### Model Architecture:
```
- Embedding Layer (256 dimensions)
- LSTM Layer 1 (512 units, dropout=0.3, recurrent_dropout=0.2)
- Batch Normalization
- LSTM Layer 2 (512 units, dropout=0.3, recurrent_dropout=0.2)
- Batch Normalization
- LSTM Layer 3 (256 units, dropout=0.3)
- Dense Hidden Layer (256 units, ReLU activation)
- Dropout (0.3)
- Dense Output Layer (softmax)
```

#### Preprocessing Pipeline:
The model includes advanced preprocessing for better accuracy:
1. **Stop Word Removal**: Removes common words (the, a, an, is, was, etc.) that don't add context
2. **Whitespace Normalization**: Removes extra spaces, tabs, and unnecessary newlines
3. **Punctuation Preservation**: Keeps important dialogue punctuation (: ! ? .)
4. **Vocabulary Optimization**: Focuses on meaningful content, reducing training data by 18.7%

#### Training Configuration:
- Epochs: 50 (increased for better convergence)
- Batch size: 64 (optimized for better gradient updates)
- Train/Val split: 90/10
- Sequence length: 80 characters (optimized context window)
- Optimizer: Adam (learning_rate=0.001)
- Loss: Sparse categorical crossentropy

#### Saved Models:
Models are saved to Google Drive at:
- Model: `/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/aot_language_model.keras`
- Vocabulary: `/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/aot_vocab.json`
- Training history: `/content/drive/MyDrive/DLA_Notebooks_Data_PGPM/aot_training_history.json`

## Getting Started

### For Google Colab:
1. Upload the notebook to Google Colab
2. Upload `AoTS1.txt` when prompted or place it in your Colab workspace
3. Run all cells sequentially
4. Mount Google Drive when prompted to save models

### Local Setup:
```bash
# Install dependencies
pip install tensorflow numpy matplotlib

# Run Jupyter
jupyter notebook 8D_AoT_Language_Model.ipynb
```

## Repository Structure
```
DLA/
├── README.md
├── 8D_AoT_Language_Model.ipynb    # Main notebook
└── AoTS1.txt                       # Attack on Titan Season 1 script dataset
```

## Future Enhancements
- Word-level tokenization option
- Transformer-based architecture
- Character-specific fine-tuning
- Beam search for generation
- Interactive web interface

## Recent Improvements (v2.0)
✨ **Enhanced for Better Accuracy:**
- Added intelligent preprocessing with stop word removal
- Increased model depth to 3 LSTM layers
- Added Batch Normalization for training stability
- Added recurrent dropout to prevent overfitting
- Optimized sequence length (100 → 80) for better context
- Increased training epochs (30 → 50) for better convergence
- Reduced batch size (128 → 64) for better gradient updates
- Added dense hidden layer for better feature extraction
- **Result**: Cleaner training data, deeper architecture, better accuracy!

## License
Educational purposes only. Attack on Titan content is property of Hajime Isayama and respective copyright holders.

## Author
DLA Notebooks - Deep Learning Applications