# Quick Start: Using Your Own Dataset

## What's New?

The notebook now supports **flexible formats** and **multiple files**!

✅ **Multiple .txt files** in a folder  
✅ **Messy formats** with context lines  
✅ **Smart character detection**  
✅ **No strict formatting required**

## Files

- **`8E_Adversarial_Dialogue_GAN.ipynb`** - Main notebook (now with flexible parsing)
- **`sample_dialogues.txt`** - Sample data with clean format
- **`messy_dataset/`** - Example messy format with multiple files (NEW!)
- **`DATASET_README.md`** - Comprehensive dataset guide

## How to Use Your Dataset

### Step 1: Prepare Your Data

You have flexibility now! Your data can be:

**Option A: Clean format**
```
[SCENE: Your Scene]
Character: Dialogue
```

**Option B: Simple format (no scenes)**
```
Character: Dialogue
AnotherChar: Response
```

**Option C: Messy format (NEW!)**
```
Context about what's happening
Character: Dialogue
More context
AnotherChar: Response
```

**Option D: Multiple files (NEW!)**
Just put multiple .txt files in a folder!

### Step 2: Configure the Notebook

Open `8E_Adversarial_Dialogue_GAN.ipynb` and find the **Configuration cell**:

**For a single file:**
```python
USE_SAMPLE_DATA = False
DATA_PATH = '/path/to/your/dataset.txt'
```

**For multiple files in a folder (NEW!):**
```python
USE_SAMPLE_DATA = False
DATA_PATH = '/path/to/your/dataset/folder/'
```

**To test messy format (NEW!):**
```python
USE_MESSY_EXAMPLE = True
# Uses included messy_dataset/ folder
```

### Step 3: Run the Notebook

Execute all cells! The notebook will:
1. Load your dataset (file or folder with multiple files)
2. **Smart detection** of characters (automatically filtered)
3. **Flexible parsing** handles context lines and messy formats
4. Extract unique characters and scenes automatically
5. Train the GAN on your dialogue style
6. Create an autocomplete tool for your specific characters

## New Features

### Smart Character Detection
- Automatically finds `Character: dialogue` patterns
- Filters out false positives (like "Note:", "Context:")
- Requires characters to appear at least 2 times (configurable)

### Context Line Handling
Lines without `:` are treated as context and can enrich scene descriptions:
```
Meeting in progress
John: We need to act fast.
Sarah: I agree completely.
```
→ Scene becomes: "Unknown (Meeting in progress)"

### Multiple File Support
Process entire folders at once:
```
dataset/
  ├── conversation1.txt  → 10 dialogues
  ├── conversation2.txt  → 15 dialogues
  └── conversation3.txt  → 8 dialogues
Total: 33 dialogues automatically combined!
```

## Examples

### Movie Scripts
```
[SCENE: Opening]
Hero: We need to save the city!
Sidekick: I'm with you!
```

### Customer Service
```
[SCENE: Technical Support]
Agent: How can I help?
Customer: My device is broken.
```

### Any Dialogue!
The format is flexible - just follow the pattern:
- `[SCENE: description]` for scenes
- `Character: dialogue` for lines

## Need Help?

See `DATASET_README.md` for:
- Detailed format specifications
- Multiple examples
- Troubleshooting tips
- Advanced configuration

## What's the Same?

All the GAN features still work:
- ✅ Generator & Discriminator architecture
- ✅ Policy gradient training
- ✅ Interactive autocomplete tool
- ✅ Character and scene conditioning
- ✅ Evaluation metrics and visualizations

The only difference: it works with **your** data now!
