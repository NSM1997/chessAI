from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import logging
from typing import Optional, List, Dict
import asyncio
import chess
import chess.engine
import chess.pgn
import json

from app.api.endpoints import router as api_router
from app.core.config import settings
from app.services.chess_engine import ChessEngineService
from app.services.explanation_engine import ExplanationEngine
from app.services.ml_service import MLService
from app.services.tactical_analysis import get_tactical_service
from app.models.chess_models import (
    AnalysisRequest, AnalysisResponse, MoveExplanationRequest, 
    HealthResponse, ErrorResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Explainable Chess AI API",
    description="Real-time chess move explanation and analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize services
chess_engine = ChessEngineService()
explanation_engine = ExplanationEngine()
ml_service = MLService()
tactical_service = get_tactical_service()

# Models are now imported from chess_models.py

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Explainable Chess AI API...")
    await chess_engine.initialize()
    await ml_service.load_models()
    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down API...")
    await chess_engine.cleanup()

@app.get("/")
async def root():
    return {"message": "Explainable Chess AI API", "status": "running", "version": "1.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=asyncio.get_event_loop().time(),
        version="1.0.0",
        services={
            "chess_engine": chess_engine.is_initialized,
            "ml_service": ml_service.is_initialized
        }
    )

@app.post("/analyze-position", response_model=AnalysisResponse)
async def analyze_position(request: AnalysisRequest):
    """
    Analyze chess position and return explanations
    """
    try:
        # Validate FEN
        try:
            board = chess.Board(request.fen)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid FEN string")
        
        # Get engine analysis
        engine_result = await chess_engine.analyze_position(
            request.fen, 
            depth=request.depth
        )
        
        # Generate explanations (await the async function)
        explanations = await explanation_engine.generate_explanations(
            request.fen,
            engine_result,
            skill_level=request.user_skill_level,
            explanation_type=request.explanation_type
        )
        
        # Get ML insights (await the async function)
        ml_insights = await ml_service.get_position_insights(request.fen)
        
        # Get tactical themes from hybrid ensemble
        tactical_themes = await tactical_service.analyze_tactics(board, top_k=5)
        
        response = AnalysisResponse(
            fen=request.fen,
            best_moves=engine_result["best_moves"],
            explanations=explanations,
            position_evaluation=engine_result["evaluation"],
            learning_insights=ml_insights,
            tactical_themes=tactical_themes.get('themes', []),
            analysis_time=None  # Could add timing if needed
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/explain-move")
async def explain_move(request: MoveExplanationRequest):
    """
    Explain a specific move in context
    """
    try:
        board = chess.Board(request.fen)
        move_obj = chess.Move.from_uci(request.move)
        
        if move_obj not in board.legal_moves:
            raise HTTPException(status_code=400, detail="Illegal move")
        
        explanation = await explanation_engine.explain_specific_move(
            request.fen, request.move, request.skill_level
        )
        
        return {"move": request.move, "explanation": explanation}
        
    except Exception as e:
        logger.error(f"Move explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tactical-themes")
async def get_tactical_themes(fen: str):
    """
    Get tactical themes for a position using hybrid ensemble
    (Recall models for common tactics + Precision models for critical themes)
    """
    try:
        # Validate FEN
        try:
            board = chess.Board(fen)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid FEN string")
        
        # Get tactical themes from hybrid ensemble
        tactical_analysis = await tactical_service.analyze_tactics(board, top_k=5)
        
        return {
            "fen": fen,
            "tactical_themes": tactical_analysis.get('themes', []),
            "available": tactical_analysis.get('available', False),
            "message": tactical_analysis.get('message', '')
        }
        
    except Exception as e:
        logger.error(f"Tactical analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tactical analysis failed: {str(e)}")

# Include API router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
