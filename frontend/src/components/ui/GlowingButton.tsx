import { GlowingEffect } from "@/components/ui/GlowingEffect";
import { cn } from "@/lib/utils";

interface GlowingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    children: React.ReactNode;
}

export function GlowingButton({ children, className, ...props }: GlowingButtonProps) {
    return (
        <button className={cn("relative group rounded-xl p-[2px]", className)} {...props}>
            <GlowingEffect
                spread={40}
                glow={true}
                disabled={false}
                proximity={64}
                inactiveZone={0.01}
                className="absolute inset-0 rounded-xl"
            />
            <div className="relative rounded-xl bg-primary px-8 py-3 text-white transition-colors group-hover:bg-primary/90">
                {children}
            </div>
        </button>
    );
}
