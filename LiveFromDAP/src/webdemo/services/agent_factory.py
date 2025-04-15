from typing import Any
from webdemo.agents import (
    AutoCLiveAgent, 
    AutoJavaLiveAgent,
    AutoPythonLiveAgent,
    AutoJavascriptLiveAgent,
    AutoJavaJDILiveAgent,
    AutoGoAgent,
    AutoPolyglotAgent,
    AutoPolyLiveAgent
)

class AgentFactory:
    @staticmethod
    def create_agent(language: str, raw: bool = False) -> Any:
        agents = {
            "c": AutoCLiveAgent,
            "java": AutoJavaLiveAgent,
            "python": AutoPythonLiveAgent,
            "javascript": AutoJavascriptLiveAgent,
            "go": AutoGoAgent,
            "polyglot": AutoPolyglotAgent,
            "polyglot_livex": AutoPolyLiveAgent,
        }
        
        if language not in agents:
            raise NotImplementedError(f"Language {language} not supported")
            
        return agents[language](raw=raw) 