import re
from typing import List, Optional, Tuple
from webdemo.config import Config

class CodeProcessor:
    @staticmethod
    def clean_code(code: str, language: str) -> str:
        prefix = Config.get_language_prefix(language)
        return "\n".join(
            ["" if line.strip().startswith(prefix) else line 
             for line in code.split("\n")]
        )
    
    @staticmethod
    def extract_exec_request(code: str, language: str) -> Optional[List[Tuple[str, List[str]]]]:
        result = []
        prefix = Config.get_language_prefix(language)
        
        for line in code.split("\n"):
            line = line.strip()
            if line.startswith(prefix):
                exec_request = line[len(prefix):].strip()
                if "(" in exec_request and exec_request.endswith(")"):
                    method = exec_request.split("(")[0]
                    args_str = exec_request.split("(")[1][:-1]
                    args = re.split(r',(?![^\[\]\(\)\{\}]*[\]\)\}])', args_str)
                    if not "" in map(lambda x: x.strip(), args):
                        result.append((method, list(map(lambda x: x.strip(), args))))
                        
        return result if result else None
    
    @staticmethod
    def superpose_strings(first: str, second: str) -> str:
        first_list = first.split('\n')
        second_list = second.split('\n')
        
        for i in range(min(len(first_list), len(second_list))):
            if second_list[i]:
                first_list[i] = second_list[i] + '\n'
            else:
                first_list[i] = first_list[i] + '\n'
                
        return ''.join(first_list) 