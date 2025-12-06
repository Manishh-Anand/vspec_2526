import { useEffect, useRef } from 'react';
import { useWorkflowStore } from '../store/workflowStore';

export function useWebsocket(url: string | null) {
    const ws = useRef<WebSocket | null>(null);
    const {
        setConnected,
        setStatus,
        updateAgent,
        addLog,
        setResults,
        updatePartialResults,
        setProgress
    } = useWorkflowStore();

    useEffect(() => {
        if (!url) return;

        ws.current = new WebSocket(url);

        ws.current.onopen = () => {
            setConnected(true);
            console.log('WebSocket connected');
        };

        ws.current.onclose = () => {
            setConnected(false);
            console.log('WebSocket disconnected');
        };

        ws.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleEvent(data);
            } catch (e) {
                console.error('Failed to parse WebSocket message', e);
            }
        };

        return () => {
            ws.current?.close();
        };
    }, [url]);

    const handleEvent = (event: any) => {
        addLog(event);

        switch (event.type) {
            case 'status_change':
                setStatus(event.payload.status);
                if (event.payload.percent_complete) {
                    setProgress(event.payload.percent_complete);
                }
                break;
            case 'agent_start':
                updateAgent(event.payload.agent_id, {
                    name: event.payload.agent_name,
                    role: event.payload.role,
                    status: 'running'
                });
                break;
            case 'agent_thinking':
                updateAgent(event.payload.agent_id, {
                    status: 'thinking',
                    thought: event.payload.thought
                });
                break;
            case 'tool_call':
                updateAgent(event.payload.agent_id, {
                    lastToolCall: event.payload.tool_name
                });
                break;
            case 'tool_result':
                if (event.payload.data_extracted) {
                    Object.entries(event.payload.data_extracted).forEach(([key, value]) => {
                        updatePartialResults(key, value);
                    });
                }
                break;
            case 'agent_complete':
                updateAgent(event.payload.agent_id, {
                    status: 'success',
                    output: event.payload.output
                });
                break;
            case 'workflow_complete':
                setStatus('completed');
                setResults(event.payload.results);
                break;
            case 'error':
                if (event.payload.agent_id) {
                    updateAgent(event.payload.agent_id, {
                        status: 'failed'
                    });
                }
                break;
        }
    };
}
