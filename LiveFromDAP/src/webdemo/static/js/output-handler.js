class OutputHandler {
    constructor() {
        this.lastOutput = null;
        this.isStackExplorer = document.getElementById('stack') !== null;
        
        if (this.isStackExplorer) {
            this.setupStackExplorer();
        } else {
            this.setupDAPOutput();
        }
    }

    setupDAPOutput() {
        this.outputArea = document.getElementById('output');
        // Initialize CodeMirror for output
        this.output = CodeMirror.fromTextArea(this.outputArea, {
            lineNumbers: false,
            readOnly: true,
            mode: 'text',
            theme: 'default',
            lineWrapping: true,
            matchBrackets: true,
            scrollbarStyle: 'null',  // Hide scrollbars
            firstLineNumber: 1
        });

        // Match the font and size with the editor
        this.output.getWrapperElement().style.height = '100%';
        this.output.getWrapperElement().style.fontSize = '14px';
        this.output.getWrapperElement().style.fontFamily = "'Fira Code', monospace";
        
        // One-way scroll sync from editor to output
        const editor = window.editor.editor;
        this.syncScroll = () => {
            const scrollInfo = editor.getScrollInfo();
            const ratio = scrollInfo.top / (scrollInfo.height - scrollInfo.clientHeight);
            const outputScrollInfo = this.output.getScrollInfo();
            const targetScroll = ratio * (outputScrollInfo.height - outputScrollInfo.clientHeight);
            this.output.scrollTo(null, targetScroll);
        };

        editor.on('scroll', this.syncScroll);
        editor.on('change', () => {
            // Wait for CodeMirror to update its internal state
            setTimeout(() => {
                this.normalizeLineCount();
                this.syncScroll();
            }, 0);
        });

        // Disable mouse wheel scrolling on output
        this.output.getWrapperElement().addEventListener('wheel', (e) => {
            e.preventDefault();
        }, { passive: false });

        this.output.refresh();
    }

    setupStackExplorer() {
        this.stackTitle = document.getElementById('stack-title');
        this.stackVars = document.getElementById('stack-var');
        this.stackRange = document.getElementById('stack-range');
        // Initialize with empty state
        this.clearStackDisplay();
    }

    clearStackDisplay() {
        if (this.isStackExplorer) {
            this.stackTitle.textContent = 'No stack frame for this line';
            this.stackVars.innerHTML = '';
            this.stackRange.innerHTML = '';
        }
    }

    handleExecuteOutput(msg) {
        if (!msg.output) {
            if (!this.isStackExplorer) {
                this.setOutputAndSync('');
            }
            return;
        }

        // Store the raw output
        this.lastOutput = msg.output;

        // Try to parse as JSON first
        try {
            const result = JSON.parse(msg.output);
            this.displayOutput(result);
        } catch (e) {
            // If not JSON, display as plain text
            if (!this.isStackExplorer) {
                this.setOutputAndSync(msg.output);
            }
        }
    }

    displayOutput(result) {
        if (result.stacktrace) {
            if (this.isStackExplorer) {
                this.displayStackExplorerFrame(result.stacktrace[0]);
            } else {
                this.displayStackTrace(result.stacktrace);
            }
        } else if (result.stdout) {
            if (!this.isStackExplorer) {
                this.setOutputAndSync(result.stdout);
            }
        } else {
            if (!this.isStackExplorer) {
                this.setOutputAndSync(JSON.stringify(result, null, 2));
            }
        }
    }

    displayStackExplorerFrame(frame) {
        if (!frame) {
            this.clearStackDisplay();
            return;
        }

        const pos = frame.pos || {};
        const variables = frame.variables || [];
        
        // Update title
        this.stackTitle.textContent = `StackFrame #${frame.index || 1} (line ${pos.line || '?'}, height ${frame.height || '?'})`;
        
        // Update variables
        if (variables.length > 0) {
            this.stackVars.innerHTML = variables
                .map(v => `<li>${v.name} = ${v.value}${v.type ? ` (${v.type})` : ''}</li>`)
                .join('');
        } else {
            this.stackVars.innerHTML = '<li>No variables in this frame</li>';
        }
    }

    setOutputAndSync(content) {
        // Clear previous marks
        this.clearMarks();
        
        // Get old content for diff
        const oldContent = this.output.getValue();
        const oldLines = oldContent.split('\n');
        
        // Set new content
        this.output.setValue(content);
        this.normalizeLineCount();
        
        // Compare and highlight changes
        const newLines = this.output.getValue().split('\n');
        for (let i = 0; i < newLines.length; i++) {
            if (newLines[i] !== oldLines[i] && newLines[i].trim() !== '') {
                this.markLine(i);
            }
        }
        
        this.output.refresh();
        // Wait for CodeMirror to update before syncing scroll
        setTimeout(() => this.syncScroll(), 0);
    }

    clearMarks() {
        const marks = this.output.getAllMarks();
        marks.forEach(mark => mark.clear());
    }

    markLine(line) {
        const lineContent = this.output.getLine(line);
        if (lineContent !== undefined && lineContent.trim()) {
            this.output.markText(
                { line, ch: 0 },
                { line, ch: lineContent.length },
                { className: 'changed-line' }
            );
        }
    }

    normalizeLineCount() {
        const editor = window.editor.editor;
        const editorLineCount = editor.lineCount();
        const outputContent = this.output.getValue();
        const outputLines = outputContent.split('\n');
        
        if (outputLines.length < editorLineCount) {
            // Add empty lines to match editor
            const newLines = Array(editorLineCount - outputLines.length).fill('');
            outputLines.push(...newLines);
            this.output.setValue(outputLines.join('\n'));
        } else if (outputLines.length > editorLineCount) {
            // Cut extra lines from output
            outputLines.length = editorLineCount;
            this.output.setValue(outputLines.join('\n'));
        }
    }

    displayStackTrace(stacktrace) {
        let output = '';
        for (const frame of stacktrace) {
            const pos = frame.pos || {};
            const vars = frame.vars || {};
            
            output += `Line ${pos.line || '?'}: ${frame.name || 'unknown'}\n`;
            
            // Display variables
            for (const [name, value] of Object.entries(vars)) {
                output += `  ${name} = ${value}\n`;
            }
            
            output += '\n';
        }
        
        this.setOutputAndSync(output);
    }

    displayStackFrame(index) {
        try {
            // Try to parse as JSON first
            const result = JSON.parse(this.lastOutput);
            if (result.stacktrace && result.stacktrace[index]) {
                const frame = result.stacktrace[index];
                let output = `Line ${frame.pos?.line || '?'}: ${frame.name || 'unknown'}\n`;
                
                if (frame.vars) {
                    for (const [name, value] of Object.entries(frame.vars)) {
                        output += `  ${name} = ${value}\n`;
                    }
                }
                
                this.setOutputAndSync(output);
            }
        } catch (e) {
            // If not JSON, try to display the relevant section of plain text
            const lines = this.lastOutput.split('\n');
            if (lines.length > index) {
                this.setOutputAndSync(lines[index]);
            }
        }
    }

    addSlider(lineNumber, length, start, end, onSliderMove) {
        if (!this.isStackExplorer) {
            // Original slider code for DAP view
            const sliderContainer = document.createElement('div');
            sliderContainer.id = 'slider';
            sliderContainer.className = 'slider-container';
            
            const slider = document.createElement('input');
            slider.type = 'range';
            slider.min = start;
            slider.max = end;
            slider.value = start;
            slider.className = 'slider-input';
            
            const label = document.createElement('div');
            label.textContent = `Iteration ${start}/${end}`;
            
            slider.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                label.textContent = `Iteration ${value}/${end}`;
                this.displayStackFrame(value);
                if (onSliderMove) {
                    onSliderMove(value);
                }
            });
            
            sliderContainer.appendChild(label);
            sliderContainer.appendChild(slider);
            
            // Remove any existing slider
            const oldSlider = document.getElementById('slider');
            if (oldSlider) {
                oldSlider.remove();
            }
            
            // Add the new slider
            document.getElementById('editor-container').appendChild(sliderContainer);
            
            // Call the callback for initial position
            if (onSliderMove) {
                onSliderMove(start);
            }
        } else {
            // Stack explorer slider
            this.stackRange.innerHTML = `
                <input type="range" min="${start}" max="${end}" value="${start}" />
                <span>Iteration ${start}/${end}</span>
            `;
            
            const slider = this.stackRange.querySelector('input');
            const label = this.stackRange.querySelector('span');
            
            slider.addEventListener('input', (e) => {
                const value = parseInt(e.target.value);
                label.textContent = `Iteration ${value}/${end}`;
                try {
                    const result = JSON.parse(this.lastOutput);
                    if (result.stacktrace && result.stacktrace[value]) {
                        this.displayStackExplorerFrame(result.stacktrace[value]);
                        if (onSliderMove) {
                            onSliderMove(value);
                        }
                    }
                } catch (e) {
                    console.error('Failed to parse stacktrace:', e);
                }
            });
            
            // Call the callback for initial position
            if (onSliderMove) {
                onSliderMove(start);
            }
        }
    }
} 