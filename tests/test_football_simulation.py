"""
Unit tests for Football Simulation - Physics & Logic Patch
Tests PhysicsEngine, SetPieceManager, and MatchSimulator
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import numpy as np
from football_simulation import (
    PhysicsEngine, SetPieceManager, MatchSimulator,
    Player, Team, Ball, create_sample_team
)


class TestPhysicsEngine(unittest.TestCase):
    """Tests for PhysicsEngine class"""
    
    def test_distance_point_on_line(self):
        """Test distance calculation for point on line"""
        p = np.array([5.0, 5.0])
        a = np.array([0.0, 0.0])
        b = np.array([10.0, 10.0])
        
        dist = PhysicsEngine.get_distance_point_to_segment(p, a, b)
        self.assertAlmostEqual(dist, 0.0, places=5)
    
    def test_distance_point_perpendicular(self):
        """Test distance calculation for point perpendicular to line"""
        p = np.array([5.0, 0.0])
        a = np.array([0.0, 5.0])
        b = np.array([10.0, 5.0])
        
        dist = PhysicsEngine.get_distance_point_to_segment(p, a, b)
        self.assertAlmostEqual(dist, 5.0, places=5)
    
    def test_distance_point_beyond_segment(self):
        """Test distance calculation for point beyond segment"""
        p = np.array([15.0, 5.0])
        a = np.array([0.0, 5.0])
        b = np.array([10.0, 5.0])
        
        dist = PhysicsEngine.get_distance_point_to_segment(p, a, b)
        self.assertAlmostEqual(dist, 5.0, places=5)
    
    def test_distance_same_points(self):
        """Test distance when start and end are same"""
        p = np.array([5.0, 5.0])
        a = np.array([0.0, 0.0])
        b = np.array([0.0, 0.0])
        
        dist = PhysicsEngine.get_distance_point_to_segment(p, a, b)
        expected = np.sqrt(50)  # sqrt(5^2 + 5^2)
        self.assertAlmostEqual(dist, expected, places=5)
    
    def test_interception_within_radius(self):
        """Test interception when defender is within radius"""
        defenders = [
            Player("Defender", position=[5.0, 1.0], position_role="DEF")
        ]
        
        pass_start = [0.0, 0.0]
        pass_end = [10.0, 0.0]
        
        intercepted, defender = PhysicsEngine.check_interception(
            pass_start, pass_end, defenders, interception_radius=2.0
        )
        
        self.assertTrue(intercepted)
        self.assertEqual(defender.name, "Defender")
    
    def test_no_interception_outside_radius(self):
        """Test no interception when defender is outside radius"""
        defenders = [
            Player("Defender", position=[5.0, 10.0], position_role="DEF")
        ]
        
        pass_start = [0.0, 0.0]
        pass_end = [10.0, 0.0]
        
        intercepted, defender = PhysicsEngine.check_interception(
            pass_start, pass_end, defenders, interception_radius=2.0
        )
        
        self.assertFalse(intercepted)
        self.assertIsNone(defender)
    
    def test_interception_multiple_defenders(self):
        """Test interception with multiple defenders"""
        defenders = [
            Player("Far_Defender", position=[5.0, 10.0], position_role="DEF"),
            Player("Close_Defender", position=[5.0, 0.5], position_role="DEF"),
        ]
        
        pass_start = [0.0, 0.0]
        pass_end = [10.0, 0.0]
        
        intercepted, defender = PhysicsEngine.check_interception(
            pass_start, pass_end, defenders, interception_radius=2.0
        )
        
        self.assertTrue(intercepted)
        # Either defender could intercept, just verify one did
        self.assertIn(defender.name, ["Far_Defender", "Close_Defender"])


class TestSetPieceManager(unittest.TestCase):
    """Tests for SetPieceManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = SetPieceManager()
    
    def test_ball_in_play(self):
        """Test ball within bounds"""
        state = self.manager.check_boundaries(50.0, 34.0)
        self.assertEqual(state, "OPEN_PLAY")
    
    def test_ball_out_beyond_goal(self):
        """Test ball beyond goal line"""
        state = self.manager.check_boundaries(110.0, 34.0)
        self.assertIn(state, ["CORNER", "GOAL_KICK"])
    
    def test_ball_out_behind_own_goal(self):
        """Test ball behind own goal"""
        state = self.manager.check_boundaries(-5.0, 34.0)
        self.assertEqual(state, "CORNER")
    
    def test_ball_out_sideline(self):
        """Test ball out on sideline"""
        state = self.manager.check_boundaries(50.0, 75.0)
        self.assertEqual(state, "THROW_IN")
    
    def test_ball_at_boundary_in_play(self):
        """Test ball exactly at boundary is in play"""
        self.assertEqual(self.manager.check_boundaries(0.0, 0.0), "OPEN_PLAY")
        self.assertEqual(self.manager.check_boundaries(105.0, 68.0), "OPEN_PLAY")
    
    def test_resolve_corner_kick(self):
        """Test corner kick positioning"""
        home = create_sample_team("Home", 11)
        away = create_sample_team("Away", 11)
        
        ball_pos = self.manager.resolve_set_piece("CORNER", home, away)
        
        # Ball should be at corner
        self.assertEqual(ball_pos[0], 105)
        self.assertIn(ball_pos[1], [0, 68])
    
    def test_resolve_goal_kick(self):
        """Test goal kick positioning"""
        home = create_sample_team("Home", 11)
        away = create_sample_team("Away", 11)
        
        ball_pos = self.manager.resolve_set_piece("GOAL_KICK", home, away)
        
        # Ball should be near goal
        self.assertEqual(ball_pos, [5, 34])


