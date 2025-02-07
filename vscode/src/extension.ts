import * as vscode from 'vscode';
import { io, Socket } from 'socket.io-client';
import axios from 'axios';

const SERVER_PORT = 5000;
const SERVER_URL = `http://localhost:${SERVER_PORT}`;

// Add secondary http server
const HTTP_SERVER_PORT = 5001;
const HTTP_SERVER_URL = `http://localhost:${HTTP_SERVER_PORT}/api`;

interface FileSession {
    sessionId: string;
    filePath: string;
}

class ExecutionCodeLensProvider implements vscode.CodeLensProvider {
    async provideCodeLenses(document: vscode.TextDocument): Promise<vscode.CodeLens[]> {
        const codeLenses: vscode.CodeLens[] = [];
        
        try {
            const response = await axios.get(`${HTTP_SERVER_URL}/functions`, {
                params: { filePath: document.fileName }
            });

            response.data.forEach((fn: { name: string; line: number; count: number }) => {
                const line = document.lineAt(fn.line - 1);
                const range = new vscode.Range(
                    new vscode.Position(fn.line - 1, 0),
                    new vscode.Position(fn.line - 1, line.text.length)
                );

                const codeLens = new vscode.CodeLens(range, {
                    title: `📊 View Executions (${fn.count})`,
                    command: 'extension.showExecutions',
                    arguments: [fn.name, fn.line]
                });
                
                codeLenses.push(codeLens);
            });
        } catch (error) {
            console.error('Error fetching functions:', error);
        }
        
        return codeLenses;
    }
}

