import { NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { CONFIG } from "@/lib/config";

const execPromise = promisify(exec);

export async function POST() {
    try {
        // We need to execute the py script. Assuming python is in path.
        // We use the full path to the script
        const scriptPath = CONFIG.paths.starScript;
        const promptPath = CONFIG.paths.systemPrompt;
        const cwd = scriptPath.substring(0, scriptPath.lastIndexOf("\\"));

        const { stdout, stderr } = await execPromise(`python "${scriptPath}" "${promptPath}"`, { cwd });

        return NextResponse.json({ success: true, output: stdout, error: stderr });
    } catch (error: any) {
        console.error("Error executing STAR script:", error);
        return NextResponse.json({
            success: false,
            error: error.message,
            details: error.stderr || error.stdout
        }, { status: 500 });
    }
}
