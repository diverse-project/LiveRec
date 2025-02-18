import * as vscode from 'vscode';
import { SessionManager } from './session-manager';
import { FunctionData } from './types';

export class ExecutionCodeLensProvider implements vscode.CodeLensProvider {
    private onDidChangeCodeLensesEmitter = new vscode.EventEmitter<void>();
    readonly onDidChangeCodeLenses = this.onDidChangeCodeLensesEmitter.event;
    private lastFunctions: Map<string, FunctionData[]> = new Map();
    private _hasLoadedData = false;

    constructor(private sessionManager: SessionManager) {
        // Register a persistent handler for functions data
        this.sessionManager.registerHandler('functions', (message) => {
            if (message.data) {
                console.log('Received new function data, updating cache');
                this.lastFunctions.set(this.sessionManager.session?.filePath || '', message.data);
                this._hasLoadedData = true;
                this.onDidChangeCodeLensesEmitter.fire();
            }
        });
    }

    async provideCodeLenses(document: vscode.TextDocument): Promise<vscode.CodeLens[]> {
        const codeLenses: vscode.CodeLens[] = [];
        
        if (this.sessionManager.session && this._hasLoadedData) {
            // Use cached data
            const functions = this.lastFunctions.get(document.fileName) || [];
            
            functions.forEach((fn) => {
                const line = document.lineAt(fn.line - 1);
                const range = new vscode.Range(
                    new vscode.Position(fn.line - 1, 0),
                    new vscode.Position(fn.line - 1, line.text.length)
                );

                const codeLens = new vscode.CodeLens(range, {
                    title: `📊 View Executions`,
                    command: 'extension.showExecutions',
                    arguments: [fn.name, fn.line]
                });
                
                codeLenses.push(codeLens);
            });
        }
        
        return codeLenses;
    }

    refresh() {
        this.onDidChangeCodeLensesEmitter.fire();
    }

    // Only manages the state, doesn't trigger requests
    setHasLoadedData(value: boolean) {
        this._hasLoadedData = value;
        this.refresh();
    }

    // Separate method to request function data
    requestFunctions(filePath: string) {
        if (this._hasLoadedData && this.sessionManager.session) {
            console.log('Requesting function data for:', filePath);
            this.sessionManager.emit('getFunctions', {
                file_path: filePath
            });
        }
    }

    get hasLoadedData(): boolean {
        return this._hasLoadedData;
    }
} 