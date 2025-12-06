"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Target, Lightbulb, Zap, Flag } from "lucide-react"

interface StarVisualizerProps {
    content: string
}

export function StarVisualizer({ content }: StarVisualizerProps) {
    // Basic parser for STAR format
    // Assumes format roughly like "Situation: ... Task: ... Action: ... Result: ..."
    // or similar headers. If not found, falls back to text.

    const parseSection = (text: string, header: string, nextHeaders: string[]) => {
        const regex = new RegExp(`${header}[:\\s]*(.*?)(?=${nextHeaders.join("|")}|$)`, "is")
        const match = text.match(regex)
        return match ? match[1].trim() : ""
    }

    const situation = parseSection(content, "Situation", ["Task", "Action", "Result"])
    const task = parseSection(content, "Task", ["Action", "Result"])
    const action = parseSection(content, "Action", ["Result"])
    const result = parseSection(content, "Result", [])

    // If parsing failed significantly (empty fields), might not be in STAR format
    const isParsed = situation || task || action || result

    if (!isParsed) {
        return (
            <div className="p-6 bg-zinc-900/50 rounded-xl border border-zinc-800 font-mono text-sm text-zinc-300 whitespace-pre-wrap">
                {content}
            </div>
        )
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-in fade-in slide-in-from-bottom-2 duration-700">
            <Card className="bg-blue-950/30 border-blue-900/50 backdrop-blur-sm hover:bg-blue-950/50 transition-colors">
                <CardHeader className="pb-2">
                    <CardTitle className="text-blue-400 flex items-center gap-2 text-lg">
                        <Lightbulb className="h-5 w-5" /> Situation
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-zinc-300 text-sm leading-relaxed">{situation || "No situation defined."}</p>
                </CardContent>
            </Card>

            <Card className="bg-amber-950/30 border-amber-900/50 backdrop-blur-sm hover:bg-amber-950/50 transition-colors">
                <CardHeader className="pb-2">
                    <CardTitle className="text-amber-400 flex items-center gap-2 text-lg">
                        <Target className="h-5 w-5" /> Task
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-zinc-300 text-sm leading-relaxed">{task || "No task defined."}</p>
                </CardContent>
            </Card>

            <Card className="bg-purple-950/30 border-purple-900/50 backdrop-blur-sm hover:bg-purple-950/50 transition-colors">
                <CardHeader className="pb-2">
                    <CardTitle className="text-purple-400 flex items-center gap-2 text-lg">
                        <Zap className="h-5 w-5" /> Action
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-zinc-300 text-sm leading-relaxed">{action || "No action defined."}</p>
                </CardContent>
            </Card>

            <Card className="bg-emerald-950/30 border-emerald-900/50 backdrop-blur-sm hover:bg-emerald-950/50 transition-colors">
                <CardHeader className="pb-2">
                    <CardTitle className="text-emerald-400 flex items-center gap-2 text-lg">
                        <Flag className="h-5 w-5" /> Result
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-zinc-300 text-sm leading-relaxed">{result || "No result defined."}</p>
                </CardContent>
            </Card>
        </div>
    )
}
