"""
Explainability Evaluation Metrics

Metrics to quantitatively evaluate explanation quality:
1. Faithfulness: Does explanation reflect actual model reasoning?
2. Consistency: Are similar positions explained similarly?
3. Human Agreement: Do explanations match expert understanding?

RESEARCH CONTRIBUTION:
- Quantitative evaluation of chess AI explanations
- Novel metrics for tactical explanation quality
"""

import torch
import numpy as np
from typing import List, Dict, Tuple
import logging
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import spearmanr

logger = logging.getLogger(__name__)


def faithfulness_score(
    model: torch.nn.Module,
    board_tensor: torch.Tensor,
    explanation_heatmap: np.ndarray,
    target_class: int,
    num_perturbations: int = 100,
    top_k_percent: float = 0.2
) -> float:
    """
    Measure faithfulness: Does removing important squares hurt prediction?
    
    Method (inspired by "Evaluating Explanations" - Samek et al.):
    1. Get model prediction on original board
    2. Mask top-k most important squares (according to explanation)
    3. Measure drop in prediction confidence
    4. Higher drop = more faithful explanation
    
    Args:
        model: Tactical classifier
        board_tensor: (1, 12, 8, 8) original board
        explanation_heatmap: (8, 8) importance scores
        target_class: Tactical theme being explained
        num_perturbations: Number of random masks for baseline
        top_k_percent: Percentage of top squares to mask
        
    Returns:
        faithfulness: Higher is better (0-1 scale)
    """
    model.eval()
    device = next(model.parameters()).device
    board_tensor = board_tensor.to(device)
    
    # Original prediction
    with torch.no_grad():
        orig_pred = model(board_tensor)[0, target_class].item()
    
    # Mask top-k most important squares
    k = int(64 * top_k_percent)
    flat_importance = explanation_heatmap.flatten()
    top_k_indices = np.argsort(flat_importance)[-k:]
    
    # Create masked board
    masked_board = board_tensor.clone()
    for idx in top_k_indices:
        row = idx // 8
        col = idx % 8
        masked_board[0, :, row, col] = 0  # Remove all pieces from this square
    
    # Prediction on masked board
    with torch.no_grad():
        masked_pred = model(masked_board)[0, target_class].item()
    
    # Drop in confidence
    conf_drop_explanation = orig_pred - masked_pred
    
    # Compare with random masking (baseline)
    random_drops = []
    for _ in range(num_perturbations):
        random_indices = np.random.choice(64, k, replace=False)
        random_masked = board_tensor.clone()
        for idx in random_indices:
            row = idx // 8
            col = idx % 8
            random_masked[0, :, row, col] = 0
        
        with torch.no_grad():
            random_pred = model(random_masked)[0, target_class].item()
        random_drops.append(orig_pred - random_pred)
    
    # Average random drop
    avg_random_drop = np.mean(random_drops)
    
    # Faithfulness: Explanation should cause more drop than random
    # Normalize to [0, 1]
    if avg_random_drop > 0:
        faithfulness = min(conf_drop_explanation / avg_random_drop, 1.0)
    else:
        faithfulness = 1.0 if conf_drop_explanation > 0 else 0.0
    
    return max(0.0, faithfulness)


def consistency_score(
    explanations: List[np.ndarray],
    position_similarity: List[float]
) -> float:
    """
    Measure consistency: Similar positions should get similar explanations
    
    Args:
        explanations: List of (8, 8) heatmaps for similar positions
        position_similarity: List of similarity scores between positions
        
    Returns:
        consistency: Spearman correlation between position similarity 
                    and explanation similarity (0-1 scale)
    """
    if len(explanations) < 2:
        return 1.0
    
    # Flatten explanations
    flat_explanations = [exp.flatten() for exp in explanations]
    
    # Compute pairwise explanation similarity (cosine)
    n = len(flat_explanations)
    explanation_sim = []
    position_sim = []
    
    for i in range(n):
        for j in range(i + 1, n):
            # Cosine similarity of explanations
            cos_sim = cosine_similarity(
                flat_explanations[i].reshape(1, -1),
                flat_explanations[j].reshape(1, -1)
            )[0, 0]
            explanation_sim.append(cos_sim)
            
            # Position similarity (if provided)
            if i < len(position_similarity) and j < len(position_similarity):
                position_sim.append(position_similarity[j] if i == 0 else 0.5)
    
    # Spearman correlation
    if len(explanation_sim) > 1 and len(position_sim) > 1:
        corr, _ = spearmanr(position_sim, explanation_sim)
        return max(0.0, corr)  # Convert to [0, 1]
    
    return 0.5


def human_agreement_score(
    generated_explanation: str,
    expert_explanation: str,
    method: str = 'semantic'
) -> float:
    """
    Measure agreement between generated and expert explanations
    
    Args:
        generated_explanation: LLM-generated text
        expert_explanation: Human expert annotation
        method: 'semantic' (embedding similarity) or 'keyword' (overlap)
        
    Returns:
        agreement: 0-1 similarity score
    """
    if method == 'keyword':
        # Simple keyword overlap
        gen_words = set(generated_explanation.lower().split())
        expert_words = set(expert_explanation.lower().split())
        
        if len(expert_words) == 0:
            return 0.0
        
        overlap = len(gen_words & expert_words)
        return overlap / len(expert_words)
    
    elif method == 'semantic':
        # Use sentence embeddings (requires sentence-transformers)
        try:
            from sentence_transformers import SentenceTransformer, util
            
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            gen_emb = model.encode(generated_explanation, convert_to_tensor=True)
            expert_emb = model.encode(expert_explanation, convert_to_tensor=True)
            
            similarity = util.cos_sim(gen_emb, expert_emb).item()
            return max(0.0, min(1.0, similarity))
        
        except ImportError:
            logger.warning("sentence-transformers not installed. Falling back to keyword method.")
            return human_agreement_score(generated_explanation, expert_explanation, method='keyword')
    
    else:
        raise ValueError(f"Unknown method: {method}")


def completeness_score(
    explanation_heatmap: np.ndarray,
    ground_truth_squares: List[str]
) -> float:
    """
    Measure completeness: Does explanation cover all important squares?
    
    Args:
        explanation_heatmap: (8, 8) importance scores
        ground_truth_squares: List of truly important squares (human labeled)
        
    Returns:
        completeness: Recall of important squares (0-1)
    """
    if len(ground_truth_squares) == 0:
        return 1.0
    
    # Get top-k squares from explanation
    k = len(ground_truth_squares) * 2  # Consider top 2x squares
    flat_importance = explanation_heatmap.flatten()
    top_k_indices = np.argsort(flat_importance)[-k:]
    
    # Convert indices to square names
    explained_squares = set()
    for idx in top_k_indices:
        row = idx // 8
        col = idx % 8
        file = chr(ord('a') + col)
        rank = str(row + 1)
        explained_squares.add(f"{file}{rank}")
    
    # Calculate recall
    ground_truth_set = set(ground_truth_squares)
    hits = len(explained_squares & ground_truth_set)
    
    return hits / len(ground_truth_set)


def compactness_score(explanation_heatmap: np.ndarray, top_k: int = 10) -> float:
    """
    Measure compactness: Is attention focused on few squares or scattered?
    
    Lower entropy = more focused = better for human comprehension
    
    Args:
        explanation_heatmap: (8, 8) importance scores
        top_k: Consider top-k squares
        
    Returns:
        compactness: 0-1 score (higher = more focused)
    """
    from scipy.stats import entropy
    
    # Normalize to probability distribution
    flat = explanation_heatmap.flatten()
    if flat.sum() == 0:
        return 0.0
    
    probs = flat / flat.sum()
    
    # Calculate entropy
    ent = entropy(probs)
    
    # Normalize by maximum possible entropy (uniform distribution)
    max_entropy = np.log(64)
    
    # Compactness: 1 - normalized_entropy
    compactness = 1 - (ent / max_entropy)
    
    return compactness


def stability_score(
    model: torch.nn.Module,
    board_tensor: torch.Tensor,
    explanation_method,
    target_class: int,
    num_trials: int = 10,
    noise_level: float = 0.01
) -> float:
    """
    Measure stability: Small input perturbations should give similar explanations
    
    Args:
        model: Tactical classifier
        board_tensor: (1, 12, 8, 8)
        explanation_method: Function that generates explanations
        target_class: Tactical theme
        num_trials: Number of perturbations
        noise_level: Magnitude of noise
        
    Returns:
        stability: Average cosine similarity of perturbed explanations (0-1)
    """
    # Generate explanation for original
    orig_explanation = explanation_method(model, board_tensor, target_class)
    orig_flat = orig_explanation.flatten()
    
    # Generate explanations for perturbed inputs
    similarities = []
    for _ in range(num_trials):
        noise = torch.randn_like(board_tensor) * noise_level
        perturbed = board_tensor + noise
        perturbed = torch.clamp(perturbed, 0, 1)
        
        perturbed_explanation = explanation_method(model, perturbed, target_class)
        perturbed_flat = perturbed_explanation.flatten()
        
        # Cosine similarity
        sim = cosine_similarity(
            orig_flat.reshape(1, -1),
            perturbed_flat.reshape(1, -1)
        )[0, 0]
        similarities.append(sim)
    
    return np.mean(similarities)


def evaluate_explanation_suite(
    model: torch.nn.Module,
    board_tensor: torch.Tensor,
    explanation_heatmap: np.ndarray,
    target_class: int,
    expert_explanation: str = None,
    ground_truth_squares: List[str] = None
) -> Dict[str, float]:
    """
    Comprehensive evaluation of a single explanation
    
    Returns:
        dict: All metric scores
    """
    results = {}
    
    # Faithfulness
    results['faithfulness'] = faithfulness_score(
        model, board_tensor, explanation_heatmap, target_class
    )
    
    # Compactness
    results['compactness'] = compactness_score(explanation_heatmap)
    
    # Completeness (if ground truth available)
    if ground_truth_squares:
        results['completeness'] = completeness_score(
            explanation_heatmap, ground_truth_squares
        )
    
    logger.info(f"Explanation metrics: {results}")
    return results


def compare_explanation_methods(
    model: torch.nn.Module,
    test_boards: torch.Tensor,
    method1_heatmaps: List[np.ndarray],
    method2_heatmaps: List[np.ndarray],
    method1_name: str = "Method 1",
    method2_name: str = "Method 2"
) -> Dict[str, Dict[str, float]]:
    """
    Compare two explanation methods across multiple test cases
    
    Research Question: Is Grad-CAM better than Attention for chess explanations?
    
    Returns:
        dict: {'method1': metrics, 'method2': metrics}
    """
    import matplotlib.pyplot as plt
    
    metrics1 = {
        'faithfulness': [],
        'compactness': [],
    }
    
    metrics2 = {
        'faithfulness': [],
        'compactness': [],
    }
    
    for i, (board, hm1, hm2) in enumerate(zip(test_boards, method1_heatmaps, method2_heatmaps)):
        # Assume target class 0 for comparison
        f1 = faithfulness_score(model, board.unsqueeze(0), hm1, target_class=0)
        c1 = compactness_score(hm1)
        
        f2 = faithfulness_score(model, board.unsqueeze(0), hm2, target_class=0)
        c2 = compactness_score(hm2)
        
        metrics1['faithfulness'].append(f1)
        metrics1['compactness'].append(c1)
        
        metrics2['faithfulness'].append(f2)
        metrics2['compactness'].append(c2)
    
    # Aggregate results
    results = {
        method1_name: {
            'avg_faithfulness': np.mean(metrics1['faithfulness']),
            'avg_compactness': np.mean(metrics1['compactness']),
        },
        method2_name: {
            'avg_faithfulness': np.mean(metrics2['faithfulness']),
            'avg_compactness': np.mean(metrics2['compactness']),
        }
    }
    
    # Statistical significance (t-test)
    from scipy.stats import ttest_rel
    
    t_faith, p_faith = ttest_rel(metrics1['faithfulness'], metrics2['faithfulness'])
    t_comp, p_comp = ttest_rel(metrics1['compactness'], metrics2['compactness'])
    
    results['significance'] = {
        'faithfulness_p': p_faith,
        'compactness_p': p_comp
    }
    
    logger.info(f"Comparison results:\n{results}")
    return results


if __name__ == "__main__":
    """Test metrics"""
    # Create dummy data
    model = None  # Would need actual model
    board = torch.randn(1, 12, 8, 8)
    heatmap = np.random.rand(8, 8)
    
    # Test individual metrics
    compactness = compactness_score(heatmap)
    print(f"✅ Compactness score: {compactness:.3f}")
    
    completeness = completeness_score(heatmap, ['e4', 'd5', 'f3'])
    print(f"✅ Completeness score: {completeness:.3f}")
    
    # Test human agreement
    gen = "This move develops the knight and controls the center"
    exp = "Develops knight to central square, controlling e5 and d4"
    agreement = human_agreement_score(gen, exp, method='keyword')
    print(f"✅ Human agreement: {agreement:.3f}")

