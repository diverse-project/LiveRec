export interface FileSession {
    sessionId: string;
    filePath: string;
}

export interface ExecutionFrame {
    pos: { line: number };
    variables: Array<{ name: string; type: string; value: string }>;
    return_value?: string;
}

export interface ExecutionData {
    stacktrace: ExecutionFrame[];
    return_value: string;
}

export interface ServerMessage {
    event: string;
    status?: string;
    output?: string;
    data?: any;
    session_id?: string;
}

export interface FunctionData {
    name: string;
    line: number;
} 