import argparse
import logging
from pathlib import Path
from maverick.data.parser import HandHistoryParser

# Set logging level to ERROR to reduce noise
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def format_hand_summary(hand: dict) -> str:
    """Format a hand summary in a clean, readable way."""
    summary = []
    summary.append(f"\n{'='*50}")
    
    # Players and their stacks
    summary.append("\nPlayers:")
    for i, (player, stack) in enumerate(zip(hand['players'], hand['stacks']), 1):
        stack_str = f"${float(stack):.2f}" if stack else "Unknown"
        player_str = f"  {player} - Stack: {stack_str}"
        # Add hole cards if shown
        if str(i) in hand['hole_cards']:
            cards = hand['hole_cards'][str(i)]
            player_str += f" - Cards: {cards[0]} {cards[1]}"
        summary.append(player_str)
    
    # Community Cards
    summary.append("\nCommunity Cards:")
    if hand['community_cards']:
        summary.append("  " + " ".join(str(card) for card in hand['community_cards']))
    else:
        summary.append("  None")
    
    # Actions
    summary.append("\nActions:")
    for action in hand['actions']:
        amount_str = f" ${action['amount']:.2f}" if action['amount'] else ""
        summary.append(f"  Player {action['player']} {action['type']}{amount_str} ({action['street']})")
    
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description='Parse poker hand histories')
    parser.add_argument('--sample', action='store_true', help='Only process one file')
    parser.add_argument('--limit', type=int, default=6, help='Limit number of hands to process')
    args = parser.parse_args()
    
    # Initialize parser
    hand_parser = HandHistoryParser()
    
    # Use the specific file we want to parse
    file_path = Path('maverick/data/dataset/handhq/ABS-2009-07-01_2009-07-23_1000NLH_OBFU/10/abs NLH handhq_1-OBFUSCATED.phhs')
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return
    
    print(f"\nParsing file: {file_path}")
    
    # Process file
    hands = hand_parser.parse_file(file_path)
    hands = hands[:args.limit] if args.limit else hands
    
    print(f"\nProcessed {len(hands)} hands")
    
    # Print hands
    if hands:
        for hand in hands:
            print(format_hand_summary(hand))

if __name__ == '__main__':
    main() 