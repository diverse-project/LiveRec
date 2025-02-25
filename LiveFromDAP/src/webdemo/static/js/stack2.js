var carousel = document.querySelectorAll('.carousel')[0];

var carousel_instance = M.Carousel.init(carousel, {
    fullWidth: true,
    indicators: true,
    noWrap: true,
    onCycleTo: onCycle
});

function onCycle(data) {
    if (carousel_instance == undefined) {
        return;
    }
    let current_stack = getStack(carousel_instance.center);
    editor.getAllMarks().forEach(function(mark) { mark.clear(); });
    //highlight the current line
    editor.markText({line: current_stack["pos"]["line"]-1, ch: current_stack["pos"]["column"]-1}, {line: current_stack["pos"]["line"]-1, ch: 1000}, {className: "highlight"});
}




var curentStackRecord = {
    "stacktrace": []
};

function getStack(id){
    return curentStackRecord["stacktrace"][id];
}

function displayStack() {
    /* Need to create for each stack a slide in the carousel liek this
    <div class="carousel-item red" href="#">
        <h2>Stack #? line ?</h2>
        <p>
            <ul>
                <li>x = 1</li>
                <li>y = 2</li>
            </ul>   
        </p>
    </div>
    */
    if (carousel_instance != undefined){
        carousel_instance.destroy();
    }
    carousel.innerHTML = "";
    for(var i = 0; i < curentStackRecord["stacktrace"].length; i++) {
        var stack = getStack(i);
        var slide = document.createElement("div");
        slide.classList.add("carousel-item");
        slide.setAttribute("href", "#");
        var h2 = document.createElement("h2");
        h2.innerHTML = "Stack #" + i + " line " + stack["pos"]["line"];
        var p = document.createElement("p");
        var ul = document.createElement("ul");
        for(var j = 0; j < stack["variables"].length; j++) {
            var li = document.createElement("li");
            li.innerHTML = stack["variables"][j]["name"] + " = " + stack["variables"][j]["value"];
            ul.appendChild(li);
        }
        p.appendChild(ul);
        slide.appendChild(h2);
        slide.appendChild(p);
        carousel.appendChild(slide);
    }
    carousel_instance = M.Carousel.init(carousel, {
        fullWidth: true,
        indicators: true,
        noWrap: true,
        onCycleTo: onCycle
    }); 
}

function handle_executeOutput(msg) {
    //parse the output into a json
    msg.output = JSON.parse(msg.output);
    // check if the output is a stacktrace
    if (msg.output["stacktrace"] == undefined) {
        return;
    }
    curentStackRecord = msg.output;
    
    displayStack();
}