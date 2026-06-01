#!/usr/bin/env python3
"""
8Bit Skills Library - Approval State Manager

Manages approval state for skills being pushed to public repo.
Tracks denied skills (never asked again) and pending approvals.

Usage:
  python3 approval-state.py check          # Find new/changed skills
  python3 approval-state.py deny <name>    # Deny a skill
  python3 approval-state.py approve <name> # Approve a skill (requires confirmation)
  python3 approval-state.py push           # Push confirmed skills to public repo
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
        return True
    return False

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

def confirm_skill(skill_name):
    state = load_json(STATE_FILE, {})
    for item in state.get("pending", []):
        if item["name"] == skill_name:
            item["confirmed"] = True
            save_json(STATE_FILE, state)
            return True
    return False

def get_confirmed_skills():
    state = load_json(STATE_FILE, {})
    return [item["name"] for item in state.get("pending", []) if item.get("confirmed")]

def get_new_or_changed_skills():
    """Compare local skills with public repo to find new/changed skills."""
    try:
        subprocess.run(
            ["git", "fetch", PUBLIC_REMOTE],
            cwd=REPO_DIR,
            capture_output=True,
            timeout=30
        )
        
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{PUBLIC_REMOTE}/main...HEAD"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return list((REPO_DIR / "skills").glob("*/SKILL.md"))
        
        changed_files = result.stdout.strip().split("\n")
        return [Path(f) for f in changed_files if f.startswith("skills/") and f.endswith("SKILL.md")]
    except Exception as e:
        print(f"Error comparing with public repo: {e}")
        return list((REPO_DIR / "skills").glob("*/SKILL.md"))

def skill_name_from_path(path):
    return path.parent.name

def format_skill_preview(skill_path):
    try:
        content = skill_path.read_text()
        preview = content[:300].replace("`", "'")
        lines = content.split("\n")
        name = lines[0].replace("#", "").strip() if lines else skill_name_from_path(skill_path)
        return f"**{name}**\n\n{preview}"
    except Exception:
        return f"**{skill_name_from_path(skill_path)}**"

def send_telegram_message(text, reply_markup=None):
    """Send message to Telegram via Bot API with optional inline keyboard."""
    import requests
    
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "530910105")
    
    if not bot_token:
        # Try loading from .env file
        env_path = Path(os.environ["HOME"]) / ".hermes" / ".env"
        if env_path.exists():
            content = env_path.read_text()
            for line in content.split("\n"):
                if line.startswith("TELEGRAM_BOT_TOKEN=") and not line.startswith("#"):
                    bot_token = line.split("=", 1)[1].strip()
                    break
    
    if not bot_token:
        print(f"No Telegram bot token. Would send: {text[:100]}...")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False

def create_approval_keyboard(skill_name):
    """Create inline keyboard with green approve and red deny buttons."""
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Approve", "callback_data": f"approve:{skill_name}"},
                {"text": "❌ Deny", "callback_data": f"deny:{skill_name}"}
            ]
        ]
    }

def create_confirmation_keyboard(skill_name):
    """Create confirmation keyboard for double-confirmation."""
    return {
        "inline_keyboard": [
            [
                {"text": "🟢 Yes, push this skill", "callback_data": f"confirm_push:{skill_name}"},
                {"text": "🔴 Cancel", "callback_data": f"cancel:{skill_name}"}
            ]
        ]
    }

def push_to_public():
    """Push confirmed skills to public repo."""
    state = load_json(STATE_FILE, {})
    confirmed = [item for item in state.get("pending", []) if item.get("confirmed")]
    
    if not confirmed:
        print("No confirmed skills to push.")
        return False
    
    print(f"Pushing {len(confirmed)} confirmed skills to public repo...")
    
    # Add remote if not exists
    try:
        subprocess.run(
            ["git", "remote", "add", PUBLIC_REMOTE, PUBLIC_URL],
            cwd=REPO_DIR,
            capture_output=True,
            timeout=10
        )
    except Exception:
        pass
    
    # Fetch latest
    subprocess.run(
        ["git", "fetch", PUBLIC_REMOTE],
        cwd=REPO_DIR,
        capture_output=True,
        timeout=15
    )
    
    # Merge if needed
    subprocess.run(
        ["git", "merge", f"{PUBLIC_REMOTE}/main", "--allow-unrelated-histories", "--no-edit"],
        cwd=REPO_DIR,
        capture_output=True,
        timeout=15
    )
    
    # Resolve conflicts by keeping our version
    subprocess.run(
        ["git", "checkout", "--ours", "."],
        cwd=REPO_DIR,
        capture_output=True,
        timeout=10
    )
    subprocess.run(
        ["git", "add", "."],
        cwd=REPO_DIR,
        capture_output=True,
        timeout=10
    )
    subprocess.run(
        ["git", "commit", "-m", "Merge with public repo - resolve conflicts"],
        cwd=REPO_DIR,
        capture_output=True,
        timeout=10
    )
    
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
        return True
    else:
        print(f"Push failed: {result.stderr}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: approval-state.py <check|deny|approve|push>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "check":
        denied = get_denied_skills()
        new_skills = get_new_or_changed_skills()
        
        if not new_skills:
            print("No new or changed skills to approve.")
            return
        
        pending_count = 0
        for skill_path in new_skills:
            skill_name = skill_name_from_path(skill_path)
            
            if skill_name in denied:
                print(f"Skipping denied skill: {skill_name}")
                continue
            
            preview = format_skill_preview(skill_path)
            add_pending(skill_name, preview)
            pending_count += 1
            
            # Send approval request with clickable buttons
            keyboard = create_approval_keyboard(skill_name)
            send_telegram_message(preview, keyboard)
        
        print(f"Found {pending_count} skills requiring approval.")
        
    elif action == "deny" and len(sys.argv) > 2:
        skill_name = sys.argv[2]
        if add_denied(skill_name):
            print(f"Skill '{skill_name}' denied and added to permanent block list.")
        else:
            print(f"Skill '{skill_name}' already in denied list.")
            
    elif action == "approve" and len(sys.argv) > 2:
        skill_name = sys.argv[2]
        if confirm_skill(skill_name):
            # Send double confirmation
            keyboard = create_confirmation_keyboard(skill_name)
            send_telegram_message(f"Confirm push skill '{skill_name}' to public repo?", keyboard)
            print(f"Skill '{skill_name}' confirmed for push.")
        else:
            print(f"Skill '{skill_name}' not found in pending approvals.")
            
    elif action == "push":
        push_to_public()
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
