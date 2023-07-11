import os
import subprocess
import time
from debugpy.common.messaging import JsonIOStream
from debugpy.common import sockets

from livefromdap.utils.StackRecording import Stackframe, StackRecording
from .JavaLiveAgent import JavaLiveAgent

class JavaLiveAgentPerf(JavaLiveAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_local_variables(self):
        stacktrace = self.get_stackframes(thread_id=self.thread_id, levels=1)
        frame_id = stacktrace[0]["id"]
        scope_name,line_number = stacktrace[0]["name"], stacktrace[0]["line"]
        scope = self.get_scopes(frame_id)[0]
        variables = self.get_variables(scope["variablesReference"])
        return (not self.method_loaded in scope_name), line_number, variables


    def execute(self, clazz, method, args):
        """Execute a method with the given arguments"""
        print(f"Executing {clazz}.{method} with args {args}")
        t1 = time.time()
        if not clazz in self.loaded_classes.keys(): # error, class not loaded
            raise Exception(f"Class {clazz} not loaded")
        self.load_method(method)
        # Setup function breakpoints
        breakpoint = self.get_start_line(self.loaded_classes[clazz], clazz, method) + 1
        self.set_breakpoint(self.loaded_classes[clazz], [breakpoint])
        frame_id = self.get_stackframes(self.thread_id)[0]["id"]
        t4 = time.time()
        # We need to load the arguments into the target program
        self.evaluate(f"runner.args = new Object[{len(args)}]", frame_id)
        for i, arg in enumerate(args):
            if arg.startswith('{') and arg.endswith('}'):
                raise NotImplementedError("Array need to be created, for example replace {'a', 'b'} with new char[]{'a', 'b'}")
            self.evaluate(f"runner.args[{i}] = {arg}", frame_id)
        t5 = time.time()
        # we now continue
        self.next_breakpoint()
        self.wait("event", "stopped")
        t6 = time.time()
        # We can now start the stack recording
        stacktrace = StackRecording()
        times = {
            "init": (t4 - t1) + (t6 - t5),
            "load_arguments": t5 - t4,
            "get_variables": 0,
            "execution_step": 0
        }
        while True:
            t7 = time.time()
            stop, line, variables = self.get_local_variables()
            t8 = time.time()
            stackframe = Stackframe(line, variables)
            stacktrace.add_stackframe(stackframe)
            if stop:
                self.next_breakpoint()
                self.wait("event", event="stopped")
                if variables[0]["name"].startswith(f"->{method}"):
                    return_value = variables[0]["value"]
                else:
                    return_value = None
                break
            self.step(thread_id=self.thread_id)
            self.wait("event", event="stopped")
            t9 = time.time()
            times["get_variables"] += t8 - t7
            times["execution_step"] += t9 - t8
        return return_value, stacktrace, times
