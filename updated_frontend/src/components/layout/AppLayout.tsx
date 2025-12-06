"use client"

import { Sidebar } from "@/components/layout/Sidebar"
import { Header } from "@/components/layout/Header"
import { ScrollArea } from "@/components/ui/scroll-area"

export function AppLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex min-h-screen bg-zinc-950 text-zinc-50">
            {/* Desktop Sidebar */}
            <aside className="hidden w-64 flex-col border-r border-zinc-800 bg-zinc-950 md:flex">
                <ScrollArea className="flex-1">
                    <Sidebar />
                </ScrollArea>
            </aside>

            {/* Main Content */}
            <div className="flex flex-1 flex-col">
                <Header />
                <main className="flex-1 overflow-y-auto p-4 md:p-8 pt-6">
                    {children}
                </main>
            </div>
        </div>
    )
}
