# Dataset Configuration Guide

## Overview

The `8E_Adversarial_Dialogue_GAN.ipynb` notebook is designed to work with any dialogue dataset. This guide explains how to prepare and configure your custom dataset.

## NEW: Flexible Format Support

The notebook now supports **multiple formats** including "messy" datasets! 

### Supported Formats

#### Format 1: Structured (Original)
```
[SCENE: Scene Description]
Character1: Dialogue text here
Character2: Response text here
```

#### Format 2: Simple Character-Dialogue (No scenes)
```
Character1: Dialogue text here
Character2: Response text here
Character1: More dialogue
```

#### Format 3: Mixed with Context Lines (NEW!)
```
Context about the situation
Character1: Dialogue text here
More context or description
Character2: Response text here
```

#### Format 4: Multiple Files in a Folder (NEW!)
You can now provide a **folder path** containing multiple .txt files!

```
dataset_folder/
  ├── conversation1.txt
  ├── conversation2.txt
  └── conversation3.txt
```

### Smart Character Detection

The parser automatically:
- ✅ Detects character names from `Character: dialogue` patterns
- ✅ Filters out false positives (like "Note:", "Context:", etc.)
- ✅ Requires characters to appear at least 2 times (configurable)
- ✅ Treats non-dialogue lines as context/scene information
- ✅ Works with messy, inconsistent formatting

### Format Rules (Flexible)

1. **Character Format**: `CharacterName: dialogue text` (colon required)
2. **Character Names**: Should be 1-3 words, capitalized
3. **Scene Headers**: Optional `[SCENE: Description]`
4. **Context Lines**: Any line without `:` is treated as context
5. **Multiple Files**: All .txt files in a folder are processed together

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

### Option 2: Use Messy Dataset Example (NEW!)

Test the flexible format parser with the included messy dataset:

```python
USE_MESSY_EXAMPLE = True
# This will use the messy_dataset/ folder with multiple files
```

### Option 3: Use Your Own Dataset - Single File

1. Prepare your dataset file
2. Save it anywhere accessible
3. Update the configuration:

```python
USE_SAMPLE_DATA = False
DATA_PATH = '/path/to/your/dialogues.txt'
```

### Option 4: Use Your Own Dataset - Multiple Files (NEW!)

1. Create a folder with multiple .txt files
2. Each file can have different conversations
3. Update the configuration:

```python
USE_SAMPLE_DATA = False
DATA_PATH = '/path/to/your/dataset/folder/'
```

The parser will automatically process all .txt files in the folder!

## Example Datasets

### Example 1: Movie Dialogue (Structured)

```
[SCENE: Opening Scene]
Hero: We need to stop them before it's too late!
Sidekick: I'm with you all the way.
Villain: You'll never succeed!

[SCENE: Final Battle]
Hero: This ends now!
Villain: We'll see about that.
```

### Example 2: Customer Service (Simple)

```
Agent: How can I help you today?
Customer: My device isn't working properly.
Agent: Let me check that for you.

Agent: I see you have a question about your bill.
Customer: Yes, I noticed an unexpected charge.
```

### Example 3: Messy Format (NEW!)

```
In a busy office, people are discussing the project
John: We need to finish this by Friday.
Sarah: That's going to be challenging.
Context: They haven't started yet
Mike: I can work over the weekend if needed.
The team continues planning
Sarah: Let's divide the tasks then.
```

### Example 4: Multiple Files (NEW!)

**file1.txt:**
```
John: Hello everyone.
Sarah: Hi John!
```

**file2.txt:**
```
Mike: How's the project going?
Sarah: We're making progress.
```

Both files will be processed together automatically!

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
