from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import ast
import re
from ..core.cards import Card, Rank, Suit

# Set logging level to ERROR to reduce noise
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class HandHistoryParser:
    def __init__(self):
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
    
    def _parse_card(self, card_str: str) -> Optional[Card]:
        """Convert string notation (e.g., 'As') to Card object."""
        try:
            if len(card_str) != 2 or card_str == '??':
                return None
            
            rank_char = card_str[0].upper()
            suit_char = card_str[1].lower()
            
            if rank_char not in self._rank_map or suit_char not in self._suit_map:
                return None
            
            return Card(self._rank_map[rank_char], self._suit_map[suit_char])
        except Exception as e:
            return None
    
    def _parse_cards(self, cards: List[str]) -> List[Card]:
        """Convert list of string notations to Card objects."""
        parsed = []
        for card in cards:
            card_obj = self._parse_card(card)
            if card_obj:
                parsed.append(card_obj)
        return parsed

    def _parse_value(self, value_str: str) -> Any:
        """Parse a value string into the appropriate Python type."""
        value_str = value_str.strip()
        
        # Handle empty values
        if not value_str:
            return None
            
        # Handle boolean values
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False
            
        # Handle lists
        if value_str.startswith('[') and value_str.endswith(']'):
            # Split by comma, but preserve strings with spaces
            items = []
            current_item = ''
            in_string = False
            for char in value_str[1:-1]:
                if char == "'" and not in_string:
                    in_string = True
                    current_item += char
                elif char == "'" and in_string:
                    in_string = False
                    current_item += char
                elif char == ',' and not in_string:
                    if current_item.strip():
                        items.append(current_item.strip())
                    current_item = ''
                else:
                    current_item += char
            if current_item.strip():
                items.append(current_item.strip())
            return [item.strip("'") for item in items if item.strip()]
            
        # Handle quoted strings
        if value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]
            
        # Handle numbers
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            # If not a number, return as string
            return value_str
    
    def parse_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse a single .phh file into structured data."""
        parsed_hands = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Split content into individual hand sections
                hand_sections = content.split('\n\n')
                
                for section in hand_sections:
                    if not section.strip():
                        continue
                        
                    try:
                        # Parse the hand data
                        lines = section.strip().split('\n')
                        hand_data = {}
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                                
                            if line.startswith('[') and line.endswith(']'):
                                # This is a hand ID
                                try:
                                    hand_id = int(line.strip('[]'))
                                    hand_data['hand_id'] = hand_id
                                except ValueError:
                                    continue
                            elif '=' in line:
                                # This is a key-value pair
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                
                                try:
                                    parsed_value = self._parse_value(value)
                                    hand_data[key] = parsed_value
                                except Exception as e:
                                    continue
                        
                        if hand_data:
                            # Initialize variables for tracking community cards and current street
                            community_cards = []
                            current_street = 'preflop'
                            actions_by_street = {'preflop': [], 'flop': [], 'turn': [], 'river': []}
                            
                            if 'actions' in hand_data:
                                hole_cards = {}  # Track hole cards by player
                                for action in hand_data['actions']:
                                    if isinstance(action, str):
                                        parts = action.split()
                                        if len(parts) >= 2:
                                            if parts[0] == 'd':  # Dealer action
                                                if parts[1] == 'db':  # Deal board
                                                    if len(parts) >= 3 and parts[2] != '????':
                                                        cards = parts[2]
                                                        # If it's 6 chars, it's the flop (3 cards)
                                                        if len(cards) == 6:
                                                            current_street = 'flop'
                                                            for i in range(0, 6, 2):
                                                                card = cards[i:i+2]
                                                                if card != '??':
                                                                    community_cards.append(card)
                                                        # If it's 2 chars, it's turn or river
                                                        elif len(cards) == 2:
                                                            if current_street == 'preflop':
                                                                current_street = 'flop'
                                                            elif current_street == 'flop':
                                                                current_street = 'turn'
                                                            elif current_street == 'turn':
                                                                current_street = 'river'
                                                            if cards != '??':
                                                                community_cards.append(cards)
                                            elif parts[0].startswith('p'):  # Player action
                                                player_num = parts[0][1:]
                                                action_type = parts[1]
                                                try:
                                                    amount = float(parts[2]) if len(parts) > 2 else None
                                                except ValueError:
                                                    amount = None
                                                
                                                # Capture hole cards from showdown
                                                if action_type == 'sm' and len(parts) >= 3:
                                                    cards = parts[2]
                                                    if len(cards) == 4:  # Two cards
                                                        hole_cards[player_num] = [cards[0:2], cards[2:4]]
                                                
                                                actions_by_street[current_street].append({
                                                    'player': player_num,
                                                    'type': action_type,
                                                    'amount': amount,
                                                    'street': current_street
                                                })
                            
                            # Convert the raw data into our standard format
                            parsed_hand = {
                                'players': hand_data.get('players', []),
                                'actions': [
                                    action for street_actions in actions_by_street.values()
                                    for action in street_actions
                                ],
                                'hole_cards': hole_cards,  # Now a dictionary mapping player numbers to their hole cards
                                'community_cards': self._parse_cards(community_cards),
                                'stacks': hand_data.get('starting_stacks', [])
                            }
                            
                            parsed_hands.append(parsed_hand)
                            
                            if len(parsed_hands) % 1000 == 0:
                                logger.info(f"Parsed {len(parsed_hands)} hands...")
                                
                    except Exception as e:
                        continue
                        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            
        logger.info(f"Successfully parsed {len(parsed_hands)} hands from {file_path}")
        return parsed_hands
    
    def parse_directory(self, dir_path: Path) -> List[Dict[str, Any]]:
        """Parse all .phh files in a directory."""
        all_hands = []
        dir_path = Path(dir_path)
        
        for file_path in dir_path.glob('**/*.phh*'):
            logger.info(f"Processing {file_path}")
            hands = self.parse_file(file_path)
            all_hands.extend(hands)
        
        logger.info(f"Total hands parsed: {len(all_hands)}")
        return all_hands 