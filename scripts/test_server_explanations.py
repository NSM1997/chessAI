#!/usr/bin/env python3
"""
Test the server's explanation generation
"""

import requests
import json

def test_explanation(fen, description):
    """Test a single position"""
    print(f"\n{'='*80}")
    print(f"Testing: {description}")
    print(f"{'='*80}")
    print(f"FEN: {fen}\n")
    
    try:
        response = requests.post(
            "http://localhost:8001/analyze-position",
            json={"fen": fen},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            best_move = data['best_moves'][0]
            explanation = data['explanations'][0]
            
            print(f"Best Move: {best_move['san']}")
            print(f"Evaluation: {best_move['score']['display']}")
            print(f"\n📝 Explanation:")
            print(f"{explanation['explanation']}")
            print(f"\n✓ Tactical Motifs: {', '.join(explanation['tactical_motifs'])}")
            
            # Check if it's using board analysis
            if 'attacking' in explanation['explanation'].lower() or \
               'defending' in explanation['explanation'].lower() or \
               'safety' in explanation['explanation'].lower():
                print("✅ Uses board context!")
            else:
                print("⚠️  Generic explanation")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed: {e}")

def main():
    print("=" * 80)
    print("SERVER EXPLANATION TESTS")
    print("=" * 80)
    print("Make sure server is running: python simple_server.py")
    print()
    
    # Test 1: Starting position
    test_explanation(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "Starting Position"
    )
    
    # Test 2: Italian Game position (castling)
    test_explanation(
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4",
        "Italian Game - Time to Castle"
    )
    
    # Test 3: Position with hanging piece
    test_explanation(
        "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "Hanging Pawn on e5"
    )
    
    # Test 4: Pin tactic
    test_explanation(
        "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
        "Pin the Knight"
    )
    
    print("\n" + "=" * 80)
    print("TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()
