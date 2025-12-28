from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from typing import Dict, Any, Optional
import logging
import uuid
import asyncio
from datetime import datetime
import json
import os

from app.models.chat_models import FineTuneRequest, FineTuneResponse, TrainingStatus
from app.models.finbert_model import FinBERTModel
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Store training tasks (in production, use a proper database)
training_tasks: Dict[str, Dict[str, Any]] = {}

def get_finbert_model(request: Request) -> FinBERTModel:
    """Dependency to get FinBERT model from app state"""
    return request.app.state.finbert_model

async def run_fine_tuning(task_id: str, finbert_model: FinBERTModel, fine_tune_request: FineTuneRequest):
    """Background task to run fine-tuning"""
    try:
        # Update task status
        training_tasks[task_id]["status"] = "running"
        training_tasks[task_id]["progress"] = 0.0
        training_tasks[task_id]["updated_at"] = datetime.now()
        
        logger.info(f"Starting fine-tuning task {task_id}")
        
        # Prepare training data
        training_data = []
        for item in fine_tune_request.training_data:
            if "text" in item and "label" in item:
                # Convert string labels to numeric if needed
                label = item["label"]
                if isinstance(label, str):
                    label_map = {"negative": 0, "neutral": 1, "positive": 2}
                    label = label_map.get(label.lower(), 1)
                
                training_data.append({
                    "text": item["text"],
                    "label": label
                })
        
        # Update progress
        training_tasks[task_id]["progress"] = 0.2
        training_tasks[task_id]["current_epoch"] = 0
        training_tasks[task_id]["total_epochs"] = fine_tune_request.num_epochs
        
        # Prepare validation data if provided
        validation_data = None
        if fine_tune_request.validation_data:
            validation_data = []
            for item in fine_tune_request.validation_data:
                if "text" in item and "label" in item:
                    label = item["label"]
                    if isinstance(label, str):
                        label_map = {"negative": 0, "neutral": 1, "positive": 2}
                        label = label_map.get(label.lower(), 1)
                    
                    validation_data.append({
                        "text": item["text"],
                        "label": label
                    })
        
        # Update progress
        training_tasks[task_id]["progress"] = 0.3
        
        # Start fine-tuning
        model_path = await finbert_model.fine_tune(
            training_data=training_data,
            validation_data=validation_data,
            learning_rate=fine_tune_request.learning_rate,
            batch_size=fine_tune_request.batch_size,
            num_epochs=fine_tune_request.num_epochs
        )
        
        # Update task completion
        training_tasks[task_id]["status"] = "completed"
        training_tasks[task_id]["progress"] = 1.0
        training_tasks[task_id]["model_path"] = model_path
        training_tasks[task_id]["completed_at"] = datetime.now()
        training_tasks[task_id]["updated_at"] = datetime.now()
        
        logger.info(f"Fine-tuning task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Fine-tuning task {task_id} failed: {e}")
        training_tasks[task_id]["status"] = "failed"
        training_tasks[task_id]["error"] = str(e)
        training_tasks[task_id]["updated_at"] = datetime.now()

