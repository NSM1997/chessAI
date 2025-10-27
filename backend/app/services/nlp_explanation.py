"""
NLP Explanation Service for Chess AI
Phase 3: Natural Language Explanation Generation

This service provides AI-generated explanations for chess moves and positions
using transformer-based language models (T5/GPT-2).
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, GPT2LMHeadModel, GPT2Tokenizer
import chess
import chess.engine

logger = logging.getLogger(__name__)

class NLPExplanationService:
    """
    Service for generating natural language explanations using transformer models.
    
    Supports both T5 (primary) and GPT-2 (backup) models for explanation generation.
    """
    
    def __init__(self, model_type: str = "t5", model_name: Optional[str] = None):
        """
        Initialize the NLP explanation service.
        
        Args:
            model_type: Type of model to use ("t5" or "gpt2")
            model_name: Specific model name (uses defaults if None)
        """
        self.model_type = model_type.lower()
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.is_available = False
        
        # Default model names
        if model_name is None:
            if self.model_type == "t5":
                self.model_name = "t5-small"  # Start with small model for testing
            elif self.model_type == "gpt2":
                self.model_name = "gpt2"
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
    
    async def initialize(self) -> bool:
        """
        Initialize the NLP model and tokenizer.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info(f"Initializing {self.model_type.upper()} model: {self.model_name}")
            
            if self.model_type == "t5":
                await self._initialize_t5()
            elif self.model_type == "gpt2":
                await self._initialize_gpt2()
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            self.is_available = True
            logger.info(f"[SUCCESS] {self.model_type.upper()} model initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize {self.model_type.upper()} model: {e}")
            self.is_available = False
            return False
    
    async def _initialize_t5(self):
        """Initialize T5 model and tokenizer."""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _load_t5():
            tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            return model, tokenizer
        
        self.model, self.tokenizer = await loop.run_in_executor(None, _load_t5)
        
        # Set to evaluation mode
        self.model.eval()
        
        # Move to GPU if available
        if torch.cuda.is_available():
            self.model = self.model.cuda()
            logger.info("Model moved to GPU")
    
    async def _initialize_gpt2(self):
        """Initialize GPT-2 model and tokenizer."""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _load_gpt2():
            tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
            model = GPT2LMHeadModel.from_pretrained(self.model_name)
            return model, tokenizer
        
        self.model, self.tokenizer = await loop.run_in_executor(None, _load_gpt2)
        
        # Set to evaluation mode
        self.model.eval()
        
        # Move to GPU if available
        if torch.cuda.is_available():
            self.model = self.model.cuda()
            logger.info("Model moved to GPU")
    
    async def generate_explanation(
        self,
        fen: str,
        move: str,
        move_san: str,
        position_eval: Dict,
        tactical_themes: List[str] = None,
        opening_info: Dict = None,
        context: Dict = None
    ) -> str:
        """
        Generate natural language explanation for a chess move.
        
        Args:
            fen: FEN string of the position
            move: Move in UCI notation (e.g., "e2e4")
            move_san: Move in SAN notation (e.g., "e4")
            position_eval: Position evaluation data
            tactical_themes: List of detected tactical themes
            opening_info: Opening information (name, ECO code)
            context: Additional context information
            
        Returns:
            str: Generated explanation
        """
        if not self.is_available:
            return self._fallback_explanation(move_san, position_eval, tactical_themes)
        
        try:
            # Prepare input text for the model
            input_text = self._prepare_input_text(
                fen, move, move_san, position_eval, 
                tactical_themes, opening_info, context
            )
            
            # Generate explanation
            if self.model_type == "t5":
                explanation = await self._generate_t5_explanation(input_text)
            elif self.model_type == "gpt2":
                explanation = await self._generate_gpt2_explanation(input_text)
            else:
                return self._fallback_explanation(move_san, position_eval, tactical_themes)
            
            # Post-process and validate explanation
            explanation = self._post_process_explanation(explanation, move_san)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._fallback_explanation(move_san, position_eval, tactical_themes)
    
    def _prepare_input_text(
        self,
        fen: str,
        move: str,
        move_san: str,
        position_eval: Dict,
        tactical_themes: List[str] = None,
        opening_info: Dict = None,
        context: Dict = None
    ) -> str:
        """Prepare input text for the language model."""
        
        position_type = position_eval.get('position_type', 'unknown')
        score = position_eval.get('score', {})
        score_value = score.get('value', 0) if isinstance(score, dict) else score
        
        # Create more detailed and context-aware input
        input_parts = [
            f"Position: {fen}",
            f"Move: {move_san} ({move})",
            f"Score: {score_value/100:+.2f}",
            f"Phase: {position_type}"
        ]
        
        # Add opening information
        if opening_info and opening_info.get('name'):
            input_parts.append(f"Opening: {opening_info['name']}")
        
        # Add tactical themes with more context
        if tactical_themes:
            themes_str = ", ".join(tactical_themes)
            input_parts.append(f"Tactics: {themes_str}")
        
        # Add material balance
        material = position_eval.get('material_balance', {})
        if material:
            diff = material.get('difference', 0)
            if diff > 0:
                input_parts.append(f"Material: White +{abs(diff)}")
            elif diff < 0:
                input_parts.append(f"Material: Black +{abs(diff)}")
            else:
                input_parts.append("Material: Equal")
        
        # Add move-specific context
        if move_san.startswith('N'):
            input_parts.append("Piece: Knight")
        elif move_san.startswith('B'):
            input_parts.append("Piece: Bishop")
        elif move_san.startswith('R'):
            input_parts.append("Piece: Rook")
        elif move_san.startswith('Q'):
            input_parts.append("Piece: Queen")
        elif move_san.startswith('K'):
            input_parts.append("Piece: King")
        else:
            input_parts.append("Piece: Pawn")
        
        return " | ".join(input_parts)
    
    async def _generate_t5_explanation(self, input_text: str) -> str:
        """Generate explanation using T5 model."""
        loop = asyncio.get_event_loop()
        
        def _t5_generate():
            # Tokenize input
            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            
            # Move to GPU if available
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate explanation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=200,
                    num_beams=4,
                    early_stopping=True,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
            
            # Decode output
            explanation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return explanation
        
        return await loop.run_in_executor(None, _t5_generate)
    
    async def _generate_gpt2_explanation(self, input_text: str) -> str:
        """Generate explanation using GPT-2 model."""
        loop = asyncio.get_event_loop()
        
        def _gpt2_generate():
            # Prepare prompt
            prompt = f"Chess explanation: {input_text}\nExplanation:"
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=400,
                truncation=True,
                padding=True
            )
            
            # Move to GPU if available
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate explanation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=inputs['input_ids'].shape[1] + 100,
                    num_beams=4,
                    early_stopping=True,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode output
            full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the explanation part
            explanation = full_text.split("Explanation:")[-1].strip()
            return explanation
        
        return await loop.run_in_executor(None, _gpt2_generate)
    
    def _post_process_explanation(self, explanation: str, move_san: str) -> str:
        """Post-process and clean up the generated explanation."""
        if not explanation or explanation.strip() == "":
            return self._fallback_explanation(move_san, {}, [])
        
        # Clean up the explanation
        explanation = explanation.strip()
        
        # Remove any repeated phrases
        sentences = explanation.split('.')
        unique_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in unique_sentences:
                unique_sentences.append(sentence)
        
        explanation = '. '.join(unique_sentences)
        
        # Ensure it ends with a period
        if not explanation.endswith('.'):
            explanation += '.'
        
        # Limit length (avoid overly long explanations)
        if len(explanation) > 500:
            explanation = explanation[:500].rsplit('.', 1)[0] + '.'
        
        return explanation
    
    def _fallback_explanation(self, move_san: str, position_eval: Dict, tactical_themes: List[str]) -> str:
        """Fallback explanation when NLP model is not available."""
        position_type = position_eval.get('position_type', 'position')
        score = position_eval.get('score', {})
        score_value = score.get('value', 0) if isinstance(score, dict) else score
        
        # Determine piece type and move type
        piece_type = "piece"
        is_capture = 'x' in move_san
        is_castling = 'O-O' in move_san
        is_check = '+' in move_san
        is_checkmate = '#' in move_san
        is_promotion = '=' in move_san
        
        if move_san.startswith('N'):
            piece_type = "knight"
        elif move_san.startswith('B'):
            piece_type = "bishop"
        elif move_san.startswith('R'):
            piece_type = "rook"
        elif move_san.startswith('Q'):
            piece_type = "queen"
        elif move_san.startswith('K'):
            piece_type = "king"
        else:
            piece_type = "pawn"
        
        # Create natural explanation
        explanation_parts = []
        
        # Handle special cases first
        if is_checkmate:
            explanation_parts.append(f"Delivering checkmate with {move_san}")
            explanation_parts.append("This move ends the game immediately.")
            return " ".join(explanation_parts)
        
        # Move description - more natural language
        if is_capture:
            if piece_type == "pawn":
                explanation_parts.append(f"Capturing with the pawn {move_san}")
            else:
                explanation_parts.append(f"Capturing with the {piece_type} {move_san}")
        elif is_castling:
            if 'O-O-O' in move_san:
                explanation_parts.append("Castling queenside")
            else:
                explanation_parts.append("Castling kingside")
        elif is_promotion:
            explanation_parts.append(f"Promoting the pawn to {move_san.split('=')[1]}")
        else:
            if piece_type == "pawn":
                explanation_parts.append(f"Moving the pawn to {move_san}")
            else:
                explanation_parts.append(f"Moving the {piece_type} to {move_san}")
        
        # Add check notation
        if is_check:
            explanation_parts.append("with check")
        
        # Enhanced tactical reasoning based on themes and position
        tactical_reasons = []
        
        # Check for specific tactical themes
        if tactical_themes and len(tactical_themes) > 0:
            # Extract theme names from dictionaries
            theme_names = []
            for theme in tactical_themes:
                if isinstance(theme, dict) and 'theme' in theme:
                    theme_names.append(theme['theme'])
                elif isinstance(theme, str):
                    theme_names.append(theme)
            
            # Debug output
            print(f"[DEBUG] Tactical themes: {tactical_themes}")
            print(f"[DEBUG] Theme names: {theme_names}")
            
            if "fork" in theme_names:
                tactical_reasons.append("create a fork to attack multiple pieces")
            if "pin" in theme_names:
                tactical_reasons.append("pin an enemy piece")
            if "mate" in theme_names:
                tactical_reasons.append("create mating threats")
            if "discoveredAttack" in theme_names:
                tactical_reasons.append("prepare a discovered attack")
            if "capture_available" in theme_names:
                tactical_reasons.append("threaten to win material")
        
        # Position-specific reasoning with more detail
        if position_type == "opening":
            if is_capture:
                tactical_reasons.append("win material in the opening")
            elif piece_type in ["knight", "bishop"]:
                tactical_reasons.append("develop pieces and control key squares")
            elif piece_type == "pawn":
                tactical_reasons.append("control the center and prepare for development")
                # Add specific pawn move analysis
                if move_san in ["d4", "e4"]:
                    tactical_reasons.append("establish central control")
            else:
                tactical_reasons.append("complete development and prepare for castling")
        elif position_type == "middlegame":
            if is_capture:
                if tactical_reasons:
                    tactical_reasons.append("win material")
                else:
                    tactical_reasons.append("win material and improve the position")
            else:
                if not tactical_reasons:
                    tactical_reasons.append("improve piece coordination and create threats")
        elif position_type == "endgame":
            if is_capture:
                tactical_reasons.append("win material in the endgame")
            elif piece_type == "king":
                tactical_reasons.append("activate the king for the endgame")
            elif piece_type == "pawn":
                tactical_reasons.append("advance towards promotion")
            else:
                tactical_reasons.append("coordinate pieces for the final phase")
        
        # Add defensive considerations for specific moves
        if piece_type == "pawn" and move_san in ["d4", "e4"]:
            # Check if this move defends pieces (simplified analysis)
            tactical_reasons.append("strengthening central control")
        
        # Combine tactical reasons
        if tactical_reasons:
            if len(tactical_reasons) == 1:
                explanation_parts.append(f"to {tactical_reasons[0]}")
            else:
                explanation_parts.append(f"to {tactical_reasons[0]} and {tactical_reasons[1]}")
        else:
            explanation_parts.append("to improve the position")
        
        # Add evaluation context - more natural and specific
        if abs(score_value) > 200:
            if score_value > 0:
                explanation_parts.append("This creates a significant advantage for White.")
            else:
                explanation_parts.append("This creates a significant advantage for Black.")
        elif abs(score_value) > 50:
            if score_value > 0:
                explanation_parts.append("This gives White a slight edge.")
            else:
                explanation_parts.append("This gives Black a slight edge.")
        elif abs(score_value) < 20:
            explanation_parts.append("This maintains a balanced position.")
        
        return " ".join(explanation_parts)
    
    async def cleanup(self):
        """Clean up model resources."""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        
        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_available = False
        logger.info("NLP explanation service cleaned up")
