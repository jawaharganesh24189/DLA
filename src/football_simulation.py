"""
Football Match Simulation with Physics and Logic
Implements ray-cast interceptions and set piece management for tactical AI training
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# PART 1: PHYSICS ENGINE (Ray-Cast Interception)
# ============================================================================

class PhysicsEngine:
    """
    Implements spatial physics for football simulation.
    Prevents unrealistic ball movement through defenders.
    """
    
    @staticmethod
    def get_distance_point_to_segment(p, a, b):
        """
        Calculates distance from Point P (Defender) to Line Segment AB (Pass Trajectory).
        
        Args:
            p: numpy array [x, y] - Point (defender position)
            a: numpy array [x, y] - Line segment start (pass start)
            b: numpy array [x, y] - Line segment end (pass end)
            
        Returns:
            float: Distance from point to nearest point on segment
        """
        # Vector from A to B
        ab = b - a
        # Vector from A to P
        ap = p - a
        
        # Project AP onto AB to find the closest point on the line
        len_sq = np.sum(ab**2)
        if len_sq == 0: 
            return np.sqrt(np.sum((p - a)**2))  # A and B are same
        
        t = np.dot(ap, ab) / len_sq
        # Clamp t to segment [0, 1]
        t = np.clip(t, 0, 1)
        
        # Nearest point on the line segment
        closest = a + t * ab
        
        # Distance from P to that nearest point
        return np.sqrt(np.sum((p - closest)**2))

    @staticmethod
    def check_interception(pass_start, pass_end, defenders, interception_radius=2.0):
        """
        Returns True if any defender is close enough to the passing lane to intercept.
        
        Args:
            pass_start: [x, y] - Starting position of pass
            pass_end: [x, y] - Ending position of pass
            defenders: List of Player objects with .position attribute
            interception_radius: float - Distance threshold for interception (default 2.0 meters)
            
        Returns:
            Tuple[bool, Optional[Player]]: (intercepted, defender) - True if intercepted and the defender
        """
        a = np.array(pass_start)
        b = np.array(pass_end)
        
        for defender in defenders:
            p = np.array(defender.position)  # Assuming defender has .position [x,y]
            
            # 1. Check if defender is actually between start and end (rough check)
            # (Optimization: Don't check defenders behind the passer)
            
            # 2. Geometry check
            dist = PhysicsEngine.get_distance_point_to_segment(p, a, b)
            
            # Logic: If defender is within interception_radius of the ball path
            if dist < interception_radius:
                # Optional: Add a skill check here (e.g., if random < defender.interception_stat)
                return True, defender 
                
        return False, None


# ============================================================================
# PART 2: SET PIECE MANAGER
# ============================================================================

class SetPieceManager:
    """
    Manages game state transitions and set piece positioning.
    Handles corners, goal kicks, and throw-ins.
    """
    
    def __init__(self):
        self.game_state = "OPEN_PLAY"  # Options: OPEN_PLAY, CORNER, GOAL_KICK, THROW_IN
        
    def check_boundaries(self, ball_x, ball_y):
        """
        Checks if ball went out and returns the new state.
        Pitch dimensions: 105 x 68 meters
        
        Args:
            ball_x: float - Ball x coordinate
            ball_y: float - Ball y coordinate
            
        Returns:
            str: New game state
        """
        if 0 <= ball_x <= 105 and 0 <= ball_y <= 68:
            return "OPEN_PLAY"
            
        # Logic for boundaries
        if ball_x > 105:  # Out behind opponent goal
            # NOTE: Simplified as 50/50 random choice as per specification
            # In production, should be based on which team last touched the ball
            return "CORNER" if np.random.random() > 0.5 else "GOAL_KICK"
            
        elif ball_x < 0:  # Out behind own goal
            return "CORNER"  # Conceded a corner
            
        else:  # Side lines
            return "THROW_IN"

    def resolve_set_piece(self, state, attacking_team, defending_team):
        """
        Resets player positions based on the set piece type.
        
        Args:
            state: str - Set piece type (CORNER, GOAL_KICK, THROW_IN)
            attacking_team: Team object
            defending_team: Team object
            
        Returns:
            list: New ball position [x, y]
        """
        ball_pos = [0, 0]
        
        if state == "CORNER":
            # 1. Place Ball at corner flag
            corner_side = 0 if np.random.random() < 0.5 else 68
            ball_pos = [105, corner_side]
            
            # 2. Move players into the box (Scramble setup)
            logger.info(">>> Setting up Corner Kick...")
            for p in attacking_team.players:
                if p.position_role != 'GK':  # GK stays back
                    p.position = [np.random.uniform(95, 104), np.random.uniform(20, 48)]
            
            for p in defending_team.players:
                if p.position_role == 'GK':
                    p.position = [104, 34]  # On line
                else:
                    p.position = [np.random.uniform(95, 104), np.random.uniform(20, 48)]
                    
        elif state == "GOAL_KICK":
            # Reset to defensive formation
            logger.info(">>> Goal Kick Reset...")
            ball_pos = [5, 34]
            # (Add logic to reset teams to default formation here)
            
        return ball_pos


# ============================================================================
# SUPPORTING CLASSES
# ============================================================================

@dataclass
class Player:
    """Represents a player on the field"""
    name: str
    position: List[float] = field(default_factory=lambda: [0.0, 0.0])  # [x, y]
    position_role: str = "MF"  # GK, DEF, MF, FWD
    interception_stat: float = 0.5  # 0-1 skill level for interceptions
    
    def __repr__(self):
        return f"Player({self.name}, role={self.position_role}, pos={self.position})"


@dataclass
class Team:
    """Represents a team with players"""
    name: str
    players: List[Player] = field(default_factory=list)
    
    def __repr__(self):
        return f"Team({self.name}, {len(self.players)} players)"


@dataclass
class Ball:
    """Represents the ball"""
    position: List[float] = field(default_factory=lambda: [52.5, 34.0])  # Center of pitch
    
    def __repr__(self):
        return f"Ball(pos={self.position})"


# ============================================================================
# PART 3: MATCH SIMULATOR (Integration)
# ============================================================================

class MatchSimulator:
    """
    Main simulation engine that integrates physics and set pieces.
    Provides training data for Transformer models.
    """
    
    def __init__(self, home_team: Team, away_team: Team):
        self.home_team = home_team
        self.away_team = away_team
        self.ball = Ball()
        self.possession_team = home_team
        self.physics_engine = PhysicsEngine()
        self.set_piece_manager = SetPieceManager()
        self.events = []  # Training data log
        
    def simulate_step(self, action: str, target_pos: Optional[List[float]] = None):
        """
        Simulates one action step in the match.
        
        Args:
            action: str - Action type ("PASS", "SHOOT", "DRIBBLE", etc.)
            target_pos: Optional[List[float]] - Target position for pass/shot
            
        Returns:
            Dict: Event data for training
        """
        event = {
            "action": action,
            "ball_pos_before": self.ball.position.copy(),
            "possession_before": self.possession_team.name,
            "game_state": self.set_piece_manager.game_state
        }
        
        # Determine defending team
        defending_team = self.away_team if self.possession_team == self.home_team else self.home_team
        
        # --- ACTION HANDLING ---
        if action == "PASS" and target_pos is not None:
            # NEW: Check Physics before moving ball
            intercepted, defender = self.physics_engine.check_interception(
                self.ball.position, target_pos, defending_team.players
            )
            
            if intercepted:
                logger.info(f"!! Intercepted by {defender.name} !!")
                self.possession_team = defending_team  # TURNOVER!
                self.ball.position = defender.position.copy()  # Ball goes to defender
                event["result"] = "INTERCEPTED"
                event["interceptor"] = defender.name
            else:
                self.ball.position = target_pos.copy()  # Success
                event["result"] = "SUCCESS"
                
        elif action == "SHOOT" and target_pos is not None:
            # Simplified shooting logic
            self.ball.position = target_pos.copy()
            event["result"] = "SHOT"
            
        elif action == "DRIBBLE" and target_pos is not None:
            # Move ball with player
            self.ball.position = target_pos.copy()
            event["result"] = "DRIBBLE"
        
        # --- BOUNDARY CHECK ---
        new_state = self.set_piece_manager.check_boundaries(
            self.ball.position[0], self.ball.position[1]
        )
        
        if new_state != "OPEN_PLAY":
            # Handle Stop in Play
            self.ball.position = self.set_piece_manager.resolve_set_piece(
                new_state, self.possession_team, defending_team
            )
            self.set_piece_manager.game_state = new_state
            event["set_piece"] = new_state
        else:
            self.set_piece_manager.game_state = "OPEN_PLAY"
        
        event["ball_pos_after"] = self.ball.position.copy()
        event["possession_after"] = self.possession_team.name
        
        # Log event for training
        self.events.append(event)
        
        return event
    
    def get_training_data(self) -> List[Dict]:
        """Returns accumulated events for model training"""
        return self.events
    
    def reset(self):
        """Reset match to initial state"""
        self.ball = Ball()
        self.possession_team = self.home_team
        self.set_piece_manager.game_state = "OPEN_PLAY"
        self.events = []


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def create_sample_team(name: str, num_players: int = 11) -> Team:
    """Create a sample team with random player positions"""
    players = []
    
    # Create goalkeeper
    players.append(Player(
        name=f"{name}_GK",
        position=[5.0 if name == "Home" else 100.0, 34.0],
        position_role="GK"
    ))
    
    # Create field players
    for i in range(num_players - 1):
        if i < 4:
            role = "DEF"
            x_pos = np.random.uniform(15, 30) if name == "Home" else np.random.uniform(75, 90)
        elif i < 7:
            role = "MF"
            x_pos = np.random.uniform(35, 50) if name == "Home" else np.random.uniform(55, 70)
        else:
            role = "FWD"
            x_pos = np.random.uniform(55, 70) if name == "Home" else np.random.uniform(35, 50)
        
        y_pos = np.random.uniform(10, 58)
        
        players.append(Player(
            name=f"{name}_P{i+1}",
            position=[x_pos, y_pos],
            position_role=role,
            interception_stat=np.random.uniform(0.3, 0.8)
        ))
    
    return Team(name=name, players=players)


if __name__ == "__main__":
    # Create teams
    home = create_sample_team("Home")
    away = create_sample_team("Away")
    
    # Initialize simulator
    simulator = MatchSimulator(home, away)
    
    logger.info("=== Football Match Simulation Started ===")
    logger.info(f"Home Team: {len(home.players)} players")
    logger.info(f"Away Team: {len(away.players)} players")
    logger.info(f"Ball position: {simulator.ball.position}")
    
    # Simulate some actions
    logger.info("\n--- Simulating Pass 1 ---")
    event1 = simulator.simulate_step("PASS", target_pos=[60.0, 40.0])
    logger.info(f"Event: {event1}")
    
    logger.info("\n--- Simulating Pass 2 (through defenders) ---")
    event2 = simulator.simulate_step("PASS", target_pos=[80.0, 35.0])
    logger.info(f"Event: {event2}")
    
    logger.info("\n--- Simulating Shot (out of bounds) ---")
    event3 = simulator.simulate_step("SHOOT", target_pos=[110.0, 34.0])
    logger.info(f"Event: {event3}")
    
    logger.info("\n--- Training Data Summary ---")
    training_data = simulator.get_training_data()
    logger.info(f"Total events logged: {len(training_data)}")
    
    for i, event in enumerate(training_data, 1):
        logger.info(f"Event {i}: {event['action']} - {event.get('result', 'N/A')}")
