from enum import IntEnum
from typing import List, Tuple, Dict
from collections import Counter
from .cards import Card, Rank, Suit
from .equity_tables import get_preflop_equity

class HandRank(IntEnum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class HandEvaluator:
    def __init__(self):
        # Pre-computed lookup tables could be loaded here
        self.preflop_equity_table: Dict[Tuple[Card, Card], float] = {}
        # TODO: Load actual equity tables
    
    def evaluate_hand(self, cards: List[Card]) -> Tuple[HandRank, List[Card]]:
        """
        Evaluate the best 5-card hand from given cards.
        Returns tuple of (HandRank, kicker_cards).
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate a hand")
        
        # Check for flush
        suits_count = Counter(card.suit for card in cards)
        flush_suit = next((suit for suit, count in suits_count.items() if count >= 5), None)
        
        # Get all possible straights
        values = sorted(set(card.rank.value_int for card in cards))
        straights = []
        
        # Handle Ace-low straight
        if values[-1] == 14:  # If we have an Ace
            values.append(1)  # Add it as a low Ace
        
        for i in range(len(values) - 4):
            if values[i:i+5] == list(range(values[i], values[i] + 5)):
                straights.append(values[i:i+5])
        
        # Check for straight flush
        if flush_suit and straights:
            flush_cards = [card for card in cards if card.suit == flush_suit]
            flush_values = sorted(set(card.rank.value_int for card in flush_cards))
            
            if 14 in flush_values:  # If we have an Ace
                flush_values.append(1)
            
            for i in range(len(flush_values) - 4):
                if flush_values[i:i+5] == list(range(flush_values[i], flush_values[i] + 5)):
                    straight_flush_cards = sorted(
                        [card for card in flush_cards if card.rank.value_int in flush_values[i:i+5]],
                        key=lambda x: x.rank.value_int
                    )
                    if straight_flush_cards[-1].rank == Rank.ACE and straight_flush_cards[-1].suit == flush_suit:
                        return HandRank.ROYAL_FLUSH, straight_flush_cards
                    return HandRank.STRAIGHT_FLUSH, straight_flush_cards
        
        # Count ranks
        rank_count = Counter(card.rank for card in cards)
        
        # Four of a kind
        if 4 in rank_count.values():
            rank = next(r for r, count in rank_count.items() if count == 4)
            kickers = [card for card in cards if card.rank != rank]
            return HandRank.FOUR_OF_A_KIND, sorted(
                [card for card in cards if card.rank == rank] + [max(kickers, key=lambda x: x.rank.value_int)],
                key=lambda x: x.rank.value_int
            )
        
        # Full house
        if 3 in rank_count.values() and 2 in rank_count.values():
            three_rank = next(r for r, count in rank_count.items() if count == 3)
            pair_rank = next(r for r, count in rank_count.items() if count == 2)
            return HandRank.FULL_HOUSE, sorted(
                [card for card in cards if card.rank in (three_rank, pair_rank)],
                key=lambda x: (x.rank == three_rank, x.rank.value_int),
                reverse=True
            )[:5]
        
        # Flush
        if flush_suit:
            flush_cards = sorted(
                [card for card in cards if card.suit == flush_suit],
                key=lambda x: x.rank.value_int,
                reverse=True
            )[:5]
            return HandRank.FLUSH, flush_cards
        
        # Straight
        if straights:
            straight = max(straights)
            straight_cards = sorted(
                [card for card in cards if card.rank.value_int in straight],
                key=lambda x: x.rank.value_int
            )
            return HandRank.STRAIGHT, straight_cards
        
        # Three of a kind
        if 3 in rank_count.values():
            rank = next(r for r, count in rank_count.items() if count == 3)
            kickers = sorted(
                [card for card in cards if card.rank != rank],
                key=lambda x: x.rank.value_int,
                reverse=True
            )[:2]
            return HandRank.THREE_OF_A_KIND, sorted(
                [card for card in cards if card.rank == rank] + kickers,
                key=lambda x: x.rank.value_int
            )
        
        # Two pair
        pairs = [r for r, count in rank_count.items() if count == 2]
        if len(pairs) >= 2:
            pairs = sorted(pairs, key=lambda x: x.value_int, reverse=True)[:2]
            pair_cards = [card for card in cards if card.rank in pairs]
            kickers = [card for card in cards if card.rank not in pairs]
            return HandRank.TWO_PAIR, sorted(
                pair_cards + [max(kickers, key=lambda x: x.rank.value_int)],
                key=lambda x: x.rank.value_int
            )
        
        # One pair
        if 2 in rank_count.values():
            rank = next(r for r, count in rank_count.items() if count == 2)
            kickers = sorted(
                [card for card in cards if card.rank != rank],
                key=lambda x: x.rank.value_int,
                reverse=True
            )[:3]
            return HandRank.PAIR, sorted(
                [card for card in cards if card.rank == rank] + kickers,
                key=lambda x: x.rank.value_int
            )
        
        # High card
        return HandRank.HIGH_CARD, sorted(
            cards,
            key=lambda x: x.rank.value_int,
            reverse=True
        )[:5]
    
    def get_preflop_equity(self, hand: Tuple[Card, Card]) -> float:
        """
        Get pre-flop equity for a given starting hand.
        Returns a value between 0 and 1 representing win probability.
        """
        return get_preflop_equity(hand)
    
    def evaluate_hand_with_equity(self, cards: List[Card]) -> Tuple[HandRank, List[Card], float]:
        """
        Evaluate the best 5-card hand from given cards and calculate its equity.
        Returns tuple of (HandRank, kicker_cards, equity).
        """
        hand_rank, kicker_cards = self.evaluate_hand(cards)
        equity = self.get_preflop_equity((cards[0], cards[1]))
        return hand_rank, kicker_cards, equity 