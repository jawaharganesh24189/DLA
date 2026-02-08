# DLA - Deep Learning Academy

## Adversarial Dialogue GAN Notebook

This repository contains a production-quality Jupyter notebook for training Generative Adversarial Networks (GANs) on dialogue datasets.

### 🆕 New: Flexible Format Support!

The notebook now handles **messy, real-world datasets**:
- ✅ **Multiple .txt files** in a folder
- ✅ **Mixed formats** (context lines + dialogue)
- ✅ **Smart character detection** (no manual lists needed)
- ✅ **No preprocessing required** for messy data

### Features

- **Dataset Agnostic**: Works with any dialogue dataset in various formats
- **Flexible Parsing**: Handles clean structured data OR messy unstructured data
- **Multiple Files**: Process entire folders with many .txt files
- **GAN Architecture**: Implements SeqGAN/LeakGAN concepts for text generation
- **Interactive Autocomplete**: Generate dialogue completions with character/scene conditioning
- **Comprehensive Training**: Pre-training + adversarial training with policy gradients
- **Evaluation Suite**: Perplexity, BLEU, Self-BLEU, and visualizations

### Quick Start

1. Read **`FLEXIBLE_FORMAT_GUIDE.md`** for new format support (NEW!)
2. Read **`QUICKSTART.md`** for immediate setup
3. See **`DATASET_README.md`** for dataset format details
4. Open **`8E_Adversarial_Dialogue_GAN.ipynb`** and configure your dataset path
5. Run all cells!

### Files

- **8E_Adversarial_Dialogue_GAN.ipynb** - Main GAN notebook with flexible parser
- **sample_dialogues.txt** - Sample dataset with clean format
- **messy_dataset/** - Example messy format with multiple files (NEW!)
- **FLEXIBLE_FORMAT_GUIDE.md** - Guide to new flexible parsing features (NEW!)
- **DATASET_README.md** - Comprehensive dataset guide
- **QUICKSTART.md** - Quick start guide

### Requirements

- TensorFlow/Keras 2.x
- Python 3.8+
- GPU recommended (Colab T4 or better)

For more details, see the documentation files.