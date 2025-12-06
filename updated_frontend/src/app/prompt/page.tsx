"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { ArrowRight, Bot, User, Sparkles, SendHorizontal, Paperclip } from "lucide-react"
import { useRouter } from "next/navigation"
import { cn } from "@/lib/utils"

export default function PromptPage() {
    const [messages, setMessages] = useState<{ role: 'user' | 'ai'; content: string }[]>([
        { role: 'ai', content: "Hello! I'm your AI Architect. Describe the system you want to build, and I'll help you structure it." }
    ])
    const [input, setInput] = useState("")
    const [saving, setSaving] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const router = useRouter()

    useEffect(() => {
        // Fetch existing prompt to populate if needed, or just leave blank for "chat" feel
        // For now, we'll assume a fresh session or we could load the last prompt as a "user message"
        const fetchPrompt = async () => {
            const res = await fetch("/api/prompt")
            const data = await res.json()
            if (data.content && data.content.length > 10) {
                // Clean up python var syntax if possible or just show raw
                // Assuming user just wants to type new prompts mostly
            }
        }
        fetchPrompt()
    }, [])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    const handleSend = async () => {
        if (!input.trim()) return

        // 1. Add user message
        const userMsg = input
        setMessages(prev => [...prev, { role: 'user', content: userMsg }])
        setInput("")
        setSaving(true)

        // 2. Simulate AI "thinking" then save
        try {
            // Save to python file
            // Format strictly as python variable for backend compatibility
            const pythonContent = `system_prompt = """${userMsg.replace(/"/g, '\\"')}"""`

            await fetch("/api/prompt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: pythonContent }),
            })

            // 3. AI Response
            setTimeout(() => {
                setMessages(prev => [...prev, {
                    role: 'ai',
                    content: "I've updated the system parameters. We can now proceed to analyze this with the STAR method."
                }])
                setSaving(false)
            }, 800)

        } catch (error) {
            toast.error("Failed to save prompt")
            setSaving(false)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto w-full animate-in fade-in duration-500">
            <div className="flex items-center justify-between mb-4 px-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                        <Sparkles className="h-6 w-6 text-blue-400" />
                        Prompt Engineer
                    </h1>
                </div>
                {messages.length > 2 && (
                    <Button onClick={() => router.push("/processing")} className="bg-blue-600 hover:bg-blue-700 text-white rounded-full">
                        Next Phase <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                )}
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6 rounded-2xl bg-zinc-950/50 border border-zinc-800/50 mb-4 shadow-inner">
                {messages.map((msg, i) => (
                    <div
                        key={i}
                        className={cn(
                            "flex items-start gap-3 max-w-[80%]",
                            msg.role === 'user' ? "ml-auto flex-row-reverse" : "mr-auto"
                        )}
                    >
                        <div className={cn(
                            "p-2 rounded-full shrink-0",
                            msg.role === 'user' ? "bg-blue-600" : "bg-emerald-600"
                        )}>
                            {msg.role === 'user' ? <User className="h-4 w-4 text-white" /> : <Bot className="h-4 w-4 text-white" />}
                        </div>
                        <div className={cn(
                            "p-4 rounded-2xl text-sm leading-relaxed",
                            msg.role === 'user'
                                ? "bg-blue-600/10 text-blue-100 rounded-tr-none border border-blue-500/20"
                                : "bg-zinc-800/50 text-zinc-100 rounded-tl-none border border-zinc-700/50"
                        )}>
                            {msg.content}
                            {msg.role === 'ai' && i === messages.length - 1 && messages.length > 2 && (
                                <div className="mt-3">
                                    <Button
                                        variant="secondary"
                                        size="sm"
                                        onClick={() => router.push("/processing")}
                                        className="text-xs bg-zinc-700 hover:bg-zinc-600"
                                    >
                                        Proceed to STAR Analysis <ArrowRight className="ml-2 h-3 w-3" />
                                    </Button>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {saving && (
                    <div className="flex items-center gap-2 text-zinc-500 text-sm ml-12">
                        <span className="flex gap-1">
                            <span className="h-2 w-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                            <span className="h-2 w-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                            <span className="h-2 w-2 bg-blue-500 rounded-full animate-bounce"></span>
                        </span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="relative p-2 bg-zinc-900/50 rounded-xl border border-zinc-800 flex items-end gap-2 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
                <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-white mb-1">
                    <Paperclip className="h-5 w-5" />
                </Button>
                <Textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Describe your agent system..."
                    className="min-h-[60px] max-h-[200px] w-full resize-none bg-transparent border-0 focus-visible:ring-0 p-3 text-base"
                />
                <Button
                    onClick={handleSend}
                    disabled={!input.trim() || saving}
                    size="icon"
                    className={cn(
                        "mb-1 transition-all",
                        input.trim() ? "bg-blue-600 hover:bg-blue-500 text-white" : "bg-zinc-800 text-zinc-500"
                    )}
                >
                    <SendHorizontal className="h-5 w-5" />
                </Button>
            </div>
            <p className="text-center text-xs text-zinc-600 mt-2">
                Ai Agent Workflow can make mistakes. Review generated workflows carefully.
            </p>
        </div>
    )
}
