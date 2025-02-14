from typing import List, Set, Dict, Tuple, Counter as TypeCounter
from collections import Counter
from dataclasses import dataclass
from .cards import Card, Rank, Suit

@dataclass
class DrawInfo:
    """Information about a drawing hand."""
    draw_type: str
    outs: int
    potential_cards: Set[Card]

class OutsCalculator:
    def __init__(self):
        self.draw_values = {
            # Primary draws
            'flush_draw': 9,
            'open_straight_draw': 8,
            'gutshot_straight_draw': 4,
            'double_gutshot_draw': 8,
            'pair_to_set': 2,
            'two_overcards': 6,
            
            # Full house draws
            'trips_to_full_house': 6,  # When you have three of a kind
            'two_pair_to_full_house': 4,  # When you have two pair
            'pair_to_two_pair': 5,  # When you have one pair
            
            # Quads draw
            'set_to_quads': 1,
            
            # Backdoor draws
            'backdoor_flush_draw': 3,
            'backdoor_straight_draw': 2,
            
            # Additional draws
            'overcards_to_pair': 6,  # Two overcards to pair
            'pair_plus_gutshot': 7,  # Pair with additional gutshot draw
            'double_pair_draw': 8    # Drawing to two different pairs
        }
    
    def _count_suits(self, cards: List[Card]) -> Dict[Suit, int]:
        """Count the number of cards of each suit."""
        suit_counts = {suit: 0 for suit in Suit}
        for card in cards:
            suit_counts[card.suit] += 1
        return suit_counts
    
    def _get_straight_sequences(self, ranks: List[int]) -> List[List[int]]:
        """Find all possible straight sequences in the given ranks."""
        sequences = []
        ranks = sorted(set(ranks))  # Remove duplicates and sort
        
        # Handle Ace-low straight possibility
        if 14 in ranks:  # If we have an Ace
            ranks.append(1)  # Add it as a low Ace
        
        # Find all sequences of consecutive cards
        current_seq = [ranks[0]]
        for i in range(1, len(ranks)):
            if ranks[i] == current_seq[-1] + 1:
                current_seq.append(ranks[i])
            else:
                if len(current_seq) >= 3:  # Only keep sequences of 3+ cards
                    sequences.append(current_seq)
                current_seq = [ranks[i]]
        
        if len(current_seq) >= 3:
            sequences.append(current_seq)
        
        return sequences
    
    def check_flush_draw(self, 
                        player_hand: List[Card], 
                        community_cards: List[Card]) -> List[DrawInfo]:
        """Check for flush draws."""
        draws = []
        suit_counts = self._count_suits(player_hand + community_cards)
        
        for suit, count in suit_counts.items():
            if count == 4:
                # Regular flush draw
                potential_cards = {
                    Card(rank, suit)
                    for rank in Rank
                    if Card(rank, suit) not in (player_hand + community_cards)
                }
                draws.append(DrawInfo(
                    draw_type='flush_draw',
                    outs=9,
                    potential_cards=potential_cards
                ))
            elif count == 3 and len(community_cards) <= 3:
                # Backdoor flush draw
                potential_cards = {
                    Card(rank, suit)
                    for rank in Rank
                    if Card(rank, suit) not in (player_hand + community_cards)
                }
                draws.append(DrawInfo(
                    draw_type='backdoor_flush_draw',
                    outs=3,
                    potential_cards=potential_cards
                ))
        
        return draws
    
    def check_straight_draw(self, 
                          player_hand: List[Card], 
                          community_cards: List[Card]) -> List[DrawInfo]:
        """Check for straight draws."""
        draws = []
        ranks = [card.rank.value_int for card in (player_hand + community_cards)]
        ranks = sorted(set(ranks))  # Remove duplicates and sort
        
        # Handle Ace-low straight possibility
        if 14 in ranks:  # If we have an Ace
            ranks.append(1)  # Add it as a low Ace
        
        # Check for four-card sequences (open-ended straight draws)
        for i in range(len(ranks) - 3):
            window = ranks[i:i+4]
            if max(window) - min(window) == 3:  # Consecutive sequence
                potential_ranks = [min(window) - 1, max(window) + 1]
                potential_ranks = [r for r in potential_ranks if 2 <= r <= 14]
                if potential_ranks:
                    draws.append(DrawInfo(
                        draw_type='open_straight_draw',
                        outs=4 * len(potential_ranks),
                        potential_cards={
                            Card(rank, suit)
                            for rank in Rank
                            if rank.value_int in potential_ranks
                            for suit in Suit
                        }
                    ))
        
        # Check for gutshot straight draws
        for i in range(len(ranks) - 3):
            for j in range(i + 3, min(i + 5, len(ranks))):
                window = ranks[i:j+1]
                if len(window) == 4 and max(window) - min(window) == 4:
                    # Found a sequence with one gap
                    missing_rank = next(r for r in range(min(window), max(window)) 
                                     if r not in window)
                    if 2 <= missing_rank <= 14:
                        draws.append(DrawInfo(
                            draw_type='gutshot_straight_draw',
                            outs=4,
                            potential_cards={
                                Card(rank, suit)
                                for rank in Rank
                                if rank.value_int == missing_rank
                                for suit in Suit
                            }
                        ))
        
        return draws
    
    def check_pair_draws(self, 
                        player_hand: List[Card], 
                        community_cards: List[Card]) -> List[DrawInfo]:
        """Check for pair-related draws (set draws, etc.)."""
        draws = []
        
        # Check for pocket pair -> set draw
        if len(player_hand) == 2 and player_hand[0].rank == player_hand[1].rank:
            potential_cards = {
                Card(player_hand[0].rank, suit)
                for suit in Suit
                if Card(player_hand[0].rank, suit) not in (player_hand + community_cards)
            }
            draws.append(DrawInfo(
                draw_type='pair_to_set',
                outs=2,
                potential_cards=potential_cards
            ))
        
        # Check for overcards
        if not community_cards:  # Only relevant preflop
            if (player_hand[0].rank.value_int > 10 and 
                player_hand[1].rank.value_int > 10 and
                player_hand[0].rank != player_hand[1].rank):
                potential_cards = {
                    Card(rank, suit)
                    for rank in [player_hand[0].rank, player_hand[1].rank]
                    for suit in Suit
                    if Card(rank, suit) not in player_hand
                }
                draws.append(DrawInfo(
                    draw_type='two_overcards',
                    outs=6,
                    potential_cards=potential_cards
                ))
        
        return draws
    
    def check_full_house_draws(self, 
                             player_hand: List[Card], 
                             community_cards: List[Card]) -> List[DrawInfo]:
        """Check for draws to full house."""
        draws = []
        all_cards = player_hand + community_cards
        rank_counts = Counter(card.rank for card in all_cards)
        
        # Find three of a kind
        trips_rank = next((rank for rank, count in rank_counts.items() if count == 3), None)
        if trips_rank:
            # Three of a kind looking for a pair
            remaining_ranks = [r for r, c in rank_counts.items() if c == 1]
            potential_cards = {
                Card(rank, suit)
                for rank in remaining_ranks
                for suit in Suit
                if Card(rank, suit) not in all_cards
            }
            if potential_cards:
                draws.append(DrawInfo(
                    draw_type='trips_to_full_house',
                    outs=len(potential_cards),
                    potential_cards=potential_cards
                ))
        
        # Find two pair
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(pairs) == 2:
            # Two pair looking for full house
            for pair_rank in pairs:
                potential_cards = {
                    Card(pair_rank, suit)
                    for suit in Suit
                    if Card(pair_rank, suit) not in all_cards
                }
                if potential_cards:
                    draws.append(DrawInfo(
                        draw_type='two_pair_to_full_house',
                        outs=len(potential_cards),
                        potential_cards=potential_cards
                    ))
    
        return draws

    def check_quads_draw(self, 
                        player_hand: List[Card], 
                        community_cards: List[Card]) -> List[DrawInfo]:
        """Check for draws to four of a kind."""
        draws = []
        all_cards = player_hand + community_cards
        rank_counts = Counter(card.rank for card in all_cards)
        
        # Find three of a kind that could become quads
        trips_rank = next((rank for rank, count in rank_counts.items() if count == 3), None)
        if trips_rank:
            potential_cards = {
                Card(trips_rank, suit)
                for suit in Suit
                if Card(trips_rank, suit) not in all_cards
            }
            if potential_cards:
                draws.append(DrawInfo(
                    draw_type='set_to_quads',
                    outs=len(potential_cards),
                    potential_cards=potential_cards
                ))
        
        return draws

    def check_two_pair_draws(self, 
                            player_hand: List[Card], 
                            community_cards: List[Card]) -> List[DrawInfo]:
        """Check for draws to two pair."""
        draws = []
        all_cards = player_hand + community_cards
        rank_counts = Counter(card.rank for card in all_cards)
        
        # Find single pair
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        if len(pairs) == 1:
            pair_rank = pairs[0]
            # Look for potential second pairs
            unpaired_ranks = [r for r, c in rank_counts.items() if c == 1]
            potential_cards = {
                Card(rank, suit)
                for rank in unpaired_ranks
                for suit in Suit
                if Card(rank, suit) not in all_cards
            }
            if potential_cards:
                draws.append(DrawInfo(
                    draw_type='pair_to_two_pair',
                    outs=len(potential_cards),
                    potential_cards=potential_cards
                ))
        
        return draws

    def check_combo_draws(self, 
                         player_hand: List[Card], 
                         community_cards: List[Card]) -> List[DrawInfo]:
        """Check for combination draws (e.g., pair + gutshot)."""
        draws = []
        all_cards = player_hand + community_cards
        rank_counts = Counter(card.rank for card in all_cards)
        
        # Check for pair + gutshot combo
        has_pair = any(count == 2 for count in rank_counts.values())
        gutshot_draws = self.check_straight_draw(player_hand, community_cards)
        has_gutshot = any(d.draw_type == 'gutshot_straight_draw' for d in gutshot_draws)
        
        if has_pair and has_gutshot:
            # Combine potential cards from both draws
            potential_cards = set()
            for draw in gutshot_draws:
                if draw.draw_type == 'gutshot_straight_draw':
                    potential_cards.update(draw.potential_cards)
            
            draws.append(DrawInfo(
                draw_type='pair_plus_gutshot',
                outs=len(potential_cards),
                potential_cards=potential_cards
            ))
        
        return draws

    def calculate_outs(self, 
                      player_hand: List[Card], 
                      community_cards: List[Card]) -> Tuple[int, List[DrawInfo]]:
        """
        Calculate total number of outs and identify all possible draws.
        
        Args:
            player_hand: List of hole cards
            community_cards: List of community cards
        
        Returns:
            Tuple of (total_outs, list_of_draws)
        """
        all_draws = []
        
        # Check for various types of draws
        all_draws.extend(self.check_flush_draw(player_hand, community_cards))
        all_draws.extend(self.check_straight_draw(player_hand, community_cards))
        all_draws.extend(self.check_pair_draws(player_hand, community_cards))
        all_draws.extend(self.check_full_house_draws(player_hand, community_cards))
        all_draws.extend(self.check_quads_draw(player_hand, community_cards))
        all_draws.extend(self.check_two_pair_draws(player_hand, community_cards))
        all_draws.extend(self.check_combo_draws(player_hand, community_cards))
        
        # Calculate total unique outs
        all_potential_cards = set()
        for draw in all_draws:
            all_potential_cards.update(draw.potential_cards)
        
        return len(all_potential_cards), all_draws 