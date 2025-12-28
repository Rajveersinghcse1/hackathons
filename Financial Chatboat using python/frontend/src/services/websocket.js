import io from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
  }

  connect(onMessage, onConnect, onDisconnect, onError) {
    try {
      this.socket = io('ws://localhost:8000', {
        transports: ['websocket'],
        path: '/ws/chat'
      });

      this.socket.on('connect', () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        if (onConnect) onConnect();
      });

      this.socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        if (onDisconnect) onDisconnect();
      });

      this.socket.on('message', (data) => {
        console.log('WebSocket message received:', data);
        try {
          const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
          if (onMessage) onMessage(parsedData);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          if (onError) onError(error);
        }
      });

      this.socket.on('error', (error) => {
        console.error('WebSocket error:', error);
        if (onError) onError(error);
      });

    } catch (error) {
      console.error('Error establishing WebSocket connection:', error);
      if (onError) onError(error);
    }
  }

  sendMessage(data) {
    if (this.socket && this.isConnected) {
      this.socket.emit('message', JSON.stringify(data));
      return true;
    }
    console.warn('WebSocket not connected');
    return false;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  isSocketConnected() {
    return this.isConnected && this.socket?.connected;
  }
}

export default WebSocketService;
