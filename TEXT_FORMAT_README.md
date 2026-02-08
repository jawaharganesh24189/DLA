# Text Format Feature - README

## Quick Start

### Problem
The dialogue parser output JSON format, but models need plain text for training.

### Solution
New **text format** that takes .txt files and outputs a .txt file.

### Usage
```bash
python dialogue_parser.py anime_dataset/ text
```

**Result**: Creates `output.txt` with plain text format ready for model training.

## What You Get

### Input
```
anime_dataset/
  ├── train-anime-107.txt
  ├── train-anime-108.txt
  ├── validation-anime-8.txt
  └── validation-anime-9.txt
```

### Output
```
output.txt:
  context_1 [SEP] response_1
  context_2 [SEP] response_2
  context_3 [SEP] response_3
  ...
```

### Training
```python
with open('output.txt') as f:
    for line in f:
        context, response = line.strip().split(' [SEP] ')
        train_model(context, response)
```

## Benefits

✅ **Simple**: No JSON parsing  
✅ **Fast**: Lower overhead  
✅ **Clean**: Direct text to model  
✅ **Flexible**: Customizable separator  

## Documentation

- **Quick Start**: `TEXT_FORMAT_QUICKSTART.md`
- **Implementation**: `TEXT_FORMAT_IMPLEMENTATION.md`
- **Full Guide**: `DIALOGUE_PARSER_GUIDE.md`
- **Workflow**: `WORKFLOW_DIAGRAM.txt`

## Examples

### Default Separator
```python
text = parser.to_training_format(turns, 'text')
# Output: context [SEP] response
```

### Custom Separator
```python
text = parser.to_training_format(turns, 'text', separator=' | ')
# Output: context | response
```

### Tab Separator
```python
text = parser.to_training_format(turns, 'text', separator='\t')
# Output: contextresponse
```

## All Formats

| Format | Extension | Command |
|--------|-----------|---------|
| **text** | **.txt** | `text` |
| jsonl | .jsonl | `jsonl` |
| csv | .csv | `csv` |
| conversational | .conversational | `conversational` |

## Testing

All tests pass:
- ✅ Format output correct
- ✅ .txt to .txt workflow works
- ✅ Backward compatibility maintained
- ✅ No security issues (CodeQL clean)

## Questions?

Run the parser with no arguments for help:
```bash
python dialogue_parser.py
```

Or see full documentation in the guide files listed above.
