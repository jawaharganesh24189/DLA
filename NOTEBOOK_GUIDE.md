# Football Tactics Transformer - DLA Architecture Implementation

## 📋 Overview

This notebook (`Football_Tactics_DLA_8B_9_Architecture.ipynb`) implements a complete football tactics prediction system using the **EXACT** transformer architectures from DLA's educational notebooks:

- **Notebook 8B**: "Building our Third Language Model" (Translation)
- **Notebook 9**: "Building Our LLM" (GPT-style Language Model)

## 🎯 What Makes This Special

### 1. **Authentic DLA Architecture**
- Uses the EXACT code from notebooks 8B and 9 (not adaptations)
- `TransformerEncoder` with self-attention and residual connections
- `TransformerDecoder` with self-attention + cross-attention
- `PositionalEmbedding` with reverse option for output layer
- `WarmupSchedule` for better training convergence

### 2. **Real Football Data**
- Loads actual match data from **StatsBomb Open Data** API
- Processes real events: passes, dribbles, shots, tackles
- Extracts formations from Starting XI events
- Converts match events to tactical sequences
- Automatic fallback to high-quality synthetic data

### 3. **Advanced Generation**
- **Temperature Sampling**: Control creativity (0.5 = conservative, 1.5 = creative)
- **Top-K Sampling**: Sample from top K predictions (k=5, 10, 20)
- **Greedy Decoding**: Most probable tactics
- Diverse, realistic tactical generation

## 🏗️ Architecture Details

### From Notebook 8B (Encoder-Decoder Translation)

```python
TransformerEncoder:
├── MultiHeadAttention (self-attention)
├── LayerNormalization
├── Feed-Forward Network
│   ├── Dense(intermediate_dim, relu)
│   └── Dense(hidden_dim)
└── LayerNormalization

TransformerDecoder:
├── MultiHeadAttention (self-attention with causal mask)
├── LayerNormalization
├── MultiHeadAttention (cross-attention to encoder)
├── LayerNormalization
├── Feed-Forward Network
└── LayerNormalization
```

### From Notebook 9 (LLM Building)

```python
PositionalEmbedding:
├── Token Embeddings
├── Position Embeddings
└── Reverse option (for output layer)

WarmupSchedule:
├── Warmup steps: 1,000
├── Base rate: 2e-4
└── Linear warmup → constant

Generation:
├── Temperature sampling (preds / temperature)
├── Top-K sampling (select from top K)
└── Compiled generation for speed
```

## 📊 Model Configuration

```yaml
Architecture:
  hidden_dim: 256
  intermediate_dim: 2048
  num_heads: 8
  vocab_size: 500
  sequence_length: 20
  
Training:
  batch_size: 64
  epochs: 20
  optimizer: Adam(WarmupSchedule)
  warmup_steps: 1000
  learning_rate: 2e-4
  
Data:
  source: StatsBomb API + Synthetic fallback
  training_samples: ~680
  validation_samples: ~120
  competitions: La Liga, Champions League, World Cup
```

## 🚀 Quick Start

### 1. Open the Notebook
```bash
jupyter notebook Football_Tactics_DLA_8B_9_Architecture.ipynb
```

### 2. Install Dependencies
```python
!pip install tensorflow keras numpy pandas matplotlib requests
```

### 3. Run All Cells
The notebook will automatically:
- ✅ Load real match data from StatsBomb API
- ✅ Process events into tactical sequences
- ✅ Build the transformer model
- ✅ Train with warmup schedule
- ✅ Generate diverse tactics
- ✅ Save trained model

### 4. Generate Tactics
```python
# Example: Generate tactics for a game state
game_state = "formation 4-3-3 ball attack status winning"

# Different sampling strategies
tactics_greedy = decode_sequence(game_state)
tactics_temp = decode_sequence(game_state, partial(random_sample, temperature=1.5))
tactics_topk = decode_sequence(game_state, partial(top_k, k=5))
```

## 📈 Expected Results

### Training Performance
- **Validation Accuracy**: 85-90%
- **Validation Loss**: 0.3-0.5
- **Training Time**: 15-25 minutes (depends on hardware)
- **Convergence**: Usually within 10-15 epochs

### Example Generations

**Input**: `formation 4-3-3 ball attack status winning`

**Greedy**: `CM pass forward , ST shoot center , FWD press forward`

