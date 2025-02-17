import subprocess
import os
from abc import ABC, abstractmethod
from typing import Any
from debugpy.common.messaging import JsonIOStream

from livefromdap.utils.StackRecording import StackRecording

class DebuggeeTerminatedError(Exception):
    def __init__(self):
        super().__init__("Debuggee terminated")
    

class BaseLiveAgentInterface(ABC):
    """Interface for the LiveAgent
    This class define all methods that a LiveAgent should implement"""

    @abstractmethod
    def start_server(self) -> None:
        """Start the Agent (start the DAP server)"""
        pass
    
    @abstractmethod
    def stop_server(self) -> None:
        """Stop the Agent"""
        pass
    
    @abstractmethod
    def restart_server(self) -> None:
        """Restart the Agent"""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize and launch the adapter"""
        pass
    
    @abstractmethod
    def load_code(self, *args, **kwargs) -> None:
        """Load code in the debuggee
        If the piece of code is already loaded, it should be reloaded"""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> StackRecording:
        """Execute the method in the debuggee"""
        pass
    
class BaseLiveAgent(BaseLiveAgentInterface):
    """Base class for the LiveAgent
    This class implements the common and utility methods for a LiveAgent
    This class should not be used directly, but should be inherited by a specific LiveAgent"""

    seq : int = 0
    debug : bool = False
    
    io : JsonIOStream

    def __init__(self, **kwargs : Any):
        self.debug = kwargs.get("debug", False)
        self.seq = 0
        
    def __del__(self):
        try:
            self.stop_server()
        except:
            pass

    def new_seq(self):
        self.seq += 1
        return self.seq
        
    def _handleRunInTerminal(self, output : dict):
        """Handle the runInTerminal request from DAP"""
        if output["type"] == "request" and output["command"] == "runInTerminal":
            # if not exists, create the tmp folder
            if not os.path.exists("tmp"):
                os.makedirs("tmp")

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
    
    def set_breakpoint(self, path : str, lines : list):
        """Set breakpoints in the debuggee for the given path and lines

        Args:
            path (str): path of the source file
            lines (list): list of lines to set breakpoints
        """
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

    def set_function_breakpoint(self, names : list):
        """Set breakpoints in the debuggee for the given function names

        Args:
            names (list): list of function names to set breakpoints
        """
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


    def goto_target(self, path : str, line : int):
        """Goto the target with the given id

        Args:
            target_id (int): id of the target to goto
        """
        goto_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "gotoTargets",
            "arguments": {
                "source": {
                    "name": path,
                    "path": path
                },
                "line": line,
            }
        }
        self.io.write_json(goto_request)
        output = self.wait("response", command="gotoTargets")
        return output["body"]["targets"]
    
    def breakpoint_location(self, path : str, line : int):
        """Get the breakpoint location for the given path and line

        Args:
            path (str): path of the source file
            line (int): line to get the breakpoint location
        """
        breakpoint_location_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "breakpointLocations",
            "arguments": {
                "source": {
                    "name": path,
                    "path": path
                },
                "line": line
            }
        }
        self.io.write_json(breakpoint_location_request)
        return self.wait("response", command="breakpointLocations")

    def configuration_done(self):
        """Send the configurationDone request to the debuggee
        """
        complete_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "configurationDone"
        }
        self.io.write_json(complete_request)
    
    def get_stackframes(self, thread_id : int = 1, levels : int = 100) -> list:
        """Get the stackframes from the debuggee

        Args:
            thread_id (int, optional): Defaults to 1.
            levels (int, optional): Number of stackframes to get. Defaults to 100.

        Returns:
            list: list of stackframes
        """
        stackframe_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "stackTrace",
            "arguments": {
                "threadId": thread_id,
                "startFrame": 0,
                "levels": levels
            }
        }
        self.io.write_json(stackframe_request)
        output = self.wait("response", command="stackTrace")
        #print("|".join([frame["name"]+":"+str(frame["line"]) for frame in output["body"]["stackFrames"]]))
        return output["body"]["stackFrames"]
            
    def next_breakpoint(self, thread_id : int = 1):
        """Send the next request to the debuggee

        Args:
            thread_id (int, optional): Defaults to 1.
        """
        continue_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "continue",
            "arguments": {
                "threadId": thread_id
            }
        }
        self.io.write_json(continue_request)
    
    def step(self, thread_id : int = 1):
        """Send the step request to the debuggee

        Args:
            thread_id (int, optional): Defaults to 1.
        """
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
        """Send the stepOut request to the debuggee

        Args:
            thread_id (int, optional): Defaults to 1.
        """
        step_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "stepOut",
            "arguments": {
                "threadId": thread_id
            }
        }
        self.io.write_json(step_request)

    def get_scopes(self, frame_id : int) -> list:
        """Get the scopes from the debuggee for the given frame

        Args:
            frame_id (int): frame id

        Returns:
            list: list of scopes
        """
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
            
    def get_variables(self, scope_id: int) -> list:
        """Get the variables from the debuggee for the given scope

        Args:
            scope_id (int): scope id

        Returns:
            list: list of variables
        """
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
        if "body" not in output:
            return []
        return output["body"]["variables"]

    def evaluate(self, expression : str, frame_id : int, context : str = "repl") -> dict:
        """Evaluate the given expression in the debuggee

        Args:
            expression (str): expression to evaluate
            frame_id (int): frame id context
            context (str, optional): Defaults to "repl".

        Returns:
            dict: result of the evaluation
        """
        evaluate_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "evaluate",
            "arguments": {
                "expression": expression,
                "frameId": frame_id,
                "context": context
            }
        }
        self.io.write_json(evaluate_request)
        return self.wait("response", command="evaluate")

    def wait(self, type: str, event : str = "", command : str = "") -> dict:
        """Wait for a specific message from the debuggee

        Args:
            type (str): type of the message to wait for
            event (str, optional): If type is event, the event to wait for. Defaults to None.
            command (str, optional): If type is response, the command to wait for. Defaults to None.

        Raises:
            Exception: If the debuggee is terminated

        Returns:
            dict: the message received
        """
        while True:
            output : dict = self.io.read_json() # type: ignore
            if self.debug: print(output, flush=True)
            if output["type"] == "request" and output["command"] == "runInTerminal":
                if self._handleRunInTerminal(output):
                    continue
            if output["type"] == "event" and output["event"] == "output":
                if output["body"]["category"] == "stdout":
                    # write the output to stdout
                    print(output["body"]["output"], flush=True, end="")
                elif output["body"]["category"] == "stderr":
                    print(output["body"]["output"], flush=True, end="")
            if output["type"] == type:
                if event == "" or output["event"] == event:
                    if command == "" or output["command"] == command:
                        return output
            if output["type"] == "event" and output["event"] == "terminated":
                raise DebuggeeTerminatedError()

    def step_in(self, thread_id: int = 1, target_id: int | None = None):
        """Send the stepIn request to the debuggee

        Args:
            thread_id (int, optional): Thread ID to step into. Defaults to 1.
            target_id (int, optional): Specific target ID to step into. If provided, 
                                     will step into that specific target. Defaults to None.
        """
        step_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "stepIn",
            "arguments": {
                "threadId": thread_id
            }
        }
        if target_id is not None:
            step_request["arguments"]["targetId"] = target_id
        self.io.write_json(step_request)

    def set_variable(self, variable_reference: int, name: str, value: str) -> dict:
        """Set a new value for the specified variable

        Args:
            variable_reference (int): Reference ID for the variable's container (scope or variable)
            name (str): Name of the variable to set
            value (str): New value to set for the variable

        Returns:
            dict: Response from the debugger containing the updated variable information
        """
        set_variable_request = {
            "seq": self.new_seq(),
            "type": "request", 
            "command": "setVariable",
            "arguments": {
                "variablesReference": variable_reference,
                "name": name,
                "value": value
            }
        }
        self.io.write_json(set_variable_request)
        return self.wait("response", command="setVariable")

    def get_step_in_targets(self, frame_id: int) -> list:
        """Get possible step-in targets for the given stack frame

        Args:
            frame_id (int): ID of the stack frame to get step-in targets for

        Returns:
            list: List of possible step-in targets, each containing target info like id and label
        """
        step_targets_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "stepInTargets",
            "arguments": {
                "frameId": frame_id
            }
        }
        self.io.write_json(step_targets_request)
        response = self.wait("response", command="stepInTargets")
        return response["body"]["targets"]
