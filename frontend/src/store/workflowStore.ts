import { create } from 'zustand';

export interface Agent {
    id: string;
    name: string;
    role: string;
    status: 'idle' | 'thinking' | 'running' | 'success' | 'failed';
    thought?: string;
    lastToolCall?: string;
    output?: string;
    logs: string[];
}

export interface WorkflowState {
    workflowId: string | null;
    status: 'idle' | 'initiated' | 'running' | 'completed' | 'failed' | 'paused';
    progress: number;
    agents: Record<string, Agent>;
    logs: any[];
    results: any | null;
    partialResults: Record<string, any>;
    connected: boolean;

    setWorkflowId: (id: string) => void;
    setStatus: (status: WorkflowState['status']) => void;
    setProgress: (progress: number) => void;
    updateAgent: (agentId: string, update: Partial<Agent>) => void;
    addLog: (log: any) => void;
    setResults: (results: any) => void;
    updatePartialResults: (key: string, value: any) => void;
    setConnected: (connected: boolean) => void;
    reset: () => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
    workflowId: null,
    status: 'idle',
    progress: 0,
    agents: {},
    logs: [],
    results: null,
    partialResults: {},
    connected: false,

    setWorkflowId: (id) => set({ workflowId: id }),
    setStatus: (status) => set({ status }),
    setProgress: (progress) => set({ progress }),
    updateAgent: (agentId, update) => set((state) => {
        const currentAgent = state.agents[agentId] || {
            id: agentId,
            name: 'Unknown Agent',
            role: 'Worker',
            status: 'idle',
            logs: []
        };
        return {
            agents: {
                ...state.agents,
                [agentId]: { ...currentAgent, ...update }
            }
        };
    }),
    addLog: (log) => set((state) => ({ logs: [...state.logs, log] })),
    setResults: (results) => set({ results }),
    updatePartialResults: (key, value) => set((state) => ({
        partialResults: { ...state.partialResults, [key]: value }
    })),
    setConnected: (connected) => set({ connected }),
    reset: () => set({
        workflowId: null,
        status: 'idle',
        progress: 0,
        agents: {},
        logs: [],
        results: null,
        partialResults: {},
        connected: false
    })
}));
