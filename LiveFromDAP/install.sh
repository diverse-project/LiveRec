#!/bin/bash
# This script will download and install the debug servers for LiveFromDAP

# JDT LS
echo "[JDT LS] Checking for JDT LS..."
# check if src/livefromdap/bin/jdt-language-server directory exists
if [ ! -d "src/livefromdap/bin/jdt-language-server" ]; then
    echo "Downloading JDT LS..."
    curl -L -o src/livefromdap/bin/jdt-language-server.tar.gz https://download.eclipse.org/jdtls/snapshots/jdt-language-server-latest.tar.gz
    # Unzip the file
    echo "Installing JDT LS..."
    mkdir -p src/livefromdap/bin/jdt-language-server
    tar -xzf src/livefromdap/bin/jdt-language-server.tar.gz -C src/livefromdap/bin/jdt-language-server
    # Remove the downloaded file
    echo "Cleaning up..."
    rm src/livefromdap/bin/jdt-language-server.tar.gz
else
    echo "JDT LS already installed."
fi
# Java Debug
echo "[Java Debug] Checking for Java debug server..."
if [ ! -f "src/livefromdap/bin/com.microsoft.java.debug.plugin.jar" ]; then
    echo "Downloading Java debug server..."
    curl -L -o src/livefromdap/bin/java-debug.vsix https://github.com/microsoft/vscode-java-debug/releases/download/0.52.0/vscjava.vscode-java-debug-0.52.0.vsix
    # Unzip the file
    echo "Installing Java debug server..."
    mkdir -p src/livefromdap/bin/java-debug
    unzip -q -o src/livefromdap/bin/java-debug.vsix -d src/livefromdap/bin/java-debug
    # Copy the server to the bin folder
    #find the name of the server jar
    server_jar=$(find src/livefromdap/bin/java-debug/extension/server -name "com.microsoft.java.debug.plugin-*.jar")
    cp $server_jar src/livefromdap/bin/com.microsoft.java.debug.plugin.jar
    # Remove the downloaded file
    echo "Cleaning up..."
    rm -rf src/livefromdap/bin/java-debug
    rm src/livefromdap/bin/java-debug.vsix
else
    echo "Java debug server already installed."
fi

# C Debug
echo "[C Debug] Checking for C debug server..."
# check if src/livefromdap/bin/OpenDebugAD7 directory exists
if [ ! -d "src/livefromdap/bin/OpenDebugAD7" ]; then
    echo "Downloading C debug server..."
    # if linux
    if [ "$(uname)" == "Linux" ]; then
        curl -L -o src/livefromdap/bin/OpenDebugAD7.vsix https://github.com/microsoft/vscode-cpptools/releases/download/v1.16.3/cpptools-linux.vsix
    # if mac
    elif [ "$(uname)" == "Darwin" ]; then
        curl -L -o src/livefromdap/bin/OpenDebugAD7.vsix https://github.com/microsoft/vscode-cpptools/releases/download/v1.16.3/cpptools-osx.vsix
    fi
    # Unzip the file
    echo "Installing C debug server..."
    mkdir -p src/livefromdap/bin/OpenDebugAD7Tmp
    mkdir -p src/livefromdap/bin/OpenDebugAD7
    unzip -q -o src/livefromdap/bin/OpenDebugAD7.vsix -d src/livefromdap/bin/OpenDebugAD7Tmp
    # Copy the server to the bin folder
    cp src/livefromdap/bin/OpenDebugAD7Tmp/extension/debugAdapters/bin/* src/livefromdap/bin/OpenDebugAD7
    chmod +x src/livefromdap/bin/OpenDebugAD7/*
    # Remove the downloaded file
    echo "Cleaning up..."
    rm -rf src/livefromdap/bin/OpenDebugAD7Tmp
    rm src/livefromdap/bin/OpenDebugAD7.vsix
else
    echo "C debug server already installed."
fi

# Python Debug
echo "[Python Debug] Checking for Python debug server..."
# check if debugpy is installed
# if python -c "import debugpy" exit with 0 then it is installed
if python -c "import debugpy" &> /dev/null; then
    echo "Python debug server already installed."
else
    echo "You need to install the Python debug server with pip install debugpy"
    exit 1
fi

# Node Debug
echo "[Node Debug] Checking for Node"
# check if node is installed
# if node -v exit with 0 then it is installed
if ! node -v &> /dev/null; then
    echo "You need to install Node.js"
    exit 1
fi

# Js DAP
echo "[Js DAP] Checking for Js DAP..."
# check if src/livefromdap/bin/js-dap directory exists
if [ ! -d "src/livefromdap/bin/js-dap" ]; then
    echo "Downloading Js DAP..."
    mkdir -p src/livefromdap/bin/js-dap
    cd src/livefromdap/bin/js-dap
    git clone https://github.com/microsoft/vscode-js-debug
    cd vscode-js-debug
    npm install
    # check if gulp is installed
    # if gulp -v exit with 0 then it is installed
    if ! gulp -v &> /dev/null; then
        echo "Installing gulp..."
        npm install --global gulp-cli
    fi
    gulp dapDebugServer
    cd ../..
    cp -r js-dap/vscode-js-debug/dist/src/* js-dap/
    rm -rf js-dap/vscode-js-debug
    cd ../../..
else
    echo "Js DAP already installed."
fi


# Tree sitter
echo "[Tree sitter] Checking for tree sitters ..."
# check if src/livefromdap/bin/treesitter directory exists
if [ ! -d "src/livefromdap/bin/treesitter" ]; then
    echo "Downloading tree sitters..."
    mkdir -p src/livefromdap/bin/treesitter
    cd src/livefromdap/bin/treesitter
    git clone https://github.com/tree-sitter/tree-sitter-javascript
    git clone https://github.com/tree-sitter/tree-sitter-python
    git clone https://github.com/tree-sitter/tree-sitter-java
    git clone https://github.com/tree-sitter/tree-sitter-c
    python -c "from tree_sitter import Language;Language.build_library('javascript.so', ['tree-sitter-javascript'])"
    python -c "from tree_sitter import Language;Language.build_library('python.so', ['tree-sitter-python'])"
    python -c "from tree_sitter import Language;Language.build_library('java.so', ['tree-sitter-java'])"
    python -c "from tree_sitter import Language;Language.build_library('c.so', ['tree-sitter-c'])"
    rm -rf tree-sitter-javascript
    rm -rf tree-sitter-python
    rm -rf tree-sitter-java
    rm -rf tree-sitter-c
    cd ../../../..
else
    echo "Js tree sitter already installed."
fi

# Make runner files executable
echo "[Runner] Making runner files executable..."
cd src/livefromdap
make runner
chmod +x runner/*
cd ../..


