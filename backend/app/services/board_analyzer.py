"""
Intelligent Board Analyzer
Analyzes chess positions to understand attacks, defenses, threats, and tactical elements.
This provides context for generating meaningful explanations.
"""

import chess
from typing import Dict, List, Set, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BoardAnalyzer:
    """
    Analyzes chess board positions to extract meaningful tactical and strategic information.
    """
    
    def __init__(self):
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # King is invaluable
        }
    
    def analyze_position(self, board: chess.Board) -> Dict:
        """
        Perform comprehensive position analysis.
        
        Args:
            board: Chess board position
            
        Returns:
            Dictionary containing position analysis
        """
        return {
            'attacks': self.analyze_attacks(board),
            'defenses': self.analyze_defenses(board),
            'hanging_pieces': self.find_hanging_pieces(board),
            'threats': self.detect_threats(board),
            'king_safety': self.analyze_king_safety(board),
            'piece_activity': self.analyze_piece_activity(board),
            'control': self.analyze_square_control(board)
        }
    
    def analyze_move_impact(self, board: chess.Board, move: chess.Move) -> Dict:
        """
        Analyze what a specific move accomplishes.
        
        Args:
            board: Board position before move
            move: The move to analyze
            
        Returns:
            Dictionary describing move impact
        """
        # Make move on a copy
        board_after = board.copy()
        board_after.push(move)
        
        # Get piece info
        moving_piece = board.piece_at(move.from_square)
        captured_piece = board.piece_at(move.to_square)
        
        impact = {
            'move': move.uci(),
            'san': board.san(move),
            'moving_piece': moving_piece.piece_type if moving_piece else None,
            'captured_piece': captured_piece.piece_type if captured_piece else None,
            'is_capture': captured_piece is not None,
            'is_check': board_after.is_check(),
            'is_checkmate': board_after.is_checkmate(),
            'creates_attacks': self._new_attacks_created(board, board_after, move.to_square),
            'removes_threats': self._threats_removed(board, board_after),
            'defends_pieces': self._pieces_defended_by_move(board, board_after, move.to_square),
            'improves_position': self._positional_improvement(board, board_after, moving_piece),
            'tactical_purpose': self._detect_tactical_purpose(board, move)
        }
        
        return impact
    
    def analyze_attacks(self, board: chess.Board) -> Dict:
        """
        Find all attacks on the board.
        
        Returns:
            Dictionary mapping squares to pieces attacking them
        """
        attacks = {'white': {}, 'black': {}}
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Find what pieces attack this square
                attackers_white = board.attackers(chess.WHITE, square)
                attackers_black = board.attackers(chess.BLACK, square)
                
                if len(attackers_white) > 0:
                    attacks['white'][chess.square_name(square)] = {
                        'target_piece': piece.piece_type,
                        'num_attackers': len(attackers_white),
                        'attacker_squares': [chess.square_name(sq) for sq in attackers_white]
                    }
                
                if len(attackers_black) > 0:
                    attacks['black'][chess.square_name(square)] = {
                        'target_piece': piece.piece_type,
                        'num_attackers': len(attackers_black),
                        'attacker_squares': [chess.square_name(sq) for sq in attackers_black]
                    }
        
        return attacks
    
    def analyze_defenses(self, board: chess.Board) -> Dict:
        """
        Find defended pieces on the board.
        
        Returns:
            Dictionary of defended pieces
        """
        defenses = {'white': {}, 'black': {}}
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Find defenders of same color
                defenders = board.attackers(piece.color, square)
                defenders.discard(square)  # Don't count self
                
                if len(defenders) > 0:
                    color = 'white' if piece.color == chess.WHITE else 'black'
                    defenses[color][chess.square_name(square)] = {
                        'piece': piece.piece_type,
                        'num_defenders': len(defenders),
                        'defender_squares': [chess.square_name(sq) for sq in defenders]
                    }
        
        return defenses
    
    def find_hanging_pieces(self, board: chess.Board) -> List[Dict]:
        """
        Find undefended pieces that are attacked (hanging pieces).
        
        Returns:
            List of hanging pieces with details
        """
        hanging = []
        attacks = self.analyze_attacks(board)
        defenses = self.analyze_defenses(board)
        
        # Check white pieces attacked by black
        for square, attack_info in attacks['black'].items():
            if square not in defenses.get('white', {}):
                piece = board.piece_at(chess.parse_square(square))
                if piece:
                    hanging.append({
                        'square': square,
                        'piece': piece.piece_type,
                        'color': 'white',
                        'value': self.piece_values[piece.piece_type],
                        'attackers': attack_info['attacker_squares']
                    })
        
        # Check black pieces attacked by white
        for square, attack_info in attacks['white'].items():
            if square not in defenses.get('black', {}):
                piece = board.piece_at(chess.parse_square(square))
                if piece:
                    hanging.append({
                        'square': square,
                        'piece': piece.piece_type,
                        'color': 'black',
                        'value': self.piece_values[piece.piece_type],
                        'attackers': attack_info['attacker_squares']
                    })
        
        return hanging
    
    def detect_threats(self, board: chess.Board) -> List[Dict]:
        """
        Detect immediate threats in the position.
        
        Returns:
            List of threats
        """
        threats = []
        
        # Check if in check
        if board.is_check():
            threats.append({
                'type': 'check',
                'target': 'king',
                'severity': 'critical'
            })
        
        # Check for hanging pieces
        hanging = self.find_hanging_pieces(board)
        for piece_info in hanging:
            if piece_info['value'] >= 3:  # Significant pieces
                threats.append({
                    'type': 'hanging_piece',
                    'square': piece_info['square'],
                    'piece': piece_info['piece'],
                    'value': piece_info['value'],
                    'severity': 'high' if piece_info['value'] >= 5 else 'medium'
                })
        
        return threats
    
    def analyze_king_safety(self, board: chess.Board) -> Dict:
        """
        Evaluate king safety for both sides.
        
        Returns:
            King safety metrics
        """
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        
        return {
            'white': self._king_safety_score(board, white_king_square, chess.WHITE),
            'black': self._king_safety_score(board, black_king_square, chess.BLACK)
        }
    
    def _king_safety_score(self, board: chess.Board, king_square: int, color: chess.Color) -> Dict:
        """Calculate king safety score."""
        if king_square is None:
            return {'safe': False, 'score': 0, 'issues': ['King not found']}
        
        issues = []
        score = 10  # Start with perfect safety
        
        # Check if king has castled
        has_castled = False
        if color == chess.WHITE:
            if king_square in [chess.G1, chess.C1]:
                has_castled = True
        else:
            if king_square in [chess.G8, chess.C8]:
                has_castled = True
        
        if not has_castled and len(list(board.legal_moves)) > 10:
            score -= 2
            issues.append('King not castled')
        
        # Check enemy attacks near king
        enemy_color = not color
        king_zone = [king_square]
        for direction in [8, -8, 1, -1, 9, -9, 7, -7]:
            sq = king_square + direction
            if 0 <= sq < 64 and abs(chess.square_file(sq) - chess.square_file(king_square)) <= 1:
                king_zone.append(sq)
        
        attackers = 0
        for sq in king_zone:
            if 0 <= sq < 64:
                enemy_attackers = board.attackers(enemy_color, sq)
                attackers += len(enemy_attackers)
        
        if attackers > 3:
            score -= 3
            issues.append('King under attack')
        
        return {
            'safe': score >= 7,
            'score': score,
            'has_castled': has_castled,
            'issues': issues
        }
    
    def analyze_piece_activity(self, board: chess.Board) -> Dict:
        """
        Analyze how active pieces are.
        
        Returns:
            Piece activity metrics
        """
        activity = {'white': 0, 'black': 0}
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Count legal moves for this piece
                piece_moves = sum(1 for move in board.legal_moves if move.from_square == square)
                
                color = 'white' if piece.color == chess.WHITE else 'black'
                activity[color] += piece_moves
        
        return activity
    
    def analyze_square_control(self, board: chess.Board) -> Dict:
        """
        Analyze control of key central squares.
        
        Returns:
            Square control metrics
        """
        central_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        control = {'white': 0, 'black': 0}
        
        for square in central_squares:
            white_attackers = len(board.attackers(chess.WHITE, square))
            black_attackers = len(board.attackers(chess.BLACK, square))
            
            control['white'] += white_attackers
            control['black'] += black_attackers
        
        return control
    
    def _new_attacks_created(self, board_before: chess.Board, board_after: chess.Board, 
                            to_square: int) -> List[str]:
        """Find new attacks created by the move."""
        new_attacks = []
        color = board_after.piece_at(to_square).color
        
        # Check attacks from the piece's new position
        for square in chess.SQUARES:
            target = board_after.piece_at(square)
            if target and target.color != color:
                if board_after.is_attacked_by(color, square):
                    if not board_before.is_attacked_by(color, square):
                        new_attacks.append(chess.square_name(square))
        
        return new_attacks
    
    def _threats_removed(self, board_before: chess.Board, board_after: chess.Board) -> List[str]:
        """Find threats that were removed by the move."""
        threats_before = self.detect_threats(board_before)
        threats_after = self.detect_threats(board_after)
        
        removed = []
        for threat in threats_before:
            if threat not in threats_after:
                removed.append(threat.get('type', 'unknown'))
        
        return removed
    
    def _pieces_defended_by_move(self, board_before: chess.Board, board_after: chess.Board,
                                 to_square: int) -> List[str]:
        """Find pieces that are now defended by the moved piece."""
        defended = []
        piece = board_after.piece_at(to_square)
        if not piece:
            return defended
        
        color = piece.color
        
        for square in chess.SQUARES:
            target = board_after.piece_at(square)
            if target and target.color == color and square != to_square:
                # Check if this piece is now defended by our moved piece
                if board_after.is_attacked_by(color, square):
                    defenders_after = board_after.attackers(color, square)
                    if to_square in defenders_after:
                        defended.append(chess.square_name(square))
        
        return defended
    
    def _positional_improvement(self, board_before: chess.Board, board_after: chess.Board,
                               piece: chess.Piece) -> str:
        """Determine if move improves position."""
        if not piece:
            return 'neutral'
        
        # Simple heuristic: check piece mobility
        from_mobility = sum(1 for move in board_before.legal_moves)
        to_mobility = sum(1 for move in board_after.legal_moves)
        
        if to_mobility > from_mobility:
            return 'improves_mobility'
        elif to_mobility < from_mobility:
            return 'reduces_mobility'
        else:
            return 'neutral'
    
    def _detect_tactical_purpose(self, board: chess.Board, move: chess.Move) -> List[str]:
        """Detect tactical purposes of a move."""
        purposes = []
        
        # Check if it's a capture
        if board.is_capture(move):
            purposes.append('capture')
        
        # Check if it creates check
        board_copy = board.copy()
        board_copy.push(move)
        if board_copy.is_check():
            purposes.append('check')
        
        # Check if it's castling
        if board.is_castling(move):
            purposes.append('castling')
        
        # Check if it develops a piece (from starting square)
        from_square = move.from_square
        piece = board.piece_at(from_square)
        if piece:
            rank = chess.square_rank(from_square)
            if piece.color == chess.WHITE and rank == 0:
                purposes.append('development')
            elif piece.color == chess.BLACK and rank == 7:
                purposes.append('development')
        
        return purposes if purposes else ['positional']
