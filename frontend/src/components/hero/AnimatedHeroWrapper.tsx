import { Hero } from "@/components/ui/AnimatedHero";

export function AnimatedHeroWrapper() {
    return (
        <div className="relative w-full overflow-hidden bg-background">
            <Hero />
        </div>
    );
}
