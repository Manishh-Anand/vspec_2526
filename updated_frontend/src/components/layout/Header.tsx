"use client"

import { MobileSidebar } from "@/components/layout/Sidebar"
import { ModeToggle } from "@/components/mode-toggle"
import { Separator } from "@/components/ui/separator"

export function Header() {
    return (
        <header className="sticky top-0 z-50 w-full border-b border-zinc-800 bg-zinc-950/80 backdrop-blur supports-[backdrop-filter]:bg-zinc-950/60">
            <div className="container flex h-14 items-center px-4">
                <MobileSidebar />
                <div className="mr-4 hidden md:flex">
                    <a className="mr-6 flex items-center space-x-2" href="/">
                        <span className="font-bold sm:inline-block">VSPEC</span>
                    </a>
                </div>
                <div className="flex flex-1 items-center justify-end space-x-2">
                    {/* Search or other header items can go here */}
                    <ModeToggle />
                </div>
            </div>
        </header>
    )
}
