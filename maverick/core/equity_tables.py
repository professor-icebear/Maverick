from typing import Dict, Tuple
from .cards import Card, Rank, Suit

# Pre-flop equities based on PokerStove calculations
# Values represent approximate all-in equity against random hands
PREFLOP_EQUITY_MAP = {
    # Pocket pairs
    'AA': 0.852, 'KK': 0.823, 'QQ': 0.799, 'JJ': 0.775,
    'TT': 0.751, '99': 0.720, '88': 0.690, '77': 0.661,
    '66': 0.633, '55': 0.605, '44': 0.578, '33': 0.551, '22': 0.524,
    
    # Suited hands
    'AKs': 0.670, 'AQs': 0.662, 'AJs': 0.654, 'ATs': 0.647,
    'A9s': 0.624, 'A8s': 0.619, 'A7s': 0.614, 'A6s': 0.609,
    'A5s': 0.615, 'A4s': 0.611, 'A3s': 0.606, 'A2s': 0.601,
    'KQs': 0.632, 'KJs': 0.624, 'KTs': 0.617, 'K9s': 0.593,
    'QJs': 0.611, 'QTs': 0.604, 'Q9s': 0.580,
    'JTs': 0.599, 'J9s': 0.575,
    'T9s': 0.570,
    
    # Offsuit hands
    'AKo': 0.653, 'AQo': 0.644, 'AJo': 0.635, 'ATo': 0.627,
    'A9o': 0.602, 'A8o': 0.596, 'A7o': 0.591, 'A6o': 0.586,
    'A5o': 0.591, 'A4o': 0.587, 'A3o': 0.582, 'A2o': 0.577,
    'KQo': 0.612, 'KJo': 0.603, 'KTo': 0.595, 'K9o': 0.569,
    'QJo': 0.589, 'QTo': 0.581, 'Q9o': 0.555,
    'JTo': 0.575, 'J9o': 0.549,
    'T9o': 0.543,
}

def get_hand_notation(card1: Card, card2: Card) -> str:
    """Convert two cards to standard poker notation (e.g., 'AKs' or 'AKo')."""
    # Sort cards by rank value
    if card2.rank.value_int > card1.rank.value_int:
        card1, card2 = card2, card1
    
    # Handle pocket pairs
    if card1.rank == card2.rank:
        return f"{card1.rank.value}{card2.rank.value}"
    
    # Handle suited and offsuit hands
    suffix = 's' if card1.suit == card2.suit else 'o'
    return f"{card1.rank.value}{card2.rank.value}{suffix}"

def get_preflop_equity(hand: Tuple[Card, Card]) -> float:
    """Get pre-flop equity for a given hand."""
    notation = get_hand_notation(hand[0], hand[1])
    return PREFLOP_EQUITY_MAP.get(notation, 0.5)  # Default to 0.5 if not found

# Generate reverse map for all possible hand combinations
def generate_hand_combinations() -> Dict[Tuple[Rank, Rank, bool], str]:
    """Generate a mapping of (rank1, rank2, is_suited) to hand notation."""
    result = {}
    for rank1 in Rank:
        for rank2 in Rank:
            if rank1.value_int >= rank2.value_int:  # Maintain order
                if rank1 == rank2:
                    # Pocket pair
                    result[(rank1, rank2, False)] = f"{rank1.value}{rank2.value}"
                else:
                    # Suited
                    result[(rank1, rank2, True)] = f"{rank1.value}{rank2.value}s"
                    # Offsuit
                    result[(rank1, rank2, False)] = f"{rank1.value}{rank2.value}o"
    return result

HAND_COMBINATIONS = generate_hand_combinations() 