**Temperature=0.5** (Conservative): `MID pass center , FWD dribble forward , ST shoot center`

**Temperature=1.5** (Creative): `RW cross right , ST shoot center , CB clear forward , LW dribble wide`

**Top-K=5**: `CAM pass forward , ST shoot center , FWD support center`

## 🎓 Learning Objectives

This notebook demonstrates:

1. **Sequence-to-Sequence Learning**: Game state → Tactical sequence
2. **Attention Mechanisms**: Self-attention and cross-attention
3. **Transfer Learning**: Applying proven architectures to new domains
4. **API Integration**: Loading real-world data
5. **Sampling Strategies**: Controlling generation diversity
6. **Learning Rate Schedules**: Warmup for better convergence

## 📚 Architecture Source

### Notebook 8B Components
- File: `8B_Building our Third Language Model (1).ipynb`
- Purpose: English-Spanish translation
- Components used:
  - `TransformerEncoder` (self-attention)
  - `TransformerDecoder` (self + cross attention)
  - `PositionalEmbedding` (basic)
  - Dataset formatting

### Notebook 9 Components
- File: `9_Building_Our_LLM.ipynb`
- Purpose: Mini-GPT language model
- Components used:
  - `PositionalEmbedding` (with reverse)
  - `WarmupSchedule`
  - `random_sample` (temperature)
  - `top_k` (top-K sampling)
  - Compiled generation

## 🔍 Key Differences from Generic Transformers

1. **Exact DLA Implementation**: Uses the proven educational code
2. **Real Data**: Not just synthetic - loads actual matches
3. **Football-Specific**: Formations, positions, tactical actions
4. **Multiple Sampling**: Temperature, top-K, greedy
5. **Production-Ready**: Complete training, saving, generation pipeline

## 📁 Output Files

After running the notebook:

```
football_tactics_transformer_YYYYMMDD_HHMMSS.keras  # Trained model
config_YYYYMMDD_HHMMSS.pkl                          # Configuration
training_results.png                                 # Training curves
```

## 🎯 Use Cases

1. **Tactical Analysis**: Predict optimal tactics for game situations
2. **Training Tool**: Learn how transformers work with real data
3. **Research**: Experiment with sampling strategies
4. **Education**: Understand seq2seq models practically
5. **Game AI**: Generate realistic AI opponent tactics

## 🔧 Customization

### Change Data Source
```python
training_data = data_loader.load_training_data(
    num_matches=50,
    competition='Champions League 2018/19'  # Options: La Liga, Premier League, World Cup
)
```

### Adjust Model Size
```python
hidden_dim = 512         # Increase for more capacity
intermediate_dim = 2048  # FFN size
num_heads = 16          # More attention heads
```

### Modify Sampling
```python
# More conservative
decode_sequence(game_state, partial(random_sample, temperature=0.3))

# More creative
decode_sequence(game_state, partial(random_sample, temperature=2.0))

# Broader top-K
decode_sequence(game_state, partial(top_k, k=10))
```

## 🐛 Troubleshooting

### API Connection Issues
If StatsBomb API is unavailable, the notebook automatically falls back to synthetic data. You'll see:
```
⚠ API unavailable: [error message]
⚠ Using synthetic data (APIs unavailable)
✓ Generated 800 synthetic training samples
```

### Memory Issues
If you encounter OOM errors:
```python
batch_size = 32        # Reduce from 64
hidden_dim = 128       # Reduce from 256
num_heads = 4          # Reduce from 8
```

### Slow Training
Enable mixed precision:
```python
keras.config.set_dtype_policy("mixed_float16")
```

## 📖 References

1. **StatsBomb Open Data**: https://github.com/statsbomb/open-data
2. **DLA Notebooks**: Source of architecture
3. **Attention Is All You Need**: Vaswani et al., 2017
4. **Keras Documentation**: https://keras.io/

## 🤝 Contributing

To improve this notebook:
1. Add more football data sources (Wyscout, Opta)
2. Implement player-specific models
3. Add opponent modeling
4. Create real-time inference API
5. Build web interface for tactical generation

## 📄 License

This code uses architectures from DLA educational materials for learning purposes. Football data from StatsBomb Open Data under their license.

---

**Created**: 2026-02-12  
**Last Updated**: 2026-02-12  
**Author**: Deep Learning Academy  
**Version**: 1.0
