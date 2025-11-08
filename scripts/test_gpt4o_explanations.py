#!/usr/bin/env python3
"""
Test GPT-4o explanation quality
Run this while server is running: python simple_server.py
"""

import requests
import json
import time

def test_position(fen, description):
    """Test a position and show GPT-4o explanation"""
    print(f"\n{'='*80}")
    print(f"Position: {description}")
    print(f"{'='*80}")
    
    try:
        response = requests.post(
            "http://localhost:8001/analyze-position",
            json={"fen": fen},
            timeout=30  # GPT-4o might take a few seconds
        )
        
        if response.status_code == 200:
            data = response.json()
            best_move = data['best_moves'][0]
            explanation = data['explanations'][0]
            
            print(f"\n🎯 Best Move: {best_move['san']}")
            print(f"📊 Evaluation: {best_move['score']['display']}")
            print(f"\n💬 GPT-4o Explanation:")
            print(f"   {explanation['explanation']}")
            print(f"\n✅ Tactical Themes: {', '.join(explanation['tactical_motifs'][:3])}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        print("Make sure server is running: python simple_server.py")

def main():
    print("="*80)
    print("GPT-4o CHESS EXPLANATION TEST")
    print("="*80)
    print("Testing natural language explanations powered by GPT-4o\n")
    
    # Test 1: Starting position
    test_position(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "Opening: Starting Position"
    )
    
    time.sleep(1)
    
    # Test 2: Tactical position
    test_position(
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4",
        "Italian Game: Should Castle"
    )
    
    time.sleep(1)
    
    # Test 3: Tactical shot
    test_position(
        "r1bqkb1r/pppp1ppp/2n5/4p3/2BnP3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
        "Tactical: Knight Fork Available"
    )
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nNotice how GPT-4o:")
    print("✅ Explains the 'why' behind moves")
    print("✅ Uses natural, coach-like language")
    print("✅ References actual board features")
    print("✅ Provides strategic context")

if __name__ == "__main__":
    main()
