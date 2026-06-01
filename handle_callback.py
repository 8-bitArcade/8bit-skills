#!/usr/bin/env python3
"""
Handle Telegram callback buttons for skill approval workflow.
Called by cron job agent when user clicks approve/deny buttons.
"""

import sys
import os
from pathlib import Path

# Add repo to path
sys.path.insert(0, str(Path(__file__).parent))
import approval_state

def handle_callback(callback_data):
    """Process callback data from Telegram button clicks."""
    action, skill_name = callback_data.split(":", 1)
    
    if action == "deny":
        approval_state.add_denied(skill_name)
        return f"Skill '{skill_name}' denied and added to permanent block list."
    
    elif action == "approve":
        # Send double confirmation
        keyboard = approval_state.create_confirmation_keyboard(skill_name)
        approval_state.send_telegram_message(
            f"Confirm push skill '{skill_name}' to public repo?",
            keyboard
        )
        return f"Confirmation request sent for '{skill_name}'."
    
    elif action == "confirm_push":
        approval_state.confirm_skill(skill_name)
        return f"Skill '{skill_name}' confirmed for push."
    
    elif action == "cancel":
        return f"Cancelled push for '{skill_name}'."
    
    return f"Unknown action: {action}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: handle_callback.py <callback_data>")
        sys.exit(1)
    
    callback_data = sys.argv[1]
    result = handle_callback(callback_data)
    print(result)
