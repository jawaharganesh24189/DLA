# 🚀 Quick Start Guide - DLA Training Notebook

## 3-Minute Setup

### 1. Prepare Data
```bash
# Add your dialogue .txt files to the data/ directory
# The notebook will automatically load all .txt files
```

**Supported formats:**

**Option A: Context-Response**
```
context: Hello, how are you?
response: I'm doing great, thanks!

context: What's your favorite color?
response: I love blue!
```

**Option B: Speaker Dialogue**
```
Alice: Hello, how are you?
Bob: I'm doing great, thanks!
Alice: That's wonderful!
```

### 2. Open Notebook
```bash
jupyter notebook DLA_Training_Notebook.ipynb
```

### 3. Run All Cells
- Click "Cell" → "Run All" in Jupyter
- Or press `Shift+Enter` on each cell

**That's it!** Training will start automatically.

## 📊 What to Expect

### Training Timeline (Default Settings)
```
[0:00 - 0:30]   Loading data & building vocabulary
[0:30 - 3:00]   Generator pre-training (5 epochs)
[3:00 - 4:30]   Discriminator pre-training (3 epochs)
[4:30 - 9:00]   Adversarial training (5 epochs)
[9:00 - 9:30]   Saving models & final evaluation

Total: ~6-9 minutes
```

### Training Output
```
STEP 3: Pre-training Generator (MLE)
Epoch 1/5 - Loss: 4.5234 - Time: 32.1s
Epoch 2/5 - Loss: 3.8765 - Time: 31.8s
...

Generated Examples:
1. hello how are you doing today ?
2. i love reading books and learning new things .
```

## 🎨 Generation Examples

### After Training
```python
# Conservative generation (more coherent)
generate_dialogues(generator, tokenizer, num_samples=5, temperature=0.7)

# Balanced generation
generate_dialogues(generator, tokenizer, num_samples=5, temperature=1.0)

# Creative generation (more diverse)
generate_dialogues(generator, tokenizer, num_samples=5, temperature=1.3)
```

### Interactive Mode
```python
interactive_generation(generator, tokenizer)
# Then type prompts:
# You: hello
# DLA: hi there ! how can i help you today ?
```

## ⚙️ Quick Tweaks

### Want Faster Training?
```python
# In the Config cell, change:
GENERATOR_PRETRAIN_EPOCHS = 3      # Instead of 5
DISCRIMINATOR_PRETRAIN_EPOCHS = 2  # Instead of 3
ADVERSARIAL_EPOCHS = 3             # Instead of 5
# New total time: ~3-5 minutes
```

### Want Better Quality?
```python
# In the Config cell, change:
GENERATOR_PRETRAIN_EPOCHS = 10     # Instead of 5
DISCRIMINATOR_PRETRAIN_EPOCHS = 5  # Instead of 3
ADVERSARIAL_EPOCHS = 20            # Instead of 5
# New total time: ~20-30 minutes
```

### Out of Memory?
```python
# In the Config cell, change:
BATCH_SIZE = 32                    # Instead of 64
MAX_SEQUENCE_LENGTH = 30           # Instead of 50
```

## 📁 Output Files

After training, find your models here:
```
outputs/models/checkpoint_final/
├── generator.weights.h5       ← Load this to generate text
├── discriminator.weights.h5   ← For continued training
└── tokenizer.pkl               ← Vocabulary mapping
```

## 🔧 Troubleshooting

### Problem: "No dialogue data found"
**Solution:** Add .txt files to `data/` directory

### Problem: Training is slow
**Solution:** 
1. Reduce `BATCH_SIZE` or epochs
2. Check GPU is being used: Look for "GPU Available: True"

### Problem: Generated text is nonsensical
**Solution:**
1. Add more training data
2. Increase training epochs
3. Adjust temperature (try 0.7-1.0)

## 📖 Full Documentation

For detailed information, see:
- `NOTEBOOK_README.md` - Complete guide
- The notebook itself - Extensive inline comments
- `src/` directory - Original modular implementation

## 🎯 Next Steps

1. ✅ Run the notebook with sample data
2. 📁 Add your own dialogue data
3. 🎨 Experiment with generation parameters
4. ⚙️ Tune hyperparameters for your use case
5. 🚀 Deploy your trained model

## 💡 Pro Tips

1. **More Data = Better Results**: Try to have at least 500-1000 dialogue turns
2. **GPU Speeds Up**: Training is 3-5x faster with GPU
3. **Temperature Matters**: 0.7 = safe, 1.0 = balanced, 1.3 = creative
4. **Save Checkpoints**: Models are auto-saved after training
5. **Monitor Diversity**: Higher diversity score = more varied generation

## 🎉 You're Ready!

Open `DLA_Training_Notebook.ipynb` and start training your dialogue model!

Have questions? Check the inline documentation in the notebook cells.
