from enum import Enum
from typing import Tuple, Optional
from dataclasses import dataclass

class Action(Enum):
    FOLD = "Fold"
    CHECK = "Check"
    CALL = "Call"
    RAISE = "Raise"
    ALL_IN = "All-in"

@dataclass
class GameState:
    """Represents the current state of the game for decision making."""
    pot_size: float
    current_bet: float
    stack_size: float
    position: str  # 'early', 'middle', 'late', 'button', 'small_blind', 'big_blind'
    num_players: int
    street: str  # 'preflop', 'flop', 'turn', 'river'

class DecisionEngine:
    def __init__(self):
        # Default thresholds - these could be tuned based on player style
        self.thresholds = {
            'strong_hand': 0.7,
            'medium_hand': 0.45,
            'weak_hand': 0.3,
            'raise_multiplier': 2.5,  # Standard raise size multiplier
            'min_raise_bb': 2.5,  # Minimum raise in big blinds
        }
    
    def calculate_pot_odds(self, current_bet: float, pot_size: float) -> float:
        """
        Calculate the pot odds (required equity to break even on a call).
        
        Args:
            current_bet: Amount needed to call
            pot_size: Current size of the pot
        
        Returns:
            Float between 0 and 1 representing required equity
        """
        if current_bet <= 0:
            return 0.0
        return current_bet / (pot_size + current_bet)
    
    def calculate_raise_size(self, 
                           game_state: GameState, 
                           win_probability: float) -> Optional[float]:
        """
        Calculate recommended raise size based on win probability and pot size.
        
        Returns:
            Recommended raise size or None if raising not recommended
        """
        if win_probability < self.thresholds['medium_hand']:
            return None
        
        # Base raise on pot size and win probability
        base_raise = game_state.pot_size * self.thresholds['raise_multiplier']
        
        # Adjust based on win probability
        if win_probability > self.thresholds['strong_hand']:
            base_raise *= 1.5  # Raise bigger with strong hands
        
        # Cap raise at remaining stack
        return min(base_raise, game_state.stack_size)
    
    def get_position_multiplier(self, position: str) -> float:
        """Get multiplier based on position (more aggressive in late position)."""
        position_multipliers = {
            'early': 0.8,
            'middle': 0.9,
            'late': 1.1,
            'button': 1.2,
            'small_blind': 0.9,
            'big_blind': 1.0
        }
        return position_multipliers.get(position, 1.0)
    
    def recommend_move(self, 
                      win_probability: float,
                      game_state: GameState) -> Tuple[Action, Optional[float]]:
        """
        Recommend a poker action based on win probability and game state.
        
        Args:
            win_probability: Probability of winning (0-1)
            game_state: Current state of the game
        
        Returns:
            Tuple of (recommended_action, bet_size)
            bet_size will be None for fold/check actions
        """
        # Adjust win probability based on position
        adjusted_probability = win_probability * self.get_position_multiplier(game_state.position)
        
        # Calculate pot odds if there's a bet to call
        pot_odds = self.calculate_pot_odds(game_state.current_bet, game_state.pot_size)
        
        # All-in consideration
        if game_state.stack_size <= game_state.pot_size * 0.5:
            if adjusted_probability > max(pot_odds + 0.1, 0.5):
                return Action.ALL_IN, game_state.stack_size
        
        # Strong hand
        if adjusted_probability > self.thresholds['strong_hand']:
            raise_size = self.calculate_raise_size(game_state, adjusted_probability)
            if raise_size is not None:
                return Action.RAISE, raise_size
            return Action.CALL, None
        
        # Medium hand with positive expected value
        if adjusted_probability > self.thresholds['medium_hand'] and adjusted_probability > pot_odds:
            if game_state.current_bet == 0:
                raise_size = self.calculate_raise_size(game_state, adjusted_probability)
                if raise_size is not None:
                    return Action.RAISE, raise_size
                return Action.CHECK, None
            return Action.CALL, None
        
        # Weak hand
        if adjusted_probability < self.thresholds['weak_hand']:
            if game_state.current_bet == 0:
                return Action.CHECK, None
            return Action.FOLD, None
        
        # Marginal hand
        if game_state.current_bet == 0:
            return Action.CHECK, None
        if pot_odds < adjusted_probability:
            return Action.CALL, None
        return Action.FOLD, None
    
    def adjust_strategy(self, player_style: str = 'balanced'):
        """
        Adjust decision thresholds based on player style.
        
        Args:
            player_style: One of 'tight', 'loose', 'aggressive', 'passive', 'balanced'
        """
        if player_style == 'tight':
            self.thresholds['strong_hand'] = 0.75
            self.thresholds['medium_hand'] = 0.50
            self.thresholds['weak_hand'] = 0.35
        elif player_style == 'loose':
            self.thresholds['strong_hand'] = 0.65
            self.thresholds['medium_hand'] = 0.40
            self.thresholds['weak_hand'] = 0.25
        elif player_style == 'aggressive':
            self.thresholds['raise_multiplier'] = 3.0
            self.thresholds['min_raise_bb'] = 3.0
        elif player_style == 'passive':
            self.thresholds['raise_multiplier'] = 2.0
            self.thresholds['min_raise_bb'] = 2.0
        # 'balanced' uses default thresholds 