@router.post("/finetune/start", response_model=FineTuneResponse)
async def start_fine_tuning(
    fine_tune_request: FineTuneRequest,
    background_tasks: BackgroundTasks,
    finbert_model: FinBERTModel = Depends(get_finbert_model)
):
    """
    Start fine-tuning process with custom data
    """
    try:
        if not finbert_model.is_loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Validate training data
        if not fine_tune_request.training_data:
            raise HTTPException(status_code=400, detail="Training data is required")
        
        if len(fine_tune_request.training_data) < 10:
            raise HTTPException(status_code=400, detail="Minimum 10 training samples required")
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create task record
        training_tasks[task_id] = {
            "task_id": task_id,
            "status": "queued",
            "progress": 0.0,
            "dataset_name": fine_tune_request.dataset_name,
            "training_samples": len(fine_tune_request.training_data),
            "validation_samples": len(fine_tune_request.validation_data) if fine_tune_request.validation_data else 0,
            "parameters": {
                "learning_rate": fine_tune_request.learning_rate,
                "batch_size": fine_tune_request.batch_size,
                "num_epochs": fine_tune_request.num_epochs
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Start background task
        background_tasks.add_task(run_fine_tuning, task_id, finbert_model, fine_tune_request)
        
        # Estimate training time (rough calculation)
        estimated_time = (len(fine_tune_request.training_data) * fine_tune_request.num_epochs) // 100
        
        return FineTuneResponse(
            task_id=task_id,
            status="queued",
            message="Fine-tuning task started successfully",
            estimated_time=estimated_time
        )
        
    except Exception as e:
        logger.error(f"Error starting fine-tuning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/finetune/status/{task_id}", response_model=TrainingStatus)
async def get_training_status(task_id: str):
    """
    Get the status of a fine-tuning task
    """
    if task_id not in training_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = training_tasks[task_id]
    
    return TrainingStatus(
        task_id=task["task_id"],
        status=task["status"],
        progress=task["progress"],
        current_epoch=task.get("current_epoch"),
        total_epochs=task.get("total_epochs"),
        loss=task.get("loss"),
        accuracy=task.get("accuracy"),
        estimated_remaining_time=task.get("estimated_remaining_time"),
        created_at=task["created_at"],
        updated_at=task["updated_at"]
    )

@router.get("/finetune/tasks")
async def list_training_tasks(status: Optional[str] = None, limit: int = 50):
    """
    List all fine-tuning tasks
    """
    tasks = list(training_tasks.values())
    
    if status:
        tasks = [task for task in tasks if task["status"] == status]
    
    # Sort by creation date (newest first)
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "tasks": tasks[:limit],
        "total_count": len(tasks),
        "limit": limit
    }

@router.delete("/finetune/task/{task_id}")
async def cancel_training_task(task_id: str):
    """
    Cancel a fine-tuning task
    """
    if task_id not in training_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = training_tasks[task_id]
    
    if task["status"] == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed task")
    
    if task["status"] == "failed":
        raise HTTPException(status_code=400, detail="Cannot cancel failed task")
    
    # Update task status
    training_tasks[task_id]["status"] = "cancelled"
    training_tasks[task_id]["updated_at"] = datetime.now()
    
    return {"message": "Task cancelled successfully"}

@router.post("/finetune/load-model")
async def load_fine_tuned_model(
    model_path: str,
    finbert_model: FinBERTModel = Depends(get_finbert_model)
):
    """
    Load a fine-tuned model
    """
    try:
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail="Model path not found")
        
        await finbert_model.load_model(model_path)
        
        return {
            "message": "Fine-tuned model loaded successfully",
            "model_path": model_path,
            "model_info": finbert_model.get_model_info()
        }
        
    except Exception as e:
        logger.error(f"Error loading fine-tuned model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/finetune/models")
async def list_fine_tuned_models():
    """
    List available fine-tuned models
    """
    try:
        models = []
        fine_tuned_dir = settings.FINE_TUNED_MODEL_DIR
        
        if os.path.exists(fine_tuned_dir):
            for item in os.listdir(fine_tuned_dir):
                model_path = os.path.join(fine_tuned_dir, item)
                if os.path.isdir(model_path):
                    # Check if it's a valid model directory
                    if os.path.exists(os.path.join(model_path, "config.json")):
                        stat = os.stat(model_path)
                        models.append({
                            "name": item,
                            "path": model_path,
                            "created_at": datetime.fromtimestamp(stat.st_ctime),
                            "size_mb": sum(
                                os.path.getsize(os.path.join(model_path, f))
                                for f in os.listdir(model_path)
                                if os.path.isfile(os.path.join(model_path, f))
                            ) / (1024 * 1024)
                        })
        
        return {
            "models": sorted(models, key=lambda x: x["created_at"], reverse=True),
            "total_count": len(models)
        }
        
    except Exception as e:
        logger.error(f"Error listing fine-tuned models: {e}")
        raise HTTPException(status_code=500, detail=str(e))
