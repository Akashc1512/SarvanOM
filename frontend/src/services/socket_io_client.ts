// Socket.IO Client Manager for real-time collaboration

import { io, Socket } from 'socket.io-client';

export interface SocketIOMessage {
  type: string;
  data: any;
  timestamp: string;
  userId?: string;
  roomId?: string;
}

export interface User {
  id: string;
  name: string;
  cursor?: { x: number; y: number };
}

export interface DocumentOperation {
  type: 'insert' | 'delete' | 'replace' | 'retain';
  position: number;
  content?: string;
  length?: number;
  text?: string;
}

export interface PresenceData {
  userId: string;
  name: string;
  status: 'online' | 'offline' | 'away';
}

export interface TypingData {
  userId: string;
  isTyping: boolean;
}

export interface CursorData {
  userId: string;
  position: { x: number; y: number };
}

export interface CommentData {
  id: string;
  userId: string;
  content: string;
  position: number;
  timestamp: string;
}

class SocketIOManager {
  private socket: Socket | null = null;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private connected = false;

  constructor(private url: string) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.socket = io(this.url, {
          transports: ['websocket', 'polling'],
          timeout: 20000,
        });

        this.socket.on('connect', () => {
          console.log('Socket.IO connected');
          this.connected = true;
          resolve();
        });

        this.socket.on('disconnect', () => {
          console.log('Socket.IO disconnected');
          this.connected = false;
        });

        this.socket.on('error', (error) => {
          console.error('Socket.IO error:', error);
          reject(error);
        });

        // Handle all incoming messages
        this.socket.onAny((eventName: string, data: any) => {
          this.handleMessage(eventName, data);
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(eventName: string, data: any): void {
    const listeners = this.listeners.get(eventName);
    if (listeners) {
      listeners.forEach(listener => listener(data));
    }
  }

  on(eventName: string, callback: (data: any) => void): void {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, new Set());
    }
    this.listeners.get(eventName)!.add(callback);
  }

  off(eventName: string, callback: (data: any) => void): void {
    const listeners = this.listeners.get(eventName);
    if (listeners) {
      listeners.delete(callback);
      if (listeners.size === 0) {
        this.listeners.delete(eventName);
      }
    }
  }

  emit(eventName: string, data: any): void {
    if (this.socket && this.connected) {
      this.socket.emit(eventName, data);
    } else {
      console.warn('Socket.IO is not connected');
    }
  }

  joinRoom(roomId: string): void {
    this.emit('join_room', { roomId });
  }

  leaveRoom(roomId: string): void {
    this.emit('leave_room', { roomId });
  }

  sendDocumentOperation(roomId: string, operation: DocumentOperation): void {
    this.emit('document_operation', {
      roomId,
      operation,
      timestamp: new Date().toISOString(),
    });
  }

  updateCursor(roomId: string, cursor: { x: number; y: number }): void {
    this.emit('cursor_update', {
      roomId,
      cursor,
      timestamp: new Date().toISOString(),
    });
  }

  startTyping(roomId: string): void {
    this.emit('typing_start', { roomId });
  }

  stopTyping(roomId: string): void {
    this.emit('typing_stop', { roomId });
  }

  updateDocument(operation: DocumentOperation): void {
    this.emit('document_operation', operation);
  }

  addComment(content: string, position: number): void {
    this.emit('add_comment', { content, position });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }

  isConnected(): boolean {
    return this.connected;
  }

  getSocketId(): string | null {
    return this.socket?.id || null;
  }
}

// Create singleton instance
export const socketIOManager = new SocketIOManager(
  process.env["NEXT_PUBLIC_SOCKET_IO_URL"] || 'http://localhost:8000'
); 