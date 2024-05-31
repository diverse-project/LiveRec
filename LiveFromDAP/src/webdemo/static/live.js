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
        document.getElementById("execution-spinner").style.display = "none";
        return;
    }
    if(msg.event == "addSlider"){
        addSlider(msg.lineNumber, msg.length, msg.start, msg.end);
        document.getElementById("execution-spinner").style.display = "none";
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
        code: code
    };
    socket.emit('json', json);
}

CodeMirror.commands.save = function(insance) { 
    sendCode();
};

editor.on('mousedown', function(instance, event) {
    const lineNumber = editor.coordsChar({left: event.clientX, top: event.clientY}).line;
    const lineContent = editor.getLine(lineNumber);
    const lineTrim = lineContent.trim();

    if (!lineTrim.startsWith("#@")) {
        if(lineTrim.startsWith("for")){
            document.getElementById("execution-spinner").style.display = "block";
            const json = {
                event: 'addSlider',
                session_id: session_id,
                language: language,
                code: editor.getValue(),
                lineNumber: lineNumber
            };
            socket.emit('json', json);
            displayStackByLine(lineNumber+1);
        }else {
            slider = document.getElementById("slider");
            if (slider != undefined) {
                slider.remove();
            }
            displayStackByLine(lineNumber+1);
        }
    }
});

// send code on evry change
editor.on('change', function() {
    sendCode();
});