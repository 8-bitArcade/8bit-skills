#!/usr/bin/env python3
"""
Obsidian Linker: Injects [[wikilinks]] into markdown files based on a master entity list.
"""
import json
import os
import re
import sys

# Path to the link list
LINK_LIST_PATH = os.path.expanduser("~/.hermes/skills/note-taking/obsidian-linker/references/link-list.json")

def load_link_list():
    """Load the master link list."""
    try:
        with open(LINK_LIST_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Link list not found at {LINK_LIST_PATH}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {LINK_LIST_PATH}", file=sys.stderr)
        sys.exit(1)

def is_in_code_block(line, in_code_block):
    """Check if a line is inside a code block."""
    if line.strip().startswith('```'):
        return not in_code_block
    return in_code_block

def link_text(text, entities):
    """
    Replace entities in text with [[wikilinks]].
    Respects word boundaries and avoids double-linking.
    """
    # Sort entities by length (descending) to match longer phrases first
    sorted_entities = sorted(entities, key=len, reverse=True)
    
    for entity in sorted_entities:
        # Create a regex pattern with word boundaries
        # Escape special regex characters in the entity name
        escaped_entity = re.escape(entity)
        # Use word boundaries to avoid partial matches
        # Negative lookbehind/lookahead to skip already-linked entities
        pattern = r'(?<!\[\[)\b' + escaped_entity + r'\b(?!\]\])'
        
        # Replace with [[entity]]
        text = re.sub(
            pattern,
            lambda m: f'[[{m.group(0)}]]',
            text,
            flags=re.IGNORECASE
        )
    
    return text

def process_file(file_path):
    """Process a single markdown file."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}", file=sys.stderr)
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}", file=sys.stderr)
        return False
    
    link_list = load_link_list()
    
    # Flatten all entities into a single list
    entities = []
    for category, items in link_list.items():
        entities.extend(items)
    
    if not entities:
        print("⚠️ No entities found in link list", file=sys.stderr)
        return False
    
    # Process lines
    linked_lines = []
    in_code_block = False
    changes_made = False
    
    for line in lines:
        # Check if we're in a code block
        if is_in_code_block(line, in_code_block):
            in_code_block = not in_code_block
            linked_lines.append(line)
            continue
        
        if not in_code_block:
            # Link the text
            original_line = line
            line = link_text(line, entities)
            if line != original_line:
                changes_made = True
            linked_lines.append(line)
        else:
            linked_lines.append(line)
    
    # Write back if changes were made
    if changes_made:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(linked_lines)
            print(f"✅ Linked: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}", file=sys.stderr)
            return False
    else:
        print(f"ℹ️ No changes: {file_path}")
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 obsidian-linker.py <file_path> [file_path2 ...]", file=sys.stderr)
        sys.exit(1)
    
    files = sys.argv[1:]
    results = []
    
    for file_path in files:
        results.append(process_file(file_path))
    
    if all(results):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
