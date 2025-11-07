#!/usr/bin/env python3
"""
Test the LLM Explanation Service
Tests both fallback mode (no API key) and full integration with board analyzer
"""

import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import chess
from app.services.board_analyzer import BoardAnalyzer
from app.services.llm_explanation import LLMExplanationService


async def test_fallback_mode():
    """Test fallback explanations (no LLM required)"""
    print("=" * 80)
    print("TEST 1: Fallback Mode (Context-Aware Rules)")
    print("=" * 80)
    
    # Initialize services
    llm_service = LLMExplanationService(provider="fallback")
    await llm_service.initialize()
    
    board_analyzer = BoardAnalyzer()
    
    # Test position: e2e4 opening move
    board = chess.Board()
    move = chess.Move.from_uci("e2e4")
    
    # Analyze position and move
    board_analysis = board_analyzer.analyze_position(board)
    move_impact = board_analyzer.analyze_move_impact(board, move)
    
    # Generate explanation
    explanation = await llm_service.generate_explanation(
        fen=board.fen(),
        move_san="e4",
        move_uci="e2e4",
        board_analysis=board_analysis,
        move_impact=move_impact,
        stockfish_eval={'value': 30},
        tactical_themes=[],
        position_type="opening"
    )
    
    print(f"\nMove: e4")
    print(f"Explanation: {explanation}")
    print(f"✓ Uses actual move impact: {move_impact['tactical_purpose']}")


async def test_capture_move():
    """Test explanation for a capture"""
    print("\n" + "=" * 80)
    print("TEST 2: Capture Move Analysis")
    print("=" * 80)
    
    llm_service = LLMExplanationService(provider="fallback")
    await llm_service.initialize()
    board_analyzer = BoardAnalyzer()
    
    # Position where we can capture a hanging piece
    fen = "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    board = chess.Board(fen)
    
    # Analyze before move
    board_analysis = board_analyzer.analyze_position(board)
    print(f"\nHanging pieces before move: {len(board_analysis['hanging_pieces'])}")
    
    # Nxe5 - capture the pawn
    move = chess.Move.from_uci("f3e5")
    move_impact = board_analyzer.analyze_move_impact(board, move)
    
    explanation = await llm_service.generate_explanation(
        fen=fen,
        move_san="Nxe5",
        move_uci="f3e5",
        board_analysis=board_analysis,
        move_impact=move_impact,
        stockfish_eval={'value': 150},
        tactical_themes=['capture'],
        position_type="opening"
    )
    
    print(f"\nMove: Nxe5")
    print(f"Is capture: {move_impact['is_capture']}")
    print(f"Captured piece: {chess.piece_name(move_impact['captured_piece'])}")
    print(f"Explanation: {explanation}")


async def test_defensive_move():
    """Test explanation for a defensive move"""
    print("\n" + "=" * 80)
    print("TEST 3: Defensive Move (Moving to Safety)")
    print("=" * 80)
    
    llm_service = LLMExplanationService(provider="fallback")
    await llm_service.initialize()
    board_analyzer = BoardAnalyzer()
    
    # Position where queen needs to move to safety
    # Create position where queen is attacked
    board = chess.Board()
    # 1. e4 e5 2. Qh5?? (queen exposed)
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Qh5")
    board.push_san("Nc6")  # Develop knight, queen still exposed
    
    # Now queen should retreat
    board_analysis = board_analyzer.analyze_position(board)
    print(f"\nThreats detected: {len(board_analysis['threats'])}")
    
    # Queen retreats to e2
    move = chess.Move.from_uci("h5e2")
    move_impact = board_analyzer.analyze_move_impact(board, move)
    
    explanation = await llm_service.generate_explanation(
        fen=board.fen(),
        move_san="Qe2",
        move_uci="h5e2",
        board_analysis=board_analysis,
        move_impact=move_impact,
        stockfish_eval={'value': -50},
        tactical_themes=[],
        position_type="opening"
    )
    
    print(f"\nMove: Qe2")
    print(f"Removes threats: {move_impact['removes_threats']}")
    print(f"Explanation: {explanation}")


async def test_castling():
    """Test explanation for castling"""
    print("\n" + "=" * 80)
    print("TEST 4: Castling (King Safety)")
    print("=" * 80)
    
    llm_service = LLMExplanationService(provider="fallback")
    await llm_service.initialize()
    board_analyzer = BoardAnalyzer()
    
    # Position ready to castle
    fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4"
    board = chess.Board(fen)
    
    board_analysis = board_analyzer.analyze_position(board)
    print(f"\nWhite king safety before castling: {board_analysis['king_safety']['white']}")
    
    # Castle kingside
    move = chess.Move.from_uci("e1g1")
    move_impact = board_analyzer.analyze_move_impact(board, move)
    
    explanation = await llm_service.generate_explanation(
        fen=fen,
        move_san="O-O",
        move_uci="e1g1",
        board_analysis=board_analysis,
        move_impact=move_impact,
        stockfish_eval={'value': 20},
        tactical_themes=[],
        position_type="opening"
    )
    
    print(f"\nMove: O-O")
    print(f"Tactical purpose: {move_impact['tactical_purpose']}")
    print(f"Explanation: {explanation}")


async def test_with_openai(api_key: str):
    """Test with actual OpenAI GPT-4 (if API key provided)"""
    print("\n" + "=" * 80)
    print("TEST 5: OpenAI GPT-4 Integration (Optional)")
    print("=" * 80)
    
    if not api_key:
        print("Skipping - no API key provided")
        print("Set OPENAI_API_KEY environment variable to test GPT-4")
        return
    
    try:
        llm_service = LLMExplanationService(provider="openai-gpt4", api_key=api_key)
        await llm_service.initialize()
        
        board_analyzer = BoardAnalyzer()
        
        # Test a complex position
        fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4"
        board = chess.Board(fen)
        move = chess.Move.from_uci("e1g1")
        
        board_analysis = board_analyzer.analyze_position(board)
        move_impact = board_analyzer.analyze_move_impact(board, move)
        
        explanation = await llm_service.generate_explanation(
            fen=fen,
            move_san="O-O",
            move_uci="e1g1",
            board_analysis=board_analysis,
            move_impact=move_impact,
            stockfish_eval={'value': 20},
            tactical_themes=[],
            position_type="opening"
        )
        
        print(f"\nMove: O-O")
        print(f"GPT-4 Explanation: {explanation}")
        print("✓ GPT-4 integration working!")
        
    except Exception as e:
        print(f"✗ GPT-4 test failed: {e}")


async def main():
    """Run all tests"""
    await test_fallback_mode()
    await test_capture_move()
    await test_defensive_move()
    await test_castling()
    
    # Test with OpenAI if API key available
    api_key = os.getenv("OPENAI_API_KEY")
    await test_with_openai(api_key)
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)
    print("\nNotes:")
    print("- Fallback mode works without any API keys")
    print("- Explanations use actual board analysis (attacks, defenses, threats)")
    print("- To test GPT-4: set OPENAI_API_KEY environment variable")


if __name__ == "__main__":
    asyncio.run(main())
