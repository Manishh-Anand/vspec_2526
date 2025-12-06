export const api = {
    createWorkflow: async (_prompt: string) => {
        // Mock implementation
        return {
            workflow_id: 'workflow_' + Date.now(),
            status: 'initiated',
            websocket_url: 'ws://localhost:8080'
        };
    },
    getResults: async (_workflowId: string) => {
        return { summary: 'Mock results' };
    }
};
