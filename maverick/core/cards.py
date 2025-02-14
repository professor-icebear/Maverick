from enum import Enum
import numpy as np
from typing import List, Set, Tuple

class Suit(Enum):
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'
    SPADES = '♠'

class Rank(Enum):
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = 'T'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'

    @property
    def value_int(self) -> int:
        """Return numerical value of the rank (2-14, with Ace high)."""
        values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
            '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
        return values[self.value]

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

class Deck:
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset deck to original state with all 52 cards."""
        self.cards = [Card(rank, suit) 
                     for rank in Rank 
                     for suit in Suit]
        self.shuffle()
    
    def shuffle(self):
        """Shuffle the remaining cards in the deck."""
        np.random.shuffle(self.cards)
    
    def draw(self, n: int = 1) -> List[Card]:
        """Draw n cards from the deck."""
        if n > len(self.cards):
            raise ValueError(f"Cannot draw {n} cards, only {len(self.cards)} remaining")
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn

def generate_all_possible_hands() -> Set[Tuple[Card, Card]]:
    """Generate all possible starting hands (1326 combinations)."""
    hands = set()
    deck = [Card(rank, suit) for rank in Rank for suit in Suit]
    
    for i, card1 in enumerate(deck):
        for card2 in deck[i+1:]:
            hands.add(tuple(sorted([card1, card2], 
                                 key=lambda x: (x.rank.value_int, x.suit.value))))
    
    return hands 