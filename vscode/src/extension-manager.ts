import * as vscode from 'vscode';
import { SessionManager } from './session-manager';
import { ExecutionPanel } from './execution-panel';
import { ExecutionCodeLensProvider } from './codelens-provider';

export class ExtensionManager {
    private sessionManager: SessionManager;
    private panel: ExecutionPanel;
    private codeLensProvider: ExecutionCodeLensProvider;

    constructor(private context: vscode.ExtensionContext) {
        this.sessionManager = new SessionManager((ready) => this.panel?.updatePanel());
        this.codeLensProvider = new ExecutionCodeLensProvider(this.sessionManager);
        this.panel = new ExecutionPanel(this.sessionManager);

        // Register handler for agent_up status to load data file after session is initialized
        this.sessionManager.registerHandler('status', async (message) => {
            if (message.status === 'agent_up' && this.sessionManager.session) {
                // Check for data.jsonl in workspace root and load it if it exists
                const workspaceRoot = vscode.workspace.getWorkspaceFolder(vscode.Uri.file(this.sessionManager.session.filePath))?.uri.fsPath;
                if (workspaceRoot) {
                    console.log('Workspace root:', workspaceRoot);
                    const dataFilePath = vscode.Uri.joinPath(vscode.Uri.file(workspaceRoot), 'data.jsonl');
                    try {
                        await vscode.workspace.fs.stat(dataFilePath);
                        // File exists, load it
                        console.log('Found data.jsonl at:', dataFilePath.fsPath);
                        // Register handler before emitting loadFile
                        this.sessionManager.registerHandler('functions', (message) => {
                            console.log('Initial data load response:', message);
                            this.handleDataLoaded(message);
                        });
                        this.sessionManager.emit('loadFile', {
                            file_path: dataFilePath.fsPath
                        });
                        vscode.window.showInformationMessage('Loading data.jsonl...');
                    } catch (error) {
                        console.log('No data.jsonl found in workspace:', error);
                    }
                } else {
                    console.log('No workspace root found');
                }
            }
        });
    }

    private handleDataLoaded(message: any) {
        console.log('Received functions:', message.data);
        if (message.data && message.data.length > 0) {
            vscode.window.showInformationMessage(`Loaded ${message.data.length} functions from data file`);
        } else {
            vscode.window.showInformationMessage('No function executions found in data file');
        }
        // Only set the state, don't trigger another request
        this.codeLensProvider.setHasLoadedData(true);
    }

    async handleActiveEditor(editor: vscode.TextEditor) {
        console.log('handleActiveEditor called for:', editor.document.fileName);
        if (editor.document.languageId !== 'python') {
            console.log('Not a Python file, ignoring');
            return;
        }

        try {
            const currentSession = this.sessionManager.session;
            if (!currentSession || currentSession.filePath !== editor.document.fileName) {
                console.log('Creating new session for:', editor.document.fileName);
                if (currentSession) {
                    await this.sessionManager.closeSession();
                }

                // Reset data loading state when switching files
                this.codeLensProvider.setHasLoadedData(false);
                
                // Wait for session to be fully initialized before proceeding
                await this.sessionManager.initSession(editor.document.fileName);
                console.log('Session initialized successfully');
                this.panel.create();
                
                // Now that we have a fully initialized session, process the file
                await this.processFile(editor.document.getText());
            } else {
                console.log('Using existing session');
                // If we have a session and data is loaded, request functions
                if (this.codeLensProvider.hasLoadedData) {
                    this.codeLensProvider.requestFunctions(editor.document.fileName);
                }
                await this.processFile(editor.document.getText());
            }
        } catch (error: any) {
            console.error('Error in handleActiveEditor:', error);
            vscode.window.showErrorMessage(`Failed to initialize session: ${error.message}`);
        }
    }

    private async processFile(content: string) {
        this.sessionManager.emit('codeChange', { code: content });
    }

    registerCommands() {
        // Register command to show executions
        this.context.subscriptions.push(
            vscode.commands.registerCommand('extension.showExecutions', 
                this.handleShowExecutions.bind(this))
        );

        // Register command to load data file
        this.context.subscriptions.push(
            vscode.commands.registerCommand('extension.loadDataFile', 
                this.handleLoadDataFile.bind(this))
        );

        // Register editor change handlers
        this.context.subscriptions.push(
            vscode.window.onDidChangeActiveTextEditor(editor => {
                if (editor) {
                    this.handleActiveEditor(editor).catch(console.error);
                }
            }),
            vscode.workspace.onDidSaveTextDocument(document => { // Normally on change document for later
                const session = this.sessionManager.session;
                if (document.languageId === 'python' && 
                    session?.filePath === document.fileName) {
                    this.processFile(document.getText()).catch(console.error);
                }
            })
        );

        // Register CodeLens provider
        this.context.subscriptions.push(
            vscode.languages.registerCodeLensProvider(
                { language: 'python' }, 
                this.codeLensProvider
            )
        );

        // Register context menu contribution
        this.context.subscriptions.push(
            vscode.commands.registerCommand('extension.loadDataFileFromContext', 
                (uri: vscode.Uri) => this.handleLoadDataFile(uri.fsPath))
        );
    }

    private async handleShowExecutions(functionName: string, lineNumber: number) {
        if (!this.sessionManager.session) return;

        this.sessionManager.emit('getFunctionData', {
            file_path: this.sessionManager.session.filePath,
            functionName: functionName
        });

        const executions = await new Promise<any[]>((resolve) => {
            this.sessionManager.registerHandler('functionData', (message) => {
                resolve(message.data);
            });
        });

        const items = executions.map(exec => ({
            label: `Args: ${JSON.stringify(exec.args)}`,
            description: `Return: ${exec.return}`,
            detail: `Called at ${new Date(exec.timestamp).toLocaleString()}`,
            functionName: functionName,
            args: exec.args
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: `Select execution of ${functionName} to inspect`
        });

        if (selected) {
            this.sessionManager.emit('selectExecution', {
                functionName: selected.functionName,
                args: selected.args
            });
        }
    }

    private async handleLoadDataFile(filePath?: string) {
        console.log('handleLoadDataFile called with:', filePath);
        if (!this.sessionManager.session) {
            vscode.window.showErrorMessage('No active session. Please open a Python file first.');
            return;
        }

        let selectedPath = filePath;
        
        if (!selectedPath) {
            const result = await vscode.window.showOpenDialog({
                canSelectFiles: true,
                canSelectFolders: false,
                canSelectMany: false,
                filters: {
                    'Data Files': ['jsonl']
                },
                title: 'Select Data File to Load'
            });

            if (!result || result.length === 0) {
                console.log('No file selected');
                return;
            }

            selectedPath = result[0].fsPath;
        }

        // Verify it's a .jsonl file
        if (!selectedPath.toLowerCase().endsWith('.jsonl')) {
            vscode.window.showErrorMessage('Only .jsonl files are supported.');
            return;
        }

        console.log('Loading data file:', selectedPath);
        vscode.window.showInformationMessage('Loading data file...');
        
        // Reset data loading state before loading new file
        this.codeLensProvider.setHasLoadedData(false);
        
        // Register handler before emitting loadFile
        this.sessionManager.registerHandler('functions', (message) => {
            console.log('Manual data load response:', message);
            this.handleDataLoaded(message);
        });
        
        this.sessionManager.emit('loadFile', {
            file_path: selectedPath
        });
    }

    dispose() {
        this.panel.dispose();
        this.sessionManager.closeSession();
    }
} 