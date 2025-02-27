from abc import ABC, abstractmethod
import json
from threading import Thread
from typing import Any, Type

from livefromdap.utils.StackRecording import StackRecording
from prettyprinter.TreeSitterPrettyPrinter import TreeSitterPrettyPrinter

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:  # type: ignore
            self._return = self._target(*self._args, **self._kwargs)  # type: ignore

    def join(self, *args):
        Thread.join(self, *args)
        return self._return

class AutoLiveAgent(ABC):
    """Interface for the AutoLiveAgent
    This class define method for webdemo's agent"""

    @abstractmethod
    def update_code(self, code):
        """Update the code in the debuggee"""
        pass

    @abstractmethod
    def execute(self, method, args):
        """Execute the method in the debuggee"""
        pass

    @abstractmethod
    def restart(self):
        """Restart the debuggee"""
        pass

class BaseAutoLiveAgent(AutoLiveAgent):
    """Base implementation with common functionality for all agents"""
    
    def __init__(self, raw=False):
        self.raw = raw
        self.previous_ast = None
        self.source_path = ""
    def construct_result_json(self, method, output : tuple[Any, StackRecording], printer_class : Type[TreeSitterPrettyPrinter]):
        return_value, stacktrace = output
        if self.raw:
            stacktrace.last_stackframe.variables.append({"name": "return", "value": return_value})
            return json.dumps({
                "return_value": return_value,
                "stacktrace": stacktrace.to_json()
            })
        printer = printer_class(self.source_path, method)
        return printer.pretty_print(stacktrace, return_value=return_value)
