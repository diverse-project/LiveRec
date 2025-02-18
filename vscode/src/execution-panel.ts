import * as vscode from 'vscode';
import { SessionManager } from './session-manager';
import { ExecutionData, ExecutionFrame } from './types';

export class ExecutionPanel {
    private panel: vscode.WebviewPanel | undefined;
    private decorations: vscode.TextEditorDecorationType[] = [];
    private messageHistory: string[] = [];
    private lastExecution: ExecutionData | null = null;

    constructor(private sessionManager: SessionManager) {
        this.sessionManager.registerHandler('executeOutput', (message) => {
            try {
                this.lastExecution = JSON.parse(message.output);
                this.updatePanel();
            } catch (error) {
                console.error('Error parsing execution output:', error);
                this.lastExecution = null;
            }
        });
    }

    create() {
        if (this.panel) {
            this.panel.reveal();
            return;
        }

        this.panel = vscode.window.createWebviewPanel(
            'liveFromDAPPanel',
            'LiveFromDAP',
            vscode.ViewColumn.Two,
            { enableScripts: true }
        );

        this.setupMessageHandling();
        this.updatePanel();

        this.panel.onDidDispose(() => {
            this.panel = undefined;
        });
    }

    private setupMessageHandling() {
        this.panel?.webview.onDidReceiveMessage(async message => {
            if (message.command === 'highlightFrame') {
                this.highlightFrame(message.frame);
            } else if (message.command === 'loadDataFile') {
                // Forward the command to VSCode
                vscode.commands.executeCommand('extension.loadDataFile');
            }
        });
    }

    private highlightFrame(frame: ExecutionFrame) {
        const session = this.sessionManager.session;
        if (!session) return;

        const targetEditor = vscode.window.visibleTextEditors.find(
            e => e.document.fileName === session.filePath
        );

        if (targetEditor) {
            this.decorations.forEach(d => d.dispose());
            this.decorations = [];

            const line = frame.pos.line - 1;
            const range = new vscode.Range(
                new vscode.Position(line, 0),
                new vscode.Position(line, Number.MAX_SAFE_INTEGER)
            );

            const decorationType = vscode.window.createTextEditorDecorationType({
                backgroundColor: 'rgba(255, 255, 0, 0.3)',
                isWholeLine: true
            });

            targetEditor.setDecorations(decorationType, [range]);
            this.decorations.push(decorationType);
            targetEditor.revealRange(range, vscode.TextEditorRevealType.InCenter);
        }
    }

    addToHistory(message: any) {
        if (message.event !== 'status') {
            this.messageHistory.push(JSON.stringify(message, null, 2));
            this.updatePanel();
        }
    }

    updatePanel() {
        if (!this.panel) return;
        this.panel.webview.html = this.generateHtml();
    }

    private generateHtml(): string {
        const styles = this.getStyles();
        const script = this.getScript();

        return `<!DOCTYPE html>
        <html>
        <head>
            ${styles}
            ${script}
        </head>
        <body>
            <div class="status">
                Server Status: 
                <span class="status-indicator ${this.sessionManager.isReady ? 'status-ready' : 'status-processing'}"></span>
                ${this.sessionManager.isReady ? 'Ready' : 'Processing...'}
            </div>

            <div class="action-section">
                <button class="action-button" onclick="loadDataFile()">
                    📂 Load Data File
                </button>
            </div>

            ${this.lastExecution ? this.generateExecutionSection() : ''}

            <div class="toggle-history" onclick="toggleHistory()">
                ▼ Toggle Message History
            </div>
            
            <div class="history-section">
                <h3>Message History</h3>
                ${this.messageHistory.map(msg => `
                    <div class="message">
                        <pre>${msg}</pre>
                    </div>
                `).join('')}
            </div>
        </body>
        </html>`;
    }

    private getStyles(): string {
        return `
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
                    background-color: ${this.sessionManager.isReady ? 'var(--vscode-terminal-ansiGreen)' : 'var(--vscode-terminal-ansiRed)'};
                }
                .stack-nav {
                    margin: 15px 0;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .stack-slider {
                    flex-grow: 1;
                }
                .frame-info {
                    margin: 10px 0;
                    padding: 10px;
                    background-color: var(--vscode-editorHoverWidget-background);
                }
                .highlight-line {
                    background-color: rgba(255, 255, 0, 0.3);
                    position: absolute;
                }
                .action-button {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    margin: 10px 0;
                }
                .action-button:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
                .action-section {
                    margin: 15px 0;
                    padding: 10px;
                    background-color: var(--vscode-sideBar-background);
                    border-radius: 4px;
                }
            </style>
        `;
    }

    private getScript(): string {
        return `
            <script>
                const vscode = acquireVsCodeApi();
                let currentFrameIndex = 0;
                const stacktrace = ${JSON.stringify(this.lastExecution?.stacktrace || [])};

                function updateFrame(index) {
                    currentFrameIndex = index;
                    document.getElementById('frame-counter').textContent = \`Frame \${index + 1} of \${stacktrace.length}\`;
                    document.getElementById('current-frame').innerHTML = formatFrame(stacktrace[index]);
                    
                    vscode.postMessage({
                        command: 'highlightFrame',
                        frame: stacktrace[index]
                    });
                }

                function formatFrame(frame) {
                    return \`
                        <div class="frame-header">Line \${frame.pos.line}</div>
                        \${frame.variables.length > 0 ? \`
                            <table class="variable-table">
                                \${frame.variables.map(v => \`
                                    <tr>
                                        <td class="var-name">\${v.name}</td>
                                        <td class="var-type">\${v.type}</td>
                                        <td class="var-value">\${v.value}</td>
                                    </tr>
                                \`).join('')}
                            </table>
                        \` : 'No variables in this frame'}
                        \${currentFrameIndex === stacktrace.length - 1 ? \`
                            <div class="return-value">Return value: \${stacktrace[currentFrameIndex].return_value}</div>
                        \` : ''}
                    \`;
                }

                function handleSliderChange() {
                    const slider = document.getElementById('stack-slider');
                    updateFrame(parseInt(slider.value));
                }

                function loadDataFile() {
                    vscode.postMessage({
                        command: 'loadDataFile'
                    });
                }
            </script>
        `;
    }

    private generateExecutionSection(): string {
        if (!this.lastExecution) return '';

        return `
            <div class="execution-section">
                <h3>Execution Trace</h3>
                <div class="stack-nav">
                    <input type="range" id="stack-slider" class="stack-slider" 
                           min="0" max="${this.lastExecution.stacktrace.length - 1}" 
                           value="0" oninput="handleSliderChange()">
                    <span id="frame-counter">Frame 1 of ${this.lastExecution.stacktrace.length}</span>
                </div>
                <div id="current-frame" class="frame-info">
                    ${this.formatExecution(this.lastExecution).replace('<div class="execution-output">', '')}
                </div>
            </div>
        `;
    }

    private formatExecution(data: ExecutionData): string {
        if (!data) return '';
        
        const formatVariables = (variables: Array<{ name: string; type: string; value: string }>) => `
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

        const formatStacktrace = (stack: ExecutionFrame[]) => `
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

    dispose() {
        this.decorations.forEach(d => d.dispose());
        this.panel?.dispose();
    }
} 