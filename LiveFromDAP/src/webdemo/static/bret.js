var outputArea = document.getElementById('output');

// output not editable
var output = CodeMirror.fromTextArea(outputArea, {
    lineNumbers: true,
    indentUnit: 4,
    readOnly: false
});

var oldText = output.getValue();

function handle_executeOutput(msg) {
    // var code = editor.getValue();
    // let codeOutput = [];
    // codeOutput = String((msg.output)).split(/\n+/);
    // console.log(codeOutput);

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
    // console.log(code);
    // console.log(oldText);
    // console.log(msg.output);
    oldText = msg.output;
}