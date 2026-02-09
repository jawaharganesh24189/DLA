# DLA - Dialogue Learning Algorithm

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13%2B-orange)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A high-performance adversarial dialogue generation system using SeqGAN architecture with LSTM-based Generator and CNN-based Discriminator. Supports training on multiple .txt files with various dialogue formats.

## 🚀 Features

- **Multi-file Support**: Train on multiple .txt files with flexible dialogue formats
- **Fast Training**: Optimized TensorFlow implementation with GPU support
- **Quality Generation**: Adversarial training for natural, diverse dialogues
- **Modular Architecture**: Clean separation of concerns with well-documented code
- **Interactive Mode**: Real-time dialogue generation with adjustable parameters
- **Flexible Formats**: Handles context-response pairs and speaker-based dialogues

## 📁 Project Structure

```
DLA/
├── src/
│   ├── config.py           # Configuration and hyperparameters
│   ├── model.py            # Generator and Discriminator architectures
│   ├── utils.py            # Helper functions and metrics
│   ├── train.py            # Main training script
│   ├── generate.py         # Inference and dialogue generation
│   └── data_processor.py   # Multi-file dialogue parser
├── data/                   # Place your .txt dialogue files here
├── outputs/
│   ├── models/            # Saved model checkpoints
│   └── logs/              # Training logs
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) NVIDIA GPU with CUDA for faster training

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/jawaharganesh24189/DLA.git
cd DLA
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Prepare your data**

Place your dialogue .txt files in the `data/` directory. The system supports two formats:

**Format 1: Context-Response Pairs**
```
context: How are you doing today?
response: I'm doing great, thanks for asking!

context: What's your favorite color?
response: I really like blue, it's so calming.
```

**Format 2: Speaker Dialogue**
```
Alice: Hello, how are you?
Bob: I'm good, thanks! How about you?
Alice: Doing well, just working on a project.
```

## 🎯 Quick Start

### Training the Model

Run the training script with default configuration:

```bash
python src/train.py
```

The training pipeline includes:
1. **Data Loading**: Parses all .txt files from `data/` directory
2. **Model Building**: Constructs Generator and Discriminator
3. **Pre-training**: MLE training for Generator (10 epochs) and Discriminator (5 epochs)
4. **Adversarial Training**: Policy gradient training (30 epochs)
5. **Checkpointing**: Saves models every 5 epochs

**Expected training time**: 30-60 minutes on GPU for 1000 dialogue turns

### Generating Dialogues

**Interactive Mode** (recommended):
```bash
python src/generate.py --checkpoint checkpoint_epoch_final --interactive
```

**Single Prompt**:
```bash
python src/generate.py --prompt "Hello, how are you?" --temperature 1.0
```

**Random Generation**:
```bash
python src/generate.py --num_samples 10
```

## ⚙️ Configuration

Edit `src/config.py` to customize training:

```python
# Data Configuration
DATA_DIR = "data"                    # Directory with .txt files
MAX_SEQUENCE_LENGTH = 50             # Maximum words per dialogue
VOCAB_SIZE = 10000                   # Vocabulary size

# Model Architecture
EMBEDDING_DIM = 128                  # Word embedding size
HIDDEN_DIM = 256                     # LSTM hidden size
GENERATOR_LSTM_LAYERS = 2            # Number of LSTM layers

# Training Configuration
BATCH_SIZE = 64                      # Training batch size
GENERATOR_PRETRAIN_EPOCHS = 10       # Generator pre-training epochs
ADVERSARIAL_EPOCHS = 30              # Adversarial training epochs
GENERATOR_LR_PRETRAIN = 0.001        # Learning rate (pre-training)
GENERATOR_LR_ADVERSARIAL = 0.0001    # Learning rate (adversarial)

# Generation Configuration
TEMPERATURE = 1.0                    # Sampling temperature (0.5-1.5)
TOP_K = 50                          # Top-k sampling
```

## 📊 Model Architecture

### Generator (LSTM-based)
- **Input**: Word sequence (context)
- **Embedding Layer**: Converts words to dense vectors (128-dim)
- **LSTM Layers**: 2 stacked LSTM layers (256 hidden units each)
- **Output Layer**: Softmax over vocabulary
- **Training**: Maximum Likelihood (pre-training) + Policy Gradient (adversarial)

### Discriminator (CNN-based)
- **Input**: Word sequence (real or generated)
- **Embedding Layer**: Shared embedding space
- **Multi-kernel CNN**: Parallel convolutions with kernel sizes [3, 4, 5]
- **Pooling**: Global max pooling per kernel
- **Output**: Binary classification (real vs fake)

## 📈 Training Process

### Phase 1: Generator Pre-training (MLE)
- Train with teacher forcing
- Minimize cross-entropy loss
- Learn basic language patterns

### Phase 2: Discriminator Pre-training
- Train to distinguish real vs generated dialogues
- Binary classification task
- Provides learning signal for adversarial training

### Phase 3: Adversarial Training
- Generator: Maximize Discriminator reward (policy gradient)
- Discriminator: Maintain ability to detect fake dialogues
- Alternating updates with G_STEPS and D_STEPS

## 🎨 Generation Examples

```python
# Import generator
from src.generate import DialogueGenerator

# Load trained model
generator = DialogueGenerator('outputs/models/checkpoint_epoch_final')

# Generate response
response = generator.generate_response(
    context="What's your favorite hobby?",
    temperature=1.0,
    top_k=50
)
print(response)
# Output: "I really enjoy reading science fiction books and playing guitar."

# Interactive autocomplete
completions = generator.autocomplete("I think that", num_completions=3)
```

## 🔧 Advanced Usage

### Custom Data Format

If your dialogues have a unique format, extend the `DialogueParser` in `src/data_processor.py`:

```python
def _parse_custom_format(self, content: str) -> List[DialogueTurn]:
    # Your custom parsing logic
    pass
```

### Hyperparameter Tuning

Key parameters to tune for better results:

- **Learning Rate**: Lower (0.0001) for stable training, higher (0.001) for faster convergence
- **Temperature**: Lower (0.7) for coherent text, higher (1.3) for creative text
- **Batch Size**: Larger (128) for faster training, smaller (32) for better generalization
- **LSTM Layers**: More (3-4) for complex patterns, fewer (1-2) for simpler datasets

### Mixed Precision Training

For faster training on modern GPUs, enable mixed precision in `src/config.py`:

```python
USE_MIXED_PRECISION = True
```

## 📝 Evaluation Metrics

The system tracks:

- **Loss**: Generator and Discriminator losses
- **Accuracy**: Discriminator classification accuracy
- **Diversity**: Unique n-gram ratio (measures repetitiveness)
- **BLEU Score**: N-gram overlap with reference dialogues
- **Perplexity**: Model confidence (lower is better)

## 🐛 Troubleshooting

**Issue**: `No data found in data/`
- **Solution**: Add .txt files to the `data/` directory

**Issue**: `Out of memory error`
- **Solution**: Reduce `BATCH_SIZE` or `MAX_SEQUENCE_LENGTH` in config.py

**Issue**: `Checkpoint not found`
- **Solution**: Train the model first with `python src/train.py`

**Issue**: `Generator produces repetitive text`
- **Solution**: Increase `ADVERSARIAL_EPOCHS` or adjust `TEMPERATURE` during generation

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- SeqGAN paper: [SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient](https://arxiv.org/abs/1609.05473)
- Kim's CNN for text classification: [Convolutional Neural Networks for Sentence Classification](https://arxiv.org/abs/1408.5882)
- TensorFlow team for the excellent deep learning framework

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ for natural language generation**