#!/usr/bin/env python3
"""
8Bit Skills Library - Human-in-the-Loop Approval Workflow

Compares local skills with public repo, presents each new/changed skill
for approval via Telegram with approve/deny buttons. Requires double
confirmation for approvals. Denied skills are remembered permanently.

State file: ~/8Bit-Skills-Library/.approval-state.json
Denied skills: ~/8Bit-Skills-Library/.denied-skills.json
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_DIR = Path(os.environ["HOME"]) / "8Bit-Skills-Library"
STATE_FILE = REPO_DIR / ".approval-state.json"
DENIED_FILE = REPO_DIR / ".denied-skills.json"
PUBLIC_REMOTE = "8bit-arcade"
PUBLIC_URL = "https://github.com/8-bitArcade/8bit-skills.git"

def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_denied_skills():
    return set(load_json(DENIED_FILE, {}).get("denied", []))

def add_denied(skill_name):
    state = load_json(DENIED_FILE, {})
    if "denied" not in state:
        state["denied"] = []
    if skill_name not in state["denied"]:
        state["denied"].append(skill_name)
        state["denied_at"] = datetime.now(timezone.utc).isoformat()
        save_json(DENIED_FILE, state)

def get_pending_approvals():
    return load_json(STATE_FILE, {}).get("pending", [])

def clear_pending():
    save_json(STATE_FILE, {"pending": []})

def add_pending(skill_name, content_preview):
    state = load_json(STATE_FILE, {})
    if "pending" not in state:
        state["pending"] = []
    state["pending"].append({
        "name": skill_name,
        "preview": content_preview[:500],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "confirmed": False
    })
    save_json(STATE_FILE, state)

def get_new_or_changed_skills():
    """Compare local skills directory with public repo to find new/changed skills."""
    try:
        # Fetch public remote
        subprocess.run(
            ["git", "fetch", PUBLIC_REMOTE],
            cwd=REPO_DIR,
            capture_output=True,
            timeout=30
        )
        
        # Get diff between local and public repo
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{PUBLIC_REMOTE}/main...HEAD"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            # No public remote yet or first sync - all skills are new
            return list((REPO_DIR / "skills").glob("*/SKILL.md"))
        
        changed_files = result.stdout.strip().split("\n")
        return [Path(f) for f in changed_files if f.startswith("skills/") and f.endswith("SKILL.md")]
    except Exception as e:
        print(f"Error comparing with public repo: {e}")
        # Fallback: return all local skills
        return list((REPO_DIR / "skills").glob("*/SKILL.md"))

def skill_name_from_path(path):
    """Extract skill name from SKILL.md path."""
    return path.parent.name

def format_skill_preview(skill_path):
    """Format skill content for Telegram preview."""
    try:
        content = skill_path.read_text()
        preview = content[:300].replace("`", "'")
        lines = content.split("\n")
        name = lines[0].replace("#", "").strip() if lines else skill_name_from_path(skill_path)
        return f"**{name}**\n\n{preview}"
    except Exception:
        return f"**{skill_name_from_path(skill_path)}**"

def send_telegram_approval(skill_name, preview, skill_index, total_skills):
    """Send Telegram message with approve/deny inline buttons."""
    import requests
    
    # Get Telegram bot token from environment
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "530910105")
    
    if not bot_token:
        print(f"No Telegram bot token found. Would send approval request for: {skill_name}")
        return
    
    message = f"**8Bit Skills Library - Approval Required**\n\n"
    message += f"Skill {skill_index}/{total_skills}: {skill_name}\n\n"
    message += f"{preview}\n\n"
    message += "🔘 **Approve** | 🔘 **Deny**\n\n"
    message += "(Approve requires double confirmation. Denied skills are remembered permanently.)"
    
    # Inline keyboard with approve/deny buttons
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve:{skill_name}"},
                {"text": "❌ Deny", "callback_data": f"deny:{skill_name}"}
            ]
        ]
    }
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard)
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"Sent approval request for: {skill_name}")
        else:
            print(f"Failed to send approval for {skill_name}: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "check"
    
    if action == "check":
        # Daily check for new/changed skills
        denied = get_denied_skills()
        new_skills = get_new_or_changed_skills()
        
        if not new_skills:
            print("No new or changed skills to approve.")
            return
        
        pending_count = 0
        total_skills = len(new_skills)
        
        for i, skill_path in enumerate(new_skills, 1):
            skill_name = skill_name_from_path(skill_path)
            
            # Skip denied skills
            if skill_name in denied:
                print(f"Skipping denied skill: {skill_name}")
                continue
            
            # Add to pending and send Telegram notification
            preview = format_skill_preview(skill_path)
            add_pending(skill_name, preview)
            pending_count += 1
            
            # Send Telegram message with approve/deny buttons
            send_telegram_approval(skill_name, preview, i, total_skills)
        
        print(f"Found {pending_count} skills requiring approval.")
        
    elif action == "approve" and len(sys.argv) > 2:
        skill_name = sys.argv[2]
        # Send second confirmation request
        send_telegram_approval(skill_name, "Confirm approval?", 1, 1)
        state = load_json(STATE_FILE, {})
        for item in state.get("pending", []):
            if item["name"] == skill_name:
                item["confirmed"] = True
                save_json(STATE_FILE, state)
                print(f"Skill '{skill_name}' confirmed for push.")
                break
                
    elif action == "deny" and len(sys.argv) > 2:
        skill_name = sys.argv[2]
        add_denied(skill_name)
        print(f"Skill '{skill_name}' denied and will not be pushed.")
        
    elif action == "push_approved":
        # Push all confirmed skills to public repo
        state = load_json(STATE_FILE, {})
        confirmed = [item for item in state.get("pending", []) if item.get("confirmed")]
        
        if not confirmed:
            print("No confirmed skills to push.")
            return
            
        print(f"Pushing {len(confirmed)} confirmed skills to public repo...")
        
        # Add public remote if not exists
        try:
            subprocess.run(
                ["git", "remote", "add", PUBLIC_REMOTE, PUBLIC_URL],
                cwd=REPO_DIR,
                capture_output=True,
                timeout=10
            )
        except Exception:
            pass  # Remote may already exist
            
        # Push to public repo
        result = subprocess.run(
            ["git", "push", PUBLIC_REMOTE, "main"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("Successfully pushed to public repo.")
            clear_pending()
        else:
            print(f"Push failed: {result.stderr}")

if __name__ == "__main__":
    main()
