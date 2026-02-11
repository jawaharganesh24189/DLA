# DLA - Deep Learning Academy

## Overview
This repository contains notebooks and code for building language models, specifically focused on dialogue generation and sequence-to-sequence learning.

## Notebooks

### 1. DLA_Dialogue_Model_Rebuild.ipynb ⭐ NEW
A comprehensive notebook that demonstrates building a dialogue language model using the DLA sample code.

**Features:**
- Uses the DLA DialogueParser (`src/data_processor.py`) for data preprocessing
- Implements Transformer-based sequence-to-sequence architecture
- Supports multiple dialogue formats
- Includes training and inference examples

**See:** [NOTEBOOK_USAGE.md](NOTEBOOK_USAGE.md) for detailed usage instructions.

### 2. 8B_Building our Third Language Model (1).ipynb
Translation model using sequence-to-sequence architecture (English to Spanish).

### 3. 9_Building_Our_LLM.ipynb
Large Language Model building notebook.

### 4. Copy_of_8E_Adversarial_Dialogue_GAN.ipynb
GAN-based adversarial dialogue generation system.

## DLA Sample Code

### src/data_processor.py
Multi-format dialogue parser with the following capabilities:
- **DialogueParser**: Parse context-response and speaker-labeled dialogues
- **DatasetStatistics**: Calculate dataset metrics
- **Format Conversion**: Export to JSONL, CSV, or conversational format

**Example Usage:**
```python
from src.data_processor import DialogueParser, DatasetStatistics

# Parse dialogue files
parser = DialogueParser()
dialogue_turns = parser.parse_directory('/path/to/dialogues', pattern='*.txt')

# Calculate statistics
stats = DatasetStatistics.calculate_stats(dialogue_turns)

# Convert to training format
jsonl_output = parser.to_training_format(dialogue_turns, 'jsonl')
```

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install tensorflow numpy keras jupyter`
3. Open notebooks in Jupyter or Google Colab
4. See [NOTEBOOK_USAGE.md](NOTEBOOK_USAGE.md) for detailed instructions

## Project Structure
```
DLA/
├── src/
│   └── data_processor.py          # DLA sample code for dialogue processing
├── DLA_Dialogue_Model_Rebuild.ipynb  # NEW: Dialogue model with DLA code
├── 8B_Building our Third Language Model (1).ipynb
├── 9_Building_Our_LLM.ipynb
├── Copy_of_8E_Adversarial_Dialogue_GAN.ipynb
├── NOTEBOOK_USAGE.md              # Detailed usage guide
└── README.md                      # This file
```

## License
Deep Learning Academy - 2024