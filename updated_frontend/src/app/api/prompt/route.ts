import { NextResponse } from "next/server";
import fs from "fs/promises";
import { CONFIG } from "@/lib/config";

export async function GET() {
    try {
        const content = await fs.readFile(CONFIG.paths.systemPrompt, "utf-8");
        return NextResponse.json({ content });
    } catch (error) {
        console.error("Error reading system prompt:", error);
        return NextResponse.json({ error: "Failed to read system prompt" }, { status: 500 });
    }
}

export async function POST(req: Request) {
    try {
        const { content } = await req.json();
        await fs.writeFile(CONFIG.paths.systemPrompt, content, "utf-8");
        return NextResponse.json({ success: true });
    } catch (error) {
        console.error("Error writing system prompt:", error);
        return NextResponse.json({ error: "Failed to save system prompt" }, { status: 500 });
    }
}
