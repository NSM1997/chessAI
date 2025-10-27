"""
Chess Explanation Dataset Generator
Phase 3: Training Data for NLP Explanation Models

This module generates training data for fine-tuning transformer models
on chess position explanations.
"""

import json
import random
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import chess
import chess.engine
import asyncio
import logging

logger = logging.getLogger(__name__)

class ChessExplanationDataset:
    """
    Generates training data for chess explanation models.
    
    Creates pairs of (position, move, explanation) for training
    transformer models to generate natural language explanations.
    """
    
    def __init__(self, output_dir: str = "data/chess_explanations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Explanation templates for different types of moves
        self.explanation_templates = {
            'opening': {
                'center_control': [
                    "Playing {move} to control the center squares and establish a strong position.",
                    "This move {move} helps control the center, which is crucial in the opening.",
                    "By playing {move}, we gain central control and prepare for piece development."
                ],
                'development': [
                    "Developing the {piece} to {move} to activate the piece and prepare for castling.",
                    "This development move {move} brings the {piece} into play and improves the position.",
                    "Playing {move} develops the {piece} and follows opening principles."
                ],
                'castling': [
                    "Castling {side} to ensure king safety and connect the rooks.",
                    "This castling move {move} protects the king and activates the rook.",
                    "By castling {side}, we secure the king and prepare for the middlegame."
                ]
            },
            'middlegame': {
                'tactical': [
                    "Playing {move} to create a tactical threat and gain material advantage.",
                    "This tactical move {move} exploits the opponent's weaknesses.",
                    "By playing {move}, we set up a tactical combination that wins material."
                ],
                'positional': [
                    "This positional move {move} improves the piece placement and restricts the opponent.",
                    "Playing {move} to strengthen the position and prepare for future plans.",
                    "By playing {move}, we improve our position and create new possibilities."
                ],
                'attack': [
                    "Playing {move} to launch an attack on the opponent's king.",
                    "This attacking move {move} creates threats and puts pressure on the opponent.",
                    "By playing {move}, we initiate an attack and create tactical opportunities."
                ]
            },
            'endgame': {
                'king_activity': [
                    "Activating the king with {move} to participate in the endgame.",
                    "This king move {move} centralizes the king and improves the position.",
                    "By playing {move}, we activate the king, which is crucial in the endgame."
                ],
                'pawn_promotion': [
                    "Advancing the pawn with {move} to promote and gain a material advantage.",
                    "This pawn move {move} creates a passed pawn and threatens promotion.",
                    "By playing {move}, we advance the pawn toward promotion and victory."
                ],
                'technique': [
                    "Playing {move} to demonstrate proper endgame technique.",
                    "This technical move {move} follows endgame principles and improves the position.",
                    "By playing {move}, we apply correct endgame technique and maintain the advantage."
                ]
            }
        }
    
    async def generate_training_data(
        self,
        num_positions: int = 1000,
        use_stockfish: bool = True,
        stockfish_path: str = None
    ) -> List[Dict]:
        """
        Generate training data for chess explanations.
        
        Args:
            num_positions: Number of positions to generate
            use_stockfish: Whether to use Stockfish for move analysis
            stockfish_path: Path to Stockfish executable
            
        Returns:
            List of training examples
        """
        logger.info(f"Generating {num_positions} training examples...")
        
        training_data = []
        
        # Generate different types of positions
        position_types = [
            ('opening', 0.3),
            ('middlegame', 0.5),
            ('endgame', 0.2)
        ]
        
        for pos_type, weight in position_types:
            count = int(num_positions * weight)
            logger.info(f"Generating {count} {pos_type} positions...")
            
            positions = await self._generate_positions_by_type(
                pos_type, count, use_stockfish, stockfish_path
            )
            training_data.extend(positions)
        
        # Shuffle the data
        random.shuffle(training_data)
        
        # Save to file
        output_file = self.output_dir / "chess_explanations.json"
        with open(output_file, 'w') as f:
            json.dump(training_data, f, indent=2)
        
        logger.info(f"Generated {len(training_data)} training examples")
        logger.info(f"Saved to {output_file}")
        
        return training_data
    
    async def _generate_positions_by_type(
        self,
        position_type: str,
        count: int,
        use_stockfish: bool,
        stockfish_path: str
    ) -> List[Dict]:
        """Generate positions of a specific type."""
        positions = []
        
        for i in range(count):
            try:
                if position_type == 'opening':
                    pos_data = await self._generate_opening_position(use_stockfish, stockfish_path)
                elif position_type == 'middlegame':
                    pos_data = await self._generate_middlegame_position(use_stockfish, stockfish_path)
                elif position_type == 'endgame':
                    pos_data = await self._generate_endgame_position(use_stockfish, stockfish_path)
                else:
                    continue
                
                if pos_data:
                    positions.append(pos_data)
                    
            except Exception as e:
                logger.warning(f"Error generating {position_type} position {i}: {e}")
                continue
        
        return positions
    
    async def _generate_opening_position(
        self,
        use_stockfish: bool,
        stockfish_path: str
    ) -> Optional[Dict]:
        """Generate an opening position with explanation."""
        # Start from initial position
        board = chess.Board()
        
        # Play 3-8 moves
        num_moves = random.randint(3, 8)
        
        for _ in range(num_moves):
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break
            
            # Choose move (can be random or use engine)
            if use_stockfish and stockfish_path:
                move = await self._get_engine_move(board, stockfish_path)
            else:
                move = random.choice(legal_moves)
            
            board.push(move)
        
        # Generate explanation
        fen = board.fen()
        last_move = board.peek()
        move_san = board.san(last_move)
        move_uci = last_move.uci()
        
        explanation = self._generate_explanation(
            fen, move_uci, move_san, 'opening', board
        )
        
        return {
            'fen': fen,
            'move': move_uci,
            'move_san': move_san,
            'position_type': 'opening',
            'explanation': explanation,
            'context': {
                'move_number': board.fullmove_number,
                'turn': 'white' if board.turn else 'black'
            }
        }
    
    async def _generate_middlegame_position(
        self,
        use_stockfish: bool,
        stockfish_path: str
    ) -> Optional[Dict]:
        """Generate a middlegame position with explanation."""
        # Start from a random position (simulate middlegame)
        board = chess.Board()
        
        # Play 15-25 moves to reach middlegame
        num_moves = random.randint(15, 25)
        
        for _ in range(num_moves):
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break
            
            if use_stockfish and stockfish_path:
                move = await self._get_engine_move(board, stockfish_path)
            else:
                move = random.choice(legal_moves)
            
            board.push(move)
        
        # Generate explanation
        fen = board.fen()
        last_move = board.peek()
        move_san = board.san(last_move)
        move_uci = last_move.uci()
        
        explanation = self._generate_explanation(
            fen, move_uci, move_san, 'middlegame', board
        )
        
        return {
            'fen': fen,
            'move': move_uci,
            'move_san': move_san,
            'position_type': 'middlegame',
            'explanation': explanation,
            'context': {
                'move_number': board.fullmove_number,
                'turn': 'white' if board.turn else 'black'
            }
        }
    
    async def _generate_endgame_position(
        self,
        use_stockfish: bool,
        stockfish_path: str
    ) -> Optional[Dict]:
        """Generate an endgame position with explanation."""
        # Start from a position with few pieces
        board = chess.Board()
        
        # Play many moves to reach endgame
        num_moves = random.randint(30, 50)
        
        for _ in range(num_moves):
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break
            
            if use_stockfish and stockfish_path:
                move = await self._get_engine_move(board, stockfish_path)
            else:
                move = random.choice(legal_moves)
            
            board.push(move)
            
            # Check if we're in endgame (few pieces)
            piece_count = len(board.piece_map())
            if piece_count <= 12:
                break
        
        # Generate explanation
        fen = board.fen()
        last_move = board.peek()
        move_san = board.san(last_move)
        move_uci = last_move.uci()
        
        explanation = self._generate_explanation(
            fen, move_uci, move_san, 'endgame', board
        )
        
        return {
            'fen': fen,
            'move': move_uci,
            'move_san': move_san,
            'position_type': 'endgame',
            'explanation': explanation,
            'context': {
                'move_number': board.fullmove_number,
                'turn': 'white' if board.turn else 'black'
            }
        }
    
    async def _get_engine_move(self, board: chess.Board, stockfish_path: str) -> chess.Move:
        """Get a move from Stockfish engine."""
        try:
            with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
                result = engine.play(board, chess.engine.Limit(time=0.1))
                return result.move
        except Exception:
            # Fallback to random move
            legal_moves = list(board.legal_moves)
            return random.choice(legal_moves)
    
    def _generate_explanation(
        self,
        fen: str,
        move_uci: str,
        move_san: str,
        position_type: str,
        board: chess.Board
    ) -> str:
        """Generate explanation for a move."""
        try:
            move = chess.Move.from_uci(move_uci)
            piece = board.piece_at(move.from_square)
            piece_name = chess.piece_name(piece.piece_type) if piece else "piece"
            
            # Determine move category
            move_category = self._categorize_move(move, board, position_type)
            
            # Get template
            templates = self.explanation_templates.get(position_type, {}).get(move_category, [])
            if not templates:
                templates = ["Playing {move} to improve the position."]
            
            # Select random template
            template = random.choice(templates)
            
            # Fill in template
            explanation = template.format(
                move=move_san,
                piece=piece_name,
                side="kingside" if "O-O" in move_san else "queenside"
            )
            
            return explanation
            
        except Exception as e:
            logger.warning(f"Error generating explanation: {e}")
            return f"Playing {move_san} to improve the position."
    
    def _categorize_move(self, move: chess.Move, board: chess.Board, position_type: str) -> str:
        """Categorize a move for explanation generation."""
        move_san = board.san(move)
        
        # Check for special moves
        if "O-O" in move_san:
            return "castling"
        elif move_san.endswith("#"):
            return "mate"
        elif move_san.endswith("+"):
            return "check"
        elif "x" in move_san:
            return "capture"
        elif move_san[0].isupper():
            return "development" if position_type == "opening" else "tactical"
        else:
            return "positional"
    
    def load_training_data(self, file_path: str) -> List[Dict]:
        """Load training data from file."""
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def create_t5_training_format(self, data: List[Dict]) -> List[Dict]:
        """Convert data to T5 training format."""
        t5_data = []
        
        for example in data:
            # Input: position + move
            input_text = f"Position: {example['fen']} | Move: {example['move_san']} ({example['move']}) | Type: {example['position_type']}"
            
            # Output: explanation
            output_text = example['explanation']
            
            t5_data.append({
                'input': input_text,
                'output': output_text,
                'metadata': {
                    'fen': example['fen'],
                    'move': example['move'],
                    'move_san': example['move_san'],
                    'position_type': example['position_type']
                }
            })
        
        return t5_data
