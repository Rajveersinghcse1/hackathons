from fastapi import WebSocket
from typing import List, Dict
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket connection manager for real-time chat"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            self.user_connections[user_id] = websocket
        
        logger.info(f"New WebSocket connection established. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            # Remove disconnected websocket
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def send_message_to_user(self, message: str, user_id: str):
        """Send message to specific user"""
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            await self.send_personal_message(message, websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        disconnected_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected_connections.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected_connections:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
    
    async def send_json_to_user(self, data: dict, user_id: str):
        """Send JSON data to specific user"""
        message = json.dumps(data)
        await self.send_message_to_user(message, user_id)
    
    async def broadcast_json(self, data: dict):
        """Broadcast JSON data to all connected clients"""
        message = json.dumps(data)
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_connected_users(self) -> List[str]:
        """Get list of connected user IDs"""
        return list(self.user_connections.keys())
    
    async def send_typing_indicator(self, user_id: str, is_typing: bool):
        """Send typing indicator to user"""
        data = {
            "type": "typing_indicator",
            "is_typing": is_typing,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_json_to_user(data, user_id)
    
    async def send_system_message(self, message: str, user_id: str = None):
        """Send system message to user or broadcast"""
        data = {
            "type": "system_message",
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if user_id:
            await self.send_json_to_user(data, user_id)
        else:
            await self.broadcast_json(data)
    
    async def send_error_message(self, error: str, user_id: str = None):
        """Send error message to user or broadcast"""
        data = {
            "type": "error",
            "error": error,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if user_id:
            await self.send_json_to_user(data, user_id)
        else:
            await self.broadcast_json(data)

# Global connection manager instance
connection_manager = ConnectionManager()
