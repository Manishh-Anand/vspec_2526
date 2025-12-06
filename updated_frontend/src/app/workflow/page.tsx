"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { toast } from "sonner"
import { Loader2, Play, Terminal, CheckCircle2 } from "lucide-react"
import { ShaderBackground } from "@/components/ui/shader-background"

export default function WorkflowPage() {
    const [loading, setLoading] = useState(false)
    const [output, setOutput] = useState("")

    const runWorkflow = async () => {
        setLoading(true)
        setOutput("")
        try {
            const res = await fetch("/api/process/workflow", { method: "POST" })
            const data = await res.json()
            if (data.success) {
                toast.success("Workflow Executed Successfully")
                setOutput(data.output)
            } else {
                toast.error("Workflow Execution Failed", { description: data.error })
                setOutput(data.details || data.error)
            }
        } catch (e) {
            toast.error("Error triggering workflow")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="relative flex flex-col space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 h-[calc(100vh-8rem)]">
            <ShaderBackground />
            <div className="flex items-center justify-between z-10">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-white">Workflow Execution</h1>
                    <p className="text-zinc-400">Run the final LangGraph workflow with your configured agents.</p>
                </div>
                <Button onClick={runWorkflow} disabled={loading} size="lg" className="bg-cyan-600 hover:bg-cyan-700 text-white font-semibold shadow-lg shadow-cyan-900/20">
                    {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <Play className="mr-2 h-5 w-5" />}
                    Execute Workflow
                </Button>
            </div>

            <Card className="flex-1 flex flex-col border-zinc-800 bg-zinc-950/50 overflow-hidden shadow-2xl shadow-black/50">
                <CardHeader className="flex flex-row items-center justify-between py-4 border-b border-zinc-800/50 bg-zinc-900/30">
                    <div className="flex items-center gap-2">
                        <Terminal className="h-5 w-5 text-zinc-400" />
                        <CardTitle className="text-lg">Execution Output</CardTitle>
                    </div>
                    {output && !loading && (
                        <div className="flex items-center text-emerald-400 text-sm">
                            <CheckCircle2 className="mr-1 h-4 w-4" />
                            Completed
                        </div>
                    )}
                </CardHeader>
                <CardContent className="flex-1 p-0 overflow-hidden relative group">
                    {loading && (
                        <div className="absolute inset-0 z-10 bg-zinc-950/20 backdrop-blur-[1px] flex items-center justify-center">
                            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 shadow-xl flex items-center gap-3">
                                <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
                                <span className="text-zinc-200">Executing... this may take a while</span>
                            </div>
                        </div>
                    )}
                    <div className="h-full overflow-auto p-6 bg-[#0c0c0c] font-mono text-sm leading-relaxed text-zinc-300 selection:bg-cyan-900/30">
                        {output ? (
                            <pre className="whitespace-pre-wrap">{output}</pre>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-zinc-600 space-y-4 opacity-50">
                                <div className="p-4 rounded-full bg-zinc-900/50 border border-zinc-800/50">
                                    <Terminal className="h-8 w-8" />
                                </div>
                                <p>Ready to execute. Click the button above to start.</p>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
