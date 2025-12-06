import { motion } from 'framer-motion';
import type { Agent } from '@/store/workflowStore';
import { CheckCircle, Circle, Loader2, XCircle } from 'lucide-react';

export function AgentCard({ agent }: { agent: Agent }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-surface-card border border-white/10 rounded-xl p-4"
        >
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-surface flex items-center justify-center border border-white/10">
                        {agent.status === 'running' || agent.status === 'thinking' ? (
                            <Loader2 className="w-4 h-4 animate-spin text-accent1" />
                        ) : agent.status === 'success' ? (
                            <CheckCircle className="w-4 h-4 text-success" />
                        ) : agent.status === 'failed' ? (
                            <XCircle className="w-4 h-4 text-error" />
                        ) : (
                            <Circle className="w-4 h-4 text-muted" />
                        )}
                    </div>
                    <div>
                        <div className="font-medium text-white">{agent.name}</div>
                        <div className="text-xs text-muted">{agent.role}</div>
                    </div>
                </div>
                <div className={`text-xs px-2 py-1 rounded-full ${agent.status === 'running' ? 'bg-accent1/20 text-accent1' :
                    agent.status === 'success' ? 'bg-success/20 text-success' :
                        agent.status === 'failed' ? 'bg-error/20 text-error' :
                            'bg-white/5 text-muted'
                    }`}>
                    {agent.status}
                </div>
            </div>

            {agent.thought && (
                <div className="mb-3 p-3 bg-surface/50 rounded-lg text-sm text-muted italic border-l-2 border-accent1">
                    "{agent.thought}"
                </div>
            )}

            {agent.lastToolCall && (
                <div className="text-xs text-muted flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent2 animate-pulse" />
                    Calling: {agent.lastToolCall}
                </div>
            )}
        </motion.div>
    );
}
