import { ExpandableTabs } from "@/components/ui/ExpandableTabs";
import { FileText, List, Activity, Settings } from "lucide-react";

export function ExpandableTabsWrapper({ onChange }: { onChange?: (index: number | null) => void }) {
    const tabs = [
        { title: "Summary", icon: Activity },
        { title: "Files", icon: FileText },
        { title: "Logs", icon: List },
        { type: "separator" as const },
        { title: "Settings", icon: Settings },
    ];

    return <ExpandableTabs tabs={tabs} onTabChange={onChange} />;
}
