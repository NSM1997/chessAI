"""
LLM-Based Explanation Service
Generates intelligent, context-aware chess explanations using LLMs (GPT-4, Claude, or local models)
"""

import asyncio
import logging
from typing import Dict, List, Optional
import chess
import os
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI_GPT4 = "openai-gpt4"
    OPENAI_GPT35 = "openai-gpt3.5"
    ANTHROPIC_CLAUDE = "anthropic-claude"
    OLLAMA_LOCAL = "ollama-local"
    FALLBACK = "fallback"  # Rule-based fallback


class LLMExplanationService:
    """
    Generate chess explanations using LLMs with intelligent board analysis context.
    """
    
    def __init__(self, provider: str = "openai-gpt4", api_key: Optional[str] = None):
        """
        Initialize LLM explanation service.
        
        Args:
            provider: LLM provider to use (openai-gpt4, anthropic-claude, ollama-local)
            api_key: API key for the provider (if required)
        """
        self.provider = LLMProvider(provider) if provider != "fallback" else LLMProvider.FALLBACK
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.is_available = False
        
        # Piece name mapping
        self.piece_names = {
            chess.PAWN: "pawn",
            chess.KNIGHT: "knight",
            chess.BISHOP: "bishop",
            chess.ROOK: "rook",
            chess.QUEEN: "queen",
            chess.KING: "king"
        }
    
    async def initialize(self) -> bool:
        """
        Initialize the LLM client.
        
        Returns:
            True if initialization successful
        """
        try:
            if self.provider == LLMProvider.OPENAI_GPT4 or self.provider == LLMProvider.OPENAI_GPT35:
                await self._initialize_openai()
            elif self.provider == LLMProvider.ANTHROPIC_CLAUDE:
                await self._initialize_anthropic()
            elif self.provider == LLMProvider.OLLAMA_LOCAL:
                await self._initialize_ollama()
            else:
                logger.info("Using fallback explanation system (no LLM)")
                self.is_available = True
            
            return self.is_available
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider {self.provider}: {e}")
            logger.warning("Falling back to rule-based explanations")
            self.provider = LLMProvider.FALLBACK
            self.is_available = True
            return True
    
    async def _initialize_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            
            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
            self.client = OpenAI(api_key=self.api_key)
            self.is_available = True
            logger.info(f"OpenAI {self.provider.value} initialized successfully")
            
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    async def _initialize_anthropic(self):
        """Initialize Anthropic Claude client."""
        try:
            import anthropic
            
            if not self.api_key:
                raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
            
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.is_available = True
            logger.info("Anthropic Claude initialized successfully")
            
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    async def _initialize_ollama(self):
        """Initialize Ollama local LLM."""
        try:
            import ollama
            
            # Test if Ollama is running
            models = ollama.list()
            self.client = ollama
            self.is_available = True
            logger.info("Ollama initialized successfully")
            
        except ImportError:
            raise ImportError("ollama package not installed. Run: pip install ollama")
        except Exception as e:
            raise RuntimeError(f"Ollama not running or not accessible: {e}")
    
    async def generate_explanation(
        self,
        fen: str,
        move_san: str,
        move_uci: str,
        board_analysis: Dict,
        move_impact: Dict,
        stockfish_eval: Dict,
        tactical_themes: List[str] = None,
        position_type: str = "middlegame"
    ) -> str:
        """
        Generate intelligent explanation for a chess move.
        
        Args:
            fen: Board position in FEN notation
            move_san: Move in SAN notation
            move_uci: Move in UCI notation
            board_analysis: Analysis from BoardAnalyzer
            move_impact: Move impact analysis
            stockfish_eval: Stockfish evaluation
            tactical_themes: Tactical themes detected
            position_type: Game phase (opening/middlegame/endgame)
            
        Returns:
            Natural language explanation
        """
        if not self.is_available:
            return self._fallback_explanation(move_san, move_impact, position_type)
        
        try:
            # Build context-rich prompt
            prompt = self._build_prompt(
                fen, move_san, move_uci, board_analysis, 
                move_impact, stockfish_eval, tactical_themes, position_type
            )
            
            # Generate explanation using selected provider
            if self.provider in [LLMProvider.OPENAI_GPT4, LLMProvider.OPENAI_GPT35]:
                explanation = await self._generate_openai(prompt)
            elif self.provider == LLMProvider.ANTHROPIC_CLAUDE:
                explanation = await self._generate_anthropic(prompt)
            elif self.provider == LLMProvider.OLLAMA_LOCAL:
                explanation = await self._generate_ollama(prompt)
            else:
                explanation = self._fallback_explanation(move_san, move_impact, position_type)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._fallback_explanation(move_san, move_impact, position_type)
    
    def _build_prompt(
        self,
        fen: str,
        move_san: str,
        move_uci: str,
        board_analysis: Dict,
        move_impact: Dict,
        stockfish_eval: Dict,
        tactical_themes: List[str],
        position_type: str
    ) -> str:
        """
        Build intelligent prompt with all context.
        """
        # Extract key information
        is_capture = move_impact.get('is_capture', False)
        is_check = move_impact.get('is_check', False)
        moving_piece = self.piece_names.get(move_impact.get('moving_piece'), 'piece')
        captured_piece = self.piece_names.get(move_impact.get('captured_piece'), 'piece') if is_capture else None
        creates_attacks = move_impact.get('creates_attacks', [])
        defends_pieces = move_impact.get('defends_pieces', [])
        removes_threats = move_impact.get('removes_threats', [])
        
        # Build context with tactical awareness
        context_parts = []
        
        # Add move action
        if is_capture:
            context_parts.append(f"Captures {captured_piece}")
        else:
            context_parts.append(f"Moves {moving_piece} to {move_san[-2:] if len(move_san) >= 2 else 'new square'}")
        
        # Add tactical information if available
        if tactical_themes:
            # Map theme names to human-readable descriptions
            theme_descriptions = {
                'fork': 'creates a fork (attacking multiple pieces)',
                'pin': 'creates a pin (trapping a piece)',
                'skewer': 'creates a skewer (forcing piece movement)',
                'discoveredAttack': 'unleashes a discovered attack',
                'mate': 'threatens checkmate',
                'mateIn1': 'delivers checkmate',
                'mateIn2': 'forces checkmate in 2 moves',
                'check': 'gives check',
                'sacrifice': 'sacrifices material for attack',
                'defensiveMove': 'defends against threats'
            }
            
            for theme in tactical_themes[:2]:  # Use top 2 themes
                if theme in theme_descriptions:
                    context_parts.append(theme_descriptions[theme])
        
        # Add what the move accomplishes
        if creates_attacks:
            targets = ', '.join(creates_attacks[:2])
            context_parts.append(f"attacks pieces on {targets}")
        
        if removes_threats:
            context_parts.append("removes a threat")
        
        if defends_pieces:
            defended = ', '.join(defends_pieces[:2])
            context_parts.append(f"defends pieces on {defended}")
        
        if is_check:
            context_parts.append("gives check")
        
        # Build concise prompt
        prompt = f"""Explain the chess move {move_san} in ONE short sentence (max 20 words).

Context:
{chr(10).join(f'- {part}' for part in context_parts)}

If it's a fork/pin/skewer/discovered attack, mention that tactical pattern. Otherwise explain the main strategic purpose. Be direct and concise."""

        return prompt
    
    async def _generate_openai(self, prompt: str) -> str:
        """Generate explanation using OpenAI."""
        loop = asyncio.get_event_loop()
        
        def _call_openai():
            # Use gpt-4o (latest and best model) for GPT-4 provider
            model = "gpt-4o" if self.provider == LLMProvider.OPENAI_GPT4 else "gpt-3.5-turbo"
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a concise chess coach. Keep explanations to 1-2 short sentences maximum."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,  # Limit tokens for brevity
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        return await loop.run_in_executor(None, _call_openai)
    
    async def _generate_anthropic(self, prompt: str) -> str:
        """Generate explanation using Anthropic Claude."""
        loop = asyncio.get_event_loop()
        
        def _call_anthropic():
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=150,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text.strip()
        
        return await loop.run_in_executor(None, _call_anthropic)
    
    async def _generate_ollama(self, prompt: str) -> str:
        """Generate explanation using Ollama local LLM."""
        loop = asyncio.get_event_loop()
        
        def _call_ollama():
            response = self.client.generate(
                model='llama3.2',
                prompt=prompt,
                options={
                    'num_predict': 50,  # Limit to ~50 tokens (1-2 sentences)
                    'temperature': 0.5,  # Lower temp for more focused output
                    'top_p': 0.9
                }
            )
            
            return response['response'].strip()
        
        return await loop.run_in_executor(None, _call_ollama)
    
    def _fallback_explanation(self, move_san: str, move_impact: Dict, position_type: str) -> str:
        """
        Generate rule-based explanation when LLM is not available.
        This is smarter than templates because it uses actual board analysis.
        """
        parts = []
        
        # Start with move description
        moving_piece = self.piece_names.get(move_impact.get('moving_piece'), 'piece')
        is_capture = move_impact.get('is_capture', False)
        captured_piece = self.piece_names.get(move_impact.get('captured_piece'), 'piece')
        
        if is_capture:
            parts.append(f"{move_san} captures the {captured_piece}")
        else:
            parts.append(f"{move_san} moves the {moving_piece}")
        
        # Add purpose
        purposes = []
        
        removes_threats = move_impact.get('removes_threats', [])
        if 'hanging_piece' in removes_threats:
            purposes.append("moving it to safety from an attack")
        
        creates_attacks = move_impact.get('creates_attacks', [])
        if creates_attacks:
            targets = ', '.join(creates_attacks[:2])
            purposes.append(f"attacking enemy pieces on {targets}")
        
        defends_pieces = move_impact.get('defends_pieces', [])
        if defends_pieces:
            defended = ', '.join(defends_pieces[:2])
            purposes.append(f"defending your pieces on {defended}")
        
        tactical_purpose = move_impact.get('tactical_purpose', [])
        if 'development' in tactical_purpose and position_type == 'opening':
            purposes.append("developing the piece")
        elif 'castling' in tactical_purpose:
            purposes.append("getting the king to safety")
        
        if purposes:
            parts.append(', '.join(purposes[:2]))
        else:
            parts.append("improving the position")
        
        # Add check
        if move_impact.get('is_check'):
            parts.append("This move gives check!")
        
        return '. '.join(parts) + '.'
    
    async def cleanup(self):
        """Cleanup resources."""
        self.client = None
        self.is_available = False
        logger.info("LLM explanation service cleaned up")
