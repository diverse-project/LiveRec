LS_INITIALIZE_CAPABILITIES = {
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
}

LS_INITIALIZE_SETTINGS = {
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