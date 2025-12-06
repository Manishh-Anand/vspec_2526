import { AnimatedHeroWrapper } from '@/components/hero/AnimatedHeroWrapper';
import { TextShimmerHeader } from '@/components/hero/TextShimmerHeader';
import { PromptBuilder } from '@/components/prompt/PromptBuilder';
import { FeatureGrid } from '@/components/ui/FeatureGrid';

export function HomePage() {
    return (
        <div className="min-h-screen bg-surface relative overflow-hidden">
            {/* Hero Section */}
            <div className="relative">
                <div className="absolute inset-0 z-0 opacity-50">
                    <AnimatedHeroWrapper />
                </div>

                <div className="relative z-10 pt-20 pb-32 px-6">
                    <TextShimmerHeader />
                    <p className="text-center text-muted text-lg mb-12 max-w-2xl mx-auto">
                        Convert natural language prompts into multi-agent workflows.
                        Real-time execution, streaming results, and cost estimation.
                    </p>

                    <PromptBuilder />
                </div>
            </div>

            {/* Features Section */}
            <div className="relative z-10 bg-surface/80 backdrop-blur-lg border-t border-white/5">
                <FeatureGrid />
            </div>
        </div>
    );
}
