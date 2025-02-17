import argparse
import logging
from pathlib import Path
from maverick.data.parser import HandHistoryParser
from maverick.features import PokerFeatureCalculator, create_player_profiles

# Set logging level to ERROR to reduce noise
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def format_percentage(value: float) -> str:
    """Format float as percentage with one decimal place."""
    return f"{value*100:.1f}%"

def format_ratio(value: float) -> str:
    """Format float ratio with two decimal places."""
    return f"{value:.2f}"

def format_currency(value: float) -> str:
    """Format float as currency with two decimal places."""
    return f"${value:.2f}"

def main():
    parser = argparse.ArgumentParser(description='Analyze poker player statistics')
    parser.add_argument('--file', type=str, 
                       default='maverick/data/dataset/handhq/ABS-2009-07-01_2009-07-23_1000NLH_OBFU/10/abs NLH handhq_1-OBFUSCATED.phhs',
                       help='Path to the hand history file')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of hands to process')
    args = parser.parse_args()
    
    # Initialize parser and calculator
    hand_parser = HandHistoryParser()
    calculator = PokerFeatureCalculator()
    
    # Parse hands
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return
    
    print(f"\nParsing file: {file_path}")
    hands = hand_parser.parse_file(file_path)
    if args.limit:
        hands = hands[:args.limit]
    
    print(f"\nProcessed {len(hands)} hands")
    
    # Create player profiles
    profiles = create_player_profiles(hands)
    
    # Analyze bluff patterns
    bluff_stats = calculator.analyze_bluff_patterns(hands)
    
    # Display results
    print("\nPlayer Statistics:")
    print("=" * 100)
    
    for _, player in profiles.iterrows():
        player_name = player['player_name']
        print(f"\nPlayer: {player_name}")
        print(f"Hands played: {int(player['hands_played'])}")
        
        # Basic Stats
        print("\nBasic Stats:")
        print(f"  VPIP: {format_percentage(player['vpip'])} ({int(player['hands_played']*player['vpip'])} hands)")
        print(f"  PFR: {format_percentage(player['pfr'])} ({int(player['hands_played']*player['pfr'])} hands)")
        
        # Aggression Factors by Street
        print("\nAggression Factors:")
        for street in ['preflop', 'flop', 'turn', 'river']:
            af_key = f'af_{street}'
            if af_key in player:
                print(f"  {street.capitalize()}: {format_ratio(player[af_key])}")
        print(f"  Total AF: {format_ratio(player['af_total'])}")
        
        # Position Stats
        print("\nPosition Stats:")
        positions = ['button', 'cutoff', 'sb', 'bb', 'early', 'middle']
        for pos in positions:
            freq_key = f'pos_{pos}_freq'
            vpip_key = f'pos_{pos}_vpip'
            pfr_key = f'pos_{pos}_pfr'
            if freq_key in player and vpip_key in player and pfr_key in player:
                pos_hands = int(player['hands_played'] * player[freq_key])
                print(f"  {pos.upper()} ({pos_hands} hands):")
                print(f"    Frequency: {format_percentage(player[freq_key])}")
                print(f"    VPIP: {format_percentage(player[vpip_key])}")
                print(f"    PFR: {format_percentage(player[pfr_key])}")
        
        # Advanced Stats
        print("\nAdvanced Stats:")
        print(f"  C-Bet Frequency: {format_percentage(player['cbet_frequency'])}")
        print(f"  C-Bet Success Rate: {format_percentage(player['cbet_success_rate'])}")
        
        # Enhanced Bluff Analysis
        if player_name in bluff_stats:
            bluff_data = bluff_stats[player_name]
            print("\nBluff Analysis:")
            print(f"  Total Bluffs: {bluff_data['total_bluffs']}")
            if bluff_data['total_bluffs'] > 0:
                print(f"  Avg Bluff Size: {format_currency(bluff_data['avg_bluff_size'])}")
                
                # Display bluff types distribution
                bluff_types = {
                    'pure_bluff': 0,
                    'semi_bluff': 0
                }
                for seq in bluff_data.get('bluff_sequences', []):
                    if isinstance(seq, dict) and 'bluff_type' in seq:
                        bluff_types[seq['bluff_type']] += 1
                
                print("\n  Bluff Type Distribution:")
                for btype, count in bluff_types.items():
                    if count > 0:
                        print(f"    {btype.replace('_', ' ').title()}: {format_percentage(count/bluff_data['total_bluffs'])}")
                
                print("\n  Bluff Position Frequencies:")
                for pos, freq in bluff_data['position_frequencies'].items():
                    print(f"    {pos.upper()}: {format_percentage(freq)}")
                
                print("\n  Bluff Street Frequencies:")
                for street, freq in bluff_data['street_frequencies'].items():
                    print(f"    {street.capitalize()}: {format_percentage(freq)}")
                
                print("\n  Sample Bluff Sequences:")
                for i, sequence in enumerate(bluff_data['bluff_sequences'][:3], 1):
                    print(f"\n    Bluff #{i}:")
                    if isinstance(sequence, dict):
                        # Display board texture
                        if 'board_texture' in sequence:
                            texture = sequence['board_texture']
                            print(f"      Board Texture:")
                            print(f"        Draw Heavy: {'Yes' if texture.get('draw_heavy') else 'No'}")
                            print(f"        High Cards: {texture.get('high_cards', 0)}")
                            print(f"        Paired: {'Yes' if texture.get('paired') else 'No'}")
                            print(f"        Suited: {'Yes' if texture.get('suited') else 'No'}")
                            print(f"        Connected: {'Yes' if texture.get('connected') else 'No'}")
                        
                        # Display hand strength if available
                        if 'hand_strength' in sequence:
                            print(f"      Hand Strength: {format_percentage(sequence['hand_strength'])}")
                        
                        # Display action sequence
                        if 'action_sequence' in sequence:
                            for action in sequence['action_sequence']:
                                print(f"      {action}")
                    else:
                        for action in sequence:
                            print(f"      {action}")
        
        print("-" * 80)

if __name__ == '__main__':
    main() 