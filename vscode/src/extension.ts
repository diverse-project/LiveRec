import * as vscode from 'vscode';
import { ExtensionManager } from './extension-manager';

export function activate(context: vscode.ExtensionContext) {
    console.log("Starting extension");

    const extensionManager = new ExtensionManager(context);
    extensionManager.registerCommands();

    // Initial setup
    if (vscode.window.activeTextEditor) {
        extensionManager.handleActiveEditor(vscode.window.activeTextEditor)
            .catch(error => console.error('Error in initial setup:', error));
    }

    // Cleanup on deactivation
    context.subscriptions.push({ dispose: () => extensionManager.dispose() });
}

export function deactivate() {}