from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to analyze")
    context: Optional[List[str]] = Field(default=None, description="Previous conversation context")
    include_sentiment: bool = Field(default=True, description="Include sentiment analysis")
    include_entities: bool = Field(default=True, description="Include entity extraction")

class SentimentResult(BaseModel):
    label: SentimentLabel
    confidence: float = Field(..., ge=0.0, le=1.0)
    raw_scores: Dict[str, float]

class EntityResult(BaseModel):
    text: str
    label: str
    confidence: float
    start: int
    end: int

class ChatResponse(BaseModel):
    message: str
    sentiment: Optional[SentimentResult] = None
    entities: Optional[List[EntityResult]] = None
    response_time: float
    timestamp: datetime = Field(default_factory=datetime.now)
    conversation_id: Optional[str] = None

class FineTuneRequest(BaseModel):
    dataset_name: str = Field(..., description="Name for the fine-tuning dataset")
    training_data: List[Dict[str, Any]] = Field(..., description="Training data for fine-tuning")
    validation_data: Optional[List[Dict[str, Any]]] = Field(default=None, description="Validation data")
    learning_rate: Optional[float] = Field(default=2e-5, ge=1e-6, le=1e-3)
    batch_size: Optional[int] = Field(default=16, ge=1, le=64)
    num_epochs: Optional[int] = Field(default=3, ge=1, le=10)
    save_model: bool = Field(default=True, description="Save the fine-tuned model")

class FineTuneResponse(BaseModel):
    task_id: str
    status: str
    message: str
    estimated_time: Optional[int] = None
    progress: Optional[float] = None

class TrainingStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    loss: Optional[float] = None
    accuracy: Optional[float] = None
    estimated_remaining_time: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class ModelInfo(BaseModel):
    model_name: str
    model_type: str
    version: str
    is_fine_tuned: bool
    training_data_size: Optional[int] = None
    performance_metrics: Optional[Dict[str, float]] = None
    created_at: datetime
    last_updated: datetime
