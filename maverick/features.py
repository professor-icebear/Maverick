from typing import List, Dict, Any, Optional
import pandas as pd
from collections import defaultdict

class PokerFeatureCalculator:
    def __init__(self):
        self.action_types = {
            'cbr': 'raise',  # Call/Bet/Raise
            'cc': 'call',    # Call/Check
            'f': 'fold',     # Fold
            'sm': 'show'     # Show/Muck
        }
        self.streets = ['preflop', 'flop', 'turn', 'river']
    
    def _is_blind_position(self, position: int, num_players: int) -> bool:
        """Check if position is small blind or big blind."""
        return position in [0, 1]  # 0-based index, 0=SB, 1=BB
    
    def _get_position_name(self, position: int, num_players: int) -> str:
        """Get standardized position name based on seat and table size."""
        if position == 0:
            return 'sb'
        elif position == 1:
            return 'bb'
        elif position == num_players - 1:
            return 'button'
        elif position == num_players - 2:
            return 'cutoff'
        elif position < num_players / 2:
            return 'early'
        else:
            return 'middle'
    
    def _get_action_amount(self, action: Dict[str, Any]) -> float:
        """Safely get the amount from an action, returning 0 if not present or None."""
        return float(action.get('amount', 0) or 0)
    
    def calculate_player_stats(self, parsed_hands: List[Dict[str, Any]], player_name: str) -> Dict[str, float]:
        """Calculate comprehensive player statistics."""
        stats = {
            'hands_played': 0,
            'vpip_hands': 0,
            'pfr_hands': 0,
            'threeb_hands': 0,
            'fold_to_3bet_hands': 0,
            'fold_to_3bet_opps': 0,
            'aggression_by_street': defaultdict(lambda: {'bets': 0, 'raises': 0, 'calls': 0, 'checks': 0}),
            'cbet_made': 0,
            'cbet_opportunities': 0,
            'cbet_success': 0,
            'position_counts': defaultdict(int),
            'position_vpip': defaultdict(int),
            'position_pfr': defaultdict(int)
        }
        
        for hand in parsed_hands:
            if player_name not in hand['players']:
                continue
            
            stats['hands_played'] += 1
            player_idx = hand['players'].index(player_name)
            position = self._get_position_name(player_idx, len(hand['players']))
            stats['position_counts'][position] += 1
            
            # Get all actions by this player
            player_actions = [a for a in hand['actions'] if a['player'] == str(player_idx + 1)]
            if not player_actions:
                continue
            
            # Track preflop action
            preflop_actions = [a for a in player_actions if a['street'] == 'preflop']
            has_vpip = False
            has_pfr = False
            
            # Initialize street state
            first_raise_seen = False
            for action in preflop_actions:
                # Skip blind posts for VPIP
                if self._is_blind_position(player_idx, len(hand['players'])):
                    if action['type'] == 'cc':
                        continue
                
                if action['type'] in ['cbr', 'cc']:
                    amount = self._get_action_amount(action)
                    if amount > 0:  # Only count non-zero amounts for VPIP
                        has_vpip = True
                    
                    if action['type'] == 'cbr' and not first_raise_seen:
                        has_pfr = True
                        first_raise_seen = True
            
            if has_vpip:
                stats['vpip_hands'] += 1
                stats['position_vpip'][position] += 1
            if has_pfr:
                stats['pfr_hands'] += 1
                stats['position_pfr'][position] += 1
            
            # Track aggression by street
            for street in self.streets:
                street_actions = [a for a in player_actions if a['street'] == street]
                for action in street_actions:
                    amount = self._get_action_amount(action)
                    if action['type'] == 'cbr':
                        if action.get('is_raise', False):
                            stats['aggression_by_street'][street]['raises'] += 1
                        elif amount > 0:
                            stats['aggression_by_street'][street]['bets'] += 1
                    elif action['type'] == 'cc':
                        if amount > 0:
                            stats['aggression_by_street'][street]['calls'] += 1
                        else:
                            stats['aggression_by_street'][street]['checks'] += 1
            
            # Track continuation betting
            if has_pfr:
                flop_actions = [a for a in player_actions if a['street'] == 'flop']
                if flop_actions:
                    stats['cbet_opportunities'] += 1
                    if any(a['type'] == 'cbr' and self._get_action_amount(a) > 0 for a in flop_actions):
                        stats['cbet_made'] += 1
                        # Check if cbet was successful (everyone folded)
                        other_actions = [a for a in hand['actions'] 
                                       if a['street'] == 'flop' and a['player'] != str(player_idx + 1)]
                        if all(a['type'] == 'f' for a in other_actions):
                            stats['cbet_success'] += 1
        
        # Calculate derived statistics
        results = {
            'hands_played': stats['hands_played'],
            'vpip': stats['vpip_hands'] / stats['hands_played'] if stats['hands_played'] > 0 else 0,
            'pfr': stats['pfr_hands'] / stats['hands_played'] if stats['hands_played'] > 0 else 0,
            'cbet_frequency': stats['cbet_made'] / stats['cbet_opportunities'] if stats['cbet_opportunities'] > 0 else 0,
            'cbet_success_rate': stats['cbet_success'] / stats['cbet_made'] if stats['cbet_made'] > 0 else 0,
        }
        
        # Calculate position-based stats
        for pos in ['button', 'cutoff', 'sb', 'bb', 'early', 'middle']:
            pos_hands = stats['position_counts'][pos]
            results[f'pos_{pos}_freq'] = pos_hands / stats['hands_played'] if stats['hands_played'] > 0 else 0
            results[f'pos_{pos}_vpip'] = (stats['position_vpip'][pos] / pos_hands 
                                        if pos_hands > 0 else 0)
            results[f'pos_{pos}_pfr'] = (stats['position_pfr'][pos] / pos_hands 
                                       if pos_hands > 0 else 0)
        
        # Calculate street-by-street aggression factors
        for street in self.streets:
            street_stats = stats['aggression_by_street'][street]
            aggressive_actions = street_stats['bets'] + street_stats['raises']
            passive_actions = street_stats['calls']  # Exclude checks from AF calculation
            
            results[f'af_{street}'] = (aggressive_actions / passive_actions 
                                     if passive_actions > 0 else 
                                     aggressive_actions if aggressive_actions > 0 else 0)
        
        # Calculate total aggression factor
        total_aggressive = sum(s['bets'] + s['raises'] for s in stats['aggression_by_street'].values())
        total_passive = sum(s['calls'] for s in stats['aggression_by_street'].values())
        results['af_total'] = (total_aggressive / total_passive 
                             if total_passive > 0 else 
                             total_aggressive if total_aggressive > 0 else 0)
        
        return results

    def _get_winner_from_showdown(self, hand: Dict[str, Any]) -> Optional[str]:
        """Determine the winner of the hand from showdown actions."""
        # Get all show/muck actions
        showdown_actions = [a for a in hand['actions'] if a['type'] == 'sm']
        if not showdown_actions:
            return None
            
        # The last player to show typically has the winning hand
        # This is a heuristic since we don't have explicit winner information
        return showdown_actions[-1]['player']
    
    def extract_bluff_sequences(self, parsed_hands: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extract sequences of actions and label bluffs based on river aggression and showdown results."""
        bluff_data = []
        
        for hand in parsed_hands:
            # Get river actions
            river_actions = [a for a in hand['actions'] if a['street'] == 'river']
            if not river_actions:
                continue  # Skip if hand didn't reach river
            
            # Get the winner if there was a showdown
            winner = self._get_winner_from_showdown(hand)
            if not winner:
                continue  # Skip if no showdown
            
            # Track each player's river aggression
            for player_idx, player in enumerate(hand['players'], 1):
                player_river_actions = [a for a in river_actions if a['player'] == str(player_idx)]
                if not player_river_actions:
                    continue
                
                # Get the player's last action on the river
                last_action = player_river_actions[-1]
                
                # Check if player was aggressive (bet/raise) but lost
                if last_action['type'] == 'cbr' and str(player_idx) != winner:
                    # Get the full action sequence for this player
                    player_actions = []
                    current_street = None
                    for action in hand['actions']:
                        if action['street'] != current_street:
                            current_street = action['street']
                            player_actions.append(f"--- {current_street.upper()} ---")
                        
                        if action['player'] == str(player_idx):
                            amount_str = f" ${self._get_action_amount(action):.2f}" if self._get_action_amount(action) > 0 else ""
                            player_actions.append(f"{action['type']}{amount_str}")
                    
                    # Record the bluff sequence
                    bluff_data.append({
                        'player': player,
                        'hand_id': hand.get('hand_id', ''),
                        'position': self._get_position_name(player_idx - 1, len(hand['players'])),
                        'action_sequence': player_actions,
                        'river_amount': self._get_action_amount(last_action),
                        'is_bluff': 1,
                        'community_cards': [str(card) for card in hand.get('community_cards', [])],
                        'hole_cards': hand.get('hole_cards', {}).get(str(player_idx), [])
                    })
        
        return pd.DataFrame(bluff_data)
    
    def analyze_bluff_patterns(self, parsed_hands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze bluffing patterns and frequencies for all players."""
        bluff_df = self.extract_bluff_sequences(parsed_hands)
        if bluff_df.empty:
            return {}
        
        # Group by player and analyze patterns
        bluff_stats = {}
        for player in bluff_df['player'].unique():
            player_bluffs = bluff_df[bluff_df['player'] == player]
            
            # Calculate bluff frequencies by position
            position_counts = player_bluffs['position'].value_counts()
            total_bluffs = len(player_bluffs)
            
            # Calculate average bluff size and relative sizing
            avg_bluff_size = player_bluffs['bluff_amount'].mean()
            
            # Analyze bluff types
            bluff_type_counts = player_bluffs['bluff_type'].value_counts()
            
            # Analyze bluff streets
            street_counts = player_bluffs['bluff_street'].value_counts()
            
            # Analyze board textures in bluffs
            board_textures = player_bluffs['board_texture'].apply(lambda x: {
                'paired': x['paired'],
                'suited': x['suited'],
                'connected': x['connected'],
                'high_cards': x['high_cards'],
                'draw_heavy': x['draw_heavy']
            }).tolist()
            
            texture_stats = {
                'paired_boards': sum(1 for t in board_textures if t['paired']) / total_bluffs if total_bluffs > 0 else 0,
                'suited_boards': sum(1 for t in board_textures if t['suited']) / total_bluffs if total_bluffs > 0 else 0,
                'connected_boards': sum(1 for t in board_textures if t['connected']) / total_bluffs if total_bluffs > 0 else 0,
                'draw_heavy_boards': sum(1 for t in board_textures if t['draw_heavy']) / total_bluffs if total_bluffs > 0 else 0
            }
            
            # Analyze bet sizing patterns
            bet_sizing_patterns = player_bluffs['bet_sizing'].apply(lambda x: {
                street: size for street, size in x.items()
            }).tolist()
            
            avg_bet_sizing = {
                'flop': sum(p.get('flop', 0) for p in bet_sizing_patterns) / sum(1 for p in bet_sizing_patterns if 'flop' in p) if any('flop' in p for p in bet_sizing_patterns) else 0,
                'turn': sum(p.get('turn', 0) for p in bet_sizing_patterns) / sum(1 for p in bet_sizing_patterns if 'turn' in p) if any('turn' in p for p in bet_sizing_patterns) else 0,
                'river': sum(p.get('river', 0) for p in bet_sizing_patterns) / sum(1 for p in bet_sizing_patterns if 'river' in p) if any('river' in p for p in bet_sizing_patterns) else 0
            }
            
            bluff_stats[player] = {
                'total_bluffs': total_bluffs,
                'avg_bluff_size': avg_bluff_size,
                'position_frequencies': {
                    pos: count/total_bluffs for pos, count in position_counts.items()
                } if total_bluffs > 0 else {},
                'street_frequencies': {
                    street: count/total_bluffs for street, count in street_counts.items()
                } if total_bluffs > 0 else {},
                'bluff_type_distribution': {
                    btype: count/total_bluffs for btype, count in bluff_type_counts.items()
                } if total_bluffs > 0 else {},
                'board_texture_frequencies': texture_stats,
                'avg_bet_sizing_by_street': avg_bet_sizing,
                'bluff_sequences': [
                    {
                        'sequence': seq,
                        'type': btype,
                        'street': street,
                        'board_texture': texture,
                        'hand_strength': strength
                    }
                    for seq, btype, street, texture, strength in zip(
                        player_bluffs['action_sequence'],
                        player_bluffs['bluff_type'],
                        player_bluffs['bluff_street'],
                        player_bluffs['board_texture'],
                        player_bluffs['hand_strength']
                    )
                ]
            }
        
        return bluff_stats

def create_player_profiles(parsed_hands: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create a DataFrame with comprehensive player profiles."""
    calculator = PokerFeatureCalculator()
    
    # Get unique players
    all_players = set()
    for hand in parsed_hands:
        all_players.update(hand['players'])
    
    # Calculate stats for each player
    profiles = []
    for player in all_players:
        profile = calculator.calculate_player_stats(parsed_hands, player)
        profile['player_name'] = player
        profiles.append(profile)
    
    return pd.DataFrame(profiles) 