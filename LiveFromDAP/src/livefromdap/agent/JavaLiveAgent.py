import os
import subprocess
import time
from debugpy.common.messaging import JsonIOStream
from debugpy.common import sockets

from livefromdap.utils.StackRecording import Stackframe, StackRecording
from .BaseLiveAgent import BaseLiveAgent

class JavaLiveAgent(BaseLiveAgent):
    def __init__(self, target_file : str, target_class_path : str, target_class_name : str, target_methods : list[str] = [], auto_compile : bool = True,**kwargs):
        super().__init__(**kwargs)
        self.ls_server = None
        self.target_file = target_file
        self.target_class_path = target_class_path
        self.target_class_name = target_class_name
        self.target_methods = target_methods
        self.auto_compile = auto_compile
        if auto_compile:
            self.compile_command = kwargs.get("compile_command", f"javac -g {self.target_class_name}")
        
        self.runner_path = kwargs.get("runner_path", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runner")))
        self.runner_file = kwargs.get("runner_file", "JavaRunner.java")
        self.project_name = None
        self.method_loaded = False

    def start_ls_server(self):
        ls_server_path = os.path.join(os.path.dirname(__file__), "..", "bin", "jdt-language-server", "bin", "jdtls")
        self.ls_server = subprocess.Popen(
            [ls_server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.ls_io = JsonIOStream.from_process(self.ls_server)
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
            "processId": self.ls_server.pid,
            "rootPath": self.runner_path,
            "rootUri": f"file://{self.runner_path}",
            "capabilities": {
                "workspace": {
                    "applyEdit": True,
                    "workspaceEdit": {
                        "documentChanges": True,
                        "resourceOperations": [
                            "create",
                            "rename",
                            "delete"
                        ],
                        "failureHandling": "textOnlyTransactional",
                        "normalizesLineEndings": True,
                        "changeAnnotationSupport": {
                            "groupsOnLabel": True
                        }
                    },
                    "configuration": True,
                    "didChangeWatchedFiles": {
                        "dynamicRegistration": True,
                        "relativePatternSupport": True
                    },
                    "symbol": {
                        "dynamicRegistration": True,
                        "symbolKind": {
                            "valueSet": [
                                1,
                                2,
                                3,
                                4,
                                5,
                                6,
                                7,
                                8,
                                9,
                                10,
                                11,
                                12,
                                13,
                                14,
                                15,
                                16,
                                17,
                                18,
                                19,
                                20,
                                21,
                                22,
                                23,
                                24,
                                25,
                                26
                            ]
                        },
                        "tagSupport": {
                            "valueSet": [
                                1
                            ]
                        },
                        "resolveSupport": {
                            "properties": [
                                "location.range"
                            ]
                        }
                    },
                    "codeLens": {
                        "refreshSupport": True
                    },
                    "executeCommand": {
                        "dynamicRegistration": True
                    },
                    "didChangeConfiguration": {
                        "dynamicRegistration": True
                    },
                    "workspaceFolders": True,
                    "semanticTokens": {
                        "refreshSupport": True
                    },
                    "fileOperations": {
                        "dynamicRegistration": True,
                        "didCreate": True,
                        "didRename": True,
                        "didDelete": True,
                        "willCreate": True,
                        "willRename": True,
                        "willDelete": True
                    },
                    "inlineValue": {
                        "refreshSupport": True
                    },
                    "inlayHint": {
                        "refreshSupport": True
                    },
                    "diagnostics": {
                        "refreshSupport": True
                    }
                },
                "textDocument": {
                    "publishDiagnostics": {
                        "relatedInformation": True,
                        "versionSupport": False,
                        "tagSupport": {
                            "valueSet": [
                                1,
                                2
                            ]
                        },
                        "codeDescriptionSupport": True,
                        "dataSupport": True
                    },
                    "synchronization": {
                        "dynamicRegistration": True,
                        "willSave": True,
                        "willSaveWaitUntil": True,
                        "didSave": True
                    },
                    "completion": {
                        "dynamicRegistration": True,
                        "contextSupport": True,
                        "completionItem": {
                            "snippetSupport": True,
                            "commitCharactersSupport": True,
                            "documentationFormat": [
                                "markdown",
                                "plaintext"
                            ],
                            "deprecatedSupport": True,
                            "preselectSupport": True,
                            "tagSupport": {
                                "valueSet": [
                                    1
                                ]
                            },
                            "insertReplaceSupport": True,
                            "resolveSupport": {
                                "properties": [
                                    "documentation",
                                    "detail",
                                    "additionalTextEdits"
                                ]
                            },
                            "insertTextModeSupport": {
                                "valueSet": [
                                    1,
                                    2
                                ]
                            },
                            "labelDetailsSupport": True
                        },
                        "insertTextMode": 2,
                        "completionItemKind": {
                            "valueSet": [
                                1,
                                2,
                                3,
                                4,
                                5,
                                6,
                                7,
                                8,
                                9,
                                10,
                                11,
                                12,
                                13,
                                14,
                                15,
                                16,
                                17,
                                18,
                                19,
                                20,
                                21,
                                22,
                                23,
                                24,
                                25
                            ]
                        },
                        "completionList": {
                            "itemDefaults": [
                                "commitCharacters",
                                "editRange",
                                "insertTextFormat",
                                "insertTextMode"
                            ]
                        }
                    },
                    "hover": {
                        "dynamicRegistration": True,
                        "contentFormat": [
                            "markdown",
                            "plaintext"
                        ]
                    },
                    "signatureHelp": {
                        "dynamicRegistration": True,
                        "signatureInformation": {
                            "documentationFormat": [
                                "markdown",
                                "plaintext"
                            ],
                            "parameterInformation": {
                                "labelOffsetSupport": True
                            },
                            "activeParameterSupport": True
                        },
                        "contextSupport": True
                    },
                    "definition": {
                        "dynamicRegistration": True,
                        "linkSupport": True
                    },
                    "references": {
                        "dynamicRegistration": True
                    },
                    "documentHighlight": {
                        "dynamicRegistration": True
                    },
                    "documentSymbol": {
                        "dynamicRegistration": True,
                        "symbolKind": {
                            "valueSet": [
                                1,
                                2,
                                3,
                                4,
                                5,
                                6,
                                7,
                                8,
                                9,
                                10,
                                11,
                                12,
                                13,
                                14,
                                15,
                                16,
                                17,
                                18,
                                19,
                                20,
                                21,
                                22,
                                23,
                                24,
                                25,
                                26
                            ]
                        },
                        "hierarchicalDocumentSymbolSupport": True,
                        "tagSupport": {
                            "valueSet": [
                                1
                            ]
                        },
                        "labelSupport": True
                    },
                    "codeAction": {
                        "dynamicRegistration": True,
                        "isPreferredSupport": True,
                        "disabledSupport": True,
                        "dataSupport": True,
                        "resolveSupport": {
                            "properties": [
                                "edit"
                            ]
                        },
                        "codeActionLiteralSupport": {
                            "codeActionKind": {
                                "valueSet": [
                                    "",
                                    "quickfix",
                                    "refactor",
                                    "refactor.extract",
                                    "refactor.inline",
                                    "refactor.rewrite",
                                    "source",
                                    "source.organizeImports"
                                ]
                            }
                        },
                        "honorsChangeAnnotations": False
                    },
                    "codeLens": {
                        "dynamicRegistration": True
                    },
                    "formatting": {
                        "dynamicRegistration": True
                    },
                    "rangeFormatting": {
                        "dynamicRegistration": True
                    },
                    "onTypeFormatting": {
                        "dynamicRegistration": True
                    },
                    "rename": {
                        "dynamicRegistration": True,
                        "prepareSupport": True,
                        "prepareSupportDefaultBehavior": 1,
                        "honorsChangeAnnotations": True
                    },
                    "documentLink": {
                        "dynamicRegistration": True,
                        "tooltipSupport": True
                    },
                    "typeDefinition": {
                        "dynamicRegistration": True,
                        "linkSupport": True
                    },
                    "implementation": {
                        "dynamicRegistration": True,
                        "linkSupport": True
                    },
                    "colorProvider": {
                        "dynamicRegistration": True
                    },
                    "foldingRange": {
                        "dynamicRegistration": True,
                        "rangeLimit": 5000,
                        "lineFoldingOnly": True,
                        "foldingRangeKind": {
                            "valueSet": [
                                "comment",
                                "imports",
                                "region"
                            ]
                        },
                        "foldingRange": {
                            "collapsedText": False
                        }
                    },
                    "declaration": {
                        "dynamicRegistration": True,
                        "linkSupport": True
                    },
                    "selectionRange": {
                        "dynamicRegistration": True
                    },
                    "callHierarchy": {
                        "dynamicRegistration": True
                    },
                    "semanticTokens": {
                        "dynamicRegistration": True,
                        "tokenTypes": [
                            "namespace",
                            "type",
                            "class",
                            "enum",
                            "interface",
                            "struct",
                            "typeParameter",
                            "parameter",
                            "variable",
                            "property",
                            "enumMember",
                            "event",
                            "function",
                            "method",
                            "macro",
                            "keyword",
                            "modifier",
                            "comment",
                            "string",
                            "number",
                            "regexp",
                            "operator",
                            "decorator"
                        ],
                        "tokenModifiers": [
                            "declaration",
                            "definition",
                            "readonly",
                            "static",
                            "deprecated",
                            "abstract",
                            "async",
                            "modification",
                            "documentation",
                            "defaultLibrary"
                        ],
                        "formats": [
                            "relative"
                        ],
                        "requests": {
                            "range": True,
                            "full": {
                                "delta": True
                            }
                        },
                        "multilineTokenSupport": False,
                        "overlappingTokenSupport": False,
                        "serverCancelSupport": True,
                        "augmentsSyntaxTokens": True
                    },
                    "linkedEditingRange": {
                        "dynamicRegistration": True
                    },
                    "typeHierarchy": {
                        "dynamicRegistration": True
                    },
                    "inlineValue": {
                        "dynamicRegistration": True
                    },
                    "inlayHint": {
                        "dynamicRegistration": True,
                        "resolveSupport": {
                            "properties": [
                                "tooltip",
                                "textEdits",
                                "label.tooltip",
                                "label.location",
                                "label.command"
                            ]
                        }
                    },
                    "diagnostic": {
                        "dynamicRegistration": True,
                        "relatedDocumentSupport": False
                    }
                },
                "window": {
                    "showMessage": {
                        "messageActionItem": {
                            "additionalPropertiesSupport": True
                        }
                    },
                    "showDocument": {
                        "support": True
                    },
                    "workDoneProgress": True
                },
                "general": {
                    "staleRequestSupport": {
                        "cancel": True,
                        "retryOnContentModified": [
                            "textDocument/semanticTokens/full",
                            "textDocument/semanticTokens/range",
                            "textDocument/semanticTokens/full/delta"
                        ]
                    },
                    "regularExpressions": {
                        "engine": "ECMAScript",
                        "version": "ES2020"
                    },
                    "markdown": {
                        "parser": "marked",
                        "version": "1.1.0"
                    },
                    "positionEncodings": [
                        "utf-16"
                    ]
                },
                "notebookDocument": {
                    "synchronization": {
                        "dynamicRegistration": True,
                        "executionSummarySupport": True
                    }
                }
            },
            "initializationOptions": {
                "bundles": [
                    "/home/jbdod/.vscode-oss/extensions/vscjava.vscode-java-debug-0.52.0/server/com.microsoft.java.debug.plugin-0.47.0.jar",
                ],
                "workspaceFolders": [
                    f"file://{self.runner_path}"
                ],
                "settings": {
                    "java": {
                        "home": "/usr/lib/jvm/java-20-openjdk",
                        "jdt": {
                            "ls": {
                                "java": {
                                    "home": "/usr/lib/jvm/java-20-openjdk"
                                },
                                "vmargs": "",
                                "lombokSupport": {
                                    "enabled": True
                                },
                                "protobufSupport": {
                                    "enabled": True
                                },
                                "androidSupport": {
                                    "enabled": False
                                }
                            }
                        },
                        "errors": {
                            "incompleteClasspath": {
                                "severity": "warning"
                            }
                        },
                        "configuration": {
                            "updateBuildConfiguration": "interactive",
                            "maven": {
                                "userSettings": None
                            }
                        },
                        "trace": {
                            "server": "verbose"
                        },
                        "import": {
                            "gradle": {
                                "enabled": True
                            },
                            "maven": {
                                "enabled": True
                            },
                            "exclusions": [
                                "**/node_modules/**",
                                "**/.metadata/**",
                                "**/archetype-resources/**",
                                "**/META-INF/maven/**",
                                "/**/test/**"
                            ]
                        },
                        "referencesCodeLens": {
                            "enabled": False
                        },
                        "signatureHelp": {
                            "enabled": False
                        },
                        "implementationsCodeLens": {
                            "enabled": False
                        },
                        "format": {
                            "enabled": True
                        },
                        "saveActions": {
                            "organizeImports": False
                        },
                        "contentProvider": {
                            "preferred": None
                        },
                        "autobuild": {
                            "enabled": True
                        },
                        "project": {
                            "referencedLibraries": [
                                "lib/**/*.jar"
                            ],
                            "importOnFirstTimeStartup": "automatic",
                            "importHint": True,
                            "resourceFilters": [
                                "node_modules",
                                "\\.git"
                            ],
                            "encoding": "ignore",
                            "exportJar": {
                                "targetPath": "${workspaceFolder}/${workspaceFolderBasename}.jar"
                            },
                            "explorer": {
                                "showNonJavaResources": True
                            }
                        },
                        "completion": {
                            "favoriteStaticMembers": [
                                "org.junit.Assert.*",
                                "org.junit.Assume.*",
                                "org.junit.jupiter.api.Assertions.*",
                                "org.junit.jupiter.api.Assumptions.*",
                                "org.junit.jupiter.api.DynamicContainer.*",
                                "org.junit.jupiter.api.DynamicTest.*"
                            ],
                            "importOrder": [
                                "java",
                                "javax",
                                "com",
                                "org"
                            ]
                        }
                    }
                }
            },
            "trace": "verbose",
            "workspaceFolders": [
                {
                    "uri": f"file://{self.runner_path}",
                    "name": "runner"
                }
            ],
        }
        })
        while True:
            response = self.ls_io.read_json()
            if self.debug: print("[LanguageServer]", response)
            if "id" in response and response["id"] == 1:
                break
        # Send the initialized notification
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        })
        runner_file_path = os.path.join(self.runner_path, self.runner_file)
        with open(runner_file_path, "r") as f:
            runner_code = f.read()
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "method": "textDocument/didOpen",
            "params": {
                "textDocument": {
                    "uri": f"file://{runner_file_path}",
                    "languageId": "java",
                    "version": 1,
                    "text": runner_code
                }
            }
        })
        while True:
            response = self.ls_io.read_json()
            if self.debug: print("[LanguageServer]", response)
            if "method" in response and response["method"] == "workspace/executeClientCommand" and response["params"]["command"] == "_java.reloadBundles.command":
                break
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "id": 30,
            "method": "workspace/executeCommand",
            "params": {
                "title": "Java: Getting Started",
                "command": "java.project.getSettings",
                "arguments": [
                    f"file://{self.runner_path}",
                    [
                        "org.eclipse.jdt.ls.core.outputPath",
                    ]
                ]
            }
        })
        while True:
            response = self.ls_io.read_json()
            if self.debug: print("[LanguageServer]",response)
            if "id" in response and response["id"] == 30:
                break
        output_path = response["result"]["org.eclipse.jdt.ls.core.outputPath"]
        self.project_name = output_path.split("/")[-2]



    def restart_ls_server(self):
        self.ls_server.kill()
        self.start_ls_server()

    def start_server(self):
        """Create a subprocess with the agent"""
        if self.ls_server is None:
            self.start_ls_server()
        # check if ls server crashed
        if self.ls_server.poll() is not None:
            self.restart_ls_server()
        self.ls_io.write_json({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "workspace/executeCommand",
            "params": {
                "title": "Java: Getting Started",
                "command": "vscode.java.startDebugSession",
                "arguments": []
            }
        })
        debug_serport = None
        while True:
            response = self.ls_io.read_json()
            if self.debug: print("[LanguageServer]", response)
            if "id" in response and response["id"] == 2:
                debug_serport = response["result"]
                break
        
        self.server = sockets.create_client()
        self.server.connect(("localhost", debug_serport))
        self.io = JsonIOStream.from_socket(self.server)
    
    def restart_server(self):
        self.server.close()
        self.start_server()
         
    def initialize(self):
        """Send data to the agent"""
        init_request = init_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "initialize",
            "arguments": {
                "clientID": "vscode",
                "clientName": "Visual Studio Code",
                "adapterID": "java",
                "pathFormat": "path",
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "supportsVariableType": True,
                "supportsVariablePaging": True,
                "supportsRunInTerminalRequest": True,
                "locale": "en",
                "supportsProgressReporting": True,
                "supportsInvalidatedEvent": True,
                "supportMemoryReferences": True,
                "supportsArgsCanBeInterpretedByShell": True,
                "supportsMemoryEvent": True,
                "supportsStartDebuggingRequest": True,
            }
        }
        launch_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "launch",
            "arguments": {
                "type": "java",
                "name": "Launch Current File",
                "request": "launch",
                "cwd": self.runner_path,
                "console": "internalConsole",
                "stopOnEntry": False,
                "mainClass": "JavaRunner",
                "args": "",
                "vmArgs": "",
                "env": {},
                "noDebug": False,
                "classPaths": [
                    f"{self.runner_path}/bin",
                    self.runner_path,
                    self.target_class_path,
                ],
                "projectName": self.project_name,
            }
        }
        self.io.write_json(init_request)
        self.io.write_json(launch_request)
        self.wait("event", "initialized")
        self._setup_breakpoint()
        brk = self.wait("event", "stopped")
        self.thread_id = brk["body"]["threadId"]


    def stop(self):
        """Stop the target program"""
        self.ls_server.kill()
        self.server.close()
        

    def compile(self):
        """Compile the target file"""
        pass
    
    def _setup_breakpoint(self):
        self.set_breakpoint(os.path.join(self.runner_path, self.runner_file), [27, 28])
        self.set_breakpoint(os.path.abspath(self.target_file), [2,3,4])
        #self.set_function_breakpoint(["main"])
        self.configuration_done()

    def load_code(self):
        if self.method_loaded:
            pass # TODO: hot reload procedure
        frame_id = self.get_stackframes(self.thread_id)[0]["id"]
        self.evaluate(f"runner.loadMethod(\"{self.target_class_name}\", \"{self.target_methods[0]}\")", frame_id)
        self.method_loaded = True

    def get_threads(self):
        request= {
            "seq": self.new_seq(),
            "type": "request",
            "command": "threads",
            "arguments": {}
        }
        self.io.write_json(request)
        response = self.wait("response", command="threads")
        return response["body"]["threads"]
            

    def evaluate(self, expression, frame_id, context="repl"):
        evaluate_request = {
            "seq": self.new_seq(),
            "type": "request",
            "command": "evaluate",
            "arguments": {
                "expression": expression,
                "context": context,
                "frameId": frame_id,
            }
        }
        self.io.write_json(evaluate_request)
        self.wait("response", command="evaluate")

    def get_local_variables(self):
        stacktrace = self.get_stackframes(thread_id=self.thread_id)
        frame_id = stacktrace[0]["id"]
        scope_name,line_number = stacktrace[0]["name"], stacktrace[0]["line"]
        scope = self.get_scopes(frame_id)[0]
        variables = self.get_variables(scope["variablesReference"])
        return (not self.target_methods[0] in scope_name), line_number, variables

    
    def execute(self, method, args):
        """Execute a method with the given arguments"""
        if method not in self.target_methods:
            raise ValueError(f"Method {method} not found")
        frame_id = self.get_stackframes(self.thread_id)[0]["id"]
        # We need to load the arguments into the target program
        self.evaluate(f"runner.args = new Object[{len(args)}]", frame_id)
        for i, arg in enumerate(args):
            if arg.startswith('{') and arg.endswith('}'):
                raise NotImplementedError("Array need to be created, for example replace {'a', 'b'} with new char[]{'a', 'b'}")
            self.evaluate(f"runner.args[{i}] = {arg}", frame_id)
        # we now continue
        self.next_breakpoint()
        self.wait("event", "stopped")
        # We can now start the stack recording
        stacktrace = StackRecording()
        while True:
            stop, line, variables = self.get_local_variables()
            stackframe = Stackframe(line, variables)
            stacktrace.add_stackframe(stackframe)
            if stop:
                self.next_breakpoint()
                self.wait("event", event="stopped")
                return_value = None # TODO: get return value
                break
            self.step(thread_id=self.thread_id)
            self.wait("event", event="stopped")
        return return_value, stacktrace
