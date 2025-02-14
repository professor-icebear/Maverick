import pytest
from maverick.core import Action, GameState, DecisionEngine

class TestDecisionEngine:
    @pytest.fixture
    def engine(self):
        return DecisionEngine()
    
    @pytest.fixture
    def basic_game_state(self):
        return GameState(
            pot_size=100.0,
            current_bet=20.0,
            stack_size=1000.0,
            position='button',
            num_players=6,
            street='flop'
        )
    
    def test_pot_odds_calculation(self, engine):
        # Basic pot odds calculation
        assert abs(engine.calculate_pot_odds(20, 100) - 0.1666666666666667) < 1e-10
        
        # Zero bet should return 0 pot odds
        assert engine.calculate_pot_odds(0, 100) == 0.0
        
        # Large numbers
        assert abs(engine.calculate_pot_odds(1000, 5000) - 0.1666666666666667) < 1e-10
    
    def test_position_multipliers(self, engine):
        # Test that late position is more aggressive than early
        assert engine.get_position_multiplier('button') > engine.get_position_multiplier('early')
        assert engine.get_position_multiplier('late') > engine.get_position_multiplier('early')
        
        # Test default value for unknown position
        assert engine.get_position_multiplier('unknown') == 1.0
    
    def test_strong_hand_decision(self, engine, basic_game_state):
        # Strong hand should raise or call
        action, bet_size = engine.recommend_move(0.8, basic_game_state)
        assert action in [Action.RAISE, Action.CALL]
        
        if action == Action.RAISE:
            assert bet_size is not None
            assert bet_size > basic_game_state.current_bet
    
    def test_weak_hand_decision(self, engine, basic_game_state):
        # Weak hand should fold if facing a bet
        action, bet_size = engine.recommend_move(0.2, basic_game_state)
        assert action == Action.FOLD
        assert bet_size is None
        
        # Weak hand should check if no bet
        basic_game_state.current_bet = 0
        action, bet_size = engine.recommend_move(0.2, basic_game_state)
        assert action == Action.CHECK
        assert bet_size is None
    
    def test_all_in_decision(self, engine, basic_game_state):
        # Test all-in recommendation with short stack
        basic_game_state.stack_size = 30.0  # Very short stack
        basic_game_state.pot_size = 100.0
        
        action, bet_size = engine.recommend_move(0.7, basic_game_state)
        assert action == Action.ALL_IN
        assert bet_size == basic_game_state.stack_size
    
    def test_strategy_adjustment(self, engine):
        # Test tight strategy
        engine.adjust_strategy('tight')
        assert engine.thresholds['strong_hand'] > 0.7  # Higher threshold for tight play
        
        # Test loose strategy
        engine.adjust_strategy('loose')
        assert engine.thresholds['strong_hand'] < 0.7  # Lower threshold for loose play
        
        # Test aggressive strategy
        engine.adjust_strategy('aggressive')
        assert engine.thresholds['raise_multiplier'] > 2.5  # Bigger raises for aggressive play
    
    def test_positive_ev_call(self, engine, basic_game_state):
        # Test calling with positive expected value
        basic_game_state.current_bet = 20.0
        basic_game_state.pot_size = 100.0
        
        # Win probability > pot odds (0.167)
        action, bet_size = engine.recommend_move(0.5, basic_game_state)
        assert action == Action.CALL
        assert bet_size is None 