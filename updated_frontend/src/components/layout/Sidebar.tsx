"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import {
    LayoutDashboard,
    Terminal,
    Cpu,
    Workflow,
    FileCode,
    Menu,
    Sparkles
} from "lucide-react"
import { useState } from "react"
import { Separator } from "@/components/ui/separator"

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> { }

export function Sidebar({ className }: SidebarProps) {
    const pathname = usePathname()

    const items = [
        {
            title: "Dashboard",
            href: "/dashboard",
            icon: LayoutDashboard,
        },
        {
            title: "Prompt Editor",
            href: "/prompt",
            icon: FileCode,
        },
        {
            title: "STAR Processing",
            href: "/processing",
            icon: Sparkles,
        },
        {
            title: "Agent Graph",
            href: "/agents",
            icon: Cpu,
        },
        {
            title: "Workflow",
            href: "/workflow",
            icon: Workflow,
        },
        {
            title: "System Logs",
            href: "/logs",
            icon: Terminal,
        },
    ]

    return (
        <div className={cn("pb-12", className)}>
            <div className="space-y-4 py-4">
                <div className="px-3 py-2">
                    <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight animate-in fade-in slide-in-from-left-2 transition-all">
                        AI Agent Workflow
                    </h2>
                    <div className="space-y-1">
                        {items.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    buttonVariants({ variant: "ghost", size: "sm" }),
                                    "w-full justify-start gap-2 transition-all hover:translate-x-1",
                                    pathname === item.href
                                        ? "bg-zinc-800/50 text-white font-medium"
                                        : "text-zinc-400 hover:text-white hover:bg-zinc-800/30"
                                )}
                            >
                                <item.icon className="h-4 w-4" />
                                {item.title}
                            </Link>
                        ))}
                    </div>
                </div>
                <Separator className="bg-zinc-800/50 mx-4 w-auto" />
                <div className="px-3 py-2">
                    <h2 className="mb-2 px-4 text-xs font-semibold tracking-tight text-zinc-500">
                        System Status
                    </h2>
                    {/* Placeholder for status indicators */}
                    <div className="px-4 text-xs text-zinc-400">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                            <span>System Active</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export function MobileSidebar() {
    const [open, setOpen] = useState(false)
    return (
        <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
                <Button variant="ghost" className="mr-2 px-0 text-base hover:bg-transparent focus-visible:bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 lg:hidden">
                    <Menu className="h-6 w-6" />
                    <span className="sr-only">Toggle Menu</span>
                </Button>
            </SheetTrigger>
            <SheetContent side="left" className="pl-1 pr-0">
                <div className="px-7">
                    <Link
                        href="/"
                        className="flex items-center"
                        onClick={() => setOpen(false)}
                    >
                        <span className="font-bold">AI Agent Workflow</span>
                    </Link>
                </div>
                <ScrollArea className="my-4 h-[calc(100vh-8rem)] pb-10 pl-6">
                    <div className="flex flex-col space-y-2">
                        <Sidebar className="w-full" />
                    </div>
                </ScrollArea>
            </SheetContent>
        </Sheet>
    )
}
