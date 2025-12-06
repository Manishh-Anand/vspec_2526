"use client";
import { Mic } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface AIVoiceInputProps {
    onStart?: () => void;
    onStop?: (duration: number) => void;
    visualizerBars?: number;
    demoMode?: boolean;
    demoInterval?: number;
    className?: string;
}

export function AIVoiceInput({
    onStart,
    onStop,
    visualizerBars = 48,
    demoMode = false,
    demoInterval = 3000,
    className
}: AIVoiceInputProps) {
    const [submitted, setSubmitted] = useState(false);
    const [time, setTime] = useState(0);
    const [isClient, setIsClient] = useState(false);
    const [isDemo, setIsDemo] = useState(demoMode);

    useEffect(() => {
        setIsClient(true);
    }, []);

    useEffect(() => {
        let intervalId: ReturnType<typeof setInterval>;
        if (submitted) {
            onStart?.();
            intervalId = setInterval(() => {
                setTime((t) => t + 1);
            }, 1000);
        } else {
            onStop?.(time);
            setTime(0);
        }
        return () => clearInterval(intervalId);
    }, [submitted, time, onStart, onStop]);

    useEffect(() => {
        if (!isDemo) return;
        let timeoutId: ReturnType<typeof setTimeout>;
        const runAnimation = () => {
            setSubmitted(true);
            timeoutId = setTimeout(() => {
                setSubmitted(false);
                timeoutId = setTimeout(runAnimation, demoInterval / 2);
            }, demoInterval);
        };
        runAnimation();
        return () => clearTimeout(timeoutId);
    }, [isDemo, demoInterval]);

    const formatTime = (seconds: number) => {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    };

    const toggleRecording = () => {
        if (isDemo) setIsDemo(false);
        setSubmitted(!submitted);
    };

    return (
        <div className={cn("flex flex-col items-center", className)}>
            <div className="relative flex h-24 w-full items-center justify-center overflow-hidden rounded-xl bg-muted dark:bg-muted/50">
                {isClient && Array.from({ length: visualizerBars }).map((_, i) => (
                    <div
                        key={i}
                        className={cn(
                            "h-12 w-1 rounded-full bg-primary/30 transition-all duration-300 ease-in-out",
                            {
                                "animate-pulse bg-primary": submitted,
                                "scale-y-50": !submitted
                            }
                        )}
                        style={{
                            animationDelay: submitted ? `${i * 0.05}s` : '0s',
                            animationDuration: submitted ? '0.8s' : '0s',
                            transform: `scaleY(${submitted ? Math.random() * 0.5 + 0.5 : 0.5})`
                        }}
                    />
                ))}
                <div className="absolute inset-0 flex items-center justify-center">
                    <button
                        onClick={toggleRecording}
                        className={cn(
                            "z-10 flex h-16 w-16 items-center justify-center rounded-full transition-all duration-300",
                            submitted ? "bg-red-500 hover:bg-red-600" : "bg-primary hover:bg-primary/90"
                        )}
                        aria-label={submitted ? "Stop recording" : "Start recording"}
                    >
                        <Mic className="h-8 w-8 text-white" />
                    </button>
                </div>
            </div>
            <div className="mt-2 text-sm text-muted-foreground">
                {submitted ? formatTime(time) : "Click to record"}
            </div>
        </div>
    );
}
