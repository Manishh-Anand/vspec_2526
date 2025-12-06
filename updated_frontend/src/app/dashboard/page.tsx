import { GlowingCard } from "@/components/ui/glowing-card"
import { SystemStatus } from "@/components/dashboard/SystemStatus"
import { FileCode, Sparkles, Cpu, Workflow, Terminal, ArrowRight } from "lucide-react"
import Link from "next/link"

export default function Home() {
  const features = [
    { title: "Prompt Editor", desc: "Edit and refine your system prompt.", icon: FileCode, href: "/prompt", color: "text-blue-500" },
    { title: "STAR Processing", desc: "Convert prompts to STAR method.", icon: Sparkles, href: "/processing", color: "text-amber-500" },
    { title: "Agent Configuration", desc: "Manage agent definitions and tools.", icon: Cpu, href: "/agents", color: "text-emerald-500" },
    { title: "Workflow Builder", desc: "Visualize and execute workflows.", icon: Workflow, href: "/workflow", color: "text-cyan-500" },
    { title: "System Logs", desc: "Monitor real-time execution logs.", icon: Terminal, href: "/logs", color: "text-rose-500" },
  ]

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-white">Dashboard</h1>
        <p className="text-zinc-400">Manage your AI agent pipeline from prompt to execution.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {features.map((f, i) => (
          <Link key={i} href={f.href}>
            <GlowingCard className="h-full">
              <div className="flex items-start justify-between">
                <div className={`p-3 rounded-xl bg-zinc-900 ${f.color} bg-opacity-10 mb-4`}>
                  <f.icon className={`h-6 w-6 ${f.color}`} />
                </div>
                <ArrowRight className="h-5 w-5 text-zinc-600 group-hover:text-zinc-300 transition-colors" />
              </div>
              <div className="relative z-10">
                <h3 className="font-semibold text-zinc-100 text-lg mb-2">{f.title}</h3>
                <p className="text-zinc-400 text-sm">{f.desc}</p>
              </div>
            </GlowingCard>
          </Link>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* System Status */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-950/50 p-6">
          <h3 className="font-semibold text-zinc-100 mb-4">Pipeline Status</h3>
          <SystemStatus />
        </div>
      </div>
    </div>
  )
}
