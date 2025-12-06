"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import { Loader2, Wrench, Shield, AlertTriangle, CheckCircle, Play } from "lucide-react"

interface Tool {
    name: string
    original_name?: string
    mapping_status?: string
    description?: string
    warning?: string
}

interface Agent {
    id: string
    name: string
    role: string
    goal: string
    backstory: string
    tools: Tool[]
}

export default function AgentsPage() {
    const [data, setData] = useState<any>(null)
    const [loading, setLoading] = useState(false)
    const [fetching, setFetching] = useState(true)

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const res = await fetch("/api/ba_enhanced")
            const json = await res.json()
            if (json.content) {
                setData(json.content)
            }
        } catch (e) {
            console.error(e)
        } finally {
            setFetching(false)
        }
    }

    const runMapper = async () => {
        setLoading(true)
        try {
            const res = await fetch("/api/process/tool_mapper", { method: "POST" })
            const json = await res.json()
            if (json.success) {
                toast.success("Tool Mapping Complete")
                fetchData()
            } else {
                toast.error("Mapping Failed", { description: json.error })
            }
        } catch (e) {
            toast.error("Error executing Tool Mapper")
        } finally {
            setLoading(false)
        }
    }

    if (fetching) {
        return (
            <div className="flex h-full items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
            </div>
        )
    }

    const agents: Agent[] = data?.agents || []
    const metadata = data?.workflow_metadata

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-10">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-white">Agent Configuration</h1>
                    <p className="text-zinc-400">Review and enhance agents with real MCP tools.</p>
                </div>
                <Button onClick={runMapper} disabled={loading} className="bg-emerald-600 hover:bg-emerald-700">
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Wrench className="mr-2 h-4 w-4" />}
                    Map Tools with Claude
                </Button>
            </div>

            {data && (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-zinc-400">Total Agents</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-white">{agents.length}</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-zinc-400">Workflow ID</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-white truncate text-xs font-mono">{metadata?.workflow_id || "-"}</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900/50 border-zinc-800">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-zinc-400">Domain</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-white truncate text-lg">{metadata?.domain || "-"}</div>
                        </CardContent>
                    </Card>
                </div>
            )}

            <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2">
                {agents.map((agent, idx) => (
                    <Card key={idx} className="bg-zinc-950/50 border-zinc-800 flex flex-col">
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <CardTitle className="text-xl text-emerald-400">{agent.name}</CardTitle>
                                <Badge variant="outline" className="text-zinc-400 border-zinc-700">{agent.role}</Badge>
                            </div>
                            <CardDescription className="line-clamp-2">{agent.backstory}</CardDescription>
                        </CardHeader>
                        <CardContent className="flex-1 space-y-4">
                            <div>
                                <h4 className="text-sm font-medium text-zinc-300 mb-2">Goal</h4>
                                <p className="text-sm text-zinc-400 bg-zinc-900 p-2 rounded-md">{agent.goal}</p>
                            </div>

                            <div>
                                <h4 className="text-sm font-medium text-zinc-300 mb-2">Tools</h4>
                                <div className="space-y-2">
                                    {agent.tools.map((tool, tIdx) => (
                                        <div key={tIdx} className="flex items-start justify-between bg-zinc-900/50 p-2 rounded border border-zinc-800">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-mono text-xs text-blue-400">{tool.name}</span>
                                                    {tool.mapping_status === 'exact' && <CheckCircle className="h-3 w-3 text-emerald-500" />}
                                                    {tool.mapping_status === 'matched' && <CheckCircle className="h-3 w-3 text-emerald-500" />}
                                                    {tool.mapping_status === 'placeholder' && <AlertTriangle className="h-3 w-3 text-amber-500" />}
                                                    {tool.mapping_status === 'unmapped' && <Shield className="h-3 w-3 text-red-500" />}
                                                </div>
                                                {tool.original_name && tool.original_name !== tool.name && (
                                                    <div className="text-xs text-zinc-500 mt-1">Mapped from: {tool.original_name}</div>
                                                )}
                                                {tool.warning && (
                                                    <div className="text-xs text-amber-500/80 mt-1">{tool.warning}</div>
                                                )}
                                            </div>
                                            <Badge variant="secondary" className="text-[10px] bg-zinc-950">{tool.mapping_status || 'raw'}</Badge>
                                        </div>
                                    ))}
                                    {agent.tools.length === 0 && <span className="text-sm text-zinc-500">No tools assigned</span>}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
                {agents.length === 0 && !fetching && (
                    <div className="col-span-full flex flex-col items-center justify-center p-12 border border-dashed border-zinc-800 rounded-xl text-zinc-500">
                        <p>No agents found. Run process Base Agent first.</p>
                        <Button variant="link" className="text-emerald-500" onClick={() => window.location.href = '/processing'}>Go to Processing</Button>
                    </div>
                )}
            </div>
        </div>
    )
}
