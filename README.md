# DLA - Deep Learning Academy

## Overview
This repository contains notebooks and code for building advanced language models, including dialogue generation, sequence-to-sequence learning, and domain-specific applications like football tactics prediction.

## Notebooks

### 1. Football_Tactics_Model.ipynb ⭐ NEW
**AI-powered football tactics prediction using pure DLA Transformer techniques**

Demonstrates building a football tactics model using advanced architectures from DLA notebooks 8B and 9 (NO data_processor.py used).

**Key Features:**
- **Encoder-Decoder Transformer**: Game state → Tactical sequences
- **From Notebook 8B**: TransformerEncoder, TransformerDecoder, PositionalEmbedding, Causal masking
- **From Notebook 9**: Temperature sampling, Top-K sampling, Greedy decoding
- **Custom Football Vocabulary**: Positions, actions, formations, directions
- **Advanced Generation**: Multiple sampling strategies for diverse tactics
- **Context-Aware**: Cross-attention between game state and tactics

**Architecture:**
```
Game State (Formation + Ball + Status) 
    → Encoder (Self-attention)
    → Decoder (Causal + Cross-attention)
    → Tactical Sequence (Player actions)
```

**See:** [FOOTBALL_TACTICS_GUIDE.md](FOOTBALL_TACTICS_GUIDE.md) for comprehensive guide.

### 2. DLA_Dialogue_Model_Rebuild.ipynb
A comprehensive notebook that demonstrates building a dialogue language model using the DLA sample code.

**Features:**
- Uses the DLA DialogueParser (`src/data_processor.py`) for data preprocessing
- Implements Transformer-based sequence-to-sequence architecture
- Supports multiple dialogue formats
- Includes training and inference examples

**See:** [NOTEBOOK_USAGE.md](NOTEBOOK_USAGE.md) for detailed usage instructions.

### 3. 8B_Building our Third Language Model (1).ipynb
Translation model using sequence-to-sequence architecture (English to Spanish).

### 4. 9_Building_Our_LLM.ipynb
Large Language Model building notebook with advanced sampling strategies.

### 5. Copy_of_8E_Adversarial_Dialogue_GAN.ipynb
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
│   └── data_processor.py                    # DLA sample code for dialogue processing
├── Football_Tactics_Model.ipynb             # ⭐ NEW: Football tactics with Transformer
├── DLA_Dialogue_Model_Rebuild.ipynb         # Dialogue model with DLA code
├── 8B_Building our Third Language Model (1).ipynb
├── 9_Building_Our_LLM.ipynb
├── Copy_of_8E_Adversarial_Dialogue_GAN.ipynb
├── FOOTBALL_TACTICS_GUIDE.md                # ⭐ NEW: Football tactics guide
├── NOTEBOOK_USAGE.md                        # Dialogue model usage guide
└── README.md                                # This file
```

## DLA Transformer Techniques Showcase

### Encoder-Decoder Architecture (from Notebook 8B)
- **TransformerEncoder**: Self-attention for understanding input sequences
- **TransformerDecoder**: Causal self-attention + cross-attention for generation
- **PositionalEmbedding**: Maintains sequence order information
- **Demonstrated in**: Football_Tactics_Model.ipynb, DLA_Dialogue_Model_Rebuild.ipynb

### Advanced Sampling Strategies (from Notebook 9)
- **Greedy Decoding**: Deterministic, fast generation
- **Temperature Sampling**: Control diversity (low=conservative, high=creative)
- **Top-K Sampling**: Quality control by filtering unlikely tokens
- **Demonstrated in**: Football_Tactics_Model.ipynb

## License
Deep Learning Academy - 2024