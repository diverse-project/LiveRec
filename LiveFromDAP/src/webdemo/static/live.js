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
    mode: "text/x-csrc",
    readOnly: true
});


var socket = io();

socket.on('json', function(msg) {
    console.log(msg.event);
    if (msg.event == 'codeChange') {
        editor.setValue(msg.code);
        return;
    }
    if (msg.event == 'executeOutput') {
        output.setValue(msg.output);
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

// create a function to send a exec request to the server
function execCode(method, args) {
    // create the json object to send to the server
    var json = {
        event: 'execute',
        method: method,
        args: args
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