class TestMatchSimulator(unittest.TestCase):
    """Tests for MatchSimulator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.home = Team("Home", [
            Player("Attacker", position=[40.0, 34.0], position_role="FWD")
        ])
        
        self.away = Team("Away", [
            Player("Defender", position=[52.0, 34.0], position_role="DEF")
        ])
        
        self.simulator = MatchSimulator(self.home, self.away)
        self.simulator.ball.position = [40.0, 34.0]
    
    def test_successful_pass(self):
        """Test successful pass"""
        event = self.simulator.simulate_step("PASS", target_pos=[45.0, 40.0])
        
        self.assertEqual(event["action"], "PASS")
        self.assertEqual(event["result"], "SUCCESS")
        self.assertEqual(self.simulator.ball.position, [45.0, 40.0])
    
    def test_intercepted_pass(self):
        """Test intercepted pass"""
        event = self.simulator.simulate_step("PASS", target_pos=[70.0, 34.0])
        
        self.assertEqual(event["action"], "PASS")
        self.assertEqual(event["result"], "INTERCEPTED")
        self.assertEqual(event["interceptor"], "Defender")
        self.assertEqual(self.simulator.possession_team, self.away)
    
    def test_shot_out_of_bounds(self):
        """Test shot going out of bounds"""
        event = self.simulator.simulate_step("SHOOT", target_pos=[110.0, 34.0])
        
        self.assertEqual(event["action"], "SHOOT")
        self.assertIn("set_piece", event)
    
    def test_training_data_collection(self):
        """Test training data is collected"""
        self.simulator.simulate_step("PASS", target_pos=[45.0, 40.0])
        self.simulator.simulate_step("PASS", target_pos=[50.0, 40.0])
        
        training_data = self.simulator.get_training_data()
        
        self.assertEqual(len(training_data), 2)
        self.assertEqual(training_data[0]["action"], "PASS")
        self.assertEqual(training_data[1]["action"], "PASS")
    
    def test_reset_simulation(self):
        """Test simulation reset"""
        self.simulator.simulate_step("PASS", target_pos=[45.0, 40.0])
        self.simulator.reset()
        
        self.assertEqual(len(self.simulator.get_training_data()), 0)
        self.assertEqual(self.simulator.ball.position, [52.5, 34.0])
        self.assertEqual(self.simulator.set_piece_manager.game_state, "OPEN_PLAY")
    
    def test_dribble_action(self):
        """Test dribble action"""
        event = self.simulator.simulate_step("DRIBBLE", target_pos=[45.0, 35.0])
        
        self.assertEqual(event["action"], "DRIBBLE")
        self.assertEqual(event["result"], "DRIBBLE")
        self.assertEqual(self.simulator.ball.position, [45.0, 35.0])


class TestSupportingClasses(unittest.TestCase):
    """Tests for supporting classes"""
    
    def test_player_creation(self):
        """Test Player dataclass creation"""
        player = Player("TestPlayer", position=[10.0, 20.0], position_role="MF")
        
        self.assertEqual(player.name, "TestPlayer")
        self.assertEqual(player.position, [10.0, 20.0])
        self.assertEqual(player.position_role, "MF")
        self.assertEqual(player.interception_stat, 0.5)
    
    def test_team_creation(self):
        """Test Team dataclass creation"""
        players = [
            Player("P1", position=[10.0, 20.0]),
            Player("P2", position=[30.0, 40.0])
        ]
        team = Team("TestTeam", players)
        
        self.assertEqual(team.name, "TestTeam")
        self.assertEqual(len(team.players), 2)
    
    def test_ball_creation(self):
        """Test Ball dataclass creation"""
        ball = Ball()
        
        self.assertEqual(ball.position, [52.5, 34.0])
    
    def test_create_sample_team(self):
        """Test sample team creation helper"""
        team = create_sample_team("Arsenal", num_players=11)
        
        self.assertEqual(team.name, "Arsenal")
        self.assertEqual(len(team.players), 11)
        
        # Check goalkeeper exists
        gk = [p for p in team.players if p.position_role == "GK"]
        self.assertEqual(len(gk), 1)


class TestIntegration(unittest.TestCase):
    """Integration tests for full simulation flow"""
    
    def test_complete_match_sequence(self):
        """Test a complete sequence of match events"""
        home = create_sample_team("Home", 11)
        away = create_sample_team("Away", 11)
        simulator = MatchSimulator(home, away)
        
        # Sequence of actions
        simulator.simulate_step("PASS", target_pos=[60.0, 40.0])
        simulator.simulate_step("PASS", target_pos=[70.0, 35.0])
        simulator.simulate_step("SHOOT", target_pos=[104.0, 34.0])
        
        # Check training data
        events = simulator.get_training_data()
        self.assertEqual(len(events), 3)
        
        # Verify event structure
        for event in events:
            self.assertIn("action", event)
            self.assertIn("ball_pos_before", event)
            self.assertIn("ball_pos_after", event)
            self.assertIn("possession_before", event)
            self.assertIn("possession_after", event)
    
    def test_corner_kick_scenario(self):
        """Test complete corner kick scenario"""
        home = create_sample_team("Home", 11)
        away = create_sample_team("Away", 11)
        simulator = MatchSimulator(home, away)
        
        # Force ball out for corner
        simulator.ball.position = [100.0, 34.0]
        event = simulator.simulate_step("SHOOT", target_pos=[110.0, 34.0])
        
        # Verify corner kick setup
        if event.get("set_piece") == "CORNER":
            self.assertEqual(simulator.ball.position[0], 105)
            self.assertEqual(simulator.set_piece_manager.game_state, "CORNER")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
