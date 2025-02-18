import { Socket } from 'socket.io-client';
import { io } from 'socket.io-client';
import { FileSession, ServerMessage } from './types';

const SERVER_PORT = 5000;
const SERVER_URL = `http://localhost:${SERVER_PORT}`;

export class SessionManager {
    private socket: Socket | undefined;
    private currentSession: FileSession | undefined;
    private messageHandlers: Map<string, Set<(message: any) => void>>;
    private serverReady: boolean = true;

    constructor(private onStatusChange: (ready: boolean) => void) {
        this.messageHandlers = new Map();
    }

    async initSession(filePath: string): Promise<string> {
        const sessionId = crypto.randomUUID();
        let initializeSent = false;
        
        return new Promise((resolve, reject) => {
            this.socket = io(SERVER_URL);
            
            // Set a timeout to reject if initialization takes too long
            const timeout = setTimeout(() => {
                reject(new Error('Session initialization timed out'));
            }, 10000);  // 10 second timeout
            
            this.socket.on('connect', () => {
                console.log('Connected to server');
                this.socket?.emit('join', {
                    session_id: sessionId,
                    language: 'python'
                });
            });

            this.socket.on('json', this.handleServerMessage.bind(this));

            // Add handler for agent_up status
            this.registerHandler('status', (message: ServerMessage) => {
                if (message.status === 'agent_up' && message.session_id === sessionId && !initializeSent) {
                    console.log('Sending initialize');
                    initializeSent = true;
                    this.socket?.emit('json', {
                        session_id: sessionId,
                        event: 'initialize',
                        file_path: filePath
                    });
                } else if (message.status === 'ready' && message.session_id === sessionId) {
                    // Only resolve once we get the ready status after initialization
                    clearTimeout(timeout);
                    this.serverReady = true;
                    this.onStatusChange(this.serverReady);
                    resolve(sessionId);
                }
                this.serverReady = message.status === 'ready';
                this.onStatusChange(this.serverReady);
            });

            this.currentSession = {
                sessionId,
                filePath
            };
        });
    }

    private handleServerMessage(message: ServerMessage) {
        console.log('Received json:', message);
        
        // Call all registered handlers for this event type
        const handlers = this.messageHandlers.get(message.event);
        if (handlers) {
            handlers.forEach(handler => handler(message));
        }
    }

    registerHandler(event: string, handler: (message: any) => void) {
        if (!this.messageHandlers.has(event)) {
            this.messageHandlers.set(event, new Set());
        }
        this.messageHandlers.get(event)?.add(handler);
        console.log(`Registered handler for ${event}, total handlers:`, this.messageHandlers.get(event)?.size);
    }

    unregisterHandler(event: string, handler: (message: any) => void) {
        this.messageHandlers.get(event)?.delete(handler);
    }

    async closeSession() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = undefined;
        }
        this.currentSession = undefined;
        // Clear all handlers
        this.messageHandlers.clear();
    }

    emit(event: string, data: any) {
        if (this.socket && this.currentSession) {
            console.log('Emitting:', event, data);
            this.socket.emit('json', {
                session_id: this.currentSession.sessionId,
                event,
                ...data
            });
        } else {
            console.log('Cannot emit, no socket or session:', { socket: !!this.socket, session: !!this.currentSession });
        }
    }

    get isReady() { return this.serverReady; }
    get session() { return this.currentSession; }
} 