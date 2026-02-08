# DialogueParser Text Format - Quick Reference

## Problem Solved
The dialogue parser previously output JSON format, which required JSON parsing during model training. The new **text format** provides plain text output that models can directly consume.

**Key Feature**: Takes all .txt files as input and produces a single .txt file as output.

## Quick Start

### Command Line (Simplest Way)
```bash
# Parse all .txt files in a directory and output to .txt file
python dialogue_parser.py anime_dataset/ text

# Output: output.txt (ready for model training)
```

**What happens:**
- ✅ Reads all `.txt` files in `anime_dataset/`
- ✅ Parses and combines all dialogues
- ✅ Outputs to `output.txt` (plain text format)
- ✅ Ready for direct model training

### Python API
```python
from dialogue_parser import DialogueParser

parser = DialogueParser()
turns = parser.parse_directory('anime_dataset/')

# Default: [SEP] separator
text_output = parser.to_training_format(turns, 'text')

# Custom separators
text_pipe = parser.to_training_format(turns, 'text', separator=' | ')
text_tab = parser.to_training_format(turns, 'text', separator='\t')
text_arrow = parser.to_training_format(turns, 'text', separator=' -> ')
```

## Output Format

### Default ([SEP] separator)
```
context text [SEP] response text
another context [SEP] another response
```

### Custom Separator Examples
```
# Pipe separator
context text | response text

# Tab separator
context text	response text

# Arrow separator  
context text -> response text
```

## Model Training

### Loading Text Format
```python
with open("training_data.txt", "r") as f:
    for line in f:
        context, response = line.strip().split(" [SEP] ")
        # Train your model with context and response
```

### Benefits
- ✓ **Simpler**: No JSON parsing required
- ✓ **Faster**: Lower overhead during training
- ✓ **Cleaner**: Direct text consumption
- ✓ **Flexible**: Customizable separator for different models

## Comparison

### Before (JSONL)
```json
{"context": "Hello", "response": "Hi", "metadata": {...}}
```
Requires: `json.loads()`, dict access, parsing overhead

### After (TEXT)
```
Hello [SEP] Hi
```
Requires: `str.split()` only - simple and fast!

## All Available Formats

| Format | Use Case | Command |
|--------|----------|---------|
| `text` | **Model training** (recommended) | `parser.to_training_format(turns, 'text')` |
| `jsonl` | Structured data with metadata | `parser.to_training_format(turns, 'jsonl')` |
| `csv` | Spreadsheet analysis | `parser.to_training_format(turns, 'csv')` |
| `conversational` | Human/AI format | `parser.to_training_format(turns, 'conversational')` |

## Examples

### Example 1: Prepare Training Data
```bash
# Parse and convert to text format
python dialogue_parser.py anime_dataset/ text

# Use output.text for training
```

### Example 2: Custom Separator for Specific Model
```python
# Some models prefer tab separation
parser = DialogueParser()
turns = parser.parse_directory('my_data/')
text_output = parser.to_training_format(turns, 'text', separator='\t')

with open('training.tsv', 'w') as f:
    f.write(text_output)
```

### Example 3: Batch Processing
```python
import glob
from dialogue_parser import DialogueParser

parser = DialogueParser()
all_text = []

for dataset_dir in glob.glob('datasets/*'):
    turns = parser.parse_directory(dataset_dir)
    text = parser.to_training_format(turns, 'text')
    all_text.append(text)

# Combine all datasets
combined = '\n'.join(all_text)
with open('all_training_data.txt', 'w') as f:
    f.write(combined)
```

## Testing

All formats have been tested and validated:
- ✓ Default [SEP] separator works correctly
- ✓ Custom separators (pipe, tab, arrow) work
- ✓ Line splitting for model training verified
- ✓ Backward compatibility with JSONL, CSV maintained
- ✓ Works with all dialogue formats (context-response, speaker, mixed)

## Questions?

See the full documentation in `DIALOGUE_PARSER_GUIDE.md` for more details.
