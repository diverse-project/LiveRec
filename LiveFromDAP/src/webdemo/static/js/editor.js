class Editor {
    constructor(elementId, language) {
        this.language = language;
        this.highlightedLines = new Map();
        this.outputSelected = {};
        this.editor = this.initializeEditor(elementId);
        this.isStackExplorer = document.getElementById('stack') !== null;
        this.forLoopLines = new Set(); // Track lines involved in current for loop
        this.setupEventListeners();
    }

    getMode() {
        const modes = {
            'c': 'text/x-csrc',
            'java': 'text/x-java',
            'javascript': 'text/javascript',
            'go': 'text/x-go',
            'python': { name: 'python', version: 3, singleLineStringErrors: false },
            'pyjs': { name: 'python', version: 3, singleLineStringErrors: false }
        };
        return modes[this.language] || 'text/plain';
    }

    initializeEditor(elementId) {
        const editorArea = document.getElementById(elementId);
        return CodeMirror.fromTextArea(editorArea, {
            lineNumbers: true,
            indentUnit: 4,
            mode: this.getMode(),
            theme: 'default',
            autoCloseBrackets: true,
            matchBrackets: true,
            smartIndent: true,
            tabSize: 4,
            lineWrapping: true
        });
    }

    setupEventListeners() {
        this.editor.on('change', () => this.onEditorChange());
        this.editor.on('mousedown', (instance, event) => this.onEditorClick(event));
        CodeMirror.commands.save = () => this.onSave();
    }

    onEditorChange() {
        this.emit('codeChange', {
            code: this.getValue(),
            outputSelected: this.outputSelected
        });
    }

    onEditorClick(event) {
        const pos = this.editor.coordsChar({
            left: event.clientX,
            top: event.clientY
        });
        const lineContent = this.editor.getLine(pos.line).trim();
        
        // First check if we should keep the slider
        const shouldKeepSlider = this.shouldKeepSlider(pos.line);
        if (!shouldKeepSlider) {
            this.clearSlider();
        }

        // Clear only non-annotation highlights
        this.clearNonAnnotationHighlights();
        
        // If we kept the slider, restore the gutter markers
        if (shouldKeepSlider) {
            const forLoopLine = Array.from(this.forLoopLines).find(line => 
                this.editor.getLine(line).trim().startsWith('for')
            );
            this.forLoopLines.forEach(line => {
                const marker = this.makeGutterMarker(line === forLoopLine ? "●" : "○");
                this.editor.setGutterMarker(line, "CodeMirror-linenumbers", marker);
            });
        }
        
        if (this.isStackExplorer) {
            // For stack explorer, display stack for clicked line
            if (this.isForLoop(lineContent)) {
                this.handleForLoopClick(pos.line);
            } else if (this.isAnnotatedLine(lineContent)) {
                this.handleAnnotationClick(pos.line, lineContent);
            }
            this.displayStackByLine(pos.line + 1);
        } else {
            // Original DAP behavior
            if (this.isForLoop(lineContent)) {
                this.handleForLoopClick(pos.line);
            } else if (this.isAnnotatedLine(lineContent)) {
                this.handleAnnotationClick(pos.line, lineContent);
            }
        }
    }

    shouldKeepSlider(clickedLine) {
        // Check for slider by looking for the range input inside stack-range
        const stackRange = document.getElementById('stack-range');
        const slider = stackRange ? stackRange.querySelector('input[type="range"]') : null;
        if (!slider) return false;

        // If the line is part of our tracked for loop lines, keep the slider
        return this.forLoopLines.has(clickedLine);
    }

    isForLoop(line) {
        return line.startsWith('for');
    }

    isAnnotatedLine(line) {
        return line.startsWith('#@') || line.startsWith('//@');
    }

    handleForLoopClick(lineNumber) {
        // Process slider locally using stored output
        const lastOutput = window.socketManager.outputHandler.lastOutput;
        if (lastOutput) {
            try {
                const result = JSON.parse(lastOutput);
                let first = null;
                let last = null;
                
                // Clear previous for loop lines
                this.forLoopLines.clear();
                
                // First pass: find the bounds of the for loop execution
                for (let i = 0; i < result.stacktrace.length; i++) {
                    const frame = result.stacktrace[i];
                    if (frame.pos && frame.pos.line === lineNumber + 1) {
                        if (first === null) first = i;
                        last = i;
                    }
                }
                
                if (first !== null && last !== null) {
                    // Second pass: collect all lines that appear between first and last
                    const linesInExecution = new Set();
                    for (let i = first; i <= last; i++) {
                        const frame = result.stacktrace[i];
                        if (frame.pos) {
                            const frameLine = frame.pos.line - 1; // Convert to 0-based
                            linesInExecution.add(frameLine);
                        }
                    }
                    // Store only the lines involved in the for loop execution
                    this.forLoopLines = linesInExecution;
                    
                    // Add gutter markers only for lines involved in the execution
                    this.forLoopLines.forEach(line => {
                        const marker = this.makeGutterMarker(line === lineNumber ? "●" : "○");
                        this.editor.setGutterMarker(line, "CodeMirror-linenumbers", marker);
                    });
                    
                    // Create slider and set up frame highlighting
                    window.socketManager.outputHandler.addSlider(lineNumber, last - first, first, last, (frameIndex) => {
                        // Callback for slider movement
                        this.clearNonAnnotationHighlights();
                        
                        // Restore gutter markers
                        this.forLoopLines.forEach(line => {
                            const marker = this.makeGutterMarker(line === lineNumber ? "●" : "○");
                            this.editor.setGutterMarker(line, "CodeMirror-linenumbers", marker);
                        });
                        
                        // Highlight the current frame's line
                        const frame = result.stacktrace[frameIndex];
                        if (frame && frame.pos) {
                            const frameLine = frame.pos.line - 1; // Convert to 0-based
                            this.editor.markText(
                                { line: frameLine, ch: 0 },
                                { line: frameLine, ch: this.editor.getLine(frameLine).length },
                                { className: 'highlight-line' }
                            );
                        }
                    });
                }
            } catch (e) {
                console.error('Failed to process stacktrace:', e);
            }
        }
        
        if (typeof displayStackByLine !== 'undefined') {
            displayStackByLine(lineNumber + 1);
        }
    }

    handleAnnotationClick(lineNumber, lineContent) {
        const prefix = lineContent.startsWith('#@') ? '#@' : '//@';
        const funcData = this.parseAnnotation(lineContent, prefix);
        
        if (funcData) {
            this.updateHighlight(funcData, lineNumber, lineContent);
            this.emit('codeChange', {
                code: this.getValue(),
                outputSelected: this.outputSelected
            });
        }
    }

    parseAnnotation(line, prefix) {
        const content = line.replace(new RegExp('^' + prefix + '\\s*'), '');
        const match = content.match(/^([^(]+)\((.*)\)$/);
        
        if (match) {
            const [, func, argsStr] = match;
            const args = argsStr.match(/(?:[^,(){}[\]]+|\([^)]*\)|\{[^}]*\}|\[[^\]]*\])+/g) || [];
            return { func, args: args.map(arg => arg.trim()) };
        }
        return null;
    }

    updateHighlight(funcData, lineNumber, lineContent) {
        if (this.highlightedLines.has(funcData.func)) {
            this.clearHighlight(funcData.func);
        }
        
        this.highlightedLines.set(funcData.func, lineContent);
        this.outputSelected[funcData.func] = funcData.args;
        
        // Get the original line with potential whitespace
        const originalLine = this.editor.getLine(lineNumber);
        // Find where the actual content starts (first non-whitespace character)
        const startCh = originalLine.length - originalLine.trimLeft().length;
        // Calculate where the content ends
        const endCh = startCh + lineContent.length;
        
        this.editor.markText(
            { line: lineNumber, ch: startCh },
            { line: lineNumber, ch: endCh },
            { className: 'highlight-line' }
        );
    }

    clearHighlight(func) {
        const prevContent = this.highlightedLines.get(func);
        if (prevContent) {
            const lines = this.editor.lineCount();
            for (let i = 0; i < lines; i++) {
                const line = this.editor.getLine(i);
                if (line.trim() === prevContent) {
                    // Get the start position (first non-whitespace character)
                    const startCh = line.length - line.trimLeft().length;
                    // Calculate where the content ends
                    const endCh = startCh + prevContent.length;
                    
                    const marks = this.editor.findMarks(
                        { line: i, ch: startCh },
                        { line: i, ch: endCh }
                    );
                    marks.forEach(mark => mark.clear());
                }
            }
        }
    }

    clearSlider() {
        const stackRange = document.getElementById('stack-range');
        if (stackRange) {
            stackRange.innerHTML = '';
        }
        // Clear the tracked for loop lines
        this.forLoopLines.clear();
        if (typeof displayStackByLine !== 'undefined') {
            displayStackByLine(this.editor.getCursor().line + 1);
        }
    }

    getValue() {
        return this.editor.getValue();
    }

    setValue(code) {
        this.editor.setValue(code);
    }

    emit(event, data) {
        const customEvent = new CustomEvent('editor:' + event, {
            detail: { ...data, language: this.language }
        });
        document.dispatchEvent(customEvent);
    }

    displayStackByLine(lineNumber) {
        // Find and display corresponding stack frame from last available output
        if (window.socketManager && window.socketManager.outputHandler) {
            const handler = window.socketManager.outputHandler;
            if (!handler.lastOutput) {
                // No output yet from server, don't do anything
                return;
            }
            
            try {
                const result = JSON.parse(handler.lastOutput);
                if (result && result.stacktrace) {
                    // Find the first frame matching this line
                    const frame = result.stacktrace.find(f => f.pos && f.pos.line === lineNumber);
                    if (frame) {
                        // Only highlight and show frame if we found a matching frame
                        this.clearNonAnnotationHighlights();
                        this.editor.markText(
                            { line: lineNumber - 1, ch: 0 },
                            { line: lineNumber - 1, ch: this.editor.getLine(lineNumber - 1).length },
                            { className: 'highlight-line' }
                        );
                        handler.displayStackExplorerFrame(frame);
                    } else {
                        // Clear the stack display if no frame found for this line
                        handler.clearStackDisplay();
                    }
                }
            } catch (e) {
                // Invalid JSON or no stacktrace yet
                console.log('No valid stacktrace data available');
            }
        }
    }

    clearNonAnnotationHighlights() {
        const marks = this.editor.getAllMarks();
        marks.forEach(mark => {
            // Check if this mark is for an annotation
            const isAnnotationMark = Array.from(this.highlightedLines.values()).some(content => {
                const pos = mark.find();
                if (!pos) return false;
                const lineContent = this.editor.getLine(pos.from.line).trim();
                return lineContent === content;
            });
            
            if (!isAnnotationMark) {
                mark.clear();
            }
        });
        
        // Clear gutter markers
        const lineCount = this.editor.lineCount();
        for (let i = 0; i < lineCount; i++) {
            this.editor.setGutterMarker(i, "CodeMirror-linenumbers", null);
        }
    }

    makeGutterMarker(text) {
        const marker = document.createElement("div");
        marker.style.color = "#f0c674"; // Same color as highlight-line
        marker.style.position = "relative";
        marker.style.display = "inline-block";
        marker.style.width = "100%";
        
        // Create the line number span
        const lineNumber = document.createElement("span");
        lineNumber.style.color = "#666"; // Default line number color
        lineNumber.style.display = "inline-block";
        lineNumber.style.width = "calc(100% - 12px)"; // Leave space for marker
        lineNumber.style.textAlign = "right";
        lineNumber.style.paddingRight = "4px";
        
        // Create the marker span
        const markerSpan = document.createElement("span");
        markerSpan.style.position = "absolute";
        markerSpan.style.right = "-4px";
        markerSpan.style.top = "0";
        markerSpan.innerHTML = text;
        
        marker.appendChild(lineNumber);
        marker.appendChild(markerSpan);
        
        // Set the line number directly using the DOM
        const gutterElement = marker.closest('.CodeMirror-linenumber');
        if (gutterElement) {
            lineNumber.textContent = gutterElement.textContent;
        }
        
        return marker;
    }
} 