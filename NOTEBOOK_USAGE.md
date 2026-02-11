# Using DLA_Dialogue_Model_Rebuild.ipynb

## Overview
This notebook demonstrates how to build a sequence-to-sequence dialogue model using the DLA (Deep Learning Academy) sample code from `src/data_processor.py`.

## Features
- ✅ Uses the DLA DialogueParser for data preprocessing
- ✅ Implements a Transformer-based seq2seq model
- ✅ Supports multiple dialogue formats (context-response, speaker-labeled)
- ✅ Includes data statistics and format conversion
- ✅ Provides dialogue generation capabilities

## Requirements
To run this notebook, you need:
- Python 3.8+
- TensorFlow 2.x
- Keras
- NumPy

## Installation
```bash
pip install tensorflow numpy keras
```

## Running the Notebook

### Option 1: Google Colab (Recommended)
1. Upload the notebook to Google Colab
2. Upload `src/data_processor.py` to the Colab environment
3. Run all cells sequentially

### Option 2: Local Jupyter
1. Install Jupyter: `pip install jupyter`
2. Launch: `jupyter notebook`
3. Open `DLA_Dialogue_Model_Rebuild.ipynb`
4. Run all cells

### Option 3: JupyterLab
1. Install JupyterLab: `pip install jupyterlab`
2. Launch: `jupyter lab`
3. Open the notebook and run

## What the Notebook Does

### 1. Data Processing (Using DLA Sample Code)
- Imports `DialogueParser` from `src/data_processor.py`
- Parses dialogue data in various formats
- Calculates dataset statistics
- Converts to training-ready format

### 2. Model Building
- Creates a Transformer-based encoder-decoder architecture
- Uses positional embeddings
- Implements multi-head attention
- Supports sequence-to-sequence learning

### 3. Training
- Trains on context-response pairs
- Validates on held-out data
- Uses sparse categorical crossentropy loss

### 4. Inference
- Generates responses given dialogue context
- Uses greedy decoding
- Can be extended to beam search

## Sample Usage

The notebook includes sample dialogue data for testing. For production use:

```python
# Load your own dialogue data
parser = DialogueParser()
dialogue_turns = parser.parse_directory(
    directory='/path/to/dialogues',
    pattern='*.txt'
)

# Calculate statistics
stats = DatasetStatistics.calculate_stats(dialogue_turns)

# Convert to training format
jsonl_data = parser.to_training_format(dialogue_turns, 'jsonl')
```

## Supported Dialogue Formats

### Format 1: Context-Response Pairs
```
context: Hello, how are you?
response: I'm doing well, thank you!

context: What brings you here?
response: I wanted to learn about AI.
```

### Format 2: Speaker-Labeled Dialogue
```
Alice: Hello, how are you?
Bob: I'm doing well, thank you!
Alice: What brings you here?
Bob: I wanted to learn about AI.
```

## Model Architecture

```
Input (Context) → Positional Embedding → Transformer Encoder
                                              ↓
Input (Response) → Positional Embedding → Transformer Decoder → Output
```

- Embedding dimension: 256
- Dense dimension: 2048
- Number of heads: 8
- Vocabulary size: 5000
- Sequence length: 20

## Next Steps

1. **Larger Dataset**: Use more dialogue data for better results
2. **Hyperparameter Tuning**: Adjust model parameters
3. **Beam Search**: Implement beam search for better generation
4. **Fine-tuning**: Fine-tune on domain-specific dialogues
5. **Evaluation**: Add BLEU, ROUGE metrics

## Troubleshooting

### Issue: Import Error for DLA Sample Code
**Solution**: Ensure `src/data_processor.py` is in the correct location:
```python
import sys
sys.path.append('./src')
from data_processor import DialogueParser
```

### Issue: Out of Memory During Training
**Solution**: Reduce batch size or model dimensions:
```python
embed_dim = 128  # Instead of 256
dense_dim = 1024  # Instead of 2048
```

### Issue: Poor Generation Quality
**Solution**: 
- Train for more epochs
- Use more training data
- Increase model capacity
- Implement beam search

## References

- DLA Sample Code: `src/data_processor.py`
- Original Notebooks: `8B_Building our Third Language Model (1).ipynb`
- Transformer Architecture: "Attention Is All You Need" (Vaswani et al.)

## License
This notebook is part of the Deep Learning Academy (DLA) project.

## Author
Deep Learning Academy - 2024
