var myTextarea = document.getElementById('editor');
var myTextarea2 = document.getElementById('output');

var CodeMirror_mode = "";
if (language=="c"){
    CodeMirror_mode = "text/x-csrc";
}
if (language=="java"){
    CodeMirror_mode = "text/x-java";
}
if (language=="python"){
    CodeMirror_mode = "text/x-python";
}

// C program
var editor = CodeMirror.fromTextArea(myTextarea, {
    lineNumbers: true,
    mode: CodeMirror_mode
});
// output not editable
var output = CodeMirror.fromTextArea(myTextarea2, {
    lineNumbers: true,
    readOnly: true
});

var oldText = output.getValue();

var socket = io();

socket.on('json', function(msg) {
    console.log(msg.event);
    if (msg.event == 'codeChange') {
        editor.setValue(msg.code);
        return;
    }
    if (msg.event == 'executeOutput') {
        console.log("receive new thing");
        let old = oldText;
        let diffs = Diff.diffLines(old, msg.output);
        let line = 0;
        let lines_green =[];
        let lines_red = [];
        final_text = "";
        diffs.forEach(function(part){
            if (part.added) {
                for (let i = 0; i < part.count; i++) {
                    lines_green.push(line+i);
                }
                final_text += part.value;
                line += part.count;
            } else if (part.removed) {
                lines_red.push(line);
            } else{
                final_text += part.value;
                line += part.count;
            }
            
        });
        output.setValue(final_text);
        lines_green.forEach(function(line){
            output.markText({line: line, ch: 0}, {line: line, ch: 1000}, {className: "green-text"});
        });
        lines_red.forEach(function(line){
            output.markText({line: line, ch: 0}, {line: line, ch: 1000}, {className: "red-text"});
        });
        oldText = msg.output;
        return;
    }
    if (msg.event == 'status') {
        //M.toast({html: msg.status, displayLength: 3000});
        console.log(msg.status);
        if (msg.status == "agent_up") {
            document.getElementById("agent-ready").style.display = "block";
            document.getElementById("agent-not-ready").style.display = "none";
            sendCode();
        }
        if (msg.status == "ready") {
            document.getElementById("execution-spinner").style.display = "none";
        }
        return;
    }
});

socket.on('connect', function() {
    socket.emit('json', {event: 'initialize', session_id: session_id, language: language});
});

socket.on('disconnect', function() {
    document.getElementById("agent-ready").style.display = "none";
    document.getElementById("agent-not-ready").style.display = "block";
});


// create a function to send the message to the server
function sendCode() {
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

// send code on evry change
editor.on('change', function() {
    sendCode();
});