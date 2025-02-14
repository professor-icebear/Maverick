import pytest
from maverick.core import Card, Rank, Suit, MonteCarloSimulator, DecisionEngine, GameState, Action

class TestMonteCarloValidation:
    @pytest.fixture
    def simulator(self):
        return MonteCarloSimulator()
    
    @pytest.fixture
    def decision_engine(self):
        return DecisionEngine()
    
    def test_preflop_pocket_pairs(self, simulator):
        """Test pre-flop equities for pocket pairs."""
        # Pocket Aces
        player_hand = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS)
        ]
        win_prob, stats = simulator.simulate(
            player_hand, [], 
            num_simulations=10000,
            num_opponents=5  # Test against 5 opponents
        )
        assert 0.45 <= win_prob <= 0.55  # AA vs 5 random hands ≈ 50%
        
        # Pocket Kings
        player_hand = [
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.KING, Suit.HEARTS)
        ]
        win_prob, stats = simulator.simulate(
            player_hand, [], 
            num_simulations=10000,
            num_opponents=5
        )
        assert 0.40 <= win_prob <= 0.50  # KK vs 5 random hands ≈ 45%
    
    def test_preflop_unpaired_hands(self, simulator):
        """Test pre-flop equities for unpaired hands."""
        # AK suited
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS)
        ]
        win_prob, stats = simulator.simulate(
            player_hand, [], 
            num_simulations=10000,
            num_opponents=5
        )
        assert 0.30 <= win_prob <= 0.40  # AKs vs 5 random hands ≈ 35%
        
        # AK offsuit
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.SPADES)
        ]
        win_prob, stats = simulator.simulate(
            player_hand, [], 
            num_simulations=10000,
            num_opponents=5
        )
        assert 0.25 <= win_prob <= 0.35  # AKo vs 5 random hands ≈ 28%
    
    def test_postflop_straight_draw(self, simulator):
        """Test post-flop scenarios with straight draws."""
        # Open-ended straight draw
        player_hand = [
            Card(Rank.TEN, Suit.SPADES),
            Card(Rank.JACK, Suit.SPADES)
        ]
        community_cards = [
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.TWO, Suit.DIAMONDS),
            Card(Rank.QUEEN, Suit.CLUBS)
        ]
        win_prob, stats = simulator.simulate(
            player_hand, 
            community_cards, 
            num_simulations=10000,
            num_opponents=2  # Test against 2 opponents
        )
        assert 0.35 <= win_prob <= 0.45  # ~38% equity with 8 outs + overcards vs 2 opponents
        
        # Gutshot straight draw
        player_hand = [
            Card(Rank.TEN, Suit.SPADES),
            Card(Rank.JACK, Suit.SPADES)
        ]
        community_cards = [
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.TWO, Suit.DIAMONDS),
            Card(Rank.KING, Suit.CLUBS)
        ]
        win_prob, stats = simulator.simulate(
            player_hand, 
            community_cards,
            num_simulations=10000,
            num_opponents=2
        )
        assert 0.20 <= win_prob <= 0.30  # ~25% equity with 4 outs + overcards vs 2 opponents
    
    def test_postflop_flush_draw(self, simulator):
        """Test post-flop scenarios with flush draws."""
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS)
        ]
        community_cards = [
            Card(Rank.TWO, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.CLUBS)
        ]
        win_prob, stats = simulator.simulate(
            player_hand, 
            community_cards,
            num_simulations=10000,
            num_opponents=2
        )
        assert 0.45 <= win_prob <= 0.55  # ~49% equity with flush draw + overcards vs 2 opponents
    
    def test_decision_logic(self, decision_engine):
        """Test decision logic based on equity and pot odds."""
        # Strong hand should raise
        game_state = GameState(
            pot_size=100.0,
            current_bet=20.0,
            stack_size=1000.0,
            position='button',
            num_players=6,
            street='flop'
        )
        action, bet_size = decision_engine.recommend_move(0.75, game_state)
        assert action == Action.RAISE
        
        # Weak hand vs good pot odds should call
        game_state = GameState(
            pot_size=100.0,
            current_bet=10.0,  # Only need 10 to call into 100
            stack_size=1000.0,
            position='button',
            num_players=6,
            street='flop'
        )
        action, bet_size = decision_engine.recommend_move(0.35, game_state)
        assert action == Action.CALL
        
        # Weak hand vs bad pot odds should fold
        game_state = GameState(
            pot_size=100.0,
            current_bet=50.0,  # Need 50 to call into 100
            stack_size=1000.0,
            position='button',
            num_players=6,
            street='flop'
        )
        action, bet_size = decision_engine.recommend_move(0.25, game_state)
        assert action == Action.FOLD
    
    def test_monte_carlo_convergence(self, simulator):
        """Test that Monte Carlo results converge with more simulations."""
        player_hand = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS)
        ]
        
        # Run with different numbers of simulations
        win_prob_1k, _ = simulator.simulate(
            player_hand, [], 
            num_simulations=1000,
            num_opponents=5
        )
        win_prob_10k, _ = simulator.simulate(
            player_hand, [], 
            num_simulations=10000,
            num_opponents=5
        )
        
        # Results should be similar (within 4%)
        assert abs(win_prob_1k - win_prob_10k) < 0.04  # Allow slightly more variance with 5 opponents
    
    def test_position_based_decisions(self, decision_engine):
        """Test that position affects decision making."""
        equity = 0.55  # Marginal hand
        
        # Early position should be tighter
        game_state_early = GameState(
            pot_size=100.0,
            current_bet=20.0,
            stack_size=1000.0,
            position='early',
            num_players=6,
            street='flop'
        )
        action_early, _ = decision_engine.recommend_move(equity, game_state_early)
        
        # Late position can be looser
        game_state_late = GameState(
            pot_size=100.0,
            current_bet=20.0,
            stack_size=1000.0,
            position='button',
            num_players=6,
            street='flop'
        )
        action_late, _ = decision_engine.recommend_move(equity, game_state_late)
        
        # Should be more aggressive in late position
        assert action_late in [Action.RAISE, Action.CALL]
        if action_early == Action.RAISE:
            assert action_late == Action.RAISE 
    
    def test_performance_improvements(self, simulator):
        """Test performance improvements from vectorization and caching."""
        import time
        
        # Test case: AA vs random hands
        player_hand = [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS)
        ]
        community_cards = []
        num_simulations = 10000
        
        # Test 1: First run (no cache)
        start_time = time.time()
        win_prob1, _ = simulator.simulate(
            player_hand,
            community_cards,
            num_simulations=num_simulations,
            num_opponents=2,
            show_progress=False
        )
        first_run_time = time.time() - start_time
        
        # Test 2: Second run (with cache)
        start_time = time.time()
        win_prob2, _ = simulator.simulate(
            player_hand,
            community_cards,
            num_simulations=num_simulations,
            num_opponents=2,
            show_progress=False
        )
        cached_run_time = time.time() - start_time
        
        # Verify results are consistent
        assert abs(win_prob1 - win_prob2) < 0.01
        
        # Cached run should be significantly faster
        assert cached_run_time < first_run_time / 2
        
        print(f"\nPerformance metrics:")
        print(f"First run time: {first_run_time:.2f} seconds")
        print(f"Cached run time: {cached_run_time:.2f} seconds")
        print(f"Speedup factor: {first_run_time/cached_run_time:.1f}x") 