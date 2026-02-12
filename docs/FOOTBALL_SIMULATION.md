# Football Simulation - Physics & Logic Patch

This module implements realistic physics and game logic for football/soccer match simulation, designed to train Transformer AI models on tactical gameplay.

## Features

### 1. **Ray-Cast Interception Physics** (`PhysicsEngine`)
Prevents unrealistic ball movement through defenders using vector mathematics.

- **Distance Calculation**: Computes the shortest distance from a defender to a pass trajectory
- **Interception Detection**: Checks if any defender is within interception radius of the ball path
- **Turnover Events**: Automatically transfers possession when interception occurs

### 2. **Set Piece Management** (`SetPieceManager`)
Handles game state transitions and positioning for dead-ball situations.

- **Boundary Detection**: Monitors ball position to detect out-of-bounds
- **Game States**: Manages transitions between OPEN_PLAY, CORNER, GOAL_KICK, and THROW_IN
- **Player Repositioning**: Automatically positions players for set piece scenarios

### 3. **Match Simulation** (`MatchSimulator`)
Integrates physics and logic into a complete match engine.

- **Action Processing**: Handles PASS, SHOOT, and DRIBBLE actions
- **Training Data**: Captures events for AI model training
- **Tactical Gameplay**: Enforces realistic constraints that encourage strategic decision-making

## Installation

```bash
# Install required dependencies
pip install numpy
```

## Quick Start

```python
from football_simulation import MatchSimulator, create_sample_team

# Create teams
home = create_sample_team("Arsenal", num_players=11)
away = create_sample_team("Chelsea", num_players=11)

# Initialize simulator
simulator = MatchSimulator(home, away)

# Simulate actions
event = simulator.simulate_step("PASS", target_pos=[60.0, 40.0])

# Check result
if event.get("result") == "INTERCEPTED":
    print(f"Pass intercepted by {event['interceptor']}!")
else:
    print("Pass successful!")

# Get training data
training_data = simulator.get_training_data()
```

## Architecture

### Class Hierarchy

```
PhysicsEngine (static methods)
├── get_distance_point_to_segment()
└── check_interception()

SetPieceManager
├── check_boundaries()
└── resolve_set_piece()

MatchSimulator
├── simulate_step()
├── get_training_data()
└── reset()

Supporting Classes:
├── Player (dataclass)
├── Team (dataclass)
└── Ball (dataclass)
```

### Pitch Dimensions

- **Length**: 105 meters (x-axis: 0 to 105)
- **Width**: 68 meters (y-axis: 0 to 68)
- **Goals**: Located at x=0 and x=105

## Usage Examples

### Example 1: Basic Interception

```python
from football_simulation import MatchSimulator, Team, Player

# Create teams with specific positions
home = Team("Home", [
    Player("Attacker", position=[40.0, 34.0], position_role="FWD")
])

away = Team("Away", [
    Player("Defender", position=[52.0, 34.0], position_role="DEF")
])

simulator = MatchSimulator(home, away)
simulator.ball.position = [40.0, 34.0]

# Try to pass through defender (will be intercepted)
event = simulator.simulate_step("PASS", target_pos=[70.0, 34.0])
# Result: INTERCEPTED
```

### Example 2: Set Piece Handling

```python
# Ball goes out for corner
simulator.ball.position = [100.0, 34.0]
event = simulator.simulate_step("SHOOT", target_pos=[110.0, 34.0])

# Check game state
print(simulator.set_piece_manager.game_state)  # "CORNER"
print(simulator.ball.position)  # [105, 0] or [105, 68]
```

### Example 3: Training Data Collection

```python
# Simulate multiple actions
simulator.simulate_step("PASS", target_pos=[60.0, 40.0])
simulator.simulate_step("PASS", target_pos=[80.0, 35.0])
simulator.simulate_step("SHOOT", target_pos=[104.0, 34.0])

# Get training data
for event in simulator.get_training_data():
    print(f"{event['action']}: {event['result']}")
    if event.get('interceptor'):
        print(f"  Intercepted by: {event['interceptor']}")
```

## Running the Demo

A comprehensive demonstration is available:

```bash
python examples/demo_simulation.py
```

This demo showcases:
1. **Interception Mechanics** - Passes being blocked by defenders
2. **Set Piece Management** - Corners, goal kicks, and throw-ins
3. **Tactical Scenarios** - Realistic match situations
4. **Physics Accuracy** - Mathematical correctness of distance calculations

## API Reference

### PhysicsEngine

#### `get_distance_point_to_segment(p, a, b)`
Calculates the shortest distance from a point to a line segment.

**Parameters:**
- `p`: numpy array [x, y] - Point position
- `a`: numpy array [x, y] - Line segment start
- `b`: numpy array [x, y] - Line segment end

**Returns:** `float` - Distance in meters

#### `check_interception(pass_start, pass_end, defenders, interception_radius=2.0)`
Checks if any defender can intercept the pass.

**Parameters:**
- `pass_start`: [x, y] - Pass origin
- `pass_end`: [x, y] - Pass target
- `defenders`: List[Player] - Defending players
- `interception_radius`: float - Detection distance (default: 2.0m)

**Returns:** `(bool, Player)` - (intercepted, defender)

### SetPieceManager

#### `check_boundaries(ball_x, ball_y)`
Determines game state based on ball position.

**Returns:** `str` - Game state (OPEN_PLAY, CORNER, GOAL_KICK, THROW_IN)

#### `resolve_set_piece(state, attacking_team, defending_team)`
Repositions players and ball for set pieces.

**Returns:** `[x, y]` - New ball position

### MatchSimulator

#### `simulate_step(action, target_pos=None)`
Processes one game action with physics and boundary checks.

**Parameters:**
- `action`: str - Action type (PASS, SHOOT, DRIBBLE)
- `target_pos`: [x, y] - Optional target position

**Returns:** `dict` - Event data with result and metadata

## Why This Improves AI Training

### 1. Negative Reinforcement
The AI learns that passing through defenders results in **Loss of Possession**, encouraging:
- Passing around congested areas
- Switching play to open spaces
- Strategic positioning

### 2. Tactical Variety
Set pieces introduce distinct scenarios:
- **Corner Kicks**: Teaches crossing into the box
- **Goal Kicks**: Teaches defensive buildup
- **Throw-ins**: Teaches wide play

### 3. Realistic Constraints
The physics engine enforces spatial awareness:
- Cannot pass through multiple defenders
- Must consider defender positions
- Rewards intelligent positioning

## Configuration

### Interception Radius
Adjust the difficulty by changing the interception radius:

```python
# Easier (larger radius = more interceptions)
intercepted, defender = PhysicsEngine.check_interception(
    start, end, defenders, interception_radius=3.0
)

# Harder (smaller radius = fewer interceptions)
intercepted, defender = PhysicsEngine.check_interception(
    start, end, defenders, interception_radius=1.0
)
```

### Player Attributes
Customize player skills:

```python
Player(
    name="Elite_Defender",
    position=[50.0, 34.0],
    position_role="DEF",
    interception_stat=0.9  # 90% interception skill
)
```

## Future Enhancements

Potential additions to the system:
- Player stamina and fatigue
- Advanced shooting mechanics with goalkeeper AI
- Offside rule implementation
- Advanced tactical formations
- Weather and pitch conditions
- Injury system
- Skill-based interception probability

## License

This code is provided as part of the DLA (Deep Learning Applications) project.

## Contributing

When extending this simulation:
1. Maintain the existing API structure
2. Ensure physics calculations are mathematically sound
3. Add comprehensive tests for new features
4. Update documentation with examples
