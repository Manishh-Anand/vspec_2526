"use client";
import { memo, useCallback, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import { animate } from "motion/react";

interface GlowingEffectProps {
    blur?: number;
    inactiveZone?: number;
    proximity?: number;
    spread?: number;
    variant?: "default" | "white";
    glow?: boolean;
    className?: string;
    disabled?: boolean;
    movementDuration?: number;
    borderWidth?: number;
}

const GlowingEffect = memo(
    ({
        blur = 0,
        inactiveZone = 0.7,
        proximity = 0,
        spread = 20,
        variant = "default",
        glow = false,
        className,
        movementDuration = 2,
        borderWidth = 1,
        disabled = true,
    }: GlowingEffectProps) => {
        const containerRef = useRef<HTMLDivElement>(null);
        const lastPosition = useRef({ x: 0, y: 0 });
        const animationFrameRef = useRef<number>(0);

        const handleMove = useCallback(
            (
                e?:
                    | MouseEvent
                    | {
                        x: number;
                        y: number;
                    }
            ) => {
                if (!containerRef.current) return;
                if (animationFrameRef.current) {
                    cancelAnimationFrame(animationFrameRef.current);
                }
                animationFrameRef.current = requestAnimationFrame(() => {
                    const element = containerRef.current;
                    if (!element) return;
                    const { left, top, width, height } =
                        element.getBoundingClientRect();
                    const mouseX = e?.x ?? lastPosition.current.x;
                    const mouseY = e?.y ?? lastPosition.current.y;
                    if (e) {
                        lastPosition.current = { x: mouseX, y: mouseY };
                    }
                    const x = mouseX - left;
                    const y = mouseY - top;
                    const distance = Math.sqrt(
                        Math.pow(x - width / 2, 2) + Math.pow(y - height / 2, 2)
                    );
                    const maxDistance = Math.sqrt(
                        Math.pow(width / 2, 2) + Math.pow(height / 2, 2)
                    );
                    const opacity =
                        1 - Math.min(1, Math.max(0, distance / maxDistance));
                    const glowOpacity = glow ? opacity : 0;

                    animate(
                        element,
                        {
                            "--x": `${x}px`,
                            "--y": `${y}px`,
                            "--opacity": opacity,
                            "--glow-opacity": glowOpacity,
                            "--blur": `${blur}px`,
                            "--inactive-zone": `${inactiveZone * 100}%`,
                            "--proximity": `${proximity}px`,
                            "--spread": `${spread}px`,
                            "--border-width": `${borderWidth}px`,
                        },
                        {
                            duration: movementDuration,
                            ease: "easeOut",
                        }
                    );
                });
            },
            [
                blur,
                inactiveZone,
                proximity,
                spread,
                glow,
                movementDuration,
                borderWidth,
            ]
        );

        useEffect(() => {
            if (disabled) return;
            const element = containerRef.current;
            if (!element) return;

            const handleMouseEnter = () => {
                animate(
                    element,
                    {
                        "--opacity": 1,
                    },
                    { duration: 0.5, ease: "easeOut" }
                );
            };

            const handleMouseLeave = () => {
                animate(
                    element,
                    {
                        "--opacity": 0,
                    },
                    { duration: 0.5, ease: "easeOut" }
                );
            };

            element.addEventListener("mousemove", handleMove as EventListener);
            element.addEventListener("mouseenter", handleMouseEnter);
            element.addEventListener("mouseleave", handleMouseLeave);

            return () => {
                element.removeEventListener("mousemove", handleMove as EventListener);
                element.removeEventListener("mouseenter", handleMouseEnter);
                element.removeEventListener("mouseleave", handleMouseLeave);
                if (animationFrameRef.current) {
                    cancelAnimationFrame(animationFrameRef.current);
                }
            };
        }, [disabled, handleMove]);

        return (
            <div
                ref={containerRef}
                className={cn(
                    "relative overflow-hidden",
                    "before:absolute before:inset-0 before:opacity-[var(--opacity,0)] before:transition-opacity before:duration-500 before:ease-out",
                    "before:[background:radial-gradient(circle_at_var(--x)_var(--y),rgba(255,255,255,0.1)_0%,rgba(255,255,255,0)_var(--inactive-zone,70%))]",
                    "after:absolute after:inset-0 after:opacity-[var(--glow-opacity,0)] after:transition-opacity after:duration-500 after:ease-out",
                    "after:[background:radial-gradient(circle_at_var(--x)_var(--y),rgba(255,255,255,0.2)_0%,rgba(255,255,255,0)_var(--inactive-zone,70%))]",
                    "after:[filter:blur(var(--blur,0px))]",
                    variant === "white" &&
                    "before:[background:radial-gradient(circle_at_var(--x)_var(--y),rgba(255,255,255,0.2)_0%,rgba(255,255,255,0)_var(--inactive-zone,70%))]",
                    className
                )}
                style={
                    {
                        "--x": "0px",
                        "--y": "0px",
                        "--opacity": 0,
                        "--glow-opacity": 0,
                        "--blur": `${blur}px`,
                        "--inactive-zone": `${inactiveZone * 100}%`,
                        "--proximity": `${proximity}px`,
                        "--spread": `${spread}px`,
                        "--border-width": `${borderWidth}px`,
                    } as React.CSSProperties
                }
            >
                <div
                    className={cn(
                        "absolute inset-[var(--border-width)] rounded-[inherit] opacity-[var(--opacity,0)] transition-opacity duration-500 ease-out",
                        "[background:radial-gradient(circle_at_var(--x)_var(--y),rgba(255,255,255,0.5)_0%,rgba(255,255,255,0)_var(--spread,20px))]",
                        "[mask:linear-gradient(transparent_0%,black_var(--proximity,0px),black_calc(100%-var(--proximity,0px)),transparent_100%)]",
                        variant === "white" &&
                        "[background:radial-gradient(circle_at_var(--x)_var(--y),rgba(255,255,255,1)_0%,rgba(255,255,255,0)_var(--spread,20px))]"
                    )}
                />
            </div>
        );
    }
);

GlowingEffect.displayName = "GlowingEffect";

export { GlowingEffect };
