#!/usr/bin/env python3
"""
Interactive test script for the Chess AI server
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def analyze_position(fen, description=""):
    """Analyze a chess position"""
    print(f"\n=== Analyzing Position: {description} ===")
    print(f"FEN: {fen}")
    
    payload = {"fen": fen}
    response = requests.post(f"{BASE_URL}/analyze-position", json=payload)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nBest Move: {data['best_moves'][0]['san']} ({data['best_moves'][0]['move']})")
        print(f"Score: {data['best_moves'][0]['score']['display']}")
        print(f"\nExplanation: {data['explanations'][0]['explanation']}")
        print(f"Tactical Motifs: {', '.join(data['explanations'][0]['tactical_motifs'])}")
        print(f"Strategic Concepts: {', '.join(data['explanations'][0]['strategic_concepts'])}")
        print(f"\nPosition Type: {data['position_evaluation']['position_type']}")
        print(f"Material Balance: {data['position_evaluation']['material_balance']['difference']}")
        print(f"\nLearning Insights:")
        for insight in data['learning_insights']:
            print(f"  • {insight}")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def main():
    """Run interactive tests"""
    print("=" * 60)
    print("Chess AI Server Test Suite")
    print("=" * 60)
    
    # Test basic endpoints
    if not test_health():
        print("\n[FAIL] Health check failed!")
        return
    
    if not test_root():
        print("\n[FAIL] Root endpoint failed!")
        return
    
    print("\n[SUCCESS] Server is healthy and responding!")
    
    # Test various positions
    test_positions = [
        {
            "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
            "description": "Opening - After 1.e4"
        },
        {
            "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
            "description": "Opening - After 1.e4 e5 2.Nf3 Nc6"
        },
        {
            "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5",
            "description": "Opening - Italian Game"
        },
        {
            "fen": "8/5k2/3p4/1p1Pp2p/pP2Pp1P/P4P1K/8/8 b - - 99 50",
            "description": "Endgame - King and Pawns"
        }
    ]
    
    for i, pos in enumerate(test_positions, 1):
        print(f"\n{'=' * 60}")
        print(f"Test {i}/{len(test_positions)}")
        if not analyze_position(pos["fen"], pos["description"]):
            print(f"\n[FAIL] Analysis failed for position {i}")
        else:
            print(f"\n[SUCCESS] Position {i} analyzed successfully!")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)

