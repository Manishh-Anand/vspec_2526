import { NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { CONFIG } from "@/lib/config";
import fs from "fs/promises";
import path from "path";

const execPromise = promisify(exec);

export async function POST() {
    try {
        const scriptPath = CONFIG.paths.workflowBuilder;
        const cwd = scriptPath.substring(0, scriptPath.lastIndexOf("\\"));

        // Executes claude_code_executor.py via main pipeline logic or direct call
        // Using "python script.py json" pattern
        const cmd = `python "${scriptPath}" BA_enhanced.json`;

        const { stdout, stderr } = await execPromise(cmd, { cwd });

        // Read the result JSON file
        const resultPath = CONFIG.paths.claudeResult;
        let executionResult = null;
        try {
            const resultData = await fs.readFile(resultPath, "utf-8");
            executionResult = JSON.parse(resultData);
        } catch (readError) {
            console.warn("Could not read workflow_result_claude_code.json:", readError);
        }

        return NextResponse.json({
            success: true,
            output: stdout,
            error: stderr,
            result: executionResult
        });
    } catch (error: any) {
        console.error("Error executing Workflow:", error);
        return NextResponse.json({
            success: false,
            error: error.message,
            details: error.stderr || error.stdout
        }, { status: 500 });
    }
}
