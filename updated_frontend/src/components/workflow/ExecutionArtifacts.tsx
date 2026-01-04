"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ExternalLink, FileText, Github, Mail, Calendar, Check, X } from "lucide-react"

interface ExecutionArtifactsProps {
    result: any
}

export function ExecutionArtifacts({ result }: ExecutionArtifactsProps) {
    if (!result) return null

    const rawOutput = result.raw_output || ""

    // Best-effort parsing of Claude's natural language output
    const artifacts = []

    // 1. Notion Page
    const notionMatch = rawOutput.match(/Notion Page[\s\S]*?URL: (https:\/\/www\.notion\.so\/[^\s\)]+)/)
    if (notionMatch) {
        artifacts.push({
            type: "notion",
            title: "VSPEC Summary Doc",
            url: notionMatch[1],
            icon: FileText,
            color: "text-zinc-100",
            bgColor: "bg-zinc-800"
        })
    }

    // 2. GitHub Repo
    const githubMatch = rawOutput.match(/GitHub Repository[\s\S]*?Repository: (https:\/\/github\.com\/[^\s\)]+)/)
    if (githubMatch) {
        artifacts.push({
            type: "github",
            title: "Project Repository",
            url: githubMatch[1],
            icon: Github,
            color: "text-zinc-100",
            bgColor: "bg-zinc-800"
        })
    }

    // 3. Email
    const emailMatch = rawOutput.match(/Email Sent[\s\S]*?To: ([^\n]+)/)
    if (emailMatch) {
        artifacts.push({
            type: "email",
            title: "Notification Email",
            detail: `Sent to: ${emailMatch[1].trim()}`,
            icon: Mail,
            color: "text-blue-400",
            bgColor: "bg-blue-950/30"
        })
    }

    // 4. Calendar
    // Look for success or failure
    const calendarMatch = rawOutput.match(/Calendar Event[\s\S]*?Title: ([^\n]+)/)
    const calendarFail = rawOutput.match(/Calendar Event[\s\S]*?Failed/)

    if (calendarMatch) {
        artifacts.push({
            type: "calendar",
            title: "Calendar Event",
            detail: calendarMatch[1].trim(),
            icon: Calendar,
            color: "text-orange-400",
            bgColor: "bg-orange-950/30"
        })
    } else if (calendarFail) {
        artifacts.push({
            type: "calendar_fail",
            title: "Calendar Event",
            detail: "Failed (Permissions)",
            icon: Calendar,
            color: "text-red-400",
            bgColor: "bg-red-950/30",
            failed: true
        })
    }

    if (artifacts.length === 0) return null

    return (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Check className="h-5 w-5 text-emerald-400" />
                Execution Artifacts
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {artifacts.map((art, idx) => (
                    <Card key={idx} className="bg-zinc-950/50 border-zinc-800 hover:border-zinc-700 transition-all overflow-hidden group">
                        <div className={`h-1 w-full ${art.failed ? 'bg-red-500' : 'bg-emerald-500'} opacity-60`} />
                        <CardHeader className="p-4 pb-2">
                            <div className="flex justify-between items-start">
                                <div className={`p-2 rounded-lg ${art.bgColor}`}>
                                    <art.icon className={`h-5 w-5 ${art.color}`} />
                                </div>
                                {art.url && (
                                    <a href={art.url} target="_blank" rel="noopener noreferrer" className="text-zinc-500 hover:text-white transition-colors">
                                        <ExternalLink className="h-4 w-4" />
                                    </a>
                                )}
                                {art.failed && <X className="h-4 w-4 text-red-500" />}
                            </div>
                        </CardHeader>
                        <CardContent className="p-4 pt-2">
                            <CardTitle className="text-sm font-semibold text-zinc-200 mb-1">{art.title}</CardTitle>
                            <CardDescription className="text-xs text-zinc-500 line-clamp-2">
                                {art.detail || (art.url ? art.url.replace('https://', '') : "Successfully Created")}
                            </CardDescription>
                            {art.url && (
                                <a
                                    href={art.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="mt-3 inline-flex items-center text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                                >
                                    Open Resource <ExternalLink className="ml-1 h-3 w-3" />
                                </a>
                            )}
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    )
}
