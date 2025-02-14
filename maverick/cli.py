import argparse
from typing import List
from .core.poker_utils import PokerUtils

def parse_args():
    parser = argparse.ArgumentParser(description='Poker Copilot - Hand Analysis Tool')
    parser.add_argument('player_hand', type=str, help='Player hand (e.g., "As Kh")')
    parser.add_argument('--community', '-c', type=str, help='Community cards (e.g., "Jh Td Qc")')
    parser.add_argument('--simulations', '-n', type=int, default=10000,
                       help='Number of Monte Carlo simulations')
    parser.add_argument('--opponents', '-o', type=int, default=2,
                       help='Number of opponents')
    parser.add_argument('--pot', '-p', type=float, default=100.0,
                       help='Current pot size')
    parser.add_argument('--bet', '-b', type=float, default=20.0,
                       help='Current bet to call')
    parser.add_argument('--stack', '-s', type=float, default=1000.0,
                       help='Your stack size')
    parser.add_argument('--position', type=str, default='button',
                       choices=['early', 'middle', 'late', 'button'],
                       help='Your position')
    return parser.parse_args()

def main():
    args = parse_args()
    utils = PokerUtils()
    
    print("\nPoker Copilot - Hand Analysis")
    print("=" * 40)
    
    print(f"\nAnalyzing hand: {args.player_hand}")
    if args.community:
        print(f"Community cards: {args.community}")
    print(f"Against {args.opponents} opponent(s)")
    
    # Run Monte Carlo simulation
    win_prob, stats = utils.monte_carlo_sim(
        args.player_hand,
        args.community,
        num_simulations=args.simulations,
        num_opponents=args.opponents
    )
    
    # Calculate outs if community cards are present
    if args.community:
        outs, draws = utils.calculate_outs(args.player_hand, args.community)
    
    # Get move recommendation
    move, bet_size = utils.recommend_move(
        win_probability=win_prob,
        pot_size=args.pot,
        current_bet=args.bet,
        stack_size=args.stack,
        position=args.position
    )
    
    # Print results
    print("\nResults:")
    print("-" * 40)
    print(f"Win Probability: {win_prob*100:.1f}%")
    
    if args.community:
        print(f"\nDrawing Opportunities:")
        print(f"Total outs: {outs}")
        for draw in draws:
            print(f"- {draw.draw_type}: {draw.outs} outs")
    
    print(f"\nRecommended Action: {move}")
    if bet_size:
        print(f"Suggested bet size: {bet_size:.2f}")
    
    print("\nDetailed Statistics:")
    print(f"Wins: {stats['wins']}")
    print(f"Splits: {stats['splits']}")
    print(f"Losses: {stats['losses']}")
    
    pot_odds = args.bet / (args.pot + args.bet)
    print(f"\nPot Odds: {pot_odds*100:.1f}%")
    if win_prob > pot_odds:
        print("✓ Positive expected value")
    else:
        print("✗ Negative expected value")

if __name__ == '__main__':
    main() 