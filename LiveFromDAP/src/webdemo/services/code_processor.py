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
    


import re
from typing import List, Optional, Tuple
from webdemo.config import Config
import requests as LivExReq

class LivExCodeProcessor:
    @staticmethod
    def clean_code(code: str, exec_req, language: str) -> str:
        prefix = Config.get_language_prefix(language)
        cleaned_code = ""
        line_number = 0
        for line in code.split("\n"):
            line_number += 1
            if line.strip().startswith(prefix):
                for req in exec_req:
                    for probe in req[2]: #TODO: check replacements, regexp match/replace the next line
                        if probe["line"] == line_number:
                            cond = probe["condition"]
                            line = line.split(prefix.split("@")[0])[0] + LivExCodeProcessor.get_probe_line(cond, line_number, probe["expr"]["target"], language)
            cleaned_code += line + "\n"
        return cleaned_code
    
    @staticmethod
    def get_probe_line(cond, line_number, expr, language="python"):
        condition = LivExCodeProcessor.convert_potential_true_value(cond, language).strip() # default value for probe condition is "True" in LivEx; not valid for all languages, so we convert
        if language == "python" or language == "polyglot_livex":
            return f"if {condition}: probe({line_number}, globals(), locals(), \"{expr}\")" # replace comment-probe with properly indented call to probe function
        elif language == "javascript":
            return f"if ({condition}) {{ global.probe({line_number}, \"{expr}\"); }}"
        else:
            raise NotImplementedError()

    @staticmethod
    def convert_potential_true_value(condition, language="python"):
        if language == "javascript":
            return "true" if condition == "True" else condition # JS needs lowercase boolean literal
        else:
            return condition

    @staticmethod
    def extract_exec_request(code, language="python", example_name=None):
        result = []
        exec_requests = []
        prefix = Config.get_language_prefix(language)
        line_number = 0
        for line in code.split("\n"):
            line_number += 1
            line = line.strip()
            if line.startswith(prefix):
                if "probe" in line:
                    exec_requests.append(f"[{line_number}]" + line[len(prefix):].strip())
                else:
                    exec_requests.append(line[len(prefix):].strip())
        exec_request = "\n".join(exec_requests)
        r = LivExReq.post(url="http://172.17.0.1:3000/api/code", # note: this is the URL assuming this app is ran from a docker
                              json={"example": exec_request})
        response = r.json()
        if example_name != None:
            example = response[example_name]
            return (example["method"], 
                    list(map(lambda x : str(x), 
                            example["args"])),
                            example["probes"],
                            )
        for ex in response:
            example = response[ex]
            result.append((example["method"], 
                    list(map(lambda x : str(x), 
                            example["args"])),
                            example["probes"],
                            ))
        if len(result) == 0:
            return None
        return result
    
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