var target_function = null;
var target_args = null;
var last_path = null;

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

// test file /home/jbdod/CWI/LiveProbes/test.js
while (true) {
    if (target_function != null && target_args != null) {
        let result = "Interrupted";
        try{
            let result = target_function.apply(null, target_args);
        } catch (e) {}
        target_function = null;
        target_args = null;
    }  
}