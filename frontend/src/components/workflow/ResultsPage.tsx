import { useWorkflowStore } from '@/store/workflowStore';
import { ExpandableTabsWrapper } from '@/components/ui/ExpandableTabsWrapper';
import { AnimatedHeroWrapper } from '@/components/hero/AnimatedHeroWrapper';
import { GlowingButton } from '@/components/ui/GlowingButton';
import { useNavigate } from 'react-router-dom';

export function ResultsPage() {
    const navigate = useNavigate();
    const { results, partialResults } = useWorkflowStore();

    return (
        <div className="min-h-screen bg-surface">
            <div className="relative h-[300px] overflow-hidden">
                <div className="absolute inset-0 bg-accent1/10" />
                <AnimatedHeroWrapper />
                <div className="absolute inset-0 flex items-center justify-center">
                    <h1 className="text-4xl md:text-6xl font-bold text-white text-center">
                        Workflow Complete
                    </h1>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 -mt-20 relative z-10">
                <div className="bg-surface-card border border-white/10 rounded-2xl p-8 shadow-2xl">
                    <div className="flex justify-between items-center mb-8">
                        <ExpandableTabsWrapper />
                        <div className="flex gap-4">
                            <GlowingButton onClick={() => navigate('/')}>
                                New Workflow
                            </GlowingButton>
                        </div>
                    </div>

                    <div className="bg-surface/50 rounded-xl p-6 border border-white/5">
                        <h2 className="text-xl font-bold mb-4 text-accent1">Key Findings</h2>
                        <pre className="text-white whitespace-pre-wrap font-mono text-sm">
                            {JSON.stringify(results || partialResults, null, 2)}
                        </pre>
                    </div>
                </div>
            </div>
        </div>
    );
}
