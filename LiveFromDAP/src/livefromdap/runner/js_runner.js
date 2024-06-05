
var target_function = null;
var target_args = null;
var last_path = null;
var import_file = null;

polyglotEval = function (lang, code) {
    // src_file = undefined;
    ret = -1;
    while (import_file != null) {
        var intermediate_ret = require(import_file);
        import_file = null;
    } 
    return ret;
}

var loadFile = function (filename) {
    if (last_path != null) {
        delete require.cache[require.resolve(last_path)]
    }
    last_path = filename;
    import_file = filename;
}

// test file /home/jbdod/CWI/LiveProbes/test.js
while (true) {
    if (import_file != null) {
        let content = require(import_file);
        console.log(content);
        // add content to global
        for (let key in content) {
            global[key] = content[key];
        }
        import_file = null
    }

    if (target_function != null && target_args != null) {
        let result = "Interrupted";
        try{
            let result = target_function.apply(null, target_args);
        } catch (e) {}
        target_function = null;
        target_args = null;
    }  
}