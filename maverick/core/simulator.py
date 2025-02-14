from typing import List, Tuple, Set, Dict, Optional
import numpy as np
from tqdm import tqdm
from treys import Card as TreysCard, Evaluator
from .cards import Card, Rank, Suit
from .evaluator import HandEvaluator
from functools import lru_cache

class MonteCarloSimulator:
    def __init__(self):
        self.evaluator = Evaluator()
        self.hand_evaluator = HandEvaluator()
        self._suit_map = {
            Suit.HEARTS: 'h',
            Suit.DIAMONDS: 'd',
            Suit.CLUBS: 'c',
            Suit.SPADES: 's'
        }
        self._rank_map = {
            Rank.TWO: '2', Rank.THREE: '3', Rank.FOUR: '4',
            Rank.FIVE: '5', Rank.SIX: '6', Rank.SEVEN: '7',
            Rank.EIGHT: '8', Rank.NINE: '9', Rank.TEN: 'T',
            Rank.JACK: 'J', Rank.QUEEN: 'Q', Rank.KING: 'K',
            Rank.ACE: 'A'
        }
        
        # Define hand ranges for different positions
        self.hand_ranges = {
            'early': 0.15,  # Top 15% of hands
            'middle': 0.20, # Top 20% of hands
            'late': 0.25,   # Top 25% of hands
            'button': 0.30  # Top 30% of hands
        }
        
        # Initialize result cache
        self._result_cache: Dict[str, Tuple[float, dict]] = {}
    
    def _convert_to_treys_card(self, card: Card) -> int:
        """Convert our Card object to treys card integer representation."""
        card_str = f"{self._rank_map[card.rank]}{self._suit_map[card.suit]}"
        return TreysCard.new(card_str)
    
    def _convert_cards_to_treys(self, cards: List[Card]) -> List[int]:
        """Convert a list of our Card objects to treys card integers."""
        return [self._convert_to_treys_card(card) for card in cards]
    
    def _evaluate_hand(self, hole_cards: List[int], board: List[int]) -> int:
        """Evaluate hand strength using treys evaluator."""
        return self.evaluator.evaluate(board, hole_cards)
    
    def _generate_remaining_deck(self, 
                               player_hand: List[Card], 
                               community_cards: List[Card]) -> List[Card]:
        """Generate deck of remaining cards not in player hand or community cards."""
        used_cards = set(player_hand + community_cards)
        remaining = []
        
        for rank in Rank:
            for suit in Suit:
                card = Card(rank, suit)
                if card not in used_cards:
                    remaining.append(card)
        
        return remaining
    
    def _is_made_hand(self, hand: List[Card], community: List[Card]) -> bool:
        """Check if a hand is already made (pair or better)."""
        if not community:
            # Preflop - check for pocket pairs
            return len(hand) == 2 and hand[0].rank == hand[1].rank
        
        # Post-flop - evaluate hand strength
        rank, _ = self.hand_evaluator.evaluate_hand(hand + community)
        return rank.value >= 2  # At least a pair
    
    def _generate_opponent_hand(self, 
                              remaining_deck: List[Card], 
                              community_cards: List[Card],
                              num_opponents: int = 1) -> List[List[Card]]:
        """Generate realistic opponent hands based on position and ranges."""
        opponent_hands = []
        for _ in range(num_opponents):
            valid_hand = False
            attempts = 0
            while not valid_hand and attempts < 100:
                # Sample two cards for the opponent
                hand = list(np.random.choice(remaining_deck, size=2, replace=False))
                
                # Check if this is a reasonable hand
                if community_cards:
                    # Post-flop: Higher chance to have a made hand
                    if np.random.random() < 0.8:  # 80% chance for made hand
                        valid_hand = self._is_made_hand(hand, community_cards)
                    else:
                        # For unmade hands, prefer drawing hands
                        rank_diff = abs(hand[0].rank.value_int - hand[1].rank.value_int)
                        suited = hand[0].suit == hand[1].suit
                        if suited or rank_diff <= 4:  # Connected or suited cards
                            valid_hand = True
                else:
                    # Preflop: Use position-based ranges
                    if np.random.random() < self.hand_ranges['middle']:  # Using middle position as average
                        valid_hand = True
                
                attempts += 1
            
            if valid_hand:
                opponent_hands.append(hand)
                # Remove these cards from remaining deck
                for card in hand:
                    remaining_deck.remove(card)
            else:
                # If we couldn't find a valid hand, just take random cards
                hand = list(np.random.choice(remaining_deck, size=2, replace=False))
                opponent_hands.append(hand)
                for card in hand:
                    remaining_deck.remove(card)
        
        return opponent_hands
    
    def _get_cache_key(self, 
                      player_hand: List[Card], 
                      community_cards: List[Card], 
                      num_opponents: int) -> str:
        """Generate a unique cache key for the given scenario."""
        player_str = ''.join(sorted(str(card) for card in player_hand))
        community_str = ''.join(sorted(str(card) for card in community_cards))
        return f"{player_str}|{community_str}|{num_opponents}"
    
    @lru_cache(maxsize=10000)
    def _evaluate_hand_cached(self, 
                            hole_cards_tuple: Tuple[int, ...], 
                            board_tuple: Tuple[int, ...]) -> int:
        """Cached version of hand evaluation."""
        return self.evaluator.evaluate(list(board_tuple), list(hole_cards_tuple))
    
    def _vectorized_simulate(self,
                           player_hand: List[Card],
                           community_cards: List[Card],
                           num_simulations: int = 10000,
                           num_opponents: int = 1,
                           batch_size: int = 1000) -> Tuple[float, dict]:
        """Vectorized version of Monte Carlo simulation."""
        # Convert known cards to treys format
        treys_player_hand = self._convert_cards_to_treys(player_hand)
        treys_community = self._convert_cards_to_treys(community_cards)
        
        # Generate remaining deck
        remaining_deck = self._generate_remaining_deck(player_hand, community_cards)
        cards_to_deal = 5 - len(community_cards)
        
        # Statistics tracking
        stats = {'wins': 0, 'splits': 0, 'losses': 0}
        
        # Process in batches
        for batch_start in tqdm(range(0, num_simulations, batch_size)):
            batch_end = min(batch_start + batch_size, num_simulations)
            current_batch_size = batch_end - batch_start
            
            # Create matrices for batch processing
            opponent_hands = np.zeros((current_batch_size, num_opponents, 2), dtype=int)
            community_completions = np.zeros((current_batch_size, cards_to_deal), dtype=int)
            
            # Generate hands and community cards for entire batch
            for i in range(current_batch_size):
                sim_deck = remaining_deck.copy()
                np.random.shuffle(sim_deck)
                
                # Generate opponent hands
                opp_hands = self._generate_opponent_hand(sim_deck, community_cards, num_opponents)
                for j, hand in enumerate(opp_hands):
                    opponent_hands[i, j] = self._convert_cards_to_treys(hand)
                
                # Generate community cards
                new_community = sim_deck[:cards_to_deal]
                community_completions[i] = self._convert_cards_to_treys(new_community)
            
            # Evaluate hands in parallel
            player_scores = np.zeros(current_batch_size)
            opponent_scores = np.zeros((current_batch_size, num_opponents))
            
            # Convert to tuple for caching
            treys_player_tuple = tuple(treys_player_hand)
            treys_community_tuple = tuple(treys_community)
            
            # Evaluate player hands
            for i in range(current_batch_size):
                full_board = treys_community + list(community_completions[i])
                board_tuple = tuple(full_board)
                player_scores[i] = self._evaluate_hand_cached(treys_player_tuple, board_tuple)
                
                # Evaluate opponent hands
                for j in range(num_opponents):
                    opp_hand_tuple = tuple(opponent_hands[i, j])
                    opponent_scores[i, j] = self._evaluate_hand_cached(opp_hand_tuple, board_tuple)
            
            # Determine outcomes
            min_opponent_scores = np.min(opponent_scores, axis=1)
            wins = np.sum(player_scores < min_opponent_scores)
            splits = np.sum(player_scores == min_opponent_scores)
            losses = current_batch_size - wins - splits
            
            # Update statistics
            stats['wins'] += int(wins)
            stats['splits'] += int(splits)
            stats['losses'] += int(losses)
        
        # Calculate win probability
        win_probability = (stats['wins'] + 0.5 * stats['splits']) / num_simulations
        
        return win_probability, stats
    
    def simulate(self,
                player_hand: List[Card],
                community_cards: List[Card],
                num_simulations: int = 10000,
                num_opponents: int = 1,
                show_progress: bool = True,
                use_cache: bool = True) -> Tuple[float, dict]:
        """
        Run Monte Carlo simulation with caching and vectorization.
        
        Args:
            player_hand: List of 2 Card objects representing player's hole cards
            community_cards: List of Card objects for the community cards
            num_simulations: Number of simulations to run
            num_opponents: Number of opponents to simulate against
            show_progress: Whether to show progress bar
            use_cache: Whether to use result caching
        
        Returns:
            Tuple of (win_probability, stats_dict)
        """
        if len(player_hand) != 2:
            raise ValueError("Player hand must contain exactly 2 cards")
        if len(community_cards) > 5:
            raise ValueError("Cannot have more than 5 community cards")
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(player_hand, community_cards, num_opponents)
            if cache_key in self._result_cache:
                return self._result_cache[cache_key]
        
        # Use vectorized simulation for better performance
        result = self._vectorized_simulate(
            player_hand,
            community_cards,
            num_simulations,
            num_opponents
        )
        
        # Cache the result
        if use_cache:
            self._result_cache[cache_key] = result
        
        return result 