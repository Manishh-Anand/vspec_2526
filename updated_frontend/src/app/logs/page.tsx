"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Terminal } from "lucide-react"

export default function LogsPage() {
    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 h-[calc(100vh-8rem)] flex flex-col">
            <div>
                <h1 className="text-2xl font-bold tracking-tight text-white">System Logs</h1>
                <p className="text-zinc-400">View historical execution logs and system events.</p>
            </div>

            <Card className="flex-1 flex flex-col border-zinc-800 bg-zinc-950/50 overflow-hidden">
                <CardHeader className="border-b border-zinc-800/50 py-3">
                    <div className="flex items-center gap-2">
                        <Terminal className="h-4 w-4 text-zinc-400" />
                        <CardTitle className="text-sm font-medium">Console Output</CardTitle>
                    </div>
                </CardHeader>
                <CardContent className="p-0 flex-1 bg-black font-mono text-xs text-zinc-400">
                    <ScrollArea className="h-full">
                        <div className="p-4 space-y-1">
                            <div className="text-emerald-500">[SYSTEM] Application initialized</div>
                            <div className="text-zinc-500">[INFO] Connected to local backend</div>
                            <div className="text-zinc-500">[INFO] Theme set to: dark</div>
                            <div className="text-blue-500">[AUTH] User session start</div>
                            {/* Placeholder logs */}
                            {Array.from({ length: 10 }).map((_, i) => (
                                <div key={i} className="text-zinc-600">
                                    [DEBUG] Service tick {Date.now() - i * 1000}
                                </div>
                            ))}
                            <div className="text-amber-500">[WARN] No persistent log storage configured</div>
                        </div>
                    </ScrollArea>
                </CardContent>
            </Card>
        </div>
    )
}
