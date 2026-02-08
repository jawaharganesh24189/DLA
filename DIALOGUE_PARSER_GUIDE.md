# Dialogue Parser Utility

## Overview

The `dialogue_parser.py` utility provides a flexible parser for various dialogue dataset formats. It's designed to handle unstructured dialogue data from multiple sources including anime scripts, conversations, and context-response pairs.

## Features

### Supported Formats

1. **Context-Response Format**
   ```
   context: How are you doing today?
   response: I'm doing great, thank you!
   
   context: What's your favorite hobby?
   response: I love reading books.
   ```

2. **Speaker Dialogue Format**
   ```
   John: We need to finish this project.
   Sarah: I agree, let's get started.
   Mike: I can help with the backend.
   ```

3. **Mixed Format with Scene Descriptions**
   ```
   [SCENE: Meeting Room]
   Context about the situation
   John: Let's discuss the plan.
   Sarah: Sounds good to me.
   ```

### Output Formats

- **JSONL**: One JSON object per line with context, response, and metadata
- **CSV**: Simple comma-separated format with context and response columns
- **Conversational**: Human/Assistant format suitable for conversational AI training

## Usage

### Command Line

```bash
# Parse a single file
python dialogue_parser.py sample_dialogues.txt

# Parse a directory
python dialogue_parser.py messy_dataset/

# Parse and save to specific format
python dialogue_parser.py messy_dataset/ jsonl
python dialogue_parser.py sample_dialogues.txt csv
python dialogue_parser.py messy_dataset/ conversational
```

### As a Module

```python
from dialogue_parser import DialogueParser, DatasetStatistics

# Initialize parser
parser = DialogueParser()

# Parse a single file
turns = parser.parse_file("sample_dialogues.txt")

# Parse a directory
all_turns = parser.parse_directory("messy_dataset/")

# Calculate statistics
stats = DatasetStatistics.calculate_stats(all_turns)
print(stats)

# Convert to training format
jsonl_output = parser.to_training_format(all_turns, "jsonl")
csv_output = parser.to_training_format(all_turns, "csv")
conversational_output = parser.to_training_format(all_turns, "conversational")

# Save to file
with open("training_data.jsonl", "w") as f:
    f.write(jsonl_output)
```

## Classes

### DialogueTurn

A dataclass representing a single dialogue turn:
- `context`: The context/previous dialogue
- `response`: The response to the context
- `metadata`: Optional dictionary with format info, speaker name, etc.

### DialogueParser

Main parser class with methods:
- `parse_file(filepath)`: Parse a single file
- `parse_directory(directory, pattern)`: Parse all files matching pattern in directory
- `to_training_format(turns, format_type)`: Convert turns to specified output format

### DatasetStatistics

Utility class for calculating dataset statistics:
- `calculate_stats(turns)`: Returns dictionary with statistics like:
  - total_turns
  - avg_context_length
  - avg_response_length
  - max/min context/response lengths

## Integration with Existing Tools

This parser complements the `FlexibleDialogueDataProcessor` in the main notebook:

- **dialogue_parser.py**: Standalone utility for preprocessing and format conversion
- **FlexibleDialogueDataProcessor**: Integrated into the GAN training pipeline

You can use `dialogue_parser.py` to:
1. Preprocess messy datasets into clean formats
2. Convert between formats (JSONL, CSV, conversational)
3. Calculate dataset statistics before training
4. Combine multiple dialogue files into a single training file

Then use the cleaned output with the notebook's training pipeline.

## Examples

### Example 1: Preprocess Messy Dataset

```bash
# Parse messy dataset and save as JSONL
python dialogue_parser.py messy_dataset/ jsonl

# Output saved to output.jsonl
# Can now be used for training
```

### Example 2: Calculate Statistics

```bash
# View statistics for a dataset
python dialogue_parser.py sample_dialogues.txt

# Output:
# Dataset Statistics:
# total_turns: 163
# avg_context_length: 18.50
# avg_response_length: 5.22
# ...
```

### Example 3: Batch Processing

```python
import glob
from dialogue_parser import DialogueParser

parser = DialogueParser()

# Process multiple directories
all_turns = []
for directory in glob.glob("datasets/*/"):
    turns = parser.parse_directory(directory)
    all_turns.extend(turns)

# Save combined output
output = parser.to_training_format(all_turns, "jsonl")
with open("combined_training.jsonl", "w") as f:
    f.write(output)
```

## Format Detection

The parser automatically detects the format:

1. **First attempt**: Context-response format (case-insensitive)
   - Looks for "context:" and "response:" markers
   
2. **Fallback**: Speaker dialogue format
   - Looks for "Speaker: dialogue" patterns
   - Handles scene descriptions and context lines

## Output Structure

### JSONL Format
```json
{"context": "...", "response": "...", "metadata": {"format": "dialogue", "speaker": "John"}}
{"context": "...", "response": "...", "metadata": {"format": "context_response"}}
```

### CSV Format
```csv
context,response
"...",  "..."
"...",  "..."
```

### Conversational Format
```
Human: ...
Assistant: ...