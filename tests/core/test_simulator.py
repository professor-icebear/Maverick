import pytest
from maverick.core import Card, Rank, Suit, MonteCarloSimulator

class TestMonteCarloSimulator:
    @pytest.fixture
    def simulator(self):
        return MonteCarloSimulator()
    
    def test_simulator_initialization(self, simulator):
        assert simulator.evaluator is not None
        assert len(simulator._suit_map) == 4
        assert len(simulator._rank_map) == 13
    
    def test_remaining_deck_generation(self, simulator):
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS)
        ]
        community_cards = [
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TEN, Suit.HEARTS)
        ]
        
        remaining = simulator._generate_remaining_deck(player_hand, community_cards)
        assert len(remaining) == 47  # 52 - 5 used cards
        
        # Check that none of the used cards are in remaining deck
        used_cards = set(player_hand + community_cards)
        for card in remaining:
            assert card not in used_cards
    
    def test_royal_flush_vs_high_card(self, simulator):
        # Test a case where we have a royal flush vs random cards
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS)
        ]
        community_cards = [
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TEN, Suit.HEARTS)
        ]
        
        # With a royal flush on the board, we should win almost always
        win_prob, stats = simulator.simulate(
            player_hand, 
            community_cards,
            num_simulations=1000,
            show_progress=False
        )
        
        assert win_prob > 0.99  # Should win over 99% of the time
        assert stats['wins'] > 990  # Should win almost all simulations
    
    def test_pocket_aces_preflop(self, simulator):
        # Test pocket aces preflop
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.SPADES)
        ]
        community_cards = []  # Preflop
        
        win_prob, stats = simulator.simulate(
            player_hand,
            community_cards,
            num_simulations=1000,
            show_progress=False
        )
        
        # Pocket aces should win about 85% of the time preflop
        assert 0.80 < win_prob < 0.90
    
    def test_invalid_inputs(self, simulator):
        # Test invalid number of hole cards
        with pytest.raises(ValueError):
            simulator.simulate(
                [Card(Rank.ACE, Suit.HEARTS)],  # Only one card
                [],
                num_simulations=100
            )
        
        # Test too many community cards
        with pytest.raises(ValueError):
            simulator.simulate(
                [Card(Rank.ACE, Suit.HEARTS), Card(Rank.KING, Suit.HEARTS)],
                [Card(Rank.TWO, Suit.HEARTS)] * 6,  # 6 community cards
                num_simulations=100
            ) 