import json
from queue import Queue
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple

from webdemo.services.agent_factory import AgentFactory
from webdemo.services.code_processor import CodeProcessor

class Session:
    def __init__(self, room: str, socketio: Any, language: str, raw: bool = False):
        self.room = room
        self.socketio = socketio
        self.language = language
        self.raw = raw
        self.agent = AgentFactory.create_agent(language, raw)
        self.code = ""
        self.queue: Queue = Queue()
        self.last_execution_line = None
        self.thread: Optional[Thread] = None
        self.is_launched = False
        self.current_inputs = None
        self.launch()
        
    def launch(self) -> None:
        self.thread = Thread(target=self._event_loop, daemon=True)
        self.thread.start()
        self.is_launched = True
        
    def _event_loop(self) -> None:
        while True:
            request = self.queue.get()
            if request is None:
                break
            try:
                self._handle_request(request)
            except Exception as e:
                self.send_status("error", error=str(e))
            self.queue.task_done()
            
    def _handle_request(self, request: Dict[str, Any]) -> None:
        event = request.get("event")
        session_id = request.get("session_id")
        
        if event == "codeChange":
            self._handle_code_change(request)
        elif event == "initialize":
            self.send_status("agent_up", session_id=session_id)
        elif event == "set_source_path":
            self._handle_set_source_path(request)
            
    def _handle_code_change(self, request: Dict[str, Any]) -> None:
        session_id = request["session_id"]
        code = CodeProcessor.clean_code(request["code"], self.language)
        exec_req = CodeProcessor.extract_exec_request(request["code"], self.language)
        
        if not exec_req:
            self.send_status("ready", session_id=session_id)
            return
            
        changed = self.agent.update_code(code)
        
        if self.current_inputs != request.get("outputSelected"):
            self.current_inputs = request.get("outputSelected")
            changed = True
            
        self.send_status("codeChange", session_id=session_id)
        
        if changed or exec_req != self.last_execution_line:
            self._execute_requests(exec_req, request)
            
        self.send_status("ready", session_id=session_id)
        
    def _execute_requests(self, exec_requests: List[Tuple[str, List[str]]], request: Dict[str, Any]) -> None:
        try:
            result = ""
            
            for req in exec_requests:
                method, args = req
                if self.current_inputs and method in self.current_inputs and self.current_inputs.get(method) == args:
                    new_result = self.agent.execute(method, args)
                    result = new_result if not result else CodeProcessor.superpose_strings(result, new_result)
                    
            if result:
                self.send({
                    "event": "executeOutput",
                    "output": result,
                }, json=True)
                self.last_execution_line = exec_requests
            
        except TimeoutError:
            self.send_status("timeout", session_id=request["session_id"])
            
    def _count_iterations(self, line_number: int, result: str) -> None:
        result_data = json.loads(result)
        first_occurrence = None
        last_occurrence = None
        
        for i, trace in enumerate(result_data['stacktrace']):
            if trace["pos"]["line"] == line_number + 1:
                if first_occurrence is None:
                    first_occurrence = i
                last_occurrence = i
                
        if first_occurrence is not None and last_occurrence is not None:
            self.send({
                "event": "addSlider",
                "lineNumber": line_number,
                "start": first_occurrence,
                "end": last_occurrence,
                "length": last_occurrence - first_occurrence
            }, json=True)
            
    def send(self, data: Dict[str, Any], **kwargs) -> None:
        self.socketio.send(data, to=self.room, **kwargs)
        
    def send_status(self, status: str, **kwargs) -> None:
        self.send({
            "event": "status",
            "status": status,
            **kwargs
        }, json=True)
        
    def _handle_set_source_path(self, request: Dict[str, Any]) -> None:
        """Handle a request to set the source path for the agent"""
        session_id = request.get("session_id")
        
        if hasattr(self.agent, "handle_source_path"):
            result = self.agent.handle_source_path(request)
            self.send({
                "event": "source_path_result",
                "result": result
            }, json=True)
        else:
            self.send({
                "event": "source_path_result",
                "result": {"status": "error", "message": "Agent does not support setting source path"}
            }, json=True)
        
        self.send_status("ready", session_id=session_id) 