
var target_function = null;
var target_args = null;
var last_path = null;
var result = null;

var loadFile = function (filename) {
    if (last_path != null) {
        delete require.cache[require.resolve(last_path)]
    }
    last_path = filename;
    let content = require(filename);
    console.log(content);
    // add content to global
    for (let key in content) {
        global[key] = content[key];
    }
}

probe = function (line_number, expr, val) {
    let res = eval(val);
    return 
}

while (true) {
    if (target_function != null && target_args != null) {
        result = "Interrupted";
        try{
            result = target_function.apply(null, target_args);
        } catch (e) { console.log(e) }
        target_function = null;
        target_args = null;
    }  
}