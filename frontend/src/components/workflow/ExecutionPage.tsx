import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkflowStore } from '@/store/workflowStore';
import { useWebsocket } from '@/hooks/useWebsocket';
import { AgentCard } from './AgentCard';
import { LogsPanel } from './LogsPanel';
import { ShaderBackground } from '@/components/ui/ShaderBackground';
import { Button } from '@/components/ui/button';

export function ExecutionPage() {
    const navigate = useNavigate();
    const { workflowId, status, progress, agents, partialResults } = useWorkflowStore();

    // Connect to mock WebSocket
    useWebsocket(workflowId ? `ws://localhost:8080/ws/workflow/${workflowId}` : null);

    useEffect(() => {
        if (status === 'completed') {
            setTimeout(() => navigate('/results'), 1000);
        }
    }, [status, navigate]);

    if (!workflowId) return <div>No active workflow</div>;

    return (
        <div className="min-h-screen p-6 relative">
            <ShaderBackground />

            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <div className="bg-surface-card/80 backdrop-blur-md border border-white/10 rounded-2xl p-6">
                    <div className="flex justify-between items-center mb-4">
                        <div>
                            <h1 className="text-2xl font-bold mb-1">Executing Workflow</h1>
                            <div className="text-muted text-sm">ID: {workflowId}</div>
                        </div>
                        <div className="flex gap-2">
                            <Button variant="outline" className="text-error border-error/20 hover:bg-error/10">
                                Cancel
                            </Button>
                            <Button variant="outline">Pause</Button>
                        </div>
                    </div>

                    <div className="w-full h-2 bg-surface rounded-full overflow-hidden">
                        <div
                            className="h-full bg-accent1 transition-all duration-500 ease-out"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column: Agents */}
                    <div className="lg:col-span-2 space-y-4">
                        <h2 className="text-lg font-semibold mb-4">Active Agents</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.values(agents).map((agent) => (
                                <AgentCard key={agent.id} agent={agent} />
                            ))}
                        </div>

                        {/* Partial Results */}
                        <div className="mt-8">
                            <h2 className="text-lg font-semibold mb-4">Live Findings</h2>
                            <div className="bg-surface-card border border-white/10 rounded-xl p-6 min-h-[200px]">
                                {Object.keys(partialResults).length === 0 ? (
                                    <div className="text-muted text-center py-8">Waiting for data...</div>
                                ) : (
                                    <pre className="text-sm text-accent1 overflow-auto">
                                        {JSON.stringify(partialResults, null, 2)}
                                    </pre>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Right Column: Logs */}
                    <div className="lg:col-span-1 h-[600px]">
                        <LogsPanel />
                    </div>
                </div>
            </div>
        </div>
    );
}
