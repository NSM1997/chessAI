"""
Data preprocessing for chess position classification
Converts FEN strings to tensor representations for CNN training
"""

import numpy as np
import chess
from typing import Tuple, List, Dict
import json
from pathlib import Path


class ChessBoardEncoder:
    """
    Encode chess boards as tensors for neural network input
    
    Representation: 8x8x12 tensor
    - 12 channels: 6 piece types × 2 colors (White: P,N,B,R,Q,K, Black: p,n,b,r,q,k)
    - 8x8 board squares
    """
    
    # Piece to channel mapping
    PIECE_TO_CHANNEL = {
        chess.PAWN: 0,
        chess.KNIGHT: 1,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4,
        chess.KING: 5,
    }
    
    def __init__(self):
        self.input_shape = (8, 8, 12)
    
    def encode_board(self, board: chess.Board) -> np.ndarray:
        """
        Convert a chess board to tensor representation
        
        Args:
            board: python-chess Board object
            
        Returns:
            tensor: 8x8x12 numpy array
        """
        tensor = np.zeros((8, 8, 12), dtype=np.float32)
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            
            if piece is not None:
                # Get rank and file (0-7)
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                
                # Get channel index (0-11)
                piece_type_channel = self.PIECE_TO_CHANNEL[piece.piece_type]
                
                # White pieces: channels 0-5, Black pieces: channels 6-11
                if piece.color == chess.WHITE:
                    channel = piece_type_channel
                else:
                    channel = piece_type_channel + 6
                
                # Set the position in the tensor
                tensor[rank, file, channel] = 1.0
        
        return tensor
    
    def encode_fen(self, fen: str) -> np.ndarray:
        """
        Convert FEN string to tensor
        
        Args:
            fen: FEN string
            
        Returns:
            tensor: 8x8x12 numpy array
        """
        try:
            board = chess.Board(fen)
            return self.encode_board(board)
        except Exception as e:
            print(f"Error encoding FEN '{fen}': {e}")
            # Return empty board on error
            return np.zeros((8, 8, 12), dtype=np.float32)
    
    def decode_tensor(self, tensor: np.ndarray) -> chess.Board:
        """
        Convert tensor back to chess board (for visualization/debugging)
        
        Args:
            tensor: 8x8x12 numpy array
            
        Returns:
            board: python-chess Board object
        """
        board = chess.Board(fen=None)  # Empty board
        board.clear()
        
        piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
        
        for rank in range(8):
            for file in range(8):
                # Check white pieces (channels 0-5)
                for channel in range(6):
                    if tensor[rank, file, channel] > 0.5:
                        square = chess.square(file, rank)
                        piece = chess.Piece(piece_types[channel], chess.WHITE)
                        board.set_piece_at(square, piece)
                
                # Check black pieces (channels 6-11)
                for channel in range(6, 12):
                    if tensor[rank, file, channel] > 0.5:
                        square = chess.square(file, rank)
                        piece = chess.Piece(piece_types[channel - 6], chess.BLACK)
                        board.set_piece_at(square, piece)
        
        return board


class TacticalThemeEncoder:
    """
    Encode tactical themes as labels for classification
    """
    
    # Primary tactical themes we'll classify
    # Based on Lichess taxonomy
    THEMES = [
        'fork',
        'pin',
        'skewer',
        'discoveredAttack',
        'doubleAttack',
        'mate',
        'mateIn1',
        'mateIn2',
        'attraction',
        'deflection',
        'interference',
        'clearance',
        'sacrifice',
        'backRankMate',
        'hangingPiece',
        'trappedPiece',
        'enPassant',
        'promotion',
        'underPromotion',
        'xRayAttack'
    ]
    
    def __init__(self, themes: List[str] = None):
        """
        Initialize theme encoder
        
        Args:
            themes: List of theme names. If None, uses default THEMES
        """
        self.themes = themes or self.THEMES
        self.theme_to_idx = {theme: idx for idx, theme in enumerate(self.themes)}
        self.idx_to_theme = {idx: theme for theme, idx in self.theme_to_idx.items()}
        self.num_classes = len(self.themes)
    
    def encode_themes(self, themes: List[str], multi_label: bool = True) -> np.ndarray:
        """
        Encode list of themes as vector
        
        Args:
            themes: List of theme strings
            multi_label: If True, return multi-hot encoding. If False, return single label
            
        Returns:
            encoding: Vector representation
        """
        if multi_label:
            # Multi-hot encoding (multiple themes can be active)
            encoding = np.zeros(self.num_classes, dtype=np.float32)
            for theme in themes:
                if theme in self.theme_to_idx:
                    encoding[self.theme_to_idx[theme]] = 1.0
            return encoding
        else:
            # Single label (first matching theme)
            for theme in themes:
                if theme in self.theme_to_idx:
                    return np.array([self.theme_to_idx[theme]], dtype=np.int64)
            # Return 'other' or first class if no match
            return np.array([0], dtype=np.int64)
    
    def decode_themes(self, encoding: np.ndarray, threshold: float = 0.5) -> List[str]:
        """
        Decode vector back to theme names
        
        Args:
            encoding: Vector or probabilities
            threshold: Probability threshold for multi-label
            
        Returns:
            themes: List of theme names
        """
        themes = []
        for idx, value in enumerate(encoding):
            if value >= threshold:
                themes.append(self.idx_to_theme[idx])
        return themes


