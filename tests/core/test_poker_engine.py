import pytest
from maverick.core import (
    Card, Rank, Suit, Deck, HandRank, HandEvaluator,
    get_preflop_equity, get_hand_notation, PREFLOP_EQUITY_MAP
)

class TestCard:
    def test_card_creation(self):
        card = Card(Rank.ACE, Suit.HEARTS)
        assert card.rank == Rank.ACE
        assert card.suit == Suit.HEARTS
        assert str(card) == "A♥"
    
    def test_card_equality(self):
        card1 = Card(Rank.ACE, Suit.HEARTS)
        card2 = Card(Rank.ACE, Suit.HEARTS)
        card3 = Card(Rank.KING, Suit.HEARTS)
        
        assert card1 == card2
        assert card1 != card3
        assert hash(card1) == hash(card2)
        assert hash(card1) != hash(card3)

class TestDeck:
    def test_deck_creation(self):
        deck = Deck()
        assert len(deck.cards) == 52
        
        # Check all cards are unique
        card_set = set(deck.cards)
        assert len(card_set) == 52
    
    def test_deck_draw(self):
        deck = Deck()
        drawn = deck.draw(2)
        assert len(drawn) == 2
        assert len(deck.cards) == 50
        
        # Test drawing too many cards
        with pytest.raises(ValueError):
            deck.draw(51)
    
    def test_deck_shuffle(self):
        deck1 = Deck()
        deck2 = Deck()
        # Note: There's a tiny chance this could fail randomly
        assert deck1.cards != deck2.cards

class TestHandEvaluation:
    @pytest.fixture
    def evaluator(self):
        return HandEvaluator()
    
    def test_royal_flush(self, evaluator):
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.HEARTS),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.TEN, Suit.HEARTS),
            Card(Rank.TWO, Suit.CLUBS),  # Extra cards
            Card(Rank.THREE, Suit.DIAMONDS)
        ]
        rank, hand = evaluator.evaluate_hand(cards)
        assert rank == HandRank.ROYAL_FLUSH
        assert len(hand) == 5
    
    def test_straight_flush(self, evaluator):
        cards = [
            Card(Rank.NINE, Suit.CLUBS),
            Card(Rank.EIGHT, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.CLUBS),
            Card(Rank.SIX, Suit.CLUBS),
            Card(Rank.FIVE, Suit.CLUBS)
        ]
        rank, hand = evaluator.evaluate_hand(cards)
        assert rank == HandRank.STRAIGHT_FLUSH
        assert len(hand) == 5
    
    def test_four_of_a_kind(self, evaluator):
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.ACE, Suit.CLUBS),
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.KING, Suit.HEARTS)
        ]
        rank, hand = evaluator.evaluate_hand(cards)
        assert rank == HandRank.FOUR_OF_A_KIND
        assert len(hand) == 5
    
    def test_full_house(self, evaluator):
        cards = [
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.ACE, Suit.DIAMONDS),
            Card(Rank.ACE, Suit.CLUBS),
            Card(Rank.KING, Suit.HEARTS),
            Card(Rank.KING, Suit.DIAMONDS)
        ]
        rank, hand = evaluator.evaluate_hand(cards)
        assert rank == HandRank.FULL_HOUSE
        assert len(hand) == 5

class TestEquityCalculations:
    def test_pocket_pairs(self):
        aces = (Card(Rank.ACE, Suit.HEARTS), Card(Rank.ACE, Suit.DIAMONDS))
        kings = (Card(Rank.KING, Suit.HEARTS), Card(Rank.KING, Suit.DIAMONDS))
        
        # Test pocket aces have higher equity than pocket kings
        assert get_preflop_equity(aces) > get_preflop_equity(kings)
        
        # Test specific equity values
        assert abs(get_preflop_equity(aces) - 0.852) < 0.001
        assert abs(get_preflop_equity(kings) - 0.823) < 0.001
    
    def test_suited_vs_offsuit(self):
        ak_suited = (Card(Rank.ACE, Suit.HEARTS), Card(Rank.KING, Suit.HEARTS))
        ak_offsuit = (Card(Rank.ACE, Suit.HEARTS), Card(Rank.KING, Suit.DIAMONDS))
        
        # Test suited hands have higher equity than offsuit
        assert get_preflop_equity(ak_suited) > get_preflop_equity(ak_offsuit)
    
    def test_hand_notation(self):
        # Test pocket pairs
        aces = (Card(Rank.ACE, Suit.HEARTS), Card(Rank.ACE, Suit.DIAMONDS))
        assert get_hand_notation(aces[0], aces[1]) == "AA"
        
        # Test suited hands
        ak_suited = (Card(Rank.ACE, Suit.HEARTS), Card(Rank.KING, Suit.HEARTS))
        assert get_hand_notation(ak_suited[0], ak_suited[1]) == "AKs"
        
        # Test offsuit hands
        ak_offsuit = (Card(Rank.ACE, Suit.HEARTS), Card(Rank.KING, Suit.DIAMONDS))
        assert get_hand_notation(ak_offsuit[0], ak_offsuit[1]) == "AKo"
        
        # Test order doesn't matter
        ka_offsuit = (Card(Rank.KING, Suit.DIAMONDS), Card(Rank.ACE, Suit.HEARTS))
        assert get_hand_notation(ka_offsuit[0], ka_offsuit[1]) == "AKo"

def test_preflop_equity_map_consistency():
    # Test that all pocket pairs are present
    for rank in Rank:
        pair_notation = f"{rank.value}{rank.value}"
        assert pair_notation in PREFLOP_EQUITY_MAP
    
    # Test some key hands have correct relative values
    assert PREFLOP_EQUITY_MAP['AA'] > PREFLOP_EQUITY_MAP['KK']  # Aces better than Kings
    assert PREFLOP_EQUITY_MAP['AKs'] > PREFLOP_EQUITY_MAP['AKo']  # Suited better than offsuit
    assert PREFLOP_EQUITY_MAP['AKo'] > PREFLOP_EQUITY_MAP['QJo']  # Higher ranks better than lower 