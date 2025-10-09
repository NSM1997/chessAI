import chess.pgn
import chess.engine
import pandas as pd

def process_lichess_pgn(file_path):
    """Extract FEN positions and moves from PGN files"""
    games = []
    with open(file_path, encoding="utf-8") as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            board = game.board()
            for move in game.mainline_moves():
                fen = board.fen()
                uci_move = move.uci()
                games.append({
                    "fen": fen,
                    "move": uci_move
                })
                board.push(move)
    return games