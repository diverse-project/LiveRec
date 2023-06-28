// Resizer 

// Get the necessary elements
const resizer = document.getElementById('editor-resizer');
const editorContainer = document.getElementById('editor-container');
const outputContainer = document.getElementById('output-container');

// Initialize variables
let isResizing = false;
let startX = 0;
let startWidth = 0;

// Function to handle the resizing
function resizeContainers(e) {
    if (!isResizing) return;

    const newWidth = startWidth + (e.clientX - startX);

    editorContainer.style.flex = `0 0 ${newWidth}px`;
    outputContainer.style.flex = `0 0 calc(100% - ${newWidth}px)`;
}

// Event listeners
resizer.addEventListener('mousedown', (e) => {
    isResizing = true;
    startX = e.clientX;
    startWidth = editorContainer.offsetWidth;

    document.addEventListener('mousemove', resizeContainers);
});

document.addEventListener('mouseup', () => {
    isResizing = false;
    document.removeEventListener('mousemove', resizeContainers);
});