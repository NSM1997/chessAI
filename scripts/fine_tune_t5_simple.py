#!/usr/bin/env python3
"""
Simple T5 Fine-tuning Script
Phase 3: Fine-tune T5 model on chess explanations
"""

import os
import sys
import json
import logging
from pathlib import Path
import torch
from transformers import (
    T5ForConditionalGeneration, T5Tokenizer,
    TrainingArguments, Trainer,
    DataCollatorForSeq2Seq
)
from torch.utils.data import Dataset
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChessExplanationDataset(Dataset):
    """PyTorch Dataset for chess explanations."""
    
    def __init__(self, data: list, tokenizer, max_length: int = 128):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        example = self.data[idx]
        
        # Add T5 task prefix
        input_text = f"explain chess move: {example['input']}"
        
        # Tokenize input and output
        input_encoding = self.tokenizer(
            input_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        output_encoding = self.tokenizer(
            example['output'],
            max_length=128,  # Longer for natural, coach-like explanations
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': input_encoding['input_ids'].squeeze(),
            'attention_mask': input_encoding['attention_mask'].squeeze(),
            'labels': output_encoding['input_ids'].squeeze()
        }

def load_training_data(file_path: str) -> list:
    """Load training data from file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def fine_tune_t5_model(
    data_file: str,
    output_dir: str = "models/chess_t5_finetuned",
    num_epochs: int = 3,
    batch_size: int = 8,
    learning_rate: float = 5e-5
):
    """Fine-tune T5 model on chess explanations."""
    
    logger.info("Loading T5 model and tokenizer...")
    
    # Load model and tokenizer
    model_name = "t5-small"
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    
    # Load training data
    logger.info(f"Loading training data from {data_file}")
    data = load_training_data(data_file)
    
    # Split data
    random.shuffle(data)
    split_idx = int(0.8 * len(data))
    train_data = data[:split_idx]
    val_data = data[split_idx:]
    
    logger.info(f"Training examples: {len(train_data)}")
    logger.info(f"Validation examples: {len(val_data)}")
    
    # Create datasets
    train_dataset = ChessExplanationDataset(train_data, tokenizer)
    val_dataset = ChessExplanationDataset(val_data, tokenizer)
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir=f"{output_dir}/logs",
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=50,
        save_steps=100,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        save_strategy="steps",
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )
    
    # Train
    logger.info("Starting fine-tuning...")
    trainer.train()
    
    # Save model
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    logger.info(f"Fine-tuning completed. Model saved to {output_dir}")
    
    # Test the model
    test_model(model, tokenizer, train_data[:5])
    
    return model, tokenizer

def test_model(model, tokenizer, test_examples):
    """Test the fine-tuned model."""
    logger.info("Testing fine-tuned model...")
    
    model.eval()
    
    for i, example in enumerate(test_examples):
        input_text = example['input']
        expected_output = example['output']
        
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
        
        print(f"\nTest {i+1}:")
        print(f"Input: {input_text}")
        print(f"Expected: {expected_output}")
        print(f"Generated: {generated_text}")

def main():
    """Main function."""
    data_file = "data/chess_explanations_natural.json"
    
    if not os.path.exists(data_file):
        print(f"Training data file {data_file} not found!")
        print("Please run create_natural_explanations.py first.")
        return
    
    # Fine-tune model
    model, tokenizer = fine_tune_t5_model(
        data_file=data_file,
        output_dir="models/chess_t5_finetuned",
        num_epochs=5,  # Fewer epochs with larger dataset
        batch_size=4,  # Smaller batch size for memory
        learning_rate=3e-5  # Slightly lower learning rate for fine details
    )
    
    print("\nFine-tuning completed successfully!")

if __name__ == "__main__":
    main()
