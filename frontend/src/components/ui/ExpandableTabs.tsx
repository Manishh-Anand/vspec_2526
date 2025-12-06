"use client";

import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useOnClickOutside } from "usehooks-ts";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface Tab {
    title: string;
    icon: LucideIcon;
    type?: never;
}

interface Separator {
    type: "separator";
    title?: never;
    icon?: never;
}

type TabItem = Tab | Separator;

interface ExpandableTabsProps {
    tabs: TabItem[];
    activeTabId?: number | null;
    onTabChange?: (index: number | null) => void;
    className?: string;
}

export function ExpandableTabs({
    tabs,
    activeTabId,
    onTabChange,
    className,
}: ExpandableTabsProps) {
    const [selected, setSelected] = React.useState<number | null>(activeTabId || null);
    const outsideClickRef = React.useRef<HTMLDivElement>(null);

    useOnClickOutside(outsideClickRef as React.RefObject<HTMLElement>, () => {
        setSelected(null);
        onTabChange?.(null);
    });

    const handleSelect = (index: number) => {
        setSelected(index);
        onTabChange?.(index);
    };

    const Separator = () => (
        <div className="mx-1 h-[24px] w-[1.2px] bg-border" aria-hidden="true" />
    );

    return (
        <div
            ref={outsideClickRef}
            className={cn(
                "flex flex-wrap items-center gap-2 rounded-2xl border bg-background p-1 shadow-sm",
                className
            )}
        >
            {tabs.map((tab, index) => {
                if (tab.type === "separator") {
                    return <Separator key={`separator-${index}`} />;
                }

                const Icon = tab.icon;
                return (
                    <motion.button
                        key={tab.title}
                        variants={{
                            initial: {
                                width: "40px",
                                backgroundColor: "transparent",
                            },
                            hover: {
                                width: "auto",
                                backgroundColor: "rgba(0, 0, 0, 0.05)",
                            },
                            selected: {
                                width: "auto",
                                backgroundColor: "rgba(0, 0, 0, 0.1)",
                            },
                        }}
                        initial="initial"
                        animate={selected === index ? "selected" : "initial"}
                        whileHover={selected === index ? "selected" : "hover"}
                        onClick={() => handleSelect(index)}
                        className={cn(
                            "relative flex h-10 items-center justify-center overflow-hidden rounded-xl border border-transparent px-2 text-foreground transition-all duration-200",
                            selected === index && "border-border"
                        )}
                    >
                        <Icon className="h-5 w-5 flex-shrink-0" />
                        <AnimatePresence>
                            {(selected === index || true) && (
                                <motion.span
                                    variants={{
                                        initial: { opacity: 0, width: 0, marginLeft: 0 },
                                        hover: { opacity: 1, width: "auto", marginLeft: 8 },
                                        selected: { opacity: 1, width: "auto", marginLeft: 8 },
                                    }}
                                    transition={{ duration: 0.2 }}
                                    className="whitespace-nowrap overflow-hidden"
                                >
                                    {tab.title}
                                </motion.span>
                            )}
                        </AnimatePresence>
                    </motion.button>
                );
            })}
        </div>
    );
}
