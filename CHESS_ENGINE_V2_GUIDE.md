# Hybrid Chess Engine v2.0 - Quick Start Guide

## 📚 Overview

`Hybrid_Chess_Engine_v2.ipynb` is an improved version of the chess engine that combines imitation learning from master games with self-play reinforcement. This version includes all production-ready features for training, evaluation, and deployment.

## ✨ What's New in v2.0

### Major Improvements
- **Early Stopping**: Automatically stops training when validation loss stops improving
- **Google Drive Integration**: Persistent storage for models, games, and logs
- **Improved Architecture**: Batch normalization and dropout for better training stability
- **Comprehensive Metrics**: Top-1/Top-5 accuracy tracking throughout training
- **Checkpoint Management**: Automatically saves best model and periodic checkpoints
- **Self-Play Games**: Generates and saves games in PGN format
- **Training Visualization**: Beautiful loss and accuracy plots
- **Progress Bars**: Clear training progress with tqdm
- **Model Management**: Easy save/load/resume functionality

### Architecture Improvements
- Added batch normalization layers for training stability
- Added dropout layers for regularization
- Xavier weight initialization
- Deeper CNN architecture (3 convolutional layers)
- Improved value network architecture

## 🚀 Getting Started

### 1. Open in Google Colab

Click the "Open in Colab" badge at the top of the notebook to launch it in Google Colab.

### 2. Configure Settings

Edit the `CONFIG` dictionary in Section 1:

```python
CONFIG = {
    'pgn_path': '/content/drive/MyDrive/ChessEngine/data/master_games.pgn',
    'save_dir': '/content/drive/MyDrive/ChessEngine/',
    'max_games': 200,
    'batch_size': 32,
    'epochs': 10,
    'patience': 5,
    'selfplay_games': 20,
    'mode': 'hybrid'
}
```

### 3. Prepare Your Data

1. Mount Google Drive (Section 3)
2. Upload your PGN file to `/content/drive/MyDrive/ChessEngine/data/`
3. Update `CONFIG['pgn_path']` to point to your file

### 4. Run Training

Execute cells in order to:
1. Load and split dataset (80% train, 20% validation)
2. Train policy network with early stopping
3. Generate self-play games
4. Visualize training curves
5. Play against your trained engine

## 📊 Directory Structure

The notebook automatically creates this structure on Google Drive:

```
/content/drive/MyDrive/ChessEngine/
├── models/
│   ├── policy_net_best.pth           (best model by validation loss)
│   ├── policy_net_epoch_2.pth        (periodic checkpoints)
│   └── policy_net_epoch_4.pth
├── games/
│   ├── selfplay_game_1.pgn          (self-play games)
│   ├── selfplay_game_2.pgn
│   └── ...
├── logs/
│   ├── policy_training_history.json  (training metrics)
│   └── selfplay_stats.json           (self-play statistics)
├── data/
│   └── master_games.pgn              (your training data)
└── plots/
    └── training_history.png          (loss/accuracy curves)
```

## 🎯 Training Process

### Imitation Learning Phase
1. Loads games from PGN file
2. Splits into train/validation sets
3. Trains policy network on expert moves
4. Tracks loss and Top-1/Top-5 accuracy
5. Implements early stopping when val loss plateaus
6. Saves best model and periodic checkpoints

### Self-Play Phase
1. Uses trained policy network to play against itself
2. Generates multiple complete games
3. Saves each game as separate PGN file
4. Tracks win/loss/draw statistics
5. Can use self-play games for continued training

## 📈 Monitoring Training

### Metrics Tracked
- **Training Loss**: Cross-entropy loss on training set
- **Validation Loss**: Loss on validation set (used for early stopping)
- **Top-1 Accuracy**: Percentage of times best prediction matches expert move
- **Top-5 Accuracy**: Percentage of times expert move is in top 5 predictions
- **Training Time**: Time per epoch

### Early Stopping
- Monitors validation loss
- Stops if no improvement for `patience` epochs (default: 5)
- Minimum improvement threshold: `min_delta` (default: 0.001)
- Saves best model based on lowest validation loss

### Visualization
- Loss curves (train vs validation)
- Accuracy curves (Top-1 and Top-5)
- Saved as PNG to Google Drive
- Displayed inline in notebook

## 🎮 Playing Against the Engine

After training, use the interactive play function:

```python
# Play as White
play_against_engine(policy_net, player_color=chess.WHITE)

# Play as Black
play_against_engine(policy_net, player_color=chess.BLACK)
```

