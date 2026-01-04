"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "sonner"
import { Loader2, Play, Terminal, ChevronDown, ChevronUp } from "lucide-react"
import { ShaderBackground } from "@/components/ui/shader-background"
import { ClaudeExecutionGraph } from "@/components/visualizations/ClaudeExecutionGraph"
import { ExecutionArtifacts } from "@/components/workflow/ExecutionArtifacts"
import { ScrollArea } from "@/components/ui/scroll-area"

export default function WorkflowPage() {
    const [status, setStatus] = useState<"idle" | "running" | "completed">("idle")
    const [currentStep, setCurrentStep] = useState(0)
    const [output, setOutput] = useState("")
    const [result, setResult] = useState<any>(null)
    const [logsOpen, setLogsOpen] = useState(false)
    const scrollRef = useRef<HTMLDivElement>(null)

    // Scroll to bottom of logs
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight
        }
    }, [output])

    const runWorkflow = async () => {
        setStatus("running")
        setCurrentStep(0)
        setOutput("")
        setResult(null)
        setLogsOpen(false)

        // Visual Simulation of Agents
        const interval = setInterval(() => {
            setCurrentStep(prev => {
                if (prev < 3) return prev + 1
                return prev
            })
        }, 8000) // 8 seconds per agent visual step

        try {
            const res = await fetch("/api/process/workflow", { method: "POST" })
            const data = await res.json()

            clearInterval(interval)

            if (data.success) {
                toast.success("Workflow Executed Successfully")
                setStatus("completed")
                setCurrentStep(4) // Finish line
                setOutput(data.output)
                setResult(data.result)
            } else {
                toast.error("Workflow Execution Failed", { description: data.error })
                setStatus("idle") // Reset on fail or keep visual? Let's reset for now or show fail state
                setOutput(data.details || data.error)
            }
        } catch (e) {
            toast.error("Error triggering workflow")
            clearInterval(interval)
            setStatus("idle")
        }
    }

    return (
        <div className="relative flex flex-col space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 min-h-[calc(100vh-8rem)] pb-10">
            <ShaderBackground />

            {/* Header */}
            <div className="flex items-center justify-between z-10 w-full max-w-7xl mx-auto">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                        Workflow Execution
                        {status === "completed" && <span className="text-xs bg-[#d97757] text-white px-2 py-1 rounded-full">One-Shot Mode</span>}
                    </h1>
                    <p className="text-zinc-400">Execute the planned workflow using Claude Code Runtime.</p>
                </div>
                {status === "idle" && (
                    <Button onClick={runWorkflow} size="lg" className="bg-[#d97757] hover:bg-[#c06547] text-white font-bold shadow-lg shadow-[#d97757]/20 border border-[#d97757]/50">
                        <Play className="mr-2 h-5 w-5" />
                        Execute One-Shot Workflow
                    </Button>
                )}
                {status === "running" && (
                    <Button disabled size="lg" className="bg-zinc-800 text-zinc-400 cursor-not-allowed border border-zinc-700">
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Executing via Claude Code...
                    </Button>
                )}
                {status === "completed" && (
                    <Button onClick={runWorkflow} variant="outline" className="border-zinc-700 text-zinc-300 hover:bg-zinc-800">
                        Rerun Workflow
                    </Button>
                )}
            </div>

            {/* Main Visualizer Area */}
            <Card className="border-zinc-800 bg-zinc-950/50 shadow-2xl overflow-visible z-10 w-full max-w-7xl mx-auto">
                <CardHeader className="border-b border-zinc-800/50 bg-zinc-900/30 py-6">
                    <CardTitle className="text-lg text-zinc-300">Execution Graph</CardTitle>
                </CardHeader>
                <div className="p-0 bg-zinc-950/30 min-h-[200px] flex items-center justify-center">
                    <ClaudeExecutionGraph status={status} currentStep={currentStep} />
                </div>
            </Card>

            {/* Artifacts Panel (Only on completion) */}
            {status === "completed" && result && (
                <div className="w-full max-w-7xl mx-auto z-10">
                    <ExecutionArtifacts result={result} />
                </div>
            )}

            {/* Raw Logs Section */}
            <div className="w-full max-w-7xl mx-auto z-10">
                <div className="w-full space-y-2">
                    <Button
                        variant="ghost"
                        onClick={() => setLogsOpen(!logsOpen)}
                        className="flex items-center gap-2 text-zinc-500 hover:text-zinc-300 w-full justify-start p-0 hover:bg-transparent"
                    >
                        {logsOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
                        <Terminal className="h-4 w-4" />
                        {logsOpen ? "Hide Execution Logs" : "Show Claude Execution Logs"}
                    </Button>

                    {logsOpen && (
                        <Card className="border-zinc-800 bg-[#0c0c0c] overflow-hidden animate-in slide-in-from-top-2 duration-300">
                            <div className="flex items-center justify-between px-4 py-2 bg-zinc-900/50 border-b border-zinc-800">
                                <span className="text-xs text-zinc-500 font-mono">stdout</span>
                                <span className="text-xs text-zinc-600">Raw output from Claude Code runtime</span>
                            </div>
                            <ScrollArea className="h-[400px] w-full p-4" ref={scrollRef}>
                                <pre className="font-mono text-xs text-zinc-400 whitespace-pre-wrap leading-relaxed">
                                    {output || "No output logs available."}
                                </pre>
                            </ScrollArea>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    )
}