class ChessDataset:
    """
    Dataset loader for chess tactical puzzles
    """
    
    def __init__(self, 
                 data_path: str,
                 board_encoder: ChessBoardEncoder = None,
                 theme_encoder: TacticalThemeEncoder = None):
        """
        Initialize dataset
        
        Args:
            data_path: Path to JSON file with puzzles
            board_encoder: Board encoder instance
            theme_encoder: Theme encoder instance
        """
        self.data_path = Path(data_path)
        self.board_encoder = board_encoder or ChessBoardEncoder()
        self.theme_encoder = theme_encoder or TacticalThemeEncoder()
        
        # Load puzzles
        with open(self.data_path, 'r') as f:
            self.puzzles = json.load(f)
        
        print(f"Loaded {len(self.puzzles)} puzzles from {self.data_path}")
    
    def __len__(self) -> int:
        return len(self.puzzles)
    
    def __getitem__(self, idx: int) -> Tuple[np.ndarray, np.ndarray, Dict]:
        """
        Get a single training example
        
        Args:
            idx: Index
            
        Returns:
            board_tensor: 8x8x12 tensor
            theme_label: Multi-hot theme encoding
            metadata: Puzzle metadata
        """
        puzzle = self.puzzles[idx]
        
        # Encode board
        board_tensor = self.board_encoder.encode_fen(puzzle['fen'])
        
        # Encode themes
        theme_label = self.theme_encoder.encode_themes(puzzle['themes'], multi_label=True)
        
        # Metadata
        metadata = {
            'puzzle_id': puzzle['puzzle_id'],
            'rating': puzzle.get('rating', 1500),
            'themes': puzzle['themes'],
            'fen': puzzle['fen']
        }
        
        return board_tensor, theme_label, metadata
    
    def get_batch(self, batch_size: int = 32) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
        """
        Get a random batch of training examples
        
        Args:
            batch_size: Number of examples
            
        Returns:
            boards: Batch of board tensors (batch_size, 8, 8, 12)
            labels: Batch of theme labels (batch_size, num_classes)
            metadata: List of metadata dicts
        """
        indices = np.random.choice(len(self), size=batch_size, replace=False)
        
        boards = []
        labels = []
        metadata = []
        
        for idx in indices:
            board, label, meta = self[idx]
            boards.append(board)
            labels.append(label)
            metadata.append(meta)
        
        return np.array(boards), np.array(labels), metadata
    
    def split_train_val_test(self, 
                             train_ratio: float = 0.7,
                             val_ratio: float = 0.15,
                             test_ratio: float = 0.15) -> Tuple['ChessDataset', 'ChessDataset', 'ChessDataset']:
        """
        Split dataset into train/val/test sets
        
        Args:
            train_ratio: Fraction for training
            val_ratio: Fraction for validation
            test_ratio: Fraction for testing
            
        Returns:
            train_dataset, val_dataset, test_dataset
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
        
        n = len(self.puzzles)
        indices = np.random.permutation(n)
        
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        train_puzzles = [self.puzzles[i] for i in indices[:train_end]]
        val_puzzles = [self.puzzles[i] for i in indices[train_end:val_end]]
        test_puzzles = [self.puzzles[i] for i in indices[val_end:]]
        
        # Create new datasets
        train_dataset = ChessDataset.__new__(ChessDataset)
        train_dataset.puzzles = train_puzzles
        train_dataset.board_encoder = self.board_encoder
        train_dataset.theme_encoder = self.theme_encoder
        train_dataset.data_path = self.data_path
        
        val_dataset = ChessDataset.__new__(ChessDataset)
        val_dataset.puzzles = val_puzzles
        val_dataset.board_encoder = self.board_encoder
        val_dataset.theme_encoder = self.theme_encoder
        val_dataset.data_path = self.data_path
        
        test_dataset = ChessDataset.__new__(ChessDataset)
        test_dataset.puzzles = test_puzzles
        test_dataset.board_encoder = self.board_encoder
        test_dataset.theme_encoder = self.theme_encoder
        test_dataset.data_path = self.data_path
        
        print(f"Split dataset: {len(train_puzzles)} train, {len(val_puzzles)} val, {len(test_puzzles)} test")
        
        return train_dataset, val_dataset, test_dataset


# Example usage
if __name__ == "__main__":
    # Test encoding
    encoder = ChessBoardEncoder()
    theme_encoder = TacticalThemeEncoder()
    
    # Test board encoding
    test_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    tensor = encoder.encode_fen(test_fen)
    
    print(f"Encoded FEN to tensor shape: {tensor.shape}")
    print(f"Non-zero elements: {np.count_nonzero(tensor)}")
    
    # Test decoding
    decoded_board = encoder.decode_tensor(tensor)
    print(f"\nOriginal FEN: {test_fen}")
    print(f"Decoded board:\n{decoded_board}")
    
    # Test theme encoding
    test_themes = ['fork', 'pin', 'mate']
    theme_vector = theme_encoder.encode_themes(test_themes)
    print(f"\nTheme encoding: {theme_vector}")
    print(f"Active themes: {theme_encoder.decode_themes(theme_vector)}")

