var editorArea = document.getElementById('editor');

var CodeMirror_mode = "";
if (language=="c"){
    CodeMirror_mode = "text/x-csrc";
}
if (language=="java"){
    CodeMirror_mode = "text/x-java";
}
if (language=="javascript"){
    CodeMirror_mode = "text/javascript";
}
if (language=="python" || language=="pyjs"){
    CodeMirror_mode = {name: "python",
        version: 3,
        singleLineStringErrors: false};
}

var editor = CodeMirror.fromTextArea(editorArea, {
    lineNumbers: true,
    indentUnit: 4,
    mode: CodeMirror_mode
});


var socket = io();

var send_code_sent = 0;



socket.on('json', function(msg) {
    if (msg.event == 'codeChange') {
        editor.setValue(msg.code);
        return;
    }
    if (msg.event == 'executeOutput') {
        handle_executeOutput(msg);
        return;
    }
    if (msg.event == 'status') {
        console.log(msg.status);
        //M.toast({html: msg.status, displayLength: 3000});
        if (msg.status == "agent_up") {
            send_code_sent = 0;
            document.getElementById("agent-ready").style.display = "block";
            document.getElementById("agent-not-ready").style.display = "none";
            document.getElementById("execution-spinner").style.display = "none";
            sendCode();
        }
        if (msg.status == "ready") {
            send_code_sent -= 1;
            if (send_code_sent == 0) {
                document.getElementById("execution-spinner").style.display = "none";
            }
        }
        if (msg.status == "timeout") {
            document.getElementById("execution-spinner").style.display = "none";
            M.toast({html: "Timeout, restarting...", displayLength: 3000});
        }
        if (msg.status == "launching") {
            document.getElementById("execution-spinner").style.display = "block";
        }
        return;
    }
});

socket.on('connect', function() {
    socket.emit('join', {session_id: session_id, language: language});
});

socket.on('disconnect', function() {
    document.getElementById("agent-ready").style.display = "none";
    document.getElementById("agent-not-ready").style.display = "block";
});

// create a function to send the message to the server
function sendCode() {
    send_code_sent += 1;
    document.getElementById("execution-spinner").style.display = "block";
    var code = editor.getValue();
    // create the json object to send to the server
    var json = {
        event: 'codeChange',
        session_id: session_id,
        language: language,
        code: code,
        outputSelected: outputSelected
    };
    socket.emit('json', json);
}

CodeMirror.commands.save = function(insance) { 
    sendCode();
};

var highlightedLines = {};
var outputSelected = {};

editor.on('mousedown', function(instance, event) {
    const lineNumber = editor.coordsChar({left: event.clientX, top: event.clientY}).line;
    const lineContent = editor.getLine(lineNumber).trim();

    if (lineContent.startsWith("#@")) {
        const func = lineContent.replace(/^#@\s*/, '').replace(/\s*\(.*\)$/, '');
        const argsStr = lineContent.split('(')[1].slice(0, -1);
        const args = argsStr.match(/(?:[^,(){}[\]]+|\([^)]*\)|\{[^}]*\}|\[[^\]]*\])+/g) || [];

        // Check if we are within the same function
        if (highlightedLines[func] !== undefined && highlightedLines[func] !== lineNumber) {
            // Clear previous highlights for the current function
            clearMarkerAtLine(highlightedLines[func]);
        }
        // Update the highlighted line for the function
        highlightedLines[func] = lineNumber;
        outputSelected[func] = args;

        // Highlight the selected line
        editor.markText(
            { line: lineNumber, ch: 0 },
            { line: lineNumber, ch: lineContent.length },
            { className: 'highlight-line' }
        );
        sendCode();
    }
});

function clearMarkerAtLine(lineNumber) {
    var marks = editor.findMarks(
        { line: lineNumber, ch: 0 },
        { line: lineNumber, ch: editor.getLine(lineNumber).length }
    );

    marks.forEach(function(mark) {
        mark.clear();
    });
}

// send code on evry change
editor.on('change', function() {
    sendCode();
});