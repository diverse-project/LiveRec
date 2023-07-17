var stackTitle = document.getElementById("stack-title");
var stackVar = document.getElementById("stack-var");
var stackRange = document.getElementById("stack-range");

var curentStackRecord = {
    "stacktrace": []
};

function getStack(id){
    return curentStackRecord["stacktrace"][id];
}

function displayStack(id) {
    var stack = getStack(id);
    stackTitle.innerHTML = `StackFrame #${id} (l${stack["pos"]["line"]}:${stack["pos"]["column"]}, height ${stack["height"]})`;
    // stack var is a ul, create a li for each var
    stackVar.innerHTML = "";
    // stack["variables"] is a list
    for (var i = 0; i < stack["variables"].length; i++) {
        var li = document.createElement("li");
        li.innerHTML = `${stack["variables"][i]["name"]} = ${stack["variables"][i]["value"]}`;
        stackVar.appendChild(li);
    }
    //delete the previous highlight
    editor.getAllMarks().forEach(function(mark) { mark.clear(); });
    //highlight the current line
    editor.markText({line: stack["pos"]["line"]-1, ch: stack["pos"]["column"]-1}, {line: stack["pos"]["line"]-1, ch: 1000}, {className: "highlight"});
}

function handle_executeOutput(msg) {
    //parse the output into a json
    msg.output = JSON.parse(msg.output);
    console.log(msg.output);
    // check if the output is a stacktrace
    if (msg.output["stacktrace"] == undefined) {
        return;
    }
    curentStackRecord = msg.output;
    
    stackRange.max = curentStackRecord["stacktrace"].length - 1;
    stackRange.value = 0;
    displayStack(0);
}

// on range change, display the stack
stackRange.oninput = function() {
    displayStack(this.value);
}