import { AIVoiceInput } from "@/components/ui/AIVoiceInput";

interface STTPanelProps {
    onTranscript: (text: string) => void;
}

export function STTPanel({ onTranscript }: STTPanelProps) {
    const handleStop = (_duration: number) => {
        // Mock transcription
        setTimeout(() => {
            onTranscript("This is a simulated transcription of the audio.");
        }, 1000);
    };

    return (
        <div className="w-full max-w-md mx-auto py-4">
            <AIVoiceInput onStop={handleStop} />
        </div>
    );
}
