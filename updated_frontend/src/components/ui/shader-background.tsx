"use client";

import { useEffect, useRef } from "react";

export const ShaderBackground = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let animationFrameId: number;
        let time = 0;

        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        window.addEventListener("resize", resize);
        resize();

        const render = () => {
            time += 0.005;
            canvas.width = canvas.width; // Clear canvas

            const w = canvas.width;
            const h = canvas.height;

            // Create a simple "grid" or "network" flowing effect
            ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
            ctx.fillRect(0, 0, w, h);

            for (let i = 0; i < 50; i++) {
                const x = (Math.sin(time + i) * 0.5 + 0.5) * w;
                const y = (Math.cos(time * 0.5 + i * 0.2) * 0.5 + 0.5) * h;
                const size = Math.sin(time * 2 + i) * 2 + 3;

                ctx.beginPath();
                ctx.arc(x, y, size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(50, 100, 255, ${Math.sin(time + i) * 0.5 + 0.5})`; // High opacity for visibility
                ctx.fill();
            }

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => {
            window.removeEventListener("resize", resize);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full pointer-events-none" // Removed z-index and opacity classes for debug
            style={{ zIndex: 0 }}
        />
    );
};
