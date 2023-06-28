import subprocess
from debugpy.common.messaging import JsonIOStream

class BaseLiveAgent:
    """Communicate with the debugpy adapter to get stackframes of the execution of a method"""

    seq : int = 0

    def __init__(self, runner_path : str, target_path : str, target_method : str, debug : bool = False, **kwargs):
        self.runner_path = runner_path
        self.target_path = target_path
        self.target_method = target_method
        self.debug = debug
        self.seq = 0
        self.job = self.create_job()
        self.io = JsonIOStream.from_process(self.job)

    def new_seq(self):
        self.seq += 1
        return self.seq

    def create_job(self) -> subprocess.Popen:
        """Create a subprocess with the agent"""
        return NotImplemented
    
    def stop(self):
        """Stop the agent"""
        self.job.kill()
    
    def init(self):
        """Initialize and launch the adapter"""
        raise NotImplemented
    
    def load_code(self):
        """Load the code to debug"""
        raise NotImplemented
        
    def handleRunInTerminal(self, output : dict):
        """Handle the runInTerminal request from the adapter"""
        if output["type"] == "request" and output["command"] == "runInTerminal":
            # output stdout in a file
            debuggee = subprocess.Popen(
                output["arguments"]["args"],
                stdout=open("tmp/stdout.txt", "w"),
                stderr=open("tmp/stderr.txt", "w")
            )
            process_id = debuggee.pid
            self.debugee = debuggee
            # send the response
            self.seq+=1
            response = {
                "seq": int(output["seq"]) + 1,
                "type": "response",
                "request_seq": output["seq"],
                "success": True,
                "command": "runInTerminal",
                "body": {
                    "shellProcessId": process_id
                }
            }
            self.io.write_json(response)
            return True
        return False
    
    def _set_breakpoint(self, path : str, lines : list):
        """Set a breakpoint in the debuggee"""
        breakpoint_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "setBreakpoints",
            "arguments": {
                "source": {
                    "name": path,
                    "path": path
                },
                "lines": lines,
                "breakpoints": [
                    {
                        "line": line
                    } for line in lines
                ],
                "sourceModified": False
            }
        }
        self.io.write_json(breakpoint_request)

    def _set_function_breakpoint(self, names : list):
        """Set a breakpoint in the debuggee"""
        breakpoint_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "setFunctionBreakpoints",
            "arguments": {
                "breakpoints": [
                    {
                        "name": name
                    } for name in names
                ]
            }
        }
        self.io.write_json(breakpoint_request)

    def setup_breakpoint(self):
        """Setup the first breakpoints in the debuggee"""
        complete_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "configurationDone"
        }
        self.io.write_json(complete_request)
    
    
    def get_stackframes(self, thread_id : int = 1):
        stackframe_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "stackTrace",
            "arguments": {
                "threadId": thread_id,
                "startFrame": 0,
                "levels": 100
            }
        }
        self.io.write_json(stackframe_request)
        output = self.wait("response", command="stackTrace")
        return output["body"]["stackFrames"]
            
    def _continue(self, thread_id : int = 1):
        continue_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "continue",
            "arguments": {
                "threadId": thread_id
            }
        }
        if self.debug: print("Continue req", continue_request)
        self.io.write_json(continue_request)
    
    def step(self, thread_id : int = 1):
        step_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "next",
            "arguments": {
                "threadId": thread_id
            }
        }
        self.io.write_json(step_request)

    def step_out(self, thread_id : int = 1):
        step_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "stepOut",
            "arguments": {
                "threadId": thread_id
            }
        }
        self.io.write_json(step_request)

    def get_scopes(self, frame_id):
        scopes_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "scopes",
            "arguments": {
                "frameId": frame_id
            }
        }
        self.io.write_json(scopes_request)
        output = self.wait("response", command="scopes")
        return output["body"]["scopes"]
            
    def get_variables(self, scope_id):
        variables_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "variables",
            "arguments": {
                "variablesReference": scope_id
            }
        }
        self.io.write_json(variables_request)
        output = self.wait("response", command="variables")
        return output["body"]["variables"]
            
    def evaluate(self, expression : str, frame_id : int = None):
        evaluate_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "evaluate",
            "arguments": {
                "expression": expression,
            }
        }
        if frame_id:
            evaluate_request["arguments"]["frameId"] = frame_id
        self.io.write_json(evaluate_request)
        return self.wait("response", command="evaluate")

    def execute(self, args : list):
        return NotImplemented

    def wait(self, type, event=None, command=None):
        while True:
            output = self.io.read_json()
            if self.debug: print(output)
            if output["type"] == "request" and output["command"] == "runInTerminal":
                if self.handleRunInTerminal(output):
                    continue
            if output["type"] == type:
                if event is None or output["event"] == event:
                    if command is None or output["command"] == command:
                        return output
            if output["type"] == "event" and output["event"] == "terminated":
                exit(1)
