import { NextResponse } from "next/server";
import fs from "fs/promises";
import { CONFIG } from "@/lib/config";

export async function GET() {
    try {
        const content = await fs.readFile(CONFIG.paths.enhancedAgentOutput, "utf-8");
        const json = JSON.parse(content);
        return NextResponse.json({ content: json });
    } catch (error) {
        // File might not exist
        return NextResponse.json({ content: null });
    }
}
