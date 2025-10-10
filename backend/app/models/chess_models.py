"""
Chess-related Pydantic models for the API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Literal
from enum import Enum
import chess

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ExplanationType(str, Enum):
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    TACTICAL = "tactical"
    STRATEGIC = "strategic"

class AnalysisRequest(BaseModel):
    """Request model for position analysis"""
    fen: str = Field(..., description="FEN string of the chess position")
    depth: int = Field(default=15, ge=1, le=25, description="Analysis depth")
    user_skill_level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE, description="User's skill level")
    explanation_type: ExplanationType = Field(default=ExplanationType.COMPREHENSIVE, description="Type of explanation")
    
    @validator('fen')
    def validate_fen(cls, v):
        """Validate FEN string"""
        try:
            board = chess.Board(v)
            # Check if position has legal moves
            if not list(board.legal_moves):
                raise ValueError("Position has no legal moves")
        except Exception as e:
            raise ValueError(f"Invalid FEN string: {str(e)}")
        return v

class MoveScore(BaseModel):
    """Score information for a move"""
    type: Literal["cp", "mate"] = Field(..., description="Score type")
    value: int = Field(..., description="Score value")
    display: str = Field(..., description="Human-readable score")

class BestMove(BaseModel):
    """Information about a best move"""
    move: str = Field(..., description="Move in UCI notation")
    san: str = Field(..., description="Move in Standard Algebraic Notation")
    score: MoveScore = Field(..., description="Move evaluation score")
    pv: List[str] = Field(default=[], description="Principal variation")
    depth: int = Field(..., description="Analysis depth")

class PositionEvaluation(BaseModel):
    """Position evaluation details"""
    score: MoveScore = Field(..., description="Overall position score")
    position_type: str = Field(..., description="Type of position (opening/middlegame/endgame)")
    material_balance: Dict[str, int] = Field(..., description="Material balance")
    king_safety: Dict[str, int] = Field(..., description="King safety evaluation")
    piece_activity: Dict[str, int] = Field(..., description="Piece activity evaluation")

class MoveExplanation(BaseModel):
    """Explanation for a specific move"""
    move: str = Field(..., description="Move in UCI notation")
    san: str = Field(..., description="Move in Standard Algebraic Notation")
    explanation: str = Field(..., description="Text explanation of the move")
    tactical_motifs: List[str] = Field(default=[], description="Tactical motifs in the move")
    strategic_concepts: List[str] = Field(default=[], description="Strategic concepts")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the explanation")
    engine_evaluation: BestMove = Field(..., description="Engine evaluation of the move")

class AnalysisResponse(BaseModel):
    """Response model for position analysis"""
    fen: str = Field(..., description="FEN string of the analyzed position")
    best_moves: List[BestMove] = Field(..., description="List of best moves")
    explanations: List[MoveExplanation] = Field(..., description="Move explanations")
    position_evaluation: PositionEvaluation = Field(..., description="Position evaluation")
    learning_insights: List[str] = Field(default=[], description="Learning insights")
    analysis_time: Optional[float] = Field(None, description="Analysis time in seconds")

class MoveExplanationRequest(BaseModel):
    """Request model for explaining a specific move"""
    fen: str = Field(..., description="FEN string of the position")
    move: str = Field(..., description="Move in UCI notation")
    skill_level: SkillLevel = Field(default=SkillLevel.INTERMEDIATE, description="User's skill level")
    
    @validator('fen')
    def validate_fen(cls, v):
        """Validate FEN string"""
        try:
            chess.Board(v)
        except Exception as e:
            raise ValueError(f"Invalid FEN string: {str(e)}")
        return v
    
    @validator('move')
    def validate_move(cls, v):
        """Validate move format"""
        if not v or len(v) < 4:
            raise ValueError("Invalid move format")
        return v

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: float = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")
    services: Dict[str, bool] = Field(default={}, description="Service status")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: float = Field(..., description="Error timestamp")
