import { ShaderAnimation } from "@/components/ui/ShaderAnimation";

export function ShaderBackground() {
    return (
        <div className="absolute inset-0 overflow-hidden -z-10 opacity-30 pointer-events-none">
            <ShaderAnimation />
        </div>
    );
}
