# DLA GAN Dialogue Project - Notebook Structure

## Overview
This notebook implements a complete GAN-based dialogue generation system in Google Colab.

## Notebook Sections (30 Cells Total)

### Section 1: Setup & Dependencies (Cells 1-3)
- Install required packages
- Import all libraries (TensorFlow, Keras, NumPy, etc.)
- Verify GPU availability

### Section 2: Google Drive & Data Loading (Cells 4-6)
- Mount Google Drive
- Configure dataset paths
- Set output file name (cleandata.txt)

### Section 3: Dialogue Parsing (Cells 7-9)
- **DialogueTurn** dataclass - Stores dialogue data
- **DialogueParser** class - Multi-format parser
  - Parses "context: ... response: ..." format
  - Parses "Character: dialogue" format
  - Automatically creates cleandata.txt
  - Provides statistics (lines, characters, top speakers)
- **Usage** - Parse all files from Google Drive folder

### Section 4: Data Processing & Tokenization (Cells 10-12)
- **FlexibleDialogueDataProcessor** class
  - Loads cleandata.txt
  - Extracts characters and dialogues
  - Builds vocabulary with Keras Tokenizer
  - Creates padded training sequences
- **Usage** - Process cleandata.txt for training

### Section 5: Model Architecture (Cells 13-16)
- **Generator** model - LSTM-based text generator
  - Embedding → LSTM → LSTM → Dropout → Dense (softmax)
  - Creates dialogue sequences from noise
- **Discriminator** model - LSTM-based classifier
  - Embedding → LSTM → Dropout → Dense → Dense (sigmoid)
  - Classifies sequences as real or fake
- **Initialization** - Create model instances and optimizers

### Section 6: Model Training (Cells 17-20)
- Training configuration (batch size, epochs)
- **train_gan()** function - Adversarial training loop
  - Train discriminator on real and fake sequences
  - Train generator to fool discriminator
  - Track losses and accuracy
  - Progress reporting
- **Execute training** - Start the training process

### Section 7: Dialogue Generation (Cells 21-23)
- **generate_dialogue()** function
  - Generate from random noise or seed text
  - Use trained generator model
  - Convert token IDs back to words
- **Generate samples** - Create and display sample dialogues

### Section 8: Visualization (Cells 24-25)
- Plot training history
  - Discriminator loss over epochs
  - Generator loss over epochs
  - Discriminator accuracy over epochs

### Section 9: Model Persistence (Cells 26-27)
- Save models (generator, discriminator, tokenizer)
- Load models for future use

### Section 10: Summary (Cells 28-29)
- Project summary
- Key features achieved
- Next steps and improvements

## Key Classes

### DialogueParser
```python
dialogue_parser = DialogueParser()
turns = dialogue_parser.parse_directory(
    directory='/path/to/files/',
    auto_save_txt=True,
    output_file='cleandata.txt'
)
```

### FlexibleDialogueDataProcessor
```python
processor = FlexibleDialogueDataProcessor(
    file_path='cleandata.txt',
    seq_length=50
)
dialogues = processor.load_and_parse()
tokenizer = processor.build_vocabulary(max_vocab_size=5000)
sequences = processor.create_sequences()
```

### Generator & Discriminator
```python
generator = Generator(vocab_size=vocab_size, embedding_dim=128, lstm_units=256)
discriminator = Discriminator(vocab_size=vocab_size, embedding_dim=128, lstm_units=256)
```

## Workflow

```
1. Mount Google Drive
   ↓
2. Parse dialogue files → cleandata.txt (DialogueParser)
   ↓
3. Load and tokenize cleandata.txt (FlexibleDialogueDataProcessor)
   ↓
4. Build vocabulary and create sequences
   ↓
5. Define Generator and Discriminator models
   ↓
6. Train GAN with adversarial training
   ↓
7. Generate new dialogues
   ↓
8. Visualize results
   ↓
9. Save models
```

## File Formats Supported

1. **Context-Response Format:**
   ```
   context: How are you?
   response: I'm doing great!
   context: What's your name?
   response: My name is Alice.
   ```

2. **Character Dialogue Format:**
   ```
   Alice: Hello, how are you?
   Bob: I'm doing well, thanks!
   Alice: That's great to hear!
   ```

## Output Files

- `cleandata.txt` - Processed dialogues in "Character: dialogue" format
- `models/generator.h5` - Trained generator model
- `models/discriminator.h5` - Trained discriminator model
- `models/tokenizer.pickle` - Vocabulary tokenizer

## Running the Notebook

1. Open in Google Colab
2. Run cells sequentially from top to bottom
3. Ensure Google Drive is mounted
4. Set correct DATASET_PATH to your dialogue files
5. Wait for training to complete
6. Generate sample dialogues

## Customization

- **Vocabulary size**: Change `max_vocab_size` in build_vocabulary()
- **Sequence length**: Change `seq_length` in FlexibleDialogueDataProcessor()
- **Model size**: Adjust `embedding_dim` and `lstm_units` in Generator/Discriminator
- **Training**: Modify `BATCH_SIZE` and `EPOCHS`
- **Generation**: Experiment with seed texts and temperature

## Notes

- All code is properly formatted and executable
- No commented-out code blocks
- Clear section headers for navigation
- Progress reporting during long operations
- Error handling for file operations
- Compatible with Google Colab environment
