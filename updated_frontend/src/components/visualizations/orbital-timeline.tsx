"use client"

import { Target, Lightbulb, Zap, Flag } from "lucide-react"
import RadialOrbitalTimeline, { TimelineItem } from "@/components/ui/radial-orbital-timeline"

interface StarVisualizerProps {
    content: string
}

export function OrbitalTimeline({ content }: StarVisualizerProps) {
    const parseSection = (text: string, header: string, nextHeaders: string[]) => {
        const nextHeadersPattern = nextHeaders.length > 0 ? `(?:###\\s*)?(?:${nextHeaders.join("|")})` : "$";
        const regex = new RegExp(`(?:###\\s*)?${header}(?:\\s*\\([A-Za-z]\\))?\\s*:?\\s*([\\s\\S]*?)(?=${nextHeadersPattern})`, "i")
        const match = text.match(regex)
        return match ? match[1].trim() : ""
    }

    const situation = parseSection(content, "Situation", ["Task", "Action", "Result"])
    const task = parseSection(content, "Task", ["Action", "Result"])
    const action = parseSection(content, "Action", ["Result"])
    const result = parseSection(content, "Result", [])

    // Map STAR content to Radial Timeline format
    const timelineData: TimelineItem[] = [
        {
            id: 1,
            title: "Situation",
            date: "Context",
            content: situation || "Analyzing situation...",
            category: "Analysis",
            icon: Lightbulb,
            relatedIds: [2],
            status: situation ? "completed" : "pending",
            energy: 100
        },
        {
            id: 2,
            title: "Task",
            date: "Objectives",
            content: task || "Defining tasks...",
            category: "Planning",
            icon: Target,
            relatedIds: [1, 3],
            status: task ? "completed" : "pending",
            energy: 85
        },
        {
            id: 3,
            title: "Action",
            date: "Execution",
            content: action || "Generating actions...",
            category: "Execution",
            icon: Zap,
            relatedIds: [2, 4],
            status: action ? "in-progress" : "pending",
            energy: 65
        },
        {
            id: 4,
            title: "Result",
            date: "Outcome",
            content: result || "Projecting results...",
            category: "Result",
            icon: Flag,
            relatedIds: [3],
            status: result ? "pending" : "pending",
            energy: 40
        }
    ];

    return (
        <RadialOrbitalTimeline timelineData={timelineData} />
    )
}
