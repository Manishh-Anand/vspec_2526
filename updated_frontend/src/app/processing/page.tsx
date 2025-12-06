"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { toast } from "sonner"
import { Loader2, Sparkles, Cpu, ArrowRight, Play, Eye } from "lucide-react"
import { useRouter } from "next/navigation"
import { OrbitalTimeline } from "@/components/visualizations/orbital-timeline"
import { BaseAgentVisualizer } from "@/components/visualizations/BaseAgentVisualizer"

export default function ProcessingPage() {
    const [starContent, setStarContent] = useState("")
    const [baData, setBaData] = useState<any>(null)
    const [loadingStar, setLoadingStar] = useState(false)
    const [loadingBa, setLoadingBa] = useState(false)
    const [activeTab, setActiveTab] = useState("star")
    const router = useRouter()

    useEffect(() => {
        fetchStar()
        fetchBa()
    }, [])

    const fetchStar = async () => {
        try {
            const res = await fetch("/api/star")
            const data = await res.json()
            setStarContent(data.content || "")
        } catch (e) {
            console.error(e)
        }
    }

    const fetchBa = async () => {
        try {
            const res = await fetch("/api/ba_op")
            const data = await res.json()
            if (data.content) {
                setBaData(data.content)
            }
        } catch (e) {
            console.error(e)
        }
    }

    const runStar = async () => {
        setLoadingStar(true)
        try {
            const res = await fetch("/api/process/star", { method: "POST" })
            const data = await res.json()
            if (data.success) {
                toast.success("STAR Conversion Complete")
                fetchStar()
            } else {
                toast.error("STAR Conversion Failed", { description: data.error })
            }
        } catch (e) {
            toast.error("Error running STAR script")
        } finally {
            setLoadingStar(false)
        }
    }

    const runBa = async () => {
        setLoadingBa(true)
        try {
            const res = await fetch("/api/process/base_agent", { method: "POST" })
            const data = await res.json()
            if (data.success) {
                toast.success("Base Agent Output Generated")
                fetchBa()
            } else {
                toast.error("Generation Failed", { description: data.error })
            }
        } catch (e) {
            toast.error("Error running Base Agent")
        } finally {
            setLoadingBa(false)
        }
    }

    return (
        <div className="flex flex-col space-y-4 animate-in fade-in zoom-in-95 duration-500 h-[calc(100vh-8rem)]">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-white">System Processing</h1>
                    <p className="text-zinc-400">Convert system prompt to Agent structures.</p>
                </div>
            </div>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
                <TabsList className="grid w-full grid-cols-2 bg-zinc-900 border border-zinc-800">
                    <TabsTrigger value="star" className="data-[state=active]:bg-amber-500/10 data-[state=active]:text-amber-500 transition-all">
                        <Sparkles className="mr-2 h-4 w-4" />
                        STAR Method Analysis
                    </TabsTrigger>
                    <TabsTrigger value="ba" className="data-[state=active]:bg-blue-500/10 data-[state=active]:text-blue-500 transition-all">
                        <Cpu className="mr-2 h-4 w-4" />
                        Base Agent Blueprint
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="star" className="flex-1 flex flex-col mt-4 space-y-4 overflow-hidden">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-semibold text-zinc-400">Structural Analysis</h2>
                        <Button onClick={runStar} disabled={loadingStar} size="sm" className="bg-amber-600 hover:bg-amber-700 text-white">
                            {loadingStar ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                            Run Analysis
                        </Button>
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <OrbitalTimeline content={starContent} />
                    </div>
                </TabsContent>

                <TabsContent value="ba" className="flex-1 flex flex-col mt-4 space-y-4 overflow-hidden">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-semibold text-zinc-400">Agent Architecture</h2>
                        <Button onClick={runBa} disabled={loadingBa} size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                            {loadingBa ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                            Generate Blueprint
                        </Button>
                    </div>

                    <div className="flex-1 overflow-y-auto pr-2">
                        {baData ? (
                            <BaseAgentVisualizer data={baData} />
                        ) : (
                            <div className="h-full flex items-center justify-center text-zinc-600 border border-dashed border-zinc-800 rounded-xl">
                                <p>No agent blueprint generated.</p>
                            </div>
                        )}
                    </div>

                    <div className="flex justify-end pt-2">
                        <Button onClick={() => router.push("/agents")} className="bg-emerald-600 hover:bg-emerald-700">
                            Configure Tools <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    )
}
