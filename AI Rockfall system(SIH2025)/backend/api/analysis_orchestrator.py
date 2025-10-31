"""
Analysis Orchestrator for AI Rockfall Prediction System
======================================================

Handles the execution of Jupyter notebook analysis pipelines.
Manages concurrent analysis runs, progress tracking, and result aggregation.

Features:
- Asynchronous notebook execution
- Progress monitoring and status updates
- Result aggregation and validation
- Error handling and recovery
- Resource management and queuing

Author: AI Rockfall Prediction Team
Date: October 26, 2025
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import psutil

from .config import settings
from .models import Analysis, AnalysisStatus, DeviceType
from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

class AnalysisOrchestrator:
    """Orchestrates the execution of analysis notebooks."""

    def __init__(self):
        self.active_analyses: Dict[int, asyncio.Task] = {}
        self.websocket_manager = WebSocketManager()
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_ANALYSES)
        self.analysis_queue: asyncio.Queue = asyncio.Queue()

    async def start_monitoring(self):
        """Start the analysis monitoring loop."""
        logger.info("Starting analysis orchestrator monitoring")
        asyncio.create_task(self._process_analysis_queue())
        asyncio.create_task(self._monitor_system_resources())

    async def _process_analysis_queue(self):
        """Process queued analysis requests."""
        while True:
            try:
                analysis_id = await self.analysis_queue.get()
                await self._execute_analysis(analysis_id)
                self.analysis_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing analysis queue: {e}")

    async def _monitor_system_resources(self):
        """Monitor system resources and adjust concurrency."""
        while True:
            try:
                # Check CPU and memory usage
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent

                # Adjust max workers based on resource usage
                if cpu_percent > 80 or memory_percent > 80:
                    # Reduce concurrency under high load
                    if self.executor._max_workers > 1:
                        logger.warning(f"High resource usage (CPU: {cpu_percent}%, Memory: {memory_percent}%). Reducing concurrency.")
                        # Note: In real implementation, you'd recreate the executor with fewer workers

                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error monitoring system resources: {e}")
                await asyncio.sleep(30)

    async def submit_analysis(
        self,
        analysis_id: int,
        analysis_type: str,
        parameters: Dict[str, Any],
        input_files: List[str]
    ) -> bool:
        """Submit an analysis for execution."""
        try:
            # Add to queue
            await self.analysis_queue.put(analysis_id)

            # Broadcast status update
            await self.websocket_manager.broadcast({
                "type": "analysis_update",
                "analysis_id": analysis_id,
                "status": "queued",
                "timestamp": datetime.utcnow().isoformat()
            })

            logger.info(f"Analysis {analysis_id} submitted to queue")
            return True

        except Exception as e:
            logger.error(f"Error submitting analysis {analysis_id}: {e}")
            return False

    async def _execute_analysis(self, analysis_id: int):
        """Execute a single analysis."""
        try:
            # Update status to running
            await self._update_analysis_status(analysis_id, AnalysisStatus.RUNNING)

            # Get analysis details from database
            # In real implementation, fetch from DB
            analysis_type = "lidar"  # Placeholder
            parameters = {}
            input_files = []

            # Execute based on type
            if analysis_type == "lidar":
                success, results = await self._execute_lidar_analysis(analysis_id, parameters, input_files)
            elif analysis_type == "geophone":
                success, results = await self._execute_geophone_analysis(analysis_id, parameters, input_files)
            # Add other analysis types...

            # Update final status
            if success:
                await self._update_analysis_status(analysis_id, AnalysisStatus.COMPLETED, results)
            else:
                await self._update_analysis_status(analysis_id, AnalysisStatus.FAILED)

        except Exception as e:
            logger.error(f"Error executing analysis {analysis_id}: {e}")
            await self._update_analysis_status(analysis_id, AnalysisStatus.FAILED, error_message=str(e))

    async def _execute_lidar_analysis(
        self,
        analysis_id: int,
        parameters: Dict[str, Any],
        input_files: List[str]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Execute LiDAR analysis notebook."""
        return await self._execute_notebook(
            analysis_id,
            settings.LIDAR_ANALYSIS,
            parameters,
            input_files
        )

    async def _execute_geophone_analysis(
        self,
        analysis_id: int,
        parameters: Dict[str, Any],
        input_files: List[str]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Execute geophone analysis notebook."""
        return await self._execute_notebook(
            analysis_id,
            settings.GEOPHONE_ANALYSIS,
            parameters,
            input_files
        )

    async def _execute_notebook(
        self,
        analysis_id: int,
        notebook_path: str,
        parameters: Dict[str, Any],
        input_files: List[str]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Execute a Jupyter notebook with parameters."""
        try:
            # Create temporary parameter file
            param_file = self._create_parameter_file(analysis_id, parameters, input_files)

            # Execute notebook using papermill or nbconvert
            output_notebook = f"output_{analysis_id}_{int(time.time())}.ipynb"

            # Use subprocess to run jupyter nbconvert execute
            cmd = [
                "jupyter", "nbconvert", "--to", "notebook", "--execute",
                "--output", output_notebook,
                "--ExecutePreprocessor.timeout", str(settings.JUPYTER_KERNEL_TIMEOUT),
                notebook_path
            ]

            # Set environment variables for parameters
            env = os.environ.copy()
            env["ANALYSIS_ID"] = str(analysis_id)
            env["PARAM_FILE"] = param_file

            # Execute in thread pool
            loop = asyncio.get_event_loop()
            process = await loop.run_in_executor(
                self.executor,
                self._run_subprocess,
                cmd,
                env
            )

            if process.returncode == 0:
                # Parse results from output notebook
                results = self._parse_notebook_results(output_notebook)
                return True, results
            else:
                logger.error(f"Notebook execution failed with return code {process.returncode}")
                return False, {"error": "Notebook execution failed"}

        except Exception as e:
            logger.error(f"Error executing notebook {notebook_path}: {e}")
            return False, {"error": str(e)}
        finally:
            # Cleanup temporary files
            if 'param_file' in locals():
                Path(param_file).unlink(missing_ok=True)
            if 'output_notebook' in locals():
                Path(output_notebook).unlink(missing_ok=True)

    def _run_subprocess(self, cmd: List[str], env: Dict[str, str]) -> subprocess.CompletedProcess:
        """Run subprocess in thread pool."""
        return subprocess.run(
            cmd,
            env=env,
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
            timeout=settings.JUPYTER_KERNEL_TIMEOUT
        )

    def _create_parameter_file(
        self,
        analysis_id: int,
        parameters: Dict[str, Any],
        input_files: List[str]
    ) -> str:
        """Create a temporary parameter file for the notebook."""
        param_data = {
            "analysis_id": analysis_id,
            "parameters": parameters,
            "input_files": input_files,
            "output_dir": settings.OUTPUT_DIR,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(param_data, f, indent=2)
            return f.name

    def _parse_notebook_results(self, notebook_path: str) -> Dict[str, Any]:
        """Parse results from executed notebook."""
        try:
            with open(notebook_path, 'r') as f:
                notebook = json.load(f)

            # Extract results from notebook cells
            results = {}
            for cell in notebook.get('cells', []):
                if cell.get('cell_type') == 'code':
                    # Look for result variables in cell outputs
                    for output in cell.get('outputs', []):
                        if output.get('output_type') == 'execute_result':
                            # Extract result data
                            data = output.get('data', {})
                            if 'application/json' in data:
                                results.update(data['application/json'])

            return results

        except Exception as e:
            logger.error(f"Error parsing notebook results: {e}")
            return {"error": "Failed to parse results"}

    async def _update_analysis_status(
        self,
        analysis_id: int,
        status: AnalysisStatus,
        results: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """Update analysis status in database and broadcast to clients."""
        try:
            # In real implementation, update database here
            logger.info(f"Analysis {analysis_id} status updated to {status.value}")

            # Broadcast update via WebSocket
            update_data = {
                "type": "analysis_update",
                "analysis_id": analysis_id,
                "status": status.value,
                "timestamp": datetime.utcnow().isoformat()
            }

            if results:
                update_data["results"] = results
            if error_message:
                update_data["error"] = error_message

            await self.websocket_manager.broadcast(update_data)

        except Exception as e:
            logger.error(f"Error updating analysis status: {e}")

    async def cancel_analysis(self, analysis_id: int) -> bool:
        """Cancel a running analysis."""
        try:
            if analysis_id in self.active_analyses:
                task = self.active_analyses[analysis_id]
                task.cancel()
                del self.active_analyses[analysis_id]

                await self._update_analysis_status(analysis_id, AnalysisStatus.CANCELLED)
                return True

            return False

        except Exception as e:
            logger.error(f"Error cancelling analysis {analysis_id}: {e}")
            return False

    async def get_analysis_status(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Get current status of an analysis."""
        # In real implementation, query database
        return {
            "analysis_id": analysis_id,
            "status": "running",
            "progress": 50,
            "timestamp": datetime.utcnow().isoformat()
        }