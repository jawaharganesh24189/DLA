# DLA - Deep Learning Applications

## Overview
This repository contains Jupyter notebooks for various deep learning applications, focusing on natural language processing and language modeling.

## Notebooks

### 8D - Attack on Titan Language Model
**File**: `8D_AoT_Language_Model.ipynb`

A complete implementation of a character-level language model trained on Attack on Titan Season 1 scripts. This notebook demonstrates:

- **Data Loading & Preprocessing**: Loading and parsing the AoTS1.txt script dataset
- **Character-Level Tokenization**: Creating vocabulary and character mappings
- **LSTM Architecture**: Multi-layer LSTM model with embeddings and dropout
- **Training**: Using callbacks (EarlyStopping, ModelCheckpoint) and monitoring validation metrics
- **Text Generation**: Temperature-based sampling for creative text generation
- **Model Persistence**: Saving and loading models to/from Google Drive

#### Key Features:
- ✅ LSTM-based language model with 2 layers
- ✅ Character-level tokenization (100-character sequences)
- ✅ Temperature-controlled text generation
- ✅ Training visualization (loss and accuracy plots)
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
- LSTM Layer 1 (512 units, dropout=0.3)
- LSTM Layer 2 (512 units, dropout=0.3)
- Dense Output Layer (softmax)
```

#### Training Configuration:
- Epochs: 30 (with early stopping)
- Batch size: 128
- Train/Val split: 90/10
- Optimizer: Adam
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

## License
Educational purposes only. Attack on Titan content is property of Hajime Isayama and respective copyright holders.

## Author
DLA Notebooks - Deep Learning Applications