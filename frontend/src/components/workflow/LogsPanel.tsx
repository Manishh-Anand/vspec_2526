import { useWorkflowStore } from '@/store/workflowStore';
import { useRef, useEffect } from 'react';

export function LogsPanel() {
    const logs = useWorkflowStore((state) => state.logs);
    const endRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs.length]);

    return (
        <div className="h-full bg-surface-card border border-white/10 rounded-xl overflow-hidden flex flex-col">
            <div className="p-3 border-b border-white/10 bg-surface/50">
                <h3 className="text-sm font-medium text-muted">Live Logs</h3>
            </div>
            <div className="flex-1 overflow-auto p-2 space-y-1">
                {logs.map((log, index) => (
                    <div key={index} className="px-4 py-2 text-sm font-mono border-b border-white/5 hover:bg-white/5">
                        <span className="text-muted mr-2">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                        <span className={
                            log.type === 'error' ? 'text-error' :
                                log.type === 'success' ? 'text-success' :
                                    'text-white'
                        }>
                            {JSON.stringify(log.payload)}
                        </span>
                    </div>
                ))}
                <div ref={endRef} />
            </div>
        </div>
    );
}
