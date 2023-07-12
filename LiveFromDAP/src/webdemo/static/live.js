var myTextarea = document.getElementById('editor');
var myTextarea2 = document.getElementById('output');
// C program
var editor = CodeMirror.fromTextArea(myTextarea, {
    lineNumbers: true,
    mode: "text/x-csrc"
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
        return;
    }
    if (msg.event == 'executeTimeout') {
        M.toast({html: 'Timeout, restarting gdb', displayLength: 3000});
        return;
    }
});

socket.on('connect', function() {
    socket.emit('json', {event: 'init'});
});


// create a function to send the message to the server
function sendCode() {
    var code = editor.getValue();
    // create the json object to send to the server
    var json = {
        event: 'codeChange',
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