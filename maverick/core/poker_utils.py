from typing import List, Tuple, Union, Optional
from .cards import Card, Rank, Suit
from .simulator import MonteCarloSimulator
from .outs import OutsCalculator
from .decision import DecisionEngine, GameState, Action

class PokerUtils:
    def __init__(self):
        self.simulator = MonteCarloSimulator()
        self.outs_calculator = OutsCalculator()
        self.decision_engine = DecisionEngine()
        
        # Card notation conversion maps
        self._rank_map = {
            '2': Rank.TWO, '3': Rank.THREE, '4': Rank.FOUR,
            '5': Rank.FIVE, '6': Rank.SIX, '7': Rank.SEVEN,
            '8': Rank.EIGHT, '9': Rank.NINE, 'T': Rank.TEN,
            'J': Rank.JACK, 'Q': Rank.QUEEN, 'K': Rank.KING,
            'A': Rank.ACE
        }
        self._suit_map = {
            'h': Suit.HEARTS, 'd': Suit.DIAMONDS,
            'c': Suit.CLUBS, 's': Suit.SPADES
        }
    
    def _parse_card(self, card_str: str) -> Card:
        """Convert string notation (e.g., 'As') to Card object."""
        if len(card_str) != 2:
            raise ValueError(f"Invalid card notation: {card_str}")
        
        rank_char = card_str[0].upper()
        suit_char = card_str[1].lower()
        
        if rank_char not in self._rank_map:
            raise ValueError(f"Invalid rank: {rank_char}")
        if suit_char not in self._suit_map:
            raise ValueError(f"Invalid suit: {suit_char}")
        
        return Card(self._rank_map[rank_char], self._suit_map[suit_char])
    
    def _parse_cards(self, cards: Union[List[str], str]) -> List[Card]:
        """Convert list of string notations to Card objects."""
        if isinstance(cards, str):
            cards = cards.split()
        return [self._parse_card(card) for card in cards]
    
    def monte_carlo_sim(self,
                       player_hand: Union[List[str], str],
                       community_cards: Union[List[str], str] = None,
                       num_simulations: int = 10000,
                       num_opponents: int = 1) -> Tuple[float, dict]:
        """
        Run Monte Carlo simulation with easy string notation.
        
        Args:
            player_hand: List of card strings (e.g., ['As', 'Kh']) or space-separated string
            community_cards: List of card strings or space-separated string (optional)
            num_simulations: Number of simulations to run
            num_opponents: Number of opponents to simulate against
        
        Returns:
            Tuple of (win_probability, stats_dict)
        
        Example:
            >>> utils = PokerUtils()
            >>> win_prob, stats = utils.monte_carlo_sim('As Kh', 'Jh Td Qc')
            >>> print(f"Win probability: {win_prob*100:.1f}%")
        """
        player_cards = self._parse_cards(player_hand)
        community = self._parse_cards(community_cards) if community_cards else []
        
        return self.simulator.simulate(
            player_cards,
            community,
            num_simulations=num_simulations,
            num_opponents=num_opponents,
            show_progress=True
        )
    
    def calculate_outs(self,
                      player_hand: Union[List[str], str],
                      community_cards: Union[List[str], str]) -> Tuple[int, List[dict]]:
        """
        Calculate number of outs and identify possible draws.
        
        Args:
            player_hand: List of card strings or space-separated string
            community_cards: List of card strings or space-separated string
        
        Returns:
            Tuple of (total_outs, list_of_draws)
        
        Example:
            >>> utils = PokerUtils()
            >>> outs, draws = utils.calculate_outs('Ts Js', '9h 2d Qc')
            >>> print(f"Total outs: {outs}")
            >>> for draw in draws:
            ...     print(f"{draw.draw_type}: {draw.outs} outs")
        """
        player_cards = self._parse_cards(player_hand)
        community = self._parse_cards(community_cards)
        
        return self.outs_calculator.calculate_outs(player_cards, community)
    
    def recommend_move(self,
                      win_probability: float,
                      pot_size: float,
                      current_bet: float,
                      stack_size: float,
                      position: str = 'button',
                      num_players: int = 6,
                      street: str = 'flop') -> Tuple[str, Optional[float]]:
        """
        Recommend a poker move based on win probability and game state.
        
        Args:
            win_probability: Probability of winning (0-1)
            pot_size: Current pot size
            current_bet: Amount needed to call
            stack_size: Player's remaining stack
            position: Player's position ('early', 'middle', 'late', 'button')
            num_players: Number of players in hand
            street: Current street ('preflop', 'flop', 'turn', 'river')
        
        Returns:
            Tuple of (recommended_move, bet_size)
        
        Example:
            >>> utils = PokerUtils()
            >>> move, amount = utils.recommend_move(0.75, 100, 20, 1000)
            >>> print(f"Recommended move: {move}")
            >>> if amount:
            ...     print(f"Bet/raise amount: {amount}")
        """
        game_state = GameState(
            pot_size=pot_size,
            current_bet=current_bet,
            stack_size=stack_size,
            position=position,
            num_players=num_players,
            street=street
        )
        
        action, bet_size = self.decision_engine.recommend_move(win_probability, game_state)
        return action.value, bet_size

def example_usage():
    """Example usage of the PokerUtils class."""
    utils = PokerUtils()
    
    # Example hand: AK with QJT flop
    player_hand = 'As Kh'
    community_cards = 'Jh Td Qc'
    
    # Calculate win probability
    win_prob, stats = utils.monte_carlo_sim(player_hand, community_cards)
    
    # Calculate outs
    outs, draws = utils.calculate_outs(player_hand, community_cards)
    
    # Get move recommendation
    move, bet_size = utils.recommend_move(
        win_probability=win_prob,
        pot_size=100,
        current_bet=20,
        stack_size=1000
    )
    
    # Print results
    print(f"\nHand Analysis:")
    print(f"Player hand: {player_hand}")
    print(f"Community cards: {community_cards}")
    print(f"\nWin Probability: {win_prob*100:.1f}%")
    print(f"Total outs: {outs}")
    
    print("\nPossible draws:")
    for draw in draws:
        print(f"- {draw.draw_type}: {draw.outs} outs")
    
    print(f"\nRecommended move: {move}")
    if bet_size:
        print(f"Suggested bet size: {bet_size:.2f}")
    
    print("\nDetailed statistics:")
    print(f"Wins: {stats['wins']}")
    print(f"Splits: {stats['splits']}")
    print(f"Losses: {stats['losses']}")

if __name__ == '__main__':
    example_usage() 