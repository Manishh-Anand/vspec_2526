import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({ port: 8080 });

console.log('Mock WebSocket Server running on ws://localhost:8080');

wss.on('connection', (ws) => {
    console.log('Client connected');

    // Simulate workflow events
    const workflowId = 'workflow_' + Date.now();
    let step = 0;

    const events = [
        { type: 'status_change', payload: { status: 'initiated', percent_complete: 0 } },
        { type: 'agent_start', payload: { agent_id: 'agent_1', agent_name: 'ResearchAgent', role: 'Researcher' } },
        { type: 'agent_thinking', payload: { agent_id: 'agent_1', thought: 'Searching for relevant information...' } },
        { type: 'tool_call', payload: { agent_id: 'agent_1', tool_name: 'search_web' } },
        { type: 'status_change', payload: { status: 'running', percent_complete: 25 } },
        { type: 'tool_result', payload: { agent_id: 'agent_1', tool_name: 'search_web', data_extracted: { 'topic': 'MetaFlow' } } },
        { type: 'agent_complete', payload: { agent_id: 'agent_1', output: 'Found info on MetaFlow' } },
        { type: 'agent_start', payload: { agent_id: 'agent_2', agent_name: 'WriterAgent', role: 'Writer' } },
        { type: 'status_change', payload: { status: 'running', percent_complete: 50 } },
        { type: 'agent_thinking', payload: { agent_id: 'agent_2', thought: 'Drafting the report...' } },
        { type: 'status_change', payload: { status: 'running', percent_complete: 75 } },
        { type: 'agent_complete', payload: { agent_id: 'agent_2', output: 'Report drafted.' } },
        { type: 'workflow_complete', payload: { results: { summary: 'MetaFlow is a meta-automation platform.' } } }
    ];

    const interval = setInterval(() => {
        if (step < events.length) {
            const event = {
                id: `evt_${Date.now()}`,
                workflow_id: workflowId,
                timestamp: new Date().toISOString(),
                ...events[step]
            };
            ws.send(JSON.stringify(event));
            step++;
        } else {
            clearInterval(interval);
        }
    }, 1500);

    ws.on('close', () => {
        console.log('Client disconnected');
        clearInterval(interval);
    });
});
