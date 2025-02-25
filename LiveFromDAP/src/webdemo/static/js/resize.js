// Resizer 

document.addEventListener('DOMContentLoaded', () => {
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
        const totalWidth = editorContainer.parentElement.clientWidth;
        
        // Ensure minimum width
        if (newWidth < 200 || newWidth > totalWidth - 200) return;

        // Set widths using percentages for smoother resizing
        const percentage = (newWidth / totalWidth) * 100;
        editorContainer.style.width = `${percentage}%`;
        editorContainer.style.flex = '0 0 auto';
        outputContainer.style.width = `${100 - percentage}%`;
        outputContainer.style.flex = '0 0 auto';

        // Refresh CodeMirror instances
        if (window.editor && window.editor.editor) {
            window.editor.editor.refresh();
        }
        if (window.socketManager && window.socketManager.outputHandler && window.socketManager.outputHandler.output) {
            window.socketManager.outputHandler.output.refresh();
        }
    }

    // Event listeners
    resizer.addEventListener('mousedown', (e) => {
        isResizing = true;
        startX = e.clientX;
        startWidth = editorContainer.offsetWidth;

        document.addEventListener('mousemove', resizeContainers);
        document.addEventListener('mouseup', stopResizing);
        
        // Add a class to prevent text selection while resizing
        document.body.classList.add('resizing');
    });

    function stopResizing() {
        isResizing = false;
        document.removeEventListener('mousemove', resizeContainers);
        document.removeEventListener('mouseup', stopResizing);
        document.body.classList.remove('resizing');
    }
});