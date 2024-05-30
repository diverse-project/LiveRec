var stackTitle = document.getElementById("stack-title");
var stackVar = document.getElementById("stack-var");
var stackRange = document.getElementById("stack-range");
var slider = undefined;

var curentStackRecord = {
    "stacktrace": []
};

function getStackByInterval(start, end){
    var matchingFrames = curentStackRecord["stacktrace"].slice(start, end);
    return matchingFrames;
}
function getStackByLine(line){
    var matchingFrames = curentStackRecord.stacktrace.filter(frame => frame.pos.line === line);
    return matchingFrames;
}
function displayStack(value, stacks) {
    var stack = stacks[value];
    stackTitle.innerHTML = `StackFrame (l${stack["pos"]["line"]}:${stack["pos"]["column"]}, height ${stack["height"]})`;
    // stack var is a ul, create a li for each var
    stackVar.innerHTML = "";
    // stack["variables"] is a list
    for (let i = 0; i < stack["variables"].length; i++) {
        const li = document.createElement("li");
        li.innerHTML = `${stack["variables"][i]["name"]} = ${stack["variables"][i]["value"]}`;
        stackVar.appendChild(li);
    }
    //delete the previous highlight
    editor.getAllMarks().forEach(function(mark) { mark.clear(); });
    // //highlight the current line
    editor.markText({line: stack["pos"]["line"]-1, ch: stack["pos"]["column"]-1}, {line: stack["pos"]["line"]-1, ch: 1000}, {className: "highlight"});
}

function displayStackByLine(line) {
    var stack = getStackByLine(line);
    editor.getAllMarks().forEach(function(mark) { mark.clear(); });

    if(stack.length == 0){
        return;
    }
    stackTitle.innerHTML = `StackFrame (l${stack[0]["pos"]["line"]}:${stack[0]["pos"]["column"]}, height ${stack[0]["height"]})`;
    // stack var is a ul, create a li for each var
    stackVar.innerHTML = "";
    // stack["variables"] is a list
    for (let i = 0; i < stack[0]["variables"].length; i++) {
        const li = document.createElement("li");
        li.innerHTML = `${stack[0]["variables"][i]["name"]} = ${stack[0]["variables"][i]["value"]}`;
        stackVar.appendChild(li);
    }

    editor.markText({line: stack[0]["pos"]["line"]-1, ch: stack[0]["pos"]["column"]-1}, {line: stack[0]["pos"]["line"]-1, ch: 1000}, {className: "highlight"});
}

function handle_executeOutput(msg) {
    //parse the output into a json
    try {
        msg.output = JSON.parse(msg.output);
    } catch (e) {
        console.log(msg.output);
        return;
    }
    // check if the output is a stacktrace
    if (msg.output["stacktrace"] == undefined) {
        return;
    }
    curentStackRecord = msg.output;
    console.log(curentStackRecord);
}
function addSlider(lineNumber, value, start, end){

    if(slider){
        slider.max = value.toString();
        slider.value = '0';
        slider.min = '0';
    }else{
        slider = document.createElement("input");
        slider.max = value.toString();
        slider.value = '0';
        slider.min = '0';
        slider.id = 'slider';
        slider.type = 'range';
        stackRange.appendChild(slider);
    }
    var stacks = getStackByInterval(start, end+1);
    // on range change, display the stack
    slider.oninput = function() {
        var stacks = getStackByInterval(start, end+1);
        displayStack(parseInt(this.value), stacks);
    }
}