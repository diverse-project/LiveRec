import os
import subprocess
import sys

from livefromdap.agent.JavascriptLiveAgent import JavaScriptPreprocessor

from .BaseExecutionAgent import BaseDAPManager
import debugpy
from debugpy.common.messaging import JsonIOStream
from debugpy.common import sockets

from livefromdap.utils.StackRecording import Stackframe, StackRecording

import re
import ast as python_ast

class PyDAPManager(BaseDAPManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner_path = kwargs.get("runner_path", os.path.join(os.path.dirname(__file__), "..", "runner", "py_runner.py"))
        self.debugpy_adapter_path = kwargs.get("debugpy_adapter_path", os.path.join(os.path.dirname(debugpy.__file__), "adapter"))

    def start_server(self):
        """Create a subprocess with the agent"""

        self.server = subprocess.Popen(
            ["python", self.debugpy_adapter_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            restore_signals=False,
            start_new_session=True,
        )

        self.io = JsonIOStream.from_process(self.server)
    
    def restart_server(self):
        self.server.kill()
        self.start_server()

    def stop_server(self):
        """Kill the subprocess"""
        self.server.kill()
        if getattr(self, "debugee", None) is not None:
            self.debugee.kill()
    
    def initialize(self):
        """Send data to the agent"""
        init_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "initialize",
            "arguments": {
                "clientID": "vscode",
                "clientName": "Visual Studio Code",
                "adapterID": "python",
                "pathFormat": "path",
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "supportsVariableType": True,
                "supportsVariablePaging": True,
                "supportsRunInTerminalRequest": True,
                "locale": "en",
                "supportsProgressReporting": True,
                "supportsInvalidatedEvent": True,
                "supportsMemoryReferences": True,
                "supportsArgsCanBeInterpretedByShell": True,
                "supportsMemoryEvent": True,
                "supportsStartDebuggingRequest": True
            }
        }
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "name": f"Debug Python agent live",
                "type": "python",
                "request": "launch",
                "program": self.runner_path,
                "console": "internalConsole",
                # get the current python interpreter
                "python": sys.executable,
                "debugAdapterPython": sys.executable,
                "debugLauncherPython": sys.executable,
                "clientOS": "unix",
                "cwd": os.getcwd(),
                "envFile": os.path.join(os.getcwd(), ".env"),
                "env": {
                    "PYTHONIOENCODING": "UTF-8",
                    "PYTHONUNBUFFERED": "1"
                },
                "stopOnEntry": False,
                "showReturnValue": True,
                "internalConsoleOptions": "neverOpen",
                "debugOptions": [
                    "ShowReturnValue"
                ],
                "justMyCode": False,
                "workspaceFolder": os.getcwd(),
            }
        }
        self.io.write_json(init_request)
        self.io.write_json(launch_request)
        self.wait("event", "initialized")
        self.setup_runner_breakpoint()
        self.wait("event", "stopped")
        return 5
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [19])
        self.configuration_done()
    
    def load_code(self, path: str):
        stacktrace = self.get_stackframes()
        frameId = stacktrace[0]["id"]
        self.evaluate(f"set_import('{os.path.abspath(path)}')", frameId)
        self.next_breakpoint()
        self.wait("event", "stopped")
            
    def execute(self, method, args, max_steps=50):
        pass

