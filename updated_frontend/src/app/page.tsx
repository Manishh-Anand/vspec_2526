"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { ArrowRight, Terminal, Cpu, Network, Zap, ChevronRight, Github, FileJson } from "lucide-react"
import Link from "next/link"
import { ShaderBackground } from "@/components/ui/shader-background"

export default function LandingPage() {
    return (
        <div className="flex flex-col min-h-screen bg-black text-white selection:bg-blue-500/30">
            {/* Hero Section */}
            <section className="relative h-screen flex flex-col items-center justify-center overflow-hidden">
                <ShaderBackground />
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/90 pointer-events-none" />

                <div className="z-10 text-center space-y-8 max-w-4xl px-4">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <span className="inline-block py-1 px-3 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-6">
                            Multi-Agent Automation Engine
                        </span>
                        <h1 className="text-7xl md:text-9xl font-bold tracking-tighter mb-4 bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-500">
                            VSPEC
                        </h1>
                        <h2 className="text-2xl md:text-4xl font-light text-zinc-300 tracking-tight">
                            Autonomous AI agents wired to <span className="text-blue-400 font-normal">real tools</span>.
                        </h2>
                    </motion.div>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4, duration: 0.8 }}
                        className="text-lg text-zinc-400 max-w-2xl mx-auto leading-relaxed"
                    >
                        VSPEC turns a single system prompt into a structured STAR spec, maps real MCP tools, and spins up LangGraph-powered agents that can execute across your stack.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6, duration: 0.8 }}
                        className="flex flex-col sm:flex-row items-center justify-center gap-4"
                    >
                        <Link href="/dashboard">
                            <Button size="lg" className="h-12 px-8 text-base bg-white text-black hover:bg-zinc-200 rounded-full font-medium">
                                Get Started <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </Link>
                        <Button variant="outline" size="lg" className="h-12 px-8 text-base border-zinc-800 text-zinc-400 hover:text-white hover:bg-zinc-900 rounded-full">
                            View the Pipeline
                        </Button>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 1, duration: 1 }}
                        className="flex flex-wrap justify-center gap-4 pt-8 opacity-60"
                    >
                        {["Python backend", "Claude Code + MCP", "LangGraph workflows", "LM Studio / local models"].map((tag, i) => (
                            <div key={i} className="flex items-center gap-2 text-xs text-zinc-500 font-mono uppercase tracking-widest border border-zinc-900 bg-zinc-950/50 px-3 py-1.5 rounded">
                                {tag}
                            </div>
                        ))}
                    </motion.div>
                </div>
            </section>

            {/* Pipeline Timeline */}
            <section className="py-32 px-4 relative border-t border-zinc-900">
                <div className="max-w-5xl mx-auto">
                    <div className="mb-20 text-center">
                        <h2 className="text-3xl md:text-5xl font-bold mb-6">How VSPEC Thinks</h2>
                        <p className="text-zinc-400">From raw text to executable agents in 6 steps.</p>
                    </div>

                    <div className="relative space-y-24 before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-zinc-800 before:to-transparent">
                        {[
                            { step: "01", title: "System Prompt", sub: "System_prompt.py", desc: "Start with a single Python variable. VSPEC reads this and converts it into a structured STAR representation." },
                            { step: "02", title: "STAR Transformation", sub: "system_2_starMethod.py", desc: "We parse the prompt via AST, send it through the STAR method (via LM Studio), and write a structured spec." },
                            { step: "03", title: "Base Agent Blueprint", sub: "base_agent_4.py", desc: "Generates a JSON blueprint that preserves your original intent while structuring it for agents." },
                            { step: "04", title: "Tool Mapping", sub: "tool_mapper.py", desc: "Uses Claude Code to intelligently map abstract tools to real MCP servers and capabilities." },
                            { step: "05", title: "Agent Factory", sub: "langchain_agentfactory.py", desc: "Instantiates agents with LangChain, applying pruning and quality control." },
                            { step: "06", title: "Execution", sub: "langgraph_workflow_builder.py", desc: "Assembles agents into a LangGraph workflow that executes and returns real results." }
                        ].map((item, i) => (
                            <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-zinc-800 bg-black text-zinc-500 group-hover:border-blue-500 group-hover:text-blue-500 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-[0_0_0_8px_black] z-10 transition-colors">
                                    {item.step}
                                </div>
                                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-6 rounded-2xl border border-zinc-800 bg-zinc-900/20 hover:bg-zinc-900/40 hover:border-zinc-700 transition-all">
                                    <div className="flex items-center justify-between mb-2">
                                        <h3 className="font-bold text-xl">{item.title}</h3>
                                        <span className="text-xs font-mono text-zinc-500 bg-zinc-950 px-2 py-1 rounded">{item.sub}</span>
                                    </div>
                                    <p className="text-zinc-400 text-sm leading-relaxed">{item.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Feature Grid */}
            <section className="py-32 px-4 bg-zinc-950">
                <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {[
                        { icon: Zap, title: "From Prompt to Workflow", desc: "Auto-transform plain text into complex LangGraph workflows." },
                        { icon: Network, title: "MCP-Native", desc: "First-class support for Model Context Protocol tools." },
                        { icon: Cpu, title: "Agent Factory", desc: "Agents are generated, pruned, and verified before execution." },
                        { icon: Terminal, title: "Infra-Ready", desc: "Pure Python backend that integrates with your existing stack." }
                    ].map((f, i) => (
                        <div key={i} className="p-6 rounded-3xl bg-black border border-zinc-900 hover:border-zinc-700 transition-colors group">
                            <f.icon className="h-8 w-8 text-zinc-500 group-hover:text-white mb-4 transition-colors" />
                            <h3 className="font-bold text-lg mb-2">{f.title}</h3>
                            <p className="text-zinc-500 text-sm">{f.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Code Section */}
            <section className="py-32 px-4 border-t border-zinc-900 bg-black">
                <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center gap-16">
                    <div className="flex-1 space-y-6">
                        <h2 className="text-4xl font-bold">Code-first, not slideware.</h2>
                        <p className="text-zinc-400 text-lg leading-relaxed">
                            VSPEC is real Python, JSON, and LangGraph under the hood — not a no-code toy. You keep control over the stack, VSPEC handles the agent scaffolding.
                        </p>
                        <div className="flex gap-4">
                            <Button variant="outline" className="rounded-full border-zinc-800">
                                <Github className="mr-2 h-4 w-4" /> View on GitHub
                            </Button>
                            <Button variant="outline" className="rounded-full border-zinc-800">
                                <FileJson className="mr-2 h-4 w-4" /> View Specs
                            </Button>
                        </div>
                    </div>
                    <div className="flex-1 w-full">
                        <div className="rounded-xl overflow-hidden border border-zinc-800 bg-zinc-950 shadow-2xl">
                            <div className="flex items-center gap-2 px-4 py-3 border-b border-zinc-800 bg-zinc-900/50">
                                <div className="flex gap-1.5">
                                    <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
                                    <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
                                    <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
                                </div>
                                <span className="ml-2 text-xs text-zinc-500 font-mono">main.py</span>
                            </div>
                            <div className="p-6 overflow-x-auto">
                                <pre className="font-mono text-sm text-zinc-300">
                                    <code>{`from vspec import BaseAgent, build_workflow
from system_prompt import system_prompt

# Initialize agent from prompt
agent = BaseAgent.from_system_prompt(system_prompt)

# Build executable graph
workflow = build_workflow(agent)

# Run autonomous pipeline
result = workflow.run(
    "Scout the internet for the KTM ADV 390 X"
)
print(result.summary)`}</code>
                                </pre>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer CTA */}
            <section className="py-32 px-4 text-center border-t border-zinc-900 relative overflow-hidden">
                <div className="absolute inset-0 bg-blue-600/5 blur-[100px] pointer-events-none" />
                <div className="relative z-10 max-w-2xl mx-auto space-y-8">
                    <h2 className="text-4xl md:text-5xl font-bold tracking-tight">Turn your system prompt into a working agent graph.</h2>
                    <p className="text-xl text-zinc-400">VSPEC is for builders who want agents that actually do things.</p>
                    <Link href="/dashboard">
                        <Button size="lg" className="h-14 px-8 text-lg bg-white text-black hover:bg-zinc-200 rounded-full font-bold">
                            Launch Console
                        </Button>
                    </Link>
                </div>
            </section>
        </div>
    )
}
