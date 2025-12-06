import { NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { CONFIG } from "@/lib/config";

const execPromise = promisify(exec);

export async function POST() {
    try {
        const scriptPath = CONFIG.paths.workflowBuilder;
        const cwd = scriptPath.substring(0, scriptPath.lastIndexOf("\\"));

        // The script expects BA_enhanced.json as arg, or defaults to it. 
        // According to bat file: python langgraph_workflow_builder.py BA_enhanced.json
        const cmd = `python "${scriptPath}" BA_enhanced.json`;

        const { stdout, stderr } = await execPromise(cmd, { cwd });
        return NextResponse.json({ success: true, output: stdout, error: stderr });
    } catch (error: any) {
        console.error("Error executing Workflow:", error);
        return NextResponse.json({
            success: false,
            error: error.message,
            details: error.stderr || error.stdout
        }, { status: 500 });
    }
}
