class SocketManager {
    constructor(sessionId, language) {
        this.sessionId = sessionId;
        this.language = language;
        this.socket = io();
        this.pendingRequests = 0;
        this.outputHandler = new OutputHandler();
        this.setupSocketListeners();
        this.setupEditorListeners();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => this.onConnect());
        this.socket.on('disconnect', () => this.onDisconnect());
        this.socket.on('json', (msg) => this.onMessage(msg));
    }

    setupEditorListeners() {
        document.addEventListener('editor:codeChange', (event) => {
            this.sendCode(event.detail);
        });
    }

    onConnect() {
        this.socket.emit('join', {
            session_id: this.sessionId,
            language: this.language
        });
        this.updateUIState({ loading: true, agentReady: false });
    }

    onDisconnect() {
        this.updateUIState({
            agentReady: false,
            loading: false
        });
    }

    onMessage(msg) {

        const handlers = {
            'codeChange': () => this.handleCodeChange(msg),
            'executeOutput': () => this.handleExecuteOutput(msg),
            'status': () => this.handleStatus(msg)
        };

        const handler = handlers[msg.event];
        if (handler) {
            handler();
        } else {
            console.warn('Unknown message event:', msg.event);
        }
    }

    handleCodeChange(msg) {
        window.editor.setValue(msg.code);
    }

    handleExecuteOutput(msg) {
        this.updateUIState({ loading: false });
        this.outputHandler.handleExecuteOutput(msg);
    }

    handleStatus(msg) {
        
        switch (msg.status) {
            case 'agent_up':
                this.pendingRequests = 0;
                this.updateUIState({
                    agentReady: true,
                    loading: false
                });
                this.sendCode({ code: window.editor.getValue() });
                break;

            case 'ready':
                this.pendingRequests = Math.max(0, this.pendingRequests - 1);
                if (this.pendingRequests === 0) {
                    this.updateUIState({ loading: false });
                }
                break;

            case 'timeout':
                this.updateUIState({ loading: false });
                M.toast({ html: 'Timeout, restarting...', displayLength: 3000 });
                break;

            case 'launching':
                this.updateUIState({ loading: true });
                break;

            case 'codeChange':
                // Code change status is just informational, no UI update needed
                console.log('Code change status received');
                break;

            case 'error':
                this.updateUIState({ loading: false });
                M.toast({ html: 'Error: ' + (msg.error || 'Unknown error'), displayLength: 5000 });
                console.error('Server error:', msg.error);
                break;

            default:
                console.warn('Unknown status:', msg.status);
        }
    }

    sendCode({ code, outputSelected = {} }) {
        this.pendingRequests++;
        this.updateUIState({ loading: true });
        
        this.socket.emit('json', {
            event: 'codeChange',
            session_id: this.sessionId,
            language: this.language,
            code,
            outputSelected
        });
    }

    updateUIState({ agentReady = null, loading = null }) {
        const spinner = document.getElementById('execution-spinner');
        const readyIcon = document.getElementById('agent-ready');
        const notReadyIcon = document.getElementById('agent-not-ready');

        if (loading !== null) {
            spinner.style.display = loading ? 'block' : 'none';
        }

        if (agentReady !== null) {
            readyIcon.style.display = agentReady ? 'block' : 'none';
            notReadyIcon.style.display = agentReady ? 'none' : 'block';
        }
    }
} 