# DLA - Deep Learning Academy

## Adversarial Dialogue GAN Notebook

This repository contains a production-quality Jupyter notebook for training Generative Adversarial Networks (GANs) on dialogue datasets.

### Features

- **Dataset Agnostic**: Works with any dialogue dataset in the specified format
- **GAN Architecture**: Implements SeqGAN/LeakGAN concepts for text generation
- **Interactive Autocomplete**: Generate dialogue completions with character/scene conditioning
- **Comprehensive Training**: Pre-training + adversarial training with policy gradients
- **Evaluation Suite**: Perplexity, BLEU, Self-BLEU, and visualizations

### Quick Start

1. Read `QUICKSTART.md` for immediate setup
2. See `DATASET_README.md` for dataset format details
3. Open `8E_Adversarial_Dialogue_GAN.ipynb` and configure your dataset path
4. Run all cells!

### Files

- **8E_Adversarial_Dialogue_GAN.ipynb** - Main GAN notebook
- **sample_dialogues.txt** - Sample dataset with generic characters
- **DATASET_README.md** - Comprehensive dataset guide
- **QUICKSTART.md** - Quick start guide

### Requirements

- TensorFlow/Keras 2.x
- Python 3.8+
- GPU recommended (Colab T4 or better)

For more details, see the documentation files.