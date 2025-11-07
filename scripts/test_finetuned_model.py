#!/usr/bin/env python3
"""
Test the fine-tuned T5 model with chess positions
"""

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

def test_model():
    """Test the fine-tuned model"""
    
    model_path = "models/chess_t5_finetuned"
    
    print(f"Loading model from {model_path}...")
    tokenizer = T5Tokenizer.from_pretrained(model_path)
    model = T5ForConditionalGeneration.from_pretrained(model_path)
    model.eval()
    
    # Test cases
    test_cases = [
        {
            "input": "Chess position: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 | Move: e4 (e2e4) | Type: opening",
            "expected": "Natural explanation about e4"
        },
        {
            "input": "Chess position: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 | Move: Nf3 (g1f3) | Type: opening",
            "expected": "Natural explanation about Nf3"
        },
        {
            "input": "Chess position: 8/8/8/8/8/8/4K3/4k3 w - - 0 1 | Move: Kf3 (e2f3) | Type: endgame",
            "expected": "Natural explanation about king activation"
        },
        {
            "input": "Chess position: r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 4 | Move: O-O (e1g1) | Type: middlegame",
            "expected": "Natural explanation about castling"
        },
    ]
    
    print("\n" + "="*80)
    print("Testing fine-tuned model with chess positions")
    print("="*80)
    
    for i, test_case in enumerate(test_cases):
        print(f"\n{i+1}. Input: {test_case['input'][:70]}...")
        
        # Add T5 task prefix
        input_text = f"explain chess move: {test_case['input']}"
        
        # Tokenize input
        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            max_length=128,
            truncation=True,
            padding=True
        )
        
        # Generate explanation
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=128,
                num_beams=4,
                early_stopping=True,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
        
        # Decode output
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"   Generated: {generated_text}")
        print(f"   Expected: {test_case['expected']}")

if __name__ == "__main__":
    test_model()
