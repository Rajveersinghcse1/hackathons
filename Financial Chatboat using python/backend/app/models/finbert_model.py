import torch
import numpy as np
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments, EarlyStoppingCallback
)
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
import logging
from typing import Dict, List, Tuple, Optional, Any
import asyncio
import time
import os
import json
from datetime import datetime

from app.config import settings
from app.models.chat_models import SentimentResult, SentimentLabel, EntityResult

logger = logging.getLogger(__name__)

class FinBERTModel:
    """Advanced FinBERT model with fine-tuning capabilities"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False
        self.model_name = settings.FINBERT_MODEL
        self.label_mapping = {
            0: SentimentLabel.NEGATIVE,
            1: SentimentLabel.NEUTRAL,
            2: SentimentLabel.POSITIVE
        }
        logger.info(f"Using device: {self.device}")
    
    async def load_model(self, model_path: Optional[str] = None):
        """Load FinBERT model and tokenizer"""
        try:
            model_path = model_path or self.model_name
            logger.info(f"Loading FinBERT model from {model_path}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                cache_dir=settings.MODEL_CACHE_DIR
            )
            
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_path,
                cache_dir=settings.MODEL_CACHE_DIR,
                num_labels=3  # positive, negative, neutral
            )
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            logger.info("FinBERT model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading FinBERT model: {e}")
            raise
    
    async def analyze_text(self, text: str, include_entities: bool = True) -> Dict[str, Any]:
        """Analyze text for sentiment and entities"""
        if not self.is_loaded:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        start_time = time.time()
        
        try:
            # Sentiment analysis
            sentiment_result = await self._analyze_sentiment(text)
            
            # Entity extraction (simplified - you can integrate spaCy or other NER models)
            entities = []
            if include_entities:
                entities = await self._extract_entities(text)
            
            # Generate response based on sentiment
            response_message = await self._generate_response(text, sentiment_result)
            
            response_time = time.time() - start_time
            
            return {
                "message": response_message,
                "sentiment": sentiment_result,
                "entities": entities,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            raise
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Perform sentiment analysis using FinBERT"""
        try:
            # Tokenize text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            # Convert to numpy for JSON serialization
            raw_scores = {
                "negative": probabilities[0][0].item(),
                "neutral": probabilities[0][1].item(),
                "positive": probabilities[0][2].item()
            }
            
            sentiment_label = self.label_mapping[predicted_class]
            
            return {
                "label": sentiment_label,
                "confidence": confidence,
                "raw_scores": raw_scores
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            raise
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract financial entities from text (simplified implementation)"""
        # This is a simplified entity extraction
        # In production, you'd use a proper NER model or spaCy
        entities = []
        
        # Simple keyword-based entity extraction for demo
        financial_keywords = {
            "STOCK": ["stock", "shares", "equity", "ticker"],
            "COMPANY": ["company", "corporation", "corp", "inc"],
            "CURRENCY": ["USD", "EUR", "GBP", "JPY", "dollar", "euro"],
            "FINANCIAL_METRIC": ["revenue", "profit", "earnings", "EBITDA", "ROI", "P/E ratio"]
        }
        
        text_lower = text.lower()
        for entity_type, keywords in financial_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    start_idx = text_lower.find(keyword.lower())
                    end_idx = start_idx + len(keyword)
                    entities.append({
                        "text": text[start_idx:end_idx],
                        "label": entity_type,
                        "confidence": 0.8,  # Simplified confidence
                        "start": start_idx,
                        "end": end_idx
                    })
        
        return entities
    
    async def _generate_response(self, original_text: str, sentiment: Dict[str, Any]) -> str:
        """Generate contextual response based on sentiment analysis"""
        sentiment_label = sentiment["label"]
        confidence = sentiment["confidence"]
        
        if sentiment_label == SentimentLabel.POSITIVE:
            if confidence > 0.8:
                return f"The financial sentiment in your message is strongly positive (confidence: {confidence:.2f}). This indicates optimistic market sentiment or positive financial outlook."
            else:
                return f"The financial sentiment appears to be positive (confidence: {confidence:.2f}), suggesting a generally favorable financial perspective."
        
        elif sentiment_label == SentimentLabel.NEGATIVE:
            if confidence > 0.8:
                return f"The financial sentiment is strongly negative (confidence: {confidence:.2f}). This suggests concerns or pessimistic outlook regarding financial matters."
            else:
                return f"The financial sentiment appears to be negative (confidence: {confidence:.2f}), indicating some financial concerns or caution."
        
        else:  # NEUTRAL
            return f"The financial sentiment is neutral (confidence: {confidence:.2f}), indicating a balanced or objective financial perspective without strong positive or negative bias."
    
    async def fine_tune(self, training_data: List[Dict], validation_data: Optional[List[Dict]] = None, **kwargs) -> str:
        """Fine-tune the FinBERT model with custom data"""
        try:
            logger.info("Starting fine-tuning process...")
            
            # Prepare training arguments
            training_args = TrainingArguments(
                output_dir=settings.FINE_TUNED_MODEL_DIR,
                num_train_epochs=kwargs.get("num_epochs", settings.NUM_EPOCHS),
                per_device_train_batch_size=kwargs.get("batch_size", settings.BATCH_SIZE),
                learning_rate=kwargs.get("learning_rate", settings.LEARNING_RATE),
                warmup_steps=500,
                weight_decay=0.01,
                logging_dir="./logs",
                logging_steps=10,
                evaluation_strategy="epoch" if validation_data else "no",
                save_strategy="epoch",
                load_best_model_at_end=True if validation_data else False,
                metric_for_best_model="eval_accuracy" if validation_data else None,
            )
            
            # Prepare datasets
            train_dataset = self._prepare_dataset(training_data)
            eval_dataset = self._prepare_dataset(validation_data) if validation_data else None
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=eval_dataset,
                tokenizer=self.tokenizer,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=2)] if validation_data else None,
            )
            
            # Start training
            trainer.train()
            
            # Save the fine-tuned model
            model_save_path = os.path.join(settings.FINE_TUNED_MODEL_DIR, f"finbert_finetuned_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            trainer.save_model(model_save_path)
            self.tokenizer.save_pretrained(model_save_path)
            
            logger.info(f"Fine-tuning completed. Model saved to {model_save_path}")
            return model_save_path
            
        except Exception as e:
            logger.error(f"Error during fine-tuning: {e}")
            raise
    
    def _prepare_dataset(self, data: List[Dict]) -> torch.utils.data.Dataset:
        """Prepare dataset for training"""
        # This is a simplified implementation
        # In production, you'd create a proper Dataset class
        class FinancialDataset(torch.utils.data.Dataset):
            def __init__(self, data, tokenizer, max_length=512):
                self.data = data
                self.tokenizer = tokenizer
                self.max_length = max_length
            
            def __len__(self):
                return len(self.data)
            
            def __getitem__(self, idx):
                item = self.data[idx]
                text = item["text"]
                label = item["label"]  # 0: negative, 1: neutral, 2: positive
                
                encoding = self.tokenizer(
                    text,
                    truncation=True,
                    padding="max_length",
                    max_length=self.max_length,
                    return_tensors="pt"
                )
                
                return {
                    "input_ids": encoding["input_ids"].flatten(),
                    "attention_mask": encoding["attention_mask"].flatten(),
                    "labels": torch.tensor(label, dtype=torch.long)
                }
        
        return FinancialDataset(data, self.tokenizer)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "is_loaded": self.is_loaded,
            "device": str(self.device),
            "model_type": "FinBERT",
            "num_labels": 3,
            "supported_tasks": ["sentiment_analysis", "entity_extraction"]
        }