export function activate(context: vscode.ExtensionContext) {
    let currentPanel: vscode.WebviewPanel | undefined = undefined;
    let currentSession: FileSession | undefined = undefined;
    let socket: Socket | undefined = undefined;
    let messageHistory: Array<string> = [];
    let serverReady = true;
    let lastExecution: any = null;

    console.log("Starting exte2");

    async function initSession(filePath: string): Promise<string> {
        console.log(`Initializing session for file: ${filePath}`);
        const sessionId = crypto.randomUUID();
        
        socket = io(SERVER_URL);
        
        socket.on('connect', () => {
            console.log('Connected to server');
            socket?.emit('join', {
                session_id: sessionId,
                language: 'python'
            });
        });

        socket.on('json', (message) => {
            console.log('Received json:', message);
            
            // Store raw message only if it's not a status message
            if (message.event !== 'status') {
                messageHistory.push(JSON.stringify(message, null, 2));
            }
            
            if (message.event === 'status') {
                serverReady = message.status === 'ready';
                console.log(`Server status updated to: ${message.status}`);
            }
            else if (message.event === 'executeOutput') {
                try {
                    lastExecution = JSON.parse(message.output);
                } catch (error) {
                    console.error('Error parsing execution output:', error);
                    lastExecution = null;
                }
            }

            if (currentPanel) {
                updatePanelContent(currentPanel);
            }
        });

        return sessionId;
    }

    async function closeSession(sessionId: string) {
        console.log(`Closing session: ${sessionId}`);
        if (socket) {
            socket.disconnect();
            socket = undefined;
        }
    }

    async function processFile(sessionId: string, content: string) {
        console.log(`Processing file for session: ${sessionId}`);
        serverReady = false;
        socket?.emit('json', {
            session_id: sessionId,
            event: 'codeChange',
            code: content
        });
        if (currentPanel) {
            updatePanelContent(currentPanel);
        }
    }

    const createPanel = () => {
        console.log('Creating webview panel...');
        if (currentPanel) {
            currentPanel.reveal();
            return;
        }

        currentPanel = vscode.window.createWebviewPanel(
            'liveFromDAPPanel',
            'LiveFromDAP',
            vscode.ViewColumn.Two,
            {
                enableScripts: true
            }
        );

        messageHistory = [];
        updatePanelContent(currentPanel);

        currentPanel.onDidDispose(
            () => {
                currentPanel = undefined;
            },
            null,
            context.subscriptions
        );
    };

    async function handleActiveEditor(editor: vscode.TextEditor) {
        console.log('Handling active editor...');
        if (editor.document.languageId !== 'python') {
            return;
        }

        // Only create new session if it's a different file
        if (!currentSession || currentSession.filePath !== editor.document.fileName) {
            // Close previous session if exists
            if (currentSession) {
                await closeSession(currentSession.sessionId);
            }

            // Init new session
            const sessionId = await initSession(editor.document.fileName);
            currentSession = {
                sessionId,
                filePath: editor.document.fileName
            };

            createPanel();
        }
        
        await processCurrentFile();
    }

    async function processCurrentFile() {
        console.log('Processing current file...');
        const editor = vscode.window.activeTextEditor;
        if (!editor || !currentSession || editor.document.fileName !== currentSession.filePath) {
            return;
        }

        try {
            await processFile(currentSession.sessionId, editor.document.getText());
        } catch (error) {
            console.error('Error processing file:', error);
        }
    }

    // Update initialization
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(async (editor) => {
            if (editor) {
                try {
                    await handleActiveEditor(editor);
                } catch (error) {
                    console.error('Error handling editor:', error);
                }
            }
        }),
        vscode.workspace.onDidChangeTextDocument(async (event) => {
            if (event.document.languageId === 'python' && currentSession?.filePath === event.document.fileName) {
                try {
                    await processCurrentFile();
                } catch (error) {
                    console.error('Error processing file change:', error);
                }
            }
        })
    );

    // Initial setup
    (async () => {
        if (vscode.window.activeTextEditor) {
            try {
                await handleActiveEditor(vscode.window.activeTextEditor);
            } catch (error) {
                console.error('Error in initial setup:', error);
            }
        }
    })();

    context.subscriptions.push({
        dispose: async () => {
            if (currentSession) {
                await closeSession(currentSession.sessionId);
            }
        }
    });

    function updatePanelContent(panel: vscode.WebviewPanel) {
        const styles = `
            <style>
                body {
                    color: var(--vscode-editor-foreground);
                    background-color: var(--vscode-editor-background);
                    padding: 10px;
                }
                .execution-output {
                    margin: 15px 0;
                    padding: 10px;
                    background-color: var(--vscode-sideBar-background);
                    border: 1px solid var(--vscode-editorWidget-border);
                    border-radius: 4px;
                }
                .variable-table {
                    width: 100%;
                    margin: 10px 0;
                    border-collapse: collapse;
                }
                .variable-table td {
                    padding: 4px 8px;
                    border: 1px solid var(--vscode-editor-lineHighlightBorder);
                }
                .var-name { 
                    font-weight: 500; 
                    color: var(--vscode-symbolIcon-variableForeground);
                }
                .var-type { 
                    color: var(--vscode-descriptionForeground);
                }
                .var-value {
                    color: var(--vscode-editor-foreground);
                }
                .stack-frame {
                    margin: 10px 0;
                    padding: 10px;
                    background-color: var(--vscode-editorHoverWidget-background);
                }
                .frame-header {
                    font-weight: 500;
                    margin-bottom: 8px;
                    color: var(--vscode-editor-foreground);
                }
                .return-value {
                    color: var(--vscode-terminal-ansiGreen);
                    margin-bottom: 10px;
                }
                .status-indicator {
                    background-color: ${serverReady ? 'var(--vscode-terminal-ansiGreen)' : 'var(--vscode-terminal-ansiRed)'};
                }
            </style>
        `;

        panel.webview.html = `<!DOCTYPE html>
        <html>
        <head>
            ${styles}
            <script>
                function toggleHistory() {
                    document.body.classList.toggle('show-history');
                }
            </script>
        </head>
        <body>
            <div class="status">
                Server Status: 
                <span class="status-indicator ${serverReady ? 'status-ready' : 'status-processing'}"></span>
                ${serverReady ? 'Ready' : 'Processing...'}
            </div>

            ${lastExecution ? `
            <div class="execution-section">
                <h3>Last Execution</h3>
                ${formatExecution(lastExecution)}
            </div>
            ` : ''}

            <div class="toggle-history" onclick="toggleHistory()">
                ▼ Toggle Message History
            </div>
            
            <div class="history-section">
                <h3>Message History</h3>
                ${messageHistory.map(msg => `
                    <div class="message">
                        <pre>${msg}</pre>
                    </div>
                `).join('')}
            </div>
        </body>
        </html>`;
    }

    function formatExecution(data: any): string {
        if (!data) return '';
        
        const formatVariables = (variables: any[]) => `
            <table class="variable-table">
                ${variables.map(v => `
                    <tr>
                        <td class="var-name">${v.name}</td>
                        <td class="var-type">${v.type}</td>
                        <td class="var-value">${v.value}</td>
                    </tr>
                `).join('')}
            </table>
        `;

        const formatStacktrace = (stack: any[]) => `
            <div class="stacktrace">
                ${stack.map((frame, i) => `
                    <div class="stack-frame">
                        <div class="frame-header">Step ${i + 1} (Line ${frame.pos?.line})</div>
                        ${formatVariables(frame.variables)}
                    </div>
                `).join('')}
            </div>
        `;

        return `
            <div class="execution-output">
                <div class="return-value">Return value: ${data.return_value}</div>
                ${data.stacktrace ? formatStacktrace(data.stacktrace) : ''}
            </div>
        `;
    }


    // Live Data Part

    let currentDecorations: vscode.TextEditorDecorationType[] = [];
    let statusBarItem: vscode.StatusBarItem;

    // Create status bar item for execution selection
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'extension.selectExecution';
    context.subscriptions.push(statusBarItem);

    // Register command for selecting executions
    let disposable = vscode.commands.registerCommand('extension.selectExecution', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return;

        try {
            const response = await axios.get(`${HTTP_SERVER_URL}/executions`, {
                params: { filePath: editor.document.fileName }
            });
            
            const items = response.data.map((exec: any) => ({
                label: exec.functionName,
                description: `Args: ${exec.args.join(', ')}; Return: ${exec.return}`
            }));

            const selected = await vscode.window.showQuickPick(items);
            console.log(selected, typeof selected);
            if (selected) {
                socket?.emit('json', {
                    session_id: currentSession?.sessionId,
                    event: 'selectExecution',
                    functionName: "selected.label",
                    args: "selected.description"
                });
                // Now TypeScript knows selected is a QuickPickItem with executionId
                vscode.window.showInformationMessage(`Selected execution: ${selected}, ${typeof selected}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage('Error fetching executions');
        }
    });

    context.subscriptions.push(disposable);

    // Register CodeLens provider
    const codeLensProvider = new ExecutionCodeLensProvider();
    context.subscriptions.push(
        vscode.languages.registerCodeLensProvider(
            { language: 'python' }, 
            codeLensProvider
        )
    );

    // Register command to show executions
    context.subscriptions.push(
        vscode.commands.registerCommand('extension.showExecutions', async (functionName: string, lineNumber: number) => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;

            try {
                const response = await axios.get(`${HTTP_SERVER_URL}/executions`, {
                    params: { 
                        filePath: editor.document.fileName,
                        functionName: functionName,
                        line: lineNumber
                    }
                });

                const items = response.data.map((exec: any) => ({
                    label: `Args: ${Object.entries(exec.args).map(([k, v]) => `${k}=${v}`).join(', ')}`,
                    description: `Return: ${exec.return}`,
                    detail: `Called at ${new Date(exec.timestamp).toLocaleString()}, ${exec.exec_time}s`,
                    functionName: exec.functionName,
                    args: exec.args
                }));

                const selected = await vscode.window.showQuickPick(items, {
                    placeHolder: `Select execution of ${functionName} to inspect`
                });

                if (selected) {
                    // Now we can access the QuickPickItem properties
                    socket?.emit('json', {
                        session_id: currentSession?.sessionId,
                        event: 'selectExecution',
                        functionName: selected.functionName,
                        args: JSON.stringify(selected.args)
                    });
                    vscode.window.showInformationMessage(`Selected execution ${selected.functionName}`);
                }
            } catch (error) {
                vscode.window.showErrorMessage('Error fetching executions');
            }
        })
    );

    // Refresh CodeLens when document changes
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(document => {
            if (document.languageId === 'python') {
                codeLensProvider.provideCodeLenses(document);
            }
        })
    );
}

export function deactivate() {}