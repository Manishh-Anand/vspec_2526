"use client";

import React from "react";
import { cn } from "@/lib/utils";

export const GlowingCard = ({
    children,
    className,
}: {
    children: React.ReactNode;
    className?: string;
}) => {
    return (
        <div
            className={cn(
                "group relative rounded-3xl border border-zinc-800 bg-zinc-900/50 p-1 transition-all hover:bg-zinc-900/80",
                className
            )}
        >
            <div className="absolute -inset-0.5 rounded-3xl bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 blur transition duration-500 group-hover:opacity-25" />
            <div className="relative h-full w-full rounded-[22px] bg-zinc-950 p-6">
                {children}
            </div>
        </div>
    );
};
