"""
WebSocket Manager for AI Rockfall Prediction System
==================================================

Manages WebSocket connections for real-time updates and notifications.
Handles client connections, disconnections, and message broadcasting.

Features:
- Connection management
- Real-time broadcasting
- Room-based messaging
- Connection health monitoring
- Automatic cleanup

Author: AI Rockfall Prediction Team
Date: October 26, 2025
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional
from fastapi import WebSocket
from collections import defaultdict

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and real-time messaging."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Set[str]] = defaultdict(set)
        self.connection_metadata: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str = None) -> str:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()

        # Generate client ID if not provided
        if client_id is None:
            client_id = f"client_{id(websocket)}_{int(asyncio.get_event_loop().time())}"

        # Store connection
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "user_agent": getattr(websocket, 'headers', {}).get('user-agent', 'unknown')
        }

        logger.info(f"WebSocket client connected: {client_id}")
        return client_id

    def disconnect(self, websocket: WebSocket, client_id: str = None):
        """Remove a WebSocket connection."""
        if client_id is None:
            # Find client_id by websocket
            client_id = next(
                (cid for cid, ws in self.active_connections.items() if ws == websocket),
                None
            )

        if client_id and client_id in self.active_connections:
            del self.active_connections[client_id]
            if client_id in self.connection_metadata:
                del self.connection_metadata[client_id]

            # Remove from all rooms
            for room in self.rooms:
                self.rooms[room].discard(client_id)
                if not self.rooms[room]:
                    del self.rooms[room]

            logger.info(f"WebSocket client disconnected: {client_id}")

    async def send_personal_message(self, message: Dict, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
                self.connection_metadata[client_id]["last_activity"] = datetime.utcnow().isoformat()
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                # Remove broken connection
                self.disconnect(self.active_connections[client_id], client_id)

    async def broadcast(self, message: Dict, exclude_client: str = None):
        """Broadcast a message to all connected clients."""
        disconnected_clients = []

        for client_id, websocket in self.active_connections.items():
            if client_id == exclude_client:
                continue

            try:
                await websocket.send_json(message)
                self.connection_metadata[client_id]["last_activity"] = datetime.utcnow().isoformat()
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(self.active_connections[client_id], client_id)

    async def broadcast_to_room(self, room: str, message: Dict, exclude_client: str = None):
        """Broadcast a message to all clients in a specific room."""
        if room not in self.rooms:
            return

        disconnected_clients = []

        for client_id in self.rooms[room]:
            if client_id == exclude_client or client_id not in self.active_connections:
                continue

            try:
                await self.active_connections[client_id].send_json(message)
                self.connection_metadata[client_id]["last_activity"] = datetime.utcnow().isoformat()
            except Exception as e:
                logger.error(f"Error broadcasting to room {room}, client {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(self.active_connections[client_id], client_id)

    def join_room(self, client_id: str, room: str):
        """Add a client to a room."""
        if client_id in self.active_connections:
            self.rooms[room].add(client_id)
            logger.debug(f"Client {client_id} joined room {room}")

    def leave_room(self, client_id: str, room: str):
        """Remove a client from a room."""
        if room in self.rooms:
            self.rooms[room].discard(client_id)
            if not self.rooms[room]:
                del self.rooms[room]
            logger.debug(f"Client {client_id} left room {room}")

    def get_room_clients(self, room: str) -> List[str]:
        """Get all clients in a room."""
        return list(self.rooms.get(room, set()))

    def get_connection_info(self, client_id: str) -> Optional[Dict]:
        """Get metadata for a specific connection."""
        return self.connection_metadata.get(client_id)

    def get_active_connections_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)

    def get_room_count(self, room: str) -> int:
        """Get the number of clients in a room."""
        return len(self.rooms.get(room, set()))

    async def ping_all_clients(self):
        """Send ping to all clients to check connectivity."""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast(ping_message)

    async def cleanup_inactive_connections(self, max_inactive_seconds: int = 300):
        """Remove connections that haven't been active for too long."""
        current_time = datetime.utcnow()
        inactive_clients = []

        for client_id, metadata in self.connection_metadata.items():
            last_activity = datetime.fromisoformat(metadata["last_activity"])
            if (current_time - last_activity).total_seconds() > max_inactive_seconds:
                inactive_clients.append(client_id)

        for client_id in inactive_clients:
            logger.info(f"Removing inactive client: {client_id}")
            self.disconnect(self.active_connections[client_id], client_id)

    async def send_system_status(self):
        """Broadcast current system status to all clients."""
        status_message = {
            "type": "system_status",
            "active_connections": self.get_active_connections_count(),
            "rooms": {room: len(clients) for room, clients in self.rooms.items()},
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.broadcast(status_message)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()