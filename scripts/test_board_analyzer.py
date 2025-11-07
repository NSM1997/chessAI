#!/usr/bin/env python3
"""
Test script for the intelligent board analyzer
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import chess
from app.services.board_analyzer import BoardAnalyzer
import json


def test_opening_position():
    """Test analysis on starting position"""
    print("=" * 80)
    print("TEST 1: Starting Position Analysis")
    print("=" * 80)
    
    board = chess.Board()
    analyzer = BoardAnalyzer()
    
    analysis = analyzer.analyze_position(board)
    
    print(f"\nHanging pieces: {len(analysis['hanging_pieces'])}")
    print(f"Threats: {len(analysis['threats'])}")
    print(f"White king safety: {analysis['king_safety']['white']}")
    print(f"Piece activity: {analysis['piece_activity']}")
    print(f"Central control: {analysis['control']}")


def test_move_analysis():
    """Test move analysis"""
    print("\n" + "=" * 80)
    print("TEST 2: Move Analysis - e2e4")
    print("=" * 80)
    
    board = chess.Board()
    analyzer = BoardAnalyzer()
    
    move = chess.Move.from_uci("e2e4")
    impact = analyzer.analyze_move_impact(board, move)
    
    print(f"\nMove: {impact['san']}")
    print(f"Is capture: {impact['is_capture']}")
    print(f"Is check: {impact['is_check']}")
    print(f"Tactical purpose: {impact['tactical_purpose']}")
    print(f"Creates attacks on: {impact['creates_attacks']}")
    print(f"Position improvement: {impact['improves_position']}")


def test_tactical_position():
    """Test position with hanging piece"""
    print("\n" + "=" * 80)
    print("TEST 3: Tactical Position - Hanging Knight")
    print("=" * 80)
    
    # Position where black knight on f6 is hanging
    fen = "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    board = chess.Board(fen)
    analyzer = BoardAnalyzer()
    
    analysis = analyzer.analyze_position(board)
    
    print(f"\nHanging pieces: {analysis['hanging_pieces']}")
    print(f"Threats: {analysis['threats']}")
    
    # Test capturing the hanging knight
    if analysis['hanging_pieces']:
        print("\nTesting capture of hanging piece:")
        # Find a move that captures the hanging piece
        hanging_square = chess.parse_square(analysis['hanging_pieces'][0]['square'])
        for move in board.legal_moves:
            if move.to_square == hanging_square:
                impact = analyzer.analyze_move_impact(board, move)
                print(f"Move {impact['san']}: captures hanging {chess.piece_name(impact['captured_piece'])}")
                break


def test_defensive_move():
    """Test position requiring defense"""
    print("\n" + "=" * 80)
    print("TEST 4: Defensive Position - Piece Under Attack")
    print("=" * 80)
    
    # Position where white queen is attacked
    fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPPQPPP/RNB1KBNR b KQkq - 1 2"
    board = chess.Board(fen)
    analyzer = BoardAnalyzer()
    
    analysis = analyzer.analyze_position(board)
    
    print(f"\nHanging pieces: {analysis['hanging_pieces']}")
    print(f"Threats detected: {len(analysis['threats'])}")
    
    # Test a defensive move
    if analysis['hanging_pieces']:
        print("\nAnalyzing defensive move:")
        # Queen retreats to e2
        board_white = chess.Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPPQPPP/RNB1KBNR w KQkq - 0 3")
        move = chess.Move.from_uci("e2d1")  # Queen retreats
        impact = analyzer.analyze_move_impact(board_white, move)
        print(f"Move {impact['san']}")
        print(f"Removes threats: {impact['removes_threats']}")


def main():
    """Run all tests"""
    test_opening_position()
    test_move_analysis()
    test_tactical_position()
    test_defensive_move()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
