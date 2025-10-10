"""
Backend API tests for Chess AI
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import chess

# Import your app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app
from app.models.chess_models import AnalysisRequest, SkillLevel, ExplanationType

client = TestClient(app)

class TestChessAIAPI:
    """Test cases for the Chess AI API"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Explainable Chess AI API"
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
    
    def test_analyze_position_valid_fen(self):
        """Test position analysis with valid FEN"""
        # Standard starting position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        request_data = {
            "fen": fen,
            "depth": 10,
            "user_skill_level": "intermediate",
            "explanation_type": "comprehensive"
        }
        
        with patch('app.main.chess_engine.analyze_position') as mock_analyze:
            mock_analyze.return_value = {
                "best_moves": [
                    {
                        "move": "e2e4",
                        "san": "e4",
                        "score": {"type": "cp", "value": 50, "display": "+0.50"},
                        "pv": ["e2e4"],
                        "depth": 10
                    }
                ],
                "evaluation": {
                    "score": {"type": "cp", "value": 25, "display": "+0.25"},
                    "position_type": "opening",
                    "material_balance": {"white": 0, "black": 0, "difference": 0},
                    "king_safety": {"white": 5, "black": 5},
                    "piece_activity": {"white": 0, "black": 0}
                },
                "legal_moves_count": 20,
                "is_endgame": False,
                "tactical_motifs": []
            }
            
            with patch('app.main.explanation_engine.generate_explanations') as mock_explain:
                mock_explain.return_value = [
                    {
                        "move": "e2e4",
                        "san": "e4",
                        "explanation": "This is a good opening move",
                        "tactical_motifs": [],
                        "strategic_concepts": ["development"],
                        "confidence": 0.8,
                        "engine_evaluation": {}
                    }
                ]
                
                with patch('app.main.ml_service.get_position_insights') as mock_ml:
                    mock_ml.return_value = ["Good opening position"]
                    
                    response = client.post("/analyze-position", json=request_data)
                    assert response.status_code == 200
                    data = response.json()
                    assert "fen" in data
                    assert "best_moves" in data
                    assert "explanations" in data
    
    def test_analyze_position_invalid_fen(self):
        """Test position analysis with invalid FEN"""
        request_data = {
            "fen": "invalid_fen",
            "depth": 10,
            "user_skill_level": "intermediate"
        }
        
        response = client.post("/analyze-position", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_explain_move_valid(self):
        """Test move explanation with valid input"""
        request_data = {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "move": "e2e4",
            "skill_level": "intermediate"
        }
        
        with patch('app.main.explanation_engine.explain_specific_move') as mock_explain:
            mock_explain.return_value = {
                "text": "This is a good opening move",
                "tactical_motifs": [],
                "strategic_concepts": ["development"],
                "confidence": 0.8
            }
            
            response = client.post("/explain-move", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert "move" in data
            assert "explanation" in data
    
    def test_explain_move_illegal(self):
        """Test move explanation with illegal move"""
        request_data = {
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "move": "e2e5",  # Illegal move
            "skill_level": "intermediate"
        }
        
        response = client.post("/explain-move", json=request_data)
        assert response.status_code == 400

class TestChessModels:
    """Test Pydantic models"""
    
    def test_analysis_request_validation(self):
        """Test AnalysisRequest model validation"""
        # Valid request
        valid_request = AnalysisRequest(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            depth=15,
            user_skill_level=SkillLevel.INTERMEDIATE,
            explanation_type=ExplanationType.COMPREHENSIVE
        )
        assert valid_request.fen is not None
        assert valid_request.depth == 15
        
        # Invalid FEN should raise validation error
        with pytest.raises(ValueError):
            AnalysisRequest(fen="invalid_fen")
    
    def test_skill_level_enum(self):
        """Test skill level enum values"""
        assert SkillLevel.BEGINNER == "beginner"
        assert SkillLevel.INTERMEDIATE == "intermediate"
        assert SkillLevel.ADVANCED == "advanced"
    
    def test_explanation_type_enum(self):
        """Test explanation type enum values"""
        assert ExplanationType.BASIC == "basic"
        assert ExplanationType.COMPREHENSIVE == "comprehensive"
        assert ExplanationType.TACTICAL == "tactical"
        assert ExplanationType.STRATEGIC == "strategic"

if __name__ == "__main__":
    pytest.main([__file__])