Enter moves in UCI format (e.g., `e2e4`, `g1f3`)

## 💾 Model Management

### Save Models
```python
# Automatically saved during training
# Best model: policy_net_best.pth
# Checkpoints: policy_net_epoch_X.pth
```

### Load Models
```python
# Load best model
epoch, metrics = load_best_model(CONFIG['save_dir'], policy_net)

# Load specific checkpoint
epoch, metrics = load_checkpoint('path/to/checkpoint.pth', policy_net, optimizer)
```

### Resume Training
```python
# Load checkpoint
epoch, metrics = load_checkpoint('path/to/checkpoint.pth', policy_net, optimizer)

# Continue training from that point
# Adjust CONFIG['epochs'] to train for more epochs
```

## 🔧 Hyperparameter Tuning

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `learning_rate` | 1e-3 | Learning rate for optimizer |
| `batch_size` | 32 | Training batch size |
| `epochs` | 10 | Maximum training epochs |
| `patience` | 5 | Early stopping patience |
| `train_val_split` | 0.8 | Train/validation split ratio |
| `max_games` | 200 | Number of PGN games to load |
| `selfplay_games` | 20 | Number of self-play games to generate |

### Tips for Tuning
- **Reduce batch size** if running out of memory
- **Increase patience** if training is unstable
- **Adjust learning rate** if loss isn't decreasing
- **Use more epochs** for larger datasets
- **Increase dropout** if overfitting

## 🐛 Troubleshooting

### Out of Memory
- Reduce `batch_size` (try 16 or 8)
- Use GPU runtime: Runtime → Change runtime type → GPU

### Training Too Slow
- Ensure using GPU runtime
- Reduce `max_games` for testing
- Use smaller model (reduce layers/units)

### No Improvement
- Check learning rate (try 1e-4 or 1e-2)
- Verify data quality (PGN file format)
- Ensure sufficient training data

### Overfitting
- Increase dropout rate
- Add more training data
- Reduce model complexity
- Use weight decay

## 📚 Advanced Usage

### Custom Training Loop
```python
# Create custom dataloader
train_loader, val_loader = create_dataloaders(dataset, batch_size=64)

# Train with custom settings
history = train_policy_network(
    policy_net,
    train_loader,
    val_loader,
    epochs=20,
    learning_rate=5e-4,
    save_dir=CONFIG['save_dir'],
    patience=10,
    save_every=5
)
```

### Batch Self-Play
```python
# Generate many games at once
stats = generate_selfplay_games(
    policy_net,
    num_games=100,
    save_dir=CONFIG['save_dir']
)
```

### Custom Evaluation
```python
# Evaluate on specific positions
board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
move = predict_best_move(board, policy_net)
print(f"Best move: {move.uci()}")
```

## 🎓 Learning Resources

### Understanding the Architecture
- **CNN Layers**: Extract spatial features from board representation
- **Transformer**: Captures piece relationships and tactical patterns
- **Policy Head**: Outputs probability distribution over 4544 moves
- **Value Head**: Evaluates position quality (-1 to +1)

### Training Strategies
1. **Start small**: Train on 50-100 games to verify setup
2. **Monitor metrics**: Watch validation loss for overfitting
3. **Use checkpoints**: Resume from best model if training interrupted
4. **Generate data**: Use self-play to create unlimited training positions
5. **Iterate**: Tune hyperparameters based on validation performance

## 📝 Notes

- **GPU Required**: Training is much faster on GPU (use Colab GPU runtime)
- **Storage**: Models are ~50-100 MB each, plan Google Drive space accordingly
- **PGN Format**: Ensure your PGN files are valid and well-formatted
- **Move Vocabulary**: Covers all 4544 possible chess moves including promotions
- **Compatibility**: Works with both Python 3.8+ and PyTorch 1.10+

## 🤝 Contributing

Improvements welcome! Areas for future work:
- Implement value network training with RL
- Add MCTS (Monte Carlo Tree Search) for move selection
- Implement curriculum learning
- Add position evaluation heuristics
- Create web interface for online play

## 📄 License

This project is part of the DLA repository. Check the repository license for details.

## 🙏 Acknowledgments

- Based on the original Hybrid Chess Engine
- Uses python-chess library for game logic
- Trained on master games (e.g., Hikaru Nakamura's games)

---

**Happy Training! 🧠♟️**

For questions or issues, please open an issue in the GitHub repository.
