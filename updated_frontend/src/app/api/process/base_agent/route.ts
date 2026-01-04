import { NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { CONFIG } from "@/lib/config";

const execPromise = promisify(exec);

export async function POST() {
    try {
        const scriptPath = CONFIG.paths.baseAgentScript;
        // Verify path first or just use it. The user flow said base_agent_4.py
        const cwd = scriptPath.substring(0, scriptPath.lastIndexOf("\\"));

        const { stdout, stderr } = await execPromise(`python "${scriptPath}"`, { cwd });
        return NextResponse.json({ success: true, output: stdout, error: stderr });
    } catch (error: any) {
        console.error("Error executing Base Agent:", error);
        return NextResponse.json({
            success: false,
            error: error.message,
            details: error.stderr || error.stdout
        }, { status: 500 });
    }
}
