# Quick Start: Using Your Own Dataset

## What Changed?

The notebook is now **completely dataset-agnostic**! You can use any dialogue dataset, not just Attack on Titan.

## Files

- **`8E_Adversarial_Dialogue_GAN.ipynb`** - Main notebook (now generic)
- **`sample_dialogues.txt`** - Sample data with generic characters
- **`DATASET_README.md`** - Comprehensive dataset guide

## How to Use Your Dataset

### Step 1: Prepare Your Data

Format your dialogue data as:

```
[SCENE: Your Scene Type]
CharacterA: What they say
CharacterB: Their response

[SCENE: Another Scene]
CharacterA: More dialogue
CharacterC: Different character
```

### Step 2: Configure the Notebook

Open `8E_Adversarial_Dialogue_GAN.ipynb` and find the **Configuration cell** (Section 0):

```python
# Option 1: Use your own dataset
USE_SAMPLE_DATA = False
DATA_PATH = '/path/to/your/dataset.txt'

# Option 2: Use sample data (for testing)
USE_SAMPLE_DATA = True  # This will use sample_dialogues.txt
```

### Step 3: Run the Notebook

Execute all cells! The notebook will:
1. Load your dataset
2. Extract unique characters and scenes automatically
3. Train the GAN on your dialogue style
4. Create an autocomplete tool for your specific characters

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
