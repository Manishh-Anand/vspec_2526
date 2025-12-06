import { NextResponse } from "next/server";
import fs from "fs/promises";
import { CONFIG } from "@/lib/config";

export async function GET() {
    try {
        const content = await fs.readFile(CONFIG.paths.starOutput, "utf-8");
        return NextResponse.json({ content });
    } catch (error) {
        // File might not exist yet
        return NextResponse.json({ content: "" });
    }
}
