"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Bot, Wrench, Database, Layers } from "lucide-react"

interface BaseAgentVisualizerProps {
    data: any
}

export function BaseAgentVisualizer({ data }: BaseAgentVisualizerProps) {
    if (!data) return <div className="text-zinc-500">No data available</div>

    const agents = data.agents || []

    return (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-700">
            {/* Summary Header */}
            <div className="flex gap-4 mb-6">
                <div className="bg-zinc-900/50 px-4 py-2 rounded-lg border border-zinc-800 flex items-center gap-2">
                    <Bot className="h-4 w-4 text-blue-400" />
                    <span className="text-zinc-400 text-sm">Agents:</span>
                    <span className="text-white font-bold">{agents.length}</span>
                </div>
                <div className="bg-zinc-900/50 px-4 py-2 rounded-lg border border-zinc-800 flex items-center gap-2">
                    <Database className="h-4 w-4 text-purple-400" />
                    <span className="text-zinc-400 text-sm">Domain:</span>
                    <span className="text-white font-bold">{data.workflow_metadata?.domain || "General"}</span>
                </div>
            </div>

            {/* Agent Flow (Pseudo-Graph) */}
            <div className="relative">
                {/* Connecting Line */}
                <div className="absolute left-[28px] top-8 bottom-8 w-1 bg-zinc-800 rounded-full" />

                <div className="space-y-6">
                    {agents.map((agent: any, idx: number) => (
                        <div key={idx} className="relative pl-16">
                            {/* Dot on line */}
                            <div className="absolute left-[20px] top-8 h-5 w-5 rounded-full bg-zinc-950 border-4 border-blue-600 z-10" />

                            <Card className="bg-zinc-950/40 border-zinc-800 backdrop-blur-sm overflow-hidden group hover:border-blue-500/30 transition-all hover:bg-zinc-900/40">
                                <div className="h-1 w-full bg-gradient-to-r from-blue-600 to-transparent opacity-50" />
                                <CardContent className="p-5">
                                    <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center mb-4">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
                                                <Bot className="h-6 w-6" />
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-semibold text-zinc-100">{agent.name}</h3>
                                                <div className="flex items-center gap-2 text-xs text-zinc-400">
                                                    <Badge variant="outline" className="border-zinc-700 text-zinc-500">{agent.role}</Badge>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <div className="bg-zinc-900/30 p-3 rounded-md border border-zinc-800/50">
                                            <span className="text-xs text-zinc-500 uppercase tracking-wider font-semibold">Goal</span>
                                            <p className="text-zinc-300 text-sm mt-1">{agent.goal}</p>
                                        </div>

                                        {agent.tools && agent.tools.length > 0 && (
                                            <div>
                                                <span className="text-xs text-zinc-500 uppercase tracking-wider font-semibold flex items-center gap-2 mb-2">
                                                    <Wrench className="h-3 w-3" /> Tools
                                                </span>
                                                <div className="flex flex-wrap gap-2">
                                                    {agent.tools.map((tool: any, tIdx: number) => (
                                                        <Badge key={tIdx} variant="secondary" className="bg-zinc-800/80 text-zinc-300 hover:bg-zinc-700">
                                                            {tool.name}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
