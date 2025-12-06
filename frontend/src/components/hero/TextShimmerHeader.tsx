import { TextShimmer } from "@/components/ui/TextShimmer";

export function TextShimmerHeader() {
    return (
        <div className="flex items-center justify-center py-4">
            <TextShimmer className="text-4xl font-bold md:text-6xl" duration={2}>
                MetaFlow
            </TextShimmer>
        </div>
    );
}
