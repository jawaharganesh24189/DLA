"""
Comprehensive demonstration of the Football Physics & Logic Patch
Shows interceptions, set pieces, and tactical gameplay
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from football_simulation import (
    MatchSimulator, Team, Player, Ball,
    PhysicsEngine, SetPieceManager,
    create_sample_team
)
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def demo_interception():
    """Demonstrate pass interception mechanics"""
    logger.info("\n" + "="*70)
    logger.info("DEMO 1: Pass Interception Mechanics")
    logger.info("="*70)
    
    # Create a simple scenario
    home = Team("Home", [
        Player("Attacker", position=[40.0, 34.0], position_role="FWD")
    ])
    
    away = Team("Away", [
        Player("Defender1", position=[52.0, 34.0], position_role="DEF", interception_stat=0.8),
        Player("Defender2", position=[60.0, 20.0], position_role="DEF", interception_stat=0.7),
        Player("Defender3", position=[60.0, 48.0], position_role="DEF", interception_stat=0.6),
    ])
    
    simulator = MatchSimulator(home, away)
    simulator.ball.position = [40.0, 34.0]
    
    logger.info(f"\nSetup:")
    logger.info(f"  Ball at: {simulator.ball.position}")
    logger.info(f"  Attacker at: {home.players[0].position}")
    logger.info(f"  Defender1 at: {away.players[0].position} (directly in path!)")
    logger.info(f"  Defender2 at: {away.players[1].position}")
    logger.info(f"  Defender3 at: {away.players[2].position}")
    
    # Attempt pass through Defender1 (should be intercepted)
    logger.info(f"\n➤ Attempting pass to [70, 34] - THROUGH Defender1...")
    event = simulator.simulate_step("PASS", target_pos=[70.0, 34.0])
    
    if event.get("result") == "INTERCEPTED":
        logger.info(f"  ✗ INTERCEPTED by {event['interceptor']}!")
        logger.info(f"  Ball now at: {simulator.ball.position}")
        logger.info(f"  Possession: {simulator.possession_team.name}")
    else:
        logger.info(f"  ✓ Pass successful!")
    
    # Reset and try pass around defenders
    simulator.reset()
    simulator.ball.position = [40.0, 34.0]
    logger.info(f"\n➤ Attempting pass to [70, 10] - AROUND defenders...")
    event = simulator.simulate_step("PASS", target_pos=[70.0, 10.0])
    
    if event.get("result") == "INTERCEPTED":
        logger.info(f"  ✗ INTERCEPTED by {event['interceptor']}!")
    else:
        logger.info(f"  ✓ Pass successful! Ball reached target.")
        logger.info(f"  Ball now at: {simulator.ball.position}")


def demo_set_pieces():
    """Demonstrate set piece mechanics"""
    logger.info("\n" + "="*70)
    logger.info("DEMO 2: Set Piece Management")
    logger.info("="*70)
    
    home = create_sample_team("Home", num_players=11)
    away = create_sample_team("Away", num_players=11)
    
    simulator = MatchSimulator(home, away)
    
    # Test 1: Ball goes out for corner
    logger.info(f"\n➤ Test 1: Shooting beyond goal line...")
    simulator.ball.position = [100.0, 34.0]
    logger.info(f"  Ball at: {simulator.ball.position}")
    
    event = simulator.simulate_step("SHOOT", target_pos=[110.0, 34.0])
    logger.info(f"  Result: {event.get('set_piece', 'No set piece')}")
    logger.info(f"  Ball repositioned to: {simulator.ball.position}")
    logger.info(f"  Game state: {simulator.set_piece_manager.game_state}")
    
    # Test 2: Ball goes out for goal kick
    simulator.reset()
    logger.info(f"\n➤ Test 2: Ball behind own goal...")
    simulator.ball.position = [2.0, 34.0]
    
    event = simulator.simulate_step("PASS", target_pos=[-5.0, 34.0])
    if event.get('set_piece'):
        logger.info(f"  Result: {event['set_piece']}")
        logger.info(f"  Ball repositioned to: {simulator.ball.position}")
        logger.info(f"  Game state: {simulator.set_piece_manager.game_state}")
    
    # Test 3: Ball goes out for throw-in
    simulator.reset()
    logger.info(f"\n➤ Test 3: Ball out on sideline...")
    simulator.ball.position = [50.0, 60.0]
    
    event = simulator.simulate_step("PASS", target_pos=[50.0, 75.0])
    if event.get('set_piece'):
        logger.info(f"  Result: {event['set_piece']}")
        logger.info(f"  Game state: {simulator.set_piece_manager.game_state}")


def demo_tactical_scenario():
    """Demonstrate a realistic tactical scenario"""
    logger.info("\n" + "="*70)
    logger.info("DEMO 3: Tactical Gameplay Scenario")
    logger.info("="*70)
    
    # Create teams with specific formations
    home = Team("Arsenal", [
        Player("GK_Ramsdale", position=[5.0, 34.0], position_role="GK"),
        Player("DEF_Saliba", position=[20.0, 25.0], position_role="DEF"),
        Player("DEF_Gabriel", position=[20.0, 43.0], position_role="DEF"),
        Player("MF_Odegaard", position=[50.0, 34.0], position_role="MF"),
        Player("FWD_Saka", position=[70.0, 20.0], position_role="FWD"),
        Player("FWD_Martinelli", position=[70.0, 48.0], position_role="FWD"),
    ])
    
    away = Team("Chelsea", [
        Player("GK_Sanchez", position=[100.0, 34.0], position_role="GK"),
        Player("DEF_Silva", position=[85.0, 25.0], position_role="DEF"),
        Player("DEF_James", position=[85.0, 43.0], position_role="DEF"),
        Player("MF_Enzo", position=[60.0, 34.0], position_role="MF"),
        Player("FWD_Sterling", position=[40.0, 20.0], position_role="FWD"),
    ])
    
    simulator = MatchSimulator(home, away)
    simulator.ball.position = [50.0, 34.0]
    
    logger.info(f"\nScenario: Arsenal (Home) building attack from midfield")
    logger.info(f"  Ball with Odegaard at {simulator.ball.position}")
    logger.info(f"  Options:")
    logger.info(f"    A) Pass to Saka (wing) at [70, 20]")
    logger.info(f"    B) Pass to Martinelli (wing) at [70, 48]")
    logger.info(f"    C) Pass through center to [80, 34] (risky - defender at [85, 25])")
    
    # Option A: Safe pass to wing
    logger.info(f"\n➤ Choosing Option A: Pass to Saka on the wing...")
    event1 = simulator.simulate_step("PASS", target_pos=[70.0, 20.0])
    logger.info(f"  Result: {event1['result']}")
    
    # Continue attack
    if event1['result'] == 'SUCCESS':
        logger.info(f"\n➤ Saka receives and crosses into box...")
        event2 = simulator.simulate_step("PASS", target_pos=[95.0, 34.0])
        logger.info(f"  Result: {event2['result']}")
        
        if event2.get('set_piece'):
            logger.info(f"  Set piece awarded: {event2['set_piece']}")
    
    # Show training data
    logger.info(f"\n➤ Training data captured:")
    for i, event in enumerate(simulator.get_training_data(), 1):
        logger.info(f"  Event {i}: {event['action']} - {event.get('result', 'N/A')}")
        if event.get('interceptor'):
            logger.info(f"           Intercepted by: {event['interceptor']}")


def demo_physics_accuracy():
    """Demonstrate the accuracy of the physics calculations"""
    logger.info("\n" + "="*70)
    logger.info("DEMO 4: Physics Engine Accuracy")
    logger.info("="*70)
    
    # Test distance calculations
    logger.info("\n➤ Testing distance calculations:")
    
    # Test case 1: Point directly on line
    p1 = np.array([5.0, 5.0])
    a1 = np.array([0.0, 0.0])
    b1 = np.array([10.0, 10.0])
    dist1 = PhysicsEngine.get_distance_point_to_segment(p1, a1, b1)
    logger.info(f"  Point [5,5] to line [0,0]->[10,10]: {dist1:.2f} meters (should be ~0)")
    
    # Test case 2: Point perpendicular to line
    p2 = np.array([5.0, 0.0])
    a2 = np.array([0.0, 5.0])
    b2 = np.array([10.0, 5.0])
    dist2 = PhysicsEngine.get_distance_point_to_segment(p2, a2, b2)
    logger.info(f"  Point [5,0] to line [0,5]->[10,5]: {dist2:.2f} meters (should be 5)")
    
    # Test case 3: Point beyond segment
    p3 = np.array([15.0, 5.0])
    a3 = np.array([0.0, 5.0])
    b3 = np.array([10.0, 5.0])
    dist3 = PhysicsEngine.get_distance_point_to_segment(p3, a3, b3)
    logger.info(f"  Point [15,5] to line [0,5]->[10,5]: {dist3:.2f} meters (should be 5)")
    
    logger.info(f"\n➤ Testing interception scenarios:")
    
    # Scenario: Defender in passing lane
    defenders = [
        Player("Close_Defender", position=[5.0, 1.0], position_role="DEF"),
        Player("Far_Defender", position=[5.0, 10.0], position_role="DEF"),
    ]
    
    pass_start = [0.0, 0.0]
    pass_end = [10.0, 0.0]
    
    intercepted, defender = PhysicsEngine.check_interception(
        pass_start, pass_end, defenders, interception_radius=2.0
    )
    
    logger.info(f"  Pass from {pass_start} to {pass_end}")
    logger.info(f"  Close defender at [5, 1] (1 meter from line)")
    logger.info(f"  Far defender at [5, 10] (10 meters from line)")
    logger.info(f"  Interception radius: 2.0 meters")
    logger.info(f"  Result: {'INTERCEPTED' if intercepted else 'SUCCESS'}")
    if intercepted:
        logger.info(f"  Interceptor: {defender.name}")


def main():
    """Run all demonstrations"""
    logger.info("\n" + "█"*70)
    logger.info("  FOOTBALL SIMULATION - PHYSICS & LOGIC PATCH DEMO")
    logger.info("█"*70)
    
    demo_interception()
    demo_set_pieces()
    demo_tactical_scenario()
    demo_physics_accuracy()
    
    logger.info("\n" + "█"*70)
    logger.info("  DEMO COMPLETE")
    logger.info("█"*70)
    logger.info("\nKey Features Demonstrated:")
    logger.info("  ✓ Ray-cast interception prevents unrealistic passes")
    logger.info("  ✓ Set pieces (corners, goal kicks) properly managed")
    logger.info("  ✓ Game state transitions work correctly")
    logger.info("  ✓ Training data captured for AI learning")
    logger.info("  ✓ Tactical gameplay scenarios supported")


if __name__ == "__main__":
    main()
