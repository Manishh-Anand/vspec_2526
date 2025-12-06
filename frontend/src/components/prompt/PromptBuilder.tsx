import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { STTPanel } from '@/components/prompt/STTPanel';
import { GlowingButton } from '@/components/ui/GlowingButton';
import { Button } from '@/components/ui/button';
import { useWorkflowStore } from '@/store/workflowStore';

export function PromptBuilder() {
    const navigate = useNavigate();
    const setWorkflowId = useWorkflowStore((state) => state.setWorkflowId);
    const [step, setStep] = useState(1);
    const [prompt, setPrompt] = useState('');
    const [destination, setDestination] = useState('email');
    const [settings, setSettings] = useState({
        max_agents: 3,
        timeout: 300,
        cost_limit: 5.0
    });

    const handleSTT = (text: string) => {
        setPrompt((prev) => prev + ' ' + text);
    };

    const handleGenerate = async () => {
        // Mock API call
        const mockWorkflowId = 'workflow_' + Date.now();
        setWorkflowId(mockWorkflowId);
        navigate('/execution');
    };

    return (
        <div className="w-full max-w-4xl mx-auto p-6 bg-surface-card/50 backdrop-blur-sm rounded-2xl border border-white/10">
            <div className="mb-8">
                <div className="flex justify-between items-center mb-4">
                    {[1, 2, 3, 4].map((s) => (
                        <div
                            key={s}
                            className={`h-2 flex-1 mx-1 rounded-full transition-colors ${s <= step ? 'bg-accent1' : 'bg-white/10'
                                }`}
                        />
                    ))}
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">
                    {step === 1 && 'What is your intent?'}
                    {step === 2 && 'Choose Destination'}
                    {step === 3 && 'Constraints & Options'}
                    {step === 4 && 'Review & Estimate'}
                </h2>
            </div>

            <motion.div
                key={step}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="min-h-[300px]"
            >
                {step === 1 && (
                    <div className="space-y-4">
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            className="w-full h-40 bg-surface/50 border border-white/10 rounded-xl p-4 text-white focus:ring-2 focus:ring-accent1 outline-none resize-none"
                            placeholder="Describe your workflow..."
                        />
                        <STTPanel onTranscript={handleSTT} />
                    </div>
                )}

                {step === 2 && (
                    <div className="grid grid-cols-2 gap-4">
                        {['email', 'notion', 'calendar', 'file'].map((dest) => (
                            <button
                                key={dest}
                                onClick={() => setDestination(dest)}
                                className={`p-6 rounded-xl border transition-all ${destination === dest
                                        ? 'bg-accent1/20 border-accent1 text-accent1'
                                        : 'bg-surface/50 border-white/10 hover:bg-white/5'
                                    }`}
                            >
                                <div className="capitalize font-medium">{dest}</div>
                            </button>
                        ))}
                    </div>
                )}

                {step === 3 && (
                    <div className="space-y-6">
                        <div>
                            <label className="block text-sm text-muted mb-2">Max Agents</label>
                            <input
                                type="number"
                                value={settings.max_agents}
                                onChange={(e) => setSettings({ ...settings, max_agents: parseInt(e.target.value) })}
                                className="w-full bg-surface/50 border border-white/10 rounded-lg p-3 text-white"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-muted mb-2">Timeout (seconds)</label>
                            <input
                                type="number"
                                value={settings.timeout}
                                onChange={(e) => setSettings({ ...settings, timeout: parseInt(e.target.value) })}
                                className="w-full bg-surface/50 border border-white/10 rounded-lg p-3 text-white"
                            />
                        </div>
                    </div>
                )}

                {step === 4 && (
                    <div className="space-y-4 bg-surface/50 p-6 rounded-xl border border-white/10">
                        <div className="flex justify-between">
                            <span className="text-muted">Intent Length</span>
                            <span>{prompt.length} chars</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-muted">Destination</span>
                            <span className="capitalize">{destination}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-muted">Estimated Cost</span>
                            <span className="text-accent1 font-bold">$0.05 - $0.12</span>
                        </div>
                    </div>
                )}
            </motion.div>

            <div className="flex justify-between mt-8">
                <Button
                    variant="ghost"
                    onClick={() => setStep((s) => Math.max(1, s - 1))}
                    disabled={step === 1}
                >
                    Back
                </Button>

                {step < 4 ? (
                    <Button onClick={() => setStep((s) => Math.min(4, s + 1))}>
                        Next
                    </Button>
                ) : (
                    <GlowingButton onClick={handleGenerate}>
                        Generate Workflow
                    </GlowingButton>
                )}
            </div>
        </div>
    );
}
