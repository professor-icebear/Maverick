import pytest
from maverick.core import Card, Rank, Suit, OutsCalculator

class TestOutsCalculator:
    @pytest.fixture
    def calculator(self):
        return OutsCalculator()
    
    def test_flush_draw(self, calculator):
        # Test flush draw (4 hearts)
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS)
        ]
        community_cards = [
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TWO, Suit.CLUBS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        flush_draws = [d for d in draws if d.draw_type == 'flush_draw']
        
        assert len(flush_draws) == 1
        assert flush_draws[0].outs == 9
        assert len(flush_draws[0].potential_cards) == 9
    
    def test_open_ended_straight_draw(self, calculator):
        # Test open-ended straight draw (9-T-J-Q)
        player_hand = [
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.DIAMONDS)
        ]
        community_cards = [
            Card(Rank.TEN, Suit.CLUBS),
            Card(Rank.NINE, Suit.SPADES),
            Card(Rank.TWO, Suit.HEARTS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        straight_draws = [d for d in draws if d.draw_type == 'open_straight_draw']
        
        assert len(straight_draws) == 1
        assert straight_draws[0].outs == 8
        assert len(straight_draws[0].potential_cards) == 8  # 4 Kings and 4 Eights
    
    def test_gutshot_straight_draw(self, calculator):
        # Test gutshot straight draw (9-J-Q-K missing 10)
        player_hand = [
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.DIAMONDS)
        ]
        community_cards = [
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.NINE, Suit.SPADES),
            Card(Rank.TWO, Suit.HEARTS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        gutshot_draws = [d for d in draws if d.draw_type == 'gutshot_straight_draw']
        
        assert len(gutshot_draws) == 1
        assert gutshot_draws[0].outs == 4
        assert len(gutshot_draws[0].potential_cards) == 4  # 4 Tens
    
    def test_set_draw(self, calculator):
        # Test set draw with pocket pair
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS)
        ]
        community_cards = [
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        set_draws = [d for d in draws if d.draw_type == 'pair_to_set']
        
        assert len(set_draws) == 1
        assert set_draws[0].outs == 2
        assert len(set_draws[0].potential_cards) == 2  # 2 remaining Aces
    
    def test_overcard_draw(self, calculator):
        # Test overcard draw (AK preflop)
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS)
        ]
        community_cards = []  # Preflop
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        overcard_draws = [d for d in draws if d.draw_type == 'two_overcards']
        
        assert len(overcard_draws) == 1
        assert overcard_draws[0].outs == 6
        assert len(overcard_draws[0].potential_cards) == 6  # 3 Aces and 3 Kings
    
    def test_combined_draws(self, calculator):
        # Test combined flush and straight draw
        player_hand = [
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TEN, Suit.HEARTS)
        ]
        community_cards = [
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.TWO, Suit.CLUBS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        
        # Should identify both flush and straight draws
        draw_types = {d.draw_type for d in draws}
        assert 'flush_draw' in draw_types
        assert 'open_straight_draw' in draw_types
        
        # Total outs should account for overlap
        assert total_outs < sum(d.outs for d in draws)  # Some cards complete multiple draws 
    
    def test_trips_to_full_house(self, calculator):
        # Test three of a kind drawing to full house
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS)
        ]
        community_cards = [
            Card(Rank.ACE, Suit.CLUBS),
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.QUEEN, Suit.HEARTS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        full_house_draws = [d for d in draws if d.draw_type == 'trips_to_full_house']
        
        assert len(full_house_draws) == 1
        assert full_house_draws[0].outs == 6  # 3 Kings and 3 Queens
    
    def test_two_pair_to_full_house(self, calculator):
        # Test two pair drawing to full house
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS)
        ]
        community_cards = [
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.QUEEN, Suit.HEARTS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        full_house_draws = [d for d in draws if d.draw_type == 'two_pair_to_full_house']
        
        assert len(full_house_draws) == 2  # One for each pair
        assert sum(d.outs for d in full_house_draws) == 4  # 2 Aces + 2 Kings
    
    def test_set_to_quads(self, calculator):
        # Test three of a kind drawing to quads
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS)
        ]
        community_cards = [
            Card(Rank.ACE, Suit.CLUBS),
            Card(Rank.KING, Suit.SPADES),
            Card(Rank.QUEEN, Suit.HEARTS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        quad_draws = [d for d in draws if d.draw_type == 'set_to_quads']
        
        assert len(quad_draws) == 1
        assert quad_draws[0].outs == 1  # Last Ace
    
    def test_pair_to_two_pair(self, calculator):
        # Test one pair drawing to two pair
        player_hand = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS)
        ]
        community_cards = [
            Card(Rank.KING, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        two_pair_draws = [d for d in draws if d.draw_type == 'pair_to_two_pair']
        
        assert len(two_pair_draws) == 1
        assert two_pair_draws[0].outs == 9  # 3 each of King, Queen, Jack
    
    def test_combo_pair_gutshot(self, calculator):
        # Test combination of pair and gutshot straight draw
        player_hand = [
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.JACK, Suit.DIAMONDS)
        ]
        community_cards = [
            Card(Rank.NINE, Suit.CLUBS),
            Card(Rank.QUEEN, Suit.SPADES),
            Card(Rank.KING, Suit.HEARTS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        combo_draws = [d for d in draws if d.draw_type == 'pair_plus_gutshot']
        
        assert len(combo_draws) == 1
        assert combo_draws[0].outs == 4  # 4 Tens for the gutshot
    
    def test_multiple_draws_overlap(self, calculator):
        # Test that overlapping draws are counted correctly
        player_hand = [
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TEN, Suit.HEARTS)
        ]
        community_cards = [
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.NINE, Suit.CLUBS)
        ]
        
        total_outs, draws = calculator.calculate_outs(player_hand, community_cards)
        
        # Should have flush draw and straight draw
        draw_types = {d.draw_type for d in draws}
        assert 'flush_draw' in draw_types
        assert 'open_straight_draw' in draw_types
        
        # Total outs should be less than sum of individual outs due to overlap
        total_individual_outs = sum(d.outs for d in draws)
        assert total_outs < total_individual_outs 