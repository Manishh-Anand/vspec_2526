import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { LucideIcon } from "lucide-react"
import Link from "next/link"

interface FeatureCardProps {
    title: string
    description: string
    icon: LucideIcon
    href: string
    bgClass?: string
}

export function FeatureCard({ title, description, icon: Icon, href, bgClass }: FeatureCardProps) {
    return (
        <Link href={href}>
            <Card className="h-full transition-all hover:scale-[1.02] hover:bg-zinc-900/50 cursor-pointer border-zinc-800/50 bg-zinc-950/20 group">
                <CardHeader>
                    <div className={`p-2 w-fit rounded-md mb-2 ${bgClass || "bg-zinc-800/50"}`}>
                        <Icon className="h-5 w-5 text-white" />
                    </div>
                    <CardTitle className="text-zinc-100 group-hover:text-blue-400 transition-colors">{title}</CardTitle>
                    <CardDescription className="text-zinc-400">{description}</CardDescription>
                </CardHeader>
            </Card>
        </Link>
    )
}
