from typing import Any
from webdemo.agents import (
    AutoCLiveAgent, 
    AutoJavaLiveAgent, 
    AutoPyJSDynamicAgent,
    AutoPythonLiveAgent,
    AutoJavascriptLiveAgent,
    AutoJavaJDILiveAgent,
    AutoPyJSAgent,
    AutoGoAgent
)

class AgentFactory:
    @staticmethod
    def create_agent(language: str, raw: bool = False) -> Any:
        agents = {
            "c": AutoCLiveAgent,
            "java": AutoJavaLiveAgent,
            "python": AutoPythonLiveAgent,
            "javascript": AutoJavascriptLiveAgent,
            "pyjs": AutoPyJSDynamicAgent,
            "go": AutoGoAgent
        }
        
        if language not in agents:
            raise NotImplementedError(f"Language {language} not supported")
            
        return agents[language](raw=raw) 