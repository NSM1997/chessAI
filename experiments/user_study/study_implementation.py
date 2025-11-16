"""
User Study Implementation Framework

Web interface for running explainability study
"""

import json
import random
import time
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Position:
    """Chess position for study"""
    position_id: str
    fen: str
    theme: str
    difficulty: str  # 'easy', 'medium', 'hard'
    correct_move: str
    correct_move_san: str
    alternatives: List[str]  # 3 wrong moves
    evaluation: float
    explanation_text: str
    heatmap_path: str  # Path to Grad-CAM visualization


@dataclass
class Trial:
    """Single trial result"""
    position_id: str
    participant_move: str
    is_correct: bool
    time_to_decision: float
    confidence: int
    participant_explanation: str
    timestamp: str


@dataclass
class Participant:
    """Participant data"""
    participant_id: str
    condition: str  # 'control', 'text', 'visual', 'combined'
    age: int
    elo: int
    years_experience: int
    trials: List[Trial]
    post_survey: Dict


class StudyManager:
    """
    Manages user study data collection
    """
    
    def __init__(self, positions_file: str, output_dir: str):
        """
        Args:
            positions_file: JSON file with all study positions
            output_dir: Directory to save results
        """
        self.positions = self.load_positions(positions_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Counterbalancing: ensure equal participants per condition
        self.conditions = ['control', 'text', 'visual', 'combined']
        self.condition_counts = {c: 0 for c in self.conditions}
    
    def load_positions(self, filepath: str) -> List[Position]:
        """Load study positions from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        positions = []
        for pos_data in data['positions']:
            pos = Position(**pos_data)
            positions.append(pos)
        
        return positions
    
    def assign_condition(self) -> str:
        """
        Assign participant to condition (balanced assignment)
        """
        # Find condition with fewest participants
        min_count = min(self.condition_counts.values())
        available = [c for c, count in self.condition_counts.items() 
                    if count == min_count]
        
        # Randomly select from available
        condition = random.choice(available)
        self.condition_counts[condition] += 1
        
        return condition
    
    def create_participant(
        self, 
        age: int, 
        elo: int, 
        years_exp: int
    ) -> Participant:
        """
        Create new participant with assigned condition
        """
        participant_id = f"P{len(list(self.output_dir.glob('*.json'))) + 1:03d}"
        condition = self.assign_condition()
        
        participant = Participant(
            participant_id=participant_id,
            condition=condition,
            age=age,
            elo=elo,
            years_experience=years_exp,
            trials=[],
            post_survey={}
        )
        
        return participant
    
    def get_training_positions(self, n: int = 5) -> List[Position]:
        """Get training positions (not scored)"""
        return random.sample(self.positions, n)
    
    def get_study_positions(self, n: int = 20) -> List[Position]:
        """Get main study positions (balanced by difficulty)"""
        easy = [p for p in self.positions if p.difficulty == 'easy']
        medium = [p for p in self.positions if p.difficulty == 'medium']
        hard = [p for p in self.positions if p.difficulty == 'hard']
        
        selected = (
            random.sample(easy, 8) +
            random.sample(medium, 9) +
            random.sample(hard, 3)
        )
        
        random.shuffle(selected)
        return selected
    
    def record_trial(
        self,
        participant: Participant,
        position: Position,
        selected_move: str,
        time_taken: float,
        confidence: int,
        explanation: str
    ) -> Trial:
        """
        Record a single trial
        """
        is_correct = (selected_move == position.correct_move_san)
        
        trial = Trial(
            position_id=position.position_id,
            participant_move=selected_move,
            is_correct=is_correct,
            time_to_decision=time_taken,
            confidence=confidence,
            participant_explanation=explanation,
            timestamp=datetime.now().isoformat()
        )
        
        participant.trials.append(trial)
        return trial
    
    def save_participant_data(self, participant: Participant):
        """Save participant data to JSON"""
        filepath = self.output_dir / f"{participant.participant_id}.json"
        
        with open(filepath, 'w') as f:
            json.dump(asdict(participant), f, indent=2)
        
        print(f"✅ Saved data for {participant.participant_id}")
    
    def analyze_results(self) -> Dict:
        """
        Analyze all collected data
        
        Returns:
            Summary statistics by condition
        """
        results = {condition: {
            'participants': [],
            'accuracy': [],
            'avg_time': [],
            'avg_confidence': []
        } for condition in self.conditions}
        
        # Load all participant files
        for filepath in self.output_dir.glob("P*.json"):
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            condition = data['condition']
            trials = data['trials']
            
            # Calculate metrics
            accuracy = sum(t['is_correct'] for t in trials) / len(trials)
            avg_time = sum(t['time_to_decision'] for t in trials) / len(trials)
            avg_conf = sum(t['confidence'] for t in trials) / len(trials)
            
            results[condition]['participants'].append(data['participant_id'])
            results[condition]['accuracy'].append(accuracy)
            results[condition]['avg_time'].append(avg_time)
            results[condition]['avg_confidence'].append(avg_conf)
        
        # Summary statistics
        summary = {}
        for condition in self.conditions:
            if len(results[condition]['accuracy']) > 0:
                import numpy as np
                summary[condition] = {
                    'n': len(results[condition]['participants']),
                    'mean_accuracy': np.mean(results[condition]['accuracy']),
                    'std_accuracy': np.std(results[condition]['accuracy']),
                    'mean_time': np.mean(results[condition]['avg_time']),
                    'mean_confidence': np.mean(results[condition]['avg_confidence'])
                }
        
        return summary


def generate_study_positions(
    model,
    puzzle_dataset: List[Dict],
    num_positions: int = 25,
    output_file: str = 'study_positions.json'
):
    """
    Generate positions for study with pre-computed explanations
    
    Args:
        model: Trained tactical classifier
        puzzle_dataset: List of chess puzzles
        num_positions: Total positions needed
        output_file: JSON file to save positions
    """
    from backend.app.services.chess_engine import ChessEngineService
    from backend.app.services.llm_explanation import LLMExplanationService
    from backend.app.ml.explainability.gradcam import ChessGradCAM
    import chess
    
    # Initialize services
    engine = ChessEngineService()
    llm = LLMExplanationService()
    
    # Get last conv layer for Grad-CAM
    target_layer = None
    for module in model.modules():
        if isinstance(module, torch.nn.Conv2d):
            target_layer = module
    gradcam = ChessGradCAM(model, target_layer)
    
    positions = []
    themes_count = {}
    
    for puzzle in puzzle_dataset:
        if len(positions) >= num_positions:
            break
        
        # Balance tactical themes
        theme = puzzle['themes'][0] if puzzle['themes'] else 'unknown'
        if themes_count.get(theme, 0) >= 4:
            continue
        
        try:
            board = chess.Board(puzzle['fen'])
            
            # Get engine analysis
            analysis = engine.analyze_position(puzzle['fen'])
            best_move = analysis['best_moves'][0]
            
            # Generate explanation
            explanation = llm.generate_explanation(
                fen=puzzle['fen'],
                best_move=best_move['san'],
                engine_analysis=analysis
            )
            
            # Generate Grad-CAM heatmap
            from backend.app.ml.data_preprocessing import ChessBoardEncoder
            encoder = ChessBoardEncoder()
            board_tensor = encoder.encode(board)
            board_tensor = torch.from_numpy(board_tensor).unsqueeze(0)
            
            heatmap = gradcam.generate_heatmap(board_tensor, target_class=0)
            
            # Save heatmap
            heatmap_path = f"heatmaps/position_{len(positions)}.npy"
            np.save(heatmap_path, heatmap)
            
            # Generate wrong alternatives
            legal_moves = [move.uci() for move in board.legal_moves]
            alternatives = random.sample(legal_moves, min(3, len(legal_moves) - 1))
            
            # Determine difficulty
            if puzzle.get('rating', 1500) < 1400:
                difficulty = 'easy'
            elif puzzle.get('rating', 1500) < 1800:
                difficulty = 'medium'
            else:
                difficulty = 'hard'
            
            # Create position object
            position = {
                'position_id': f"pos_{len(positions):03d}",
                'fen': puzzle['fen'],
                'theme': theme,
                'difficulty': difficulty,
                'correct_move': best_move['move'],
                'correct_move_san': best_move['san'],
                'alternatives': alternatives,
                'evaluation': best_move['score']['value'],
                'explanation_text': explanation,
                'heatmap_path': heatmap_path
            }
            
            positions.append(position)
            themes_count[theme] = themes_count.get(theme, 0) + 1
            
            print(f"Generated position {len(positions)}/{num_positions}: {theme} ({difficulty})")
        
        except Exception as e:
            print(f"Error processing puzzle: {e}")
            continue
    
    # Save positions
    output = {'positions': positions}
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Generated {len(positions)} study positions")
    print(f"📁 Saved to: {output_file}")


if __name__ == "__main__":
    """Test study manager"""
    
    # Create mock positions file
    mock_positions = {
        'positions': [
            {
                'position_id': 'pos_001',
                'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'theme': 'fork',
                'difficulty': 'easy',
                'correct_move': 'e2e4',
                'correct_move_san': 'e4',
                'alternatives': ['d2d4', 'g1f3', 'c2c4'],
                'evaluation': 0.2,
                'explanation_text': 'Control the center',
                'heatmap_path': 'heatmaps/pos_001.npy'
            }
        ]
    }
    
    with open('test_positions.json', 'w') as f:
        json.dump(mock_positions, f)
    
    # Test study manager
    study = StudyManager('test_positions.json', 'study_results')
    
    # Create participant
    participant = study.create_participant(age=25, elo=1500, years_exp=3)
    print(f"Created participant: {participant.participant_id}, Condition: {participant.condition}")
    
    # Simulate trial
    position = study.positions[0]
    study.record_trial(
        participant=participant,
        position=position,
        selected_move='e4',
        time_taken=5.2,
        confidence=4,
        explanation="Controls the center squares"
    )
    
    # Save data
    study.save_participant_data(participant)
    
    print("✅ Study framework working!")

