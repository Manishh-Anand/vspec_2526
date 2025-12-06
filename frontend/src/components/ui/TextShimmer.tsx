"use client";
import React, { useMemo, type JSX } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface TextShimmerProps {
    children: string;
    as?: React.ElementType;
    className?: string;
    duration?: number;
    spread?: number;
}

export function TextShimmer({
    children,
    as: Component = "p",
    className,
    duration = 2,
    spread = 2,
}: TextShimmerProps): JSX.Element {
    const MotionComponent = motion(Component as any) as any;

    const dynamicSpread = useMemo(() => {
        return children.length * spread;
    }, [children, spread]);

    return (
        <MotionComponent
            className={cn(
                "relative inline-block bg-[linear-gradient(110deg,transparent_25%,rgba(255,255,255,0.8)_50%,transparent_75%)] bg-[length:250%_100%] bg-clip-text text-transparent",
                className
            )}
            initial={{ backgroundPosition: "100% 0" }}
            animate={{ backgroundPosition: "-100% 0" }}
            transition={{
                repeat: Infinity,
                duration,
                ease: "linear",
            }}
            style={{
                "--spread": `${dynamicSpread}px`,
            } as React.CSSProperties}
        >
            {children}
        </MotionComponent>
    );
}
