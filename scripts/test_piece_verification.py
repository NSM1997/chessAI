#!/usr/bin/env python3
"""
Test script to verify piece map generation prevents hallucination
"""

import chess
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def generate_piece_map(board: chess.Board) -> str:
    """Generate piece map string for LLM prompt"""
    piece_symbols = {
        chess.PAWN: 'pawn', 
        chess.KNIGHT: 'knight', 
        chess.BISHOP: 'bishop', 
        chess.ROOK: 'rook',
        chess.QUEEN: 'queen', 
        chess.KING: 'king'
    }
    
    board_pieces = []
    for square, piece in board.piece_map().items():
        square_name = chess.square_name(square)
        piece_name = piece_symbols.get(piece.piece_type, 'piece')
        color = 'White' if piece.color == chess.WHITE else 'Black'
        board_pieces.append(f"{color} {piece_name} on {square_name}")
    
    return "\n".join(sorted(board_pieces))


def test_position_with_pin():
    """Test a position where a pin might be incorrectly detected"""
    # Position where knight is NOT on f3 (to catch hallucination)
    fen = "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"
    
    board = chess.Board(fen)
    piece_map = generate_piece_map(board)
    
    print("=== Test Position: Italian Game ===")
    print(f"FEN: {fen}\n")
    print("Piece Map:")
    print(piece_map)
    print("\n" + "="*60)
    
    # Check if f3 has a knight
    f3_piece = board.piece_at(chess.F3)
    if f3_piece and f3_piece.piece_type == chess.KNIGHT:
        print("✓ Knight IS on f3")
    else:
        print("✗ No knight on f3 (would catch hallucination)")
    
    print()


def test_minimal_endgame():
    """Test minimal endgame position"""
    fen = "8/8/3k4/8/8/3K4/3P4/8 w - - 0 1"
    
    board = chess.Board(fen)
    piece_map = generate_piece_map(board)
    
    print("=== Test Position: King and Pawn Endgame ===")
    print(f"FEN: {fen}\n")
    print("Piece Map:")
    print(piece_map)
    print("\n" + "="*60 + "\n")


def test_tactical_position():
    """Test a position with clear tactical themes"""
    # Back rank weakness
    fen = "6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1"
    
    board = chess.Board(fen)
    piece_map = generate_piece_map(board)
    
    print("=== Test Position: Back Rank Mate Threat ===")
    print(f"FEN: {fen}\n")
    print("Piece Map:")
    print(piece_map)
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    print("Testing Piece Map Generation for LLM Verification\n")
    print("="*60 + "\n")
    
    test_position_with_pin()
    test_minimal_endgame()
    test_tactical_position()
    
    print("\n✓ All tests completed!")
    print("\nThis piece map will be included in LLM prompts to prevent")
    print("hallucinating pieces that don't exist on the board.")
