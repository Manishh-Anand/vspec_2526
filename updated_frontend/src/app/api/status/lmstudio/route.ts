import { NextResponse } from "next/server";

export async function GET() {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);

        const res = await fetch("http://localhost:1234/v1/models", {
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (res.ok) {
            return NextResponse.json({ status: "active" });
        }
        return NextResponse.json({ status: "error" });
    } catch (error) {
        return NextResponse.json({ status: "inactive" });
    }
}
