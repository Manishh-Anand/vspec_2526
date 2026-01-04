"use client"

import { Bot, Terminal, CheckCircle2, ArrowRight, Loader2, Play } from "lucide-react"
import { cn } from "@/lib/utils"

interface ClaudeExecutionGraphProps {
    status: "idle" | "running" | "completed"
    currentStep: number
}

const AGENTS = [
    { name: "ResearchAgent", role: "Researcher", color: "blue" },
    { name: "AnalysisAgent", role: "Analyst", color: "purple" },
    { name: "DocumenterAgent", role: "Writer", color: "emerald" },
    { name: "SchedulerAgent", role: "Coordinator", color: "orange" }
]

export function ClaudeExecutionGraph({ status, currentStep }: ClaudeExecutionGraphProps) {
    return (
        <div className="w-full overflow-x-auto py-8 px-4">
            <div className="min-w-[800px] flex items-center justify-center gap-4">

                {/* Start Node */}
                <div className="flex flex-col items-center gap-2">
                    <div className={cn(
                        "h-12 w-12 rounded-full border-2 flex items-center justify-center transition-all duration-500",
                        status !== "idle" ? "bg-cyan-950 border-cyan-500 text-cyan-400" : "bg-zinc-900 border-zinc-700 text-zinc-500"
                    )}>
                        <Play className="h-5 w-5 fill-current" />
                    </div>
                    <span className="text-xs text-zinc-500 font-mono">START</span>
                </div>

                {/* Connector */}
                <div className={cn(
                    "h-[2px] w-12 transition-all duration-500",
                    status !== "idle" ? "bg-cyan-500" : "bg-zinc-800"
                )} />

                {/* Agents Loop */}
                {AGENTS.map((agent, index) => {
                    const isActive = status === "running" && currentStep === index
                    const isDone = (status === "running" && currentStep > index) || status === "completed"
                    const isPending = !isActive && !isDone

                    return (
                        <div key={agent.name} className="flex items-center gap-4">
                            <div className="relative group">
                                {/* Connection Line Overlay (Animated) */}
                                {isActive && (
                                    <div className="absolute -inset-2 rounded-xl bg-cyan-500/20 blur-md animate-pulse" />
                                )}

                                <div className={cn(
                                    "relative w-48 p-3 rounded-xl border transition-all duration-500 flex flex-col gap-1",
                                    isActive ? "bg-zinc-900 border-cyan-500 shadow-lg shadow-cyan-900/20 scale-105" :
                                        isDone ? "bg-zinc-950/50 border-emerald-500/30 opacity-80" :
                                            "bg-zinc-950 border-zinc-800 opacity-50"
                                )}>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <Bot className={cn(
                                                "h-4 w-4",
                                                isActive ? "text-cyan-400" : isDone ? "text-emerald-400" : "text-zinc-600"
                                            )} />
                                            <span className={cn(
                                                "font-semibold text-sm",
                                                isActive ? "text-white" : isDone ? "text-zinc-300" : "text-zinc-600"
                                            )}>{agent.name}</span>
                                        </div>
                                        {isActive && <Loader2 className="h-3 w-3 animate-spin text-cyan-400" />}
                                        {isDone && <CheckCircle2 className="h-3 w-3 text-emerald-500" />}
                                    </div>
                                    <div className="text-[10px] text-zinc-500 font-mono pl-6">
                                        {isActive ? "Executing via Claude..." : isDone ? "Completed" : "Waiting..."}
                                    </div>
                                </div>
                            </div>

                            {/* Connector */}
                            <div className={cn(
                                "h-[2px] w-8 transition-all duration-500",
                                isDone ? "bg-emerald-500/50" : "bg-zinc-800"
                            )} />
                        </div>
                    )
                })}

                {/* Final Executor Node */}
                <div className="flex flex-col items-center gap-2">
                    <div className={cn(
                        "h-16 w-16 rounded-2xl border-2 flex items-center justify-center transition-all duration-700 relative",
                        status === "completed" ? "bg-[#d97757]/10 border-[#d97757] text-[#d97757] shadow-xl shadow-[#d97757]/20 scale-110" : "bg-zinc-900 border-zinc-800 text-zinc-600"
                    )}>
                        {status === "completed" && (
                            <div className="absolute -inset-1 rounded-2xl bg-[#d97757]/20 blur-sm animate-pulse" />
                        )}
                        <Terminal className="h-8 w-8 relative z-10" />
                    </div>
                    <span className={cn(
                        "text-xs font-bold font-mono",
                        status === "completed" ? "text-[#d97757]" : "text-zinc-600"
                    )}>
                        CLAUDE CODE
                    </span>
                </div>

            </div>
        </div>
    )
}