class JSDAPManager(BaseDAPManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dap_adapter_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin", "js-dap", "dapDebugServer.js"))
        self.runner_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runner"))
        self.runner_name = "js_runner.js"
        self.runner_path = os.path.abspath(os.path.join(self.runner_directory, self.runner_name))
        
    def start_server(self):
        self.server_process = subprocess.Popen(
            ["node", self.dap_adapter_path, "8123", "127.0.0.1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            restore_signals=False,
            start_new_session=True,
        )
        # wait for the server to be ready
        while True:
            # check if the process returned an error
            if self.server_process.poll() is not None:
                error = self.server_process.stderr.readline() # type: ignore
                # if address already in use
                if b"Error: listen EADDRINUSE: address already in use" in error:
                    # fidn the process that is using the port
                    p = subprocess.Popen(["lsof", "-i", ":8123"], stdout=subprocess.PIPE)
                    p.wait()
                    lsof_output = p.stdout.readlines() # type: ignore
                    pid = lsof_output[-1].split()[1]
                    subprocess.Popen(["kill", pid])
                    self.start_server()
                    return
            output = self.server_process.stdout.readline() # type: ignore
            # wait for : Debug server listening at 127.0.0.1:8123
            if b"Debug server listening" in output:
                break
        self.main_server = sockets.create_client()
        self.main_server.connect(("localhost", 8123))
        self.main_io = JsonIOStream.from_socket(self.main_server)
        self._entry_line = {}
    
    def restart_server(self):
        self.stop_server()
        self.start_server()
    
    
    def stop_server(self):
        """Stop the target program"""
        # Send a stop request
        stop_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "disconnect",
            "arguments": {
                "restart": False,
                "terminateDebuggee": True
            }
        }
        try:
            self.io.write_json(stop_request)
            self.wait("event", "terminated")
            self.io.close()
        except:
            pass
        try:
            self.io = self.main_io
            self.io.write_json(stop_request)
            self.main_io.close()
        except:
            pass
        try:
            self.server_process.kill()
        except:
            pass
         
    def initialize(self):
        """Send data to the agent"""   
        init_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "initialize",
            "arguments": {
                "clientID": 'vscode',
                "clientName": 'Visual Studio Code',
                "adapterID": 'pwa-node',
                "pathFormat": 'path',
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "supportsVariableType": True,
                "supportsVariablePaging": True,
                "supportsRunInTerminalRequest": True,
                "locale": 'en',
                "supportsProgressReporting": True,
                "supportsInvalidatedEvent": True,
                "supportsMemoryReferences": True,
                "supportsArgsCanBeInterpretedByShell": True,
                "supportsMemoryEvent": True,
                "supportsStartDebuggingRequest": True
            }
        }    
            
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "type": 'pwa-node',
                "name": 'Launch Program',
                "outputCapture": 'console',
                "smartStep": True,
                "sourceMaps": True,
                "sourceMapRenames": True,
                "pauseForSourceMap": False,
                "rootPath": self.runner_directory,
                "outFiles": [
                    f"{self.runner_directory}/**/*.js", 
                     "!**/node_modules/**" 
                ],
                "sourceMapPathOverrides": {
                    'webpack:///./~/*': f'{self.runner_directory}/node_modules/*',
                    'webpack:////*': '/*',
                    'webpack://@?:*/?:*/*': f'{self.runner_directory}/*',
                    'webpack://?:*/*': f'{self.runner_directory}/*',
                    'webpack:///([a-z]):/(.+)': '$1:/$2',
                    'meteor://💻app/*': f'{self.runner_directory}/*'
                },
                "enableContentValidation": True,
                "cascadeTerminateToConfigurations": [],
                "__workspaceFolder": self.runner_directory,
                "cwd": self.runner_directory,
                "env": {},
                "envFile": None,
                "localRoot": None,
                "remoteRoot": None,
                "autoAttachChildProcesses": True,
                "program": self.runner_path,
                "stopOnEntry": False,
                "console": 'internalConsole',
                "restart": False,
                "args": [],
                "runtimeExecutable": 'node',
                "runtimeVersion": 'default',
                "runtimeArgs": [],
                "attachSimplePort": None,
                "killBehavior": 'forceful',
            }
        }
        self.io = self.main_io # we need to use the main io to initialize to create the target launch
        self.main_io.write_json(init_request)
        self.configuration_done()
        self.wait("event", "initialized")
        self.main_io.write_json(launch_request)
        debugging = self.wait("request", command="startDebugging")
        self.server = sockets.create_client()
        self.server.connect(("localhost", 8123))
        self.io = JsonIOStream.from_socket(self.server)
        self.io.write_json(init_request)
        self.setup_runner_breakpoint()
        self.io.write_json({
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": debugging["arguments"]["configuration"]
        })
        brk = self.wait("event", "stopped")
        self.thread_id = brk["body"]["threadId"]
    
    def stop_debugee(self):
        terminate_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "disconnect",
            "arguments": {
                "restart": False,
                "terminateDebuggee": True
            }
        }
        self.io.write_json(terminate_request)
        self.server.close()
    
    def setup_runner_breakpoint(self):
        self.set_breakpoint(self.runner_path, [21])
        self.configuration_done()


    def load_code(self, path : str):
        """For this agent, loading code is loading a class in the runner"""
        jspp = JavaScriptPreprocessor(path, path)
        self._entry_line[path] = jspp.functions
        frame_id = self.get_stackframes(self.thread_id)[0]["id"]
        self.evaluate(f'loadFile("{path}")', frame_id)


    def execute(self, path : str, method : str, args : list[str], max_steps : int =100) -> tuple[str, StackRecording]:
        pass


class PyJSExecutionAgent():
    
    def __init__(self):
        self.py_dap = PyDAPManager()
        self.js_dap = JSDAPManager()
        self.py_dap.start_server()
        self.js_dap.start_server()
        self.py_dap.initialize()
        self.js_dap.initialize()
        self.py_dap.evaluate("print('test')", self.py_dap.get_stackframes()[0]["id"])

    def load_code(self, path):
        self.py_dap.load_code(path)

