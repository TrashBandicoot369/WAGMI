import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import * as fs from "fs/promises";
import * as path from "path";
import * as os from "os";

const execAsync = promisify(exec);

export async function POST(req: NextRequest) {
  try {
    console.log("✅ /api/telegram/lookup hit");
    
    const { username } = await req.json();
    
    if (!username) {
      return NextResponse.json(
        { error: "Username is required" },
        { status: 400 }
      );
    }

    // Clean the username (remove @ if present and convert to lowercase)
    const cleanUsername = username.startsWith('@')
      ? username.substring(1).toLowerCase()
      : username.toLowerCase();
    
    try {
      // Create a temporary Python script that uses your get_user_ids.py logic
      const tempDir = os.tmpdir();
      const tempScriptPath = path.join(tempDir, "lookup_telegram_id.py");
      
      // Create a simplified version of your get_user_ids.py script
      const pythonScript = `
from telethon import TelegramClient
import sys
import asyncio

API_ID = 29312830
API_HASH = "24622c388a689db6cf871903fdca8c1c"

async def get_user_id(username):
    try:
        async with TelegramClient('user_session', API_ID, API_HASH) as client:
            user = await client.get_entity(username)
            print(user.id)
            return user.id
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    username = "${cleanUsername}"
    asyncio.run(get_user_id(username))
`;

      // Write the temporary script
      await fs.writeFile(tempScriptPath, pythonScript);
      
      // Execute the Python script
      const { stdout, stderr } = await execAsync(`python ${tempScriptPath}`);
      
      // Clean up the temporary file
      await fs.unlink(tempScriptPath).catch(() => {});
      
      if (stderr) {
        console.error("Python script error:", stderr);
        return NextResponse.json(
          { error: `Failed to look up Telegram ID: ${stderr}` },
          { status: 500 }
        );
      }
      
      const userId = stdout.trim();
      if (!userId || isNaN(Number(userId))) {
        return NextResponse.json(
          { error: "User not found or invalid ID returned" },
          { status: 404 }
        );
      }
      
      return NextResponse.json({ 
        userId: userId,
        source: "telethon_api"
      });
      
    } catch (error) {
      console.error("Error running Python script:", error);
      return NextResponse.json(
        { error: "Failed to execute the Telegram lookup script. Please run get_user_ids.py manually." },
        { status: 500 }
      );
    }
    
  } catch (error) {
    console.error("Error in Telegram lookup:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
