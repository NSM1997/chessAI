"""
Machine Learning models for chess position analysis
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
import numpy as np

class ModelType(str, Enum):
    POSITION_EVALUATION = "position_evaluation"
    MOVE_PREDICTION = "move_prediction"
    TACTICAL_PATTERN = "tactical_pattern"
    STRATEGIC_ANALYSIS = "strategic_analysis"

class ModelStatus(str, Enum):
    LOADED = "loaded"
    LOADING = "loading"
    ERROR = "error"
    NOT_LOADED = "not_loaded"

class ModelInfo(BaseModel):
    """Information about a loaded ML model"""
    name: str = Field(..., description="Model name")
    type: ModelType = Field(..., description="Model type")
    status: ModelStatus = Field(..., description="Model status")
    version: str = Field(..., description="Model version")
    accuracy: Optional[float] = Field(None, description="Model accuracy")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    features: List[str] = Field(default=[], description="Input features")

class PositionFeatures(BaseModel):
    """Features extracted from a chess position"""
    material_balance: float = Field(..., description="Material balance score")
    piece_activity: float = Field(..., description="Piece activity score")
    king_safety: float = Field(..., description="King safety score")
    center_control: float = Field(..., description="Center control score")
    pawn_structure: float = Field(..., description="Pawn structure score")
    development: float = Field(..., description="Development score")
    tactical_motifs: List[str] = Field(default=[], description="Detected tactical motifs")
    position_type: str = Field(..., description="Position type classification")

class MLPrediction(BaseModel):
    """ML model prediction result"""
    model_name: str = Field(..., description="Name of the model used")
    prediction: Any = Field(..., description="Model prediction")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    features_used: List[str] = Field(default=[], description="Features used for prediction")
    processing_time: float = Field(..., description="Processing time in seconds")

class TacticalPattern(BaseModel):
    """Detected tactical pattern"""
    pattern_type: str = Field(..., description="Type of tactical pattern")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    squares_involved: List[str] = Field(default=[], description="Squares involved in the pattern")
    description: str = Field(..., description="Pattern description")
    moves: List[str] = Field(default=[], description="Moves that create this pattern")

class StrategicInsight(BaseModel):
    """Strategic insight from ML analysis"""
    insight_type: str = Field(..., description="Type of strategic insight")
    description: str = Field(..., description="Insight description")
    importance: float = Field(..., ge=0.0, le=1.0, description="Importance score")
    applicable_moves: List[str] = Field(default=[], description="Moves that apply this insight")

class MLAnalysisResult(BaseModel):
    """Complete ML analysis result"""
    position_features: PositionFeatures = Field(..., description="Extracted position features")
    predictions: List[MLPrediction] = Field(default=[], description="ML predictions")
    tactical_patterns: List[TacticalPattern] = Field(default=[], description="Detected tactical patterns")
    strategic_insights: List[StrategicInsight] = Field(default=[], description="Strategic insights")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall analysis confidence")
    processing_time: float = Field(..., description="Total processing time")

class ModelTrainingConfig(BaseModel):
    """Configuration for model training"""
    model_type: ModelType = Field(..., description="Type of model to train")
    training_data_path: str = Field(..., description="Path to training data")
    validation_split: float = Field(default=0.2, ge=0.0, le=0.5, description="Validation data split")
    epochs: int = Field(default=100, ge=1, le=1000, description="Number of training epochs")
    batch_size: int = Field(default=32, ge=1, le=1024, description="Training batch size")
    learning_rate: float = Field(default=0.001, ge=0.0001, le=0.1, description="Learning rate")
    save_path: str = Field(..., description="Path to save trained model")

class TrainingResult(BaseModel):
    """Result of model training"""
    model_name: str = Field(..., description="Name of the trained model")
    accuracy: float = Field(..., description="Final model accuracy")
    loss: float = Field(..., description="Final training loss")
    training_time: float = Field(..., description="Training time in seconds")
    epochs_completed: int = Field(..., description="Number of epochs completed")
    best_epoch: int = Field(..., description="Epoch with best performance")
    model_path: str = Field(..., description="Path to saved model")
