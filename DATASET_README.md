# Dataset Configuration Guide

## Overview

The `8E_Adversarial_Dialogue_GAN.ipynb` notebook is designed to work with any dialogue dataset. This guide explains how to prepare and configure your custom dataset.

## Dataset Format

Your dataset should be a text file with dialogue formatted as:

```
[SCENE: Scene Description]
Character1: Dialogue text here
Character2: Response text here

[SCENE: Another Scene]
Character1: More dialogue
Character3: Different character speaking
```

### Format Rules

1. **Scene Headers**: Use `[SCENE: Description]` to mark scene boundaries
2. **Character Format**: Use `CharacterName: dialogue text`
3. **Blank Lines**: Separate scenes with blank lines (optional)
4. **Consistency**: Keep character names consistent throughout

## Supported Dataset Types

The notebook works with various dialogue formats:

- **Movie Scripts**: Formatted dialogue from film scripts
- **TV Show Transcripts**: Episode transcripts with character attribution
- **Play Dialogues**: Theater scripts with character lines
- **Chat Conversations**: Formatted chat logs with speaker identification
- **Customer Service**: Support conversations with agent/customer labels

## Quick Start

### Option 1: Use Sample Data (Default)

The notebook includes `sample_dialogues.txt` with generic dialogue examples. Set `USE_SAMPLE_DATA = True` in the configuration cell.

### Option 2: Use Your Own Dataset

1. Prepare your dataset file in the format above
2. Save it anywhere accessible (local path or mounted drive)
3. Update the configuration in the notebook:

```python
USE_SAMPLE_DATA = False
DATA_PATH = '/path/to/your/dialogues.txt'
```

### Option 3: Use a Dataset Folder

If you have multiple files:

```python
USE_SAMPLE_DATA = False
DATASET_FOLDER = '/path/to/your/dataset/folder/'
# The notebook will process all .txt files in the folder
```

## Example Datasets

### Example 1: Movie Dialogue

```
[SCENE: Opening Scene]
Hero: We need to stop them before it's too late!
Sidekick: I'm with you all the way.
Villain: You'll never succeed!

[SCENE: Final Battle]
Hero: This ends now!
Villain: We'll see about that.
```

### Example 2: Customer Service

```
[SCENE: Technical Support]
Agent: How can I help you today?
Customer: My device isn't working properly.
Agent: Let me check that for you.

[SCENE: Billing Inquiry]
Agent: I see you have a question about your bill.
Customer: Yes, I noticed an unexpected charge.
```

### Example 3: Training Dialogue

```
[SCENE: Orientation]
Trainer: Welcome to the team!
NewHire: Thank you, I'm excited to be here.
Trainer: Let me show you around.
```

## Dataset Size Recommendations

- **Minimum**: 1,000 lines of dialogue (~50 KB)
- **Recommended**: 10,000+ lines (~500 KB)
- **Optimal**: 50,000+ lines (~2-3 MB)

Larger datasets produce better results but require more training time.

## Custom Format Parser

If your dataset has a different format, you can modify the `DialogueDataProcessor` class in Section 2.0 of the notebook:

```python
class DialogueDataProcessor:
    def load_and_parse(self):
        # Modify this method to parse your format
        # Return: list of (character, dialogue, scene) tuples
        pass
```

## Character and Scene Types

The model automatically extracts:
- **Characters**: All unique character names from your dataset
- **Scene Types**: All unique scene descriptions from `[SCENE: ...]` tags

These are used for conditional generation in Section 7.0.

## Troubleshooting

### Issue: "Dataset file not found"
- Check that `DATA_PATH` points to the correct file
- Verify the file exists with `ls` or file browser
- Use absolute paths, not relative paths

### Issue: "No dialogues parsed"
- Check your dataset follows the format: `Character: dialogue`
- Ensure scene markers use: `[SCENE: description]`
- Verify file encoding is UTF-8

### Issue: "Too few characters/scenes"
- You need at least 2 different characters
- You need at least 2 different scene types
- Check for consistent formatting

## Advanced Configuration

### Multiple Files

Process multiple dataset files:

```python
import glob
files = glob.glob('/path/to/dataset/*.txt')
all_dialogues = []
for file in files:
    processor = DialogueDataProcessor(file_path=file)
    processor.load_and_parse()
    all_dialogues.extend(processor.dialogues)
```

### Data Augmentation

The notebook includes built-in augmentation:
- Synonym replacement
- Back-translation (optional)
- Paraphrasing
- Sentence reordering

Configure in Section 2.0.

## Next Steps

1. Prepare your dataset file
2. Update the configuration cell in the notebook
3. Run Section 2.0 to verify your data loads correctly
4. Continue with the rest of the notebook

For questions or issues, refer to the notebook's documentation cells or check the examples in `sample_dialogues.txt`.
