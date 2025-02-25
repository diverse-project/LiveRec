from typing import Dict

class Config:
    SECRET_KEY = 'secret!'
    
    LANGUAGE_PREFIXES: Dict[str, str] = {
        "python": "#@",
        "pyjs": "#@",
        "java": "//@",
        "go": "//@",
        "c": "//@",
        "javascript": "//@"
    }
    
    @classmethod
    def get_language_prefix(cls, language: str) -> str:
        if language not in cls.LANGUAGE_PREFIXES:
            raise NotImplementedError(f"Language {language} not supported")
        return cls.LANGUAGE_PREFIXES[language] 