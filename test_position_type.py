#!/usr/bin/env python3

import sys
sys.path.append('backend')
import chess

def test_position_type(fen):
    """Test position type detection logic"""
    try:
        board = chess.Board(fen)
        
        # Count pieces to determine game phase
        piece_count = len(board.piece_map())
        queens = len([p for p in board.piece_map().values() if p.piece_type == chess.QUEEN])
        pawns = len([p for p in board.piece_map().values() if p.piece_type == chess.PAWN])
        minor_pieces = len([p for p in board.piece_map().values() if p.piece_type in [chess.KNIGHT, chess.BISHOP]])
        
        print(f"FEN: {fen}")
        print(f"Piece analysis: count={piece_count}, queens={queens}, pawns={pawns}, minor={minor_pieces}")
        
        # Determine position type based on piece count and structure
        if piece_count <= 12:  # Very few pieces left
            position_type = "endgame"
            print(f"Set to endgame: piece_count <= 12")
        elif piece_count <= 20 or queens == 0:  # Few pieces or no queens
            position_type = "endgame"
            print(f"Set to endgame: piece_count <= 20 or queens == 0")
        elif piece_count <= 24 and minor_pieces <= 4:  # Reduced material
            position_type = "endgame"
            print(f"Set to endgame: piece_count <= 24 and minor_pieces <= 4")
        elif piece_count >= 30 and pawns >= 12:  # Many pieces and pawns
            position_type = "opening"
            print(f"Set to opening: piece_count >= 30 and pawns >= 12")
        elif piece_count >= 24:  # Good amount of pieces
            position_type = "middlegame"
            print(f"Set to middlegame: piece_count >= 24")
        else:
            position_type = "middlegame"
            print(f"Set to middlegame: default")
            
        print(f"Final position type: {position_type}")
        print("-" * 50)
        return position_type
        
    except Exception as e:
        print(f"Error: {e}")
        return "error"

if __name__ == "__main__":
    # Test different positions
    test_cases = [
        "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1",  # Opening
        "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",  # Complex middlegame
        "8/8/8/8/8/8/4K3/4k3 w - - 0 1",  # Endgame (only kings)
        "8/8/8/8/8/4K3/4P3/4k3 w - - 0 1",  # Endgame (king + pawn)
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",  # e4 opening
    ]
    
    for fen in test_cases:
        test_position_type(fen)
