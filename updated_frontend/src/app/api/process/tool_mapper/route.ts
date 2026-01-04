import { NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { CONFIG } from "@/lib/config";

const execPromise = promisify(exec);

export async function POST() {
    try {
        const scriptPath = CONFIG.paths.toolMapperScript;
        const inputPath = CONFIG.paths.baseAgentOutput;
        const cwd = scriptPath.substring(0, scriptPath.lastIndexOf("\\"));

        const { stdout, stderr } = await execPromise(`python "${scriptPath}" "${inputPath}"`, { cwd });
        return NextResponse.json({ success: true, output: stdout, error: stderr });
    } catch (error: any) {
        console.error("Error executing Tool Mapper:", error);
        return NextResponse.json({
            success: false,
            error: error.message,
            details: error.stderr || error.stdout
        }, { status: 500 });
    }
}
