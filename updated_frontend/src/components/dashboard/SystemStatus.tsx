"use client"

import { useState, useEffect } from "react"

export function SystemStatus() {
    const [lmStatus, setLmStatus] = useState<"checking" | "active" | "inactive" | "error">("checking")

    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await fetch("/api/status/lmstudio")
                const data = await res.json()
                setLmStatus(data.status)
            } catch (e) {
                setLmStatus("inactive")
            }
        }
        checkStatus()
        const interval = setInterval(checkStatus, 10000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Backend Environment</span>
                <span className="text-emerald-400 flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.5)]" />
                    Active
                </span>
            </div>
            <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">LangGraph Engine</span>
                <span className="text-emerald-400 flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-400" />
                    Ready
                </span>
            </div>
            <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Ollama / LM Studio</span>
                {lmStatus === "checking" && (
                    <span className="text-amber-400 flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-amber-400 animate-bounce" />
                        Checking...
                    </span>
                )}
                {lmStatus === "active" && (
                    <span className="text-emerald-400 flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]" />
                        Connected
                    </span>
                )}
                {(lmStatus === "inactive" || lmStatus === "error") && (
                    <span className="text-red-400 flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-red-400" />
                        Disconnected
                    </span>
                )}
            </div>
        </div>
    )
}
