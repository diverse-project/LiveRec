from typing import Dict, Optional
import uuid
from webdemo.models.session import Session

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._sessions_to_sid: Dict[str, str] = {}
        
    def create_session(self, socketio, language: str, raw: bool = False) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = Session(session_id, socketio, language, raw)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)
    
    def remove_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            self._sessions[session_id].agent.agent.stop_server()
            del self._sessions[session_id]
            
    def map_socket_to_session(self, socket_id: str, session_id: str) -> None:
        self._sessions_to_sid[socket_id] = session_id
        
    def get_session_by_socket(self, socket_id: str) -> Optional[str]:
        return self._sessions_to_sid.get(socket_id)
        
    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions 