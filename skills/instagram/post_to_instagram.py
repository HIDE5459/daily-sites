#!/usr/bin/env python3
"""Post images to Instagram via browser automation.
Since Instagram doesn't have a free posting API, we use the mobile web interface."""

import os
import sys
import json
import time
from pathlib import Path

# This script prepares posts for manual/browser posting
# Instagram posting requires either:
# 1. Meta Business API (requires Facebook Page + review process)
# 2. Browser automation (what we'll use)
# 3. Third-party tools

OUTPUT_DIR = Path(__file__).parent.parent.parent / "instagram" / "images"
QUEUE_FILE = Path(__file__).parent.parent.parent / "instagram" / "post_queue.json"


def load_queue() -> list:
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def save_queue(queue: list):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2))


def add_to_queue(image_path: str, caption: str):
    queue = load_queue()
    queue.append({
        "image": image_path,
        "caption": caption,
        "status": "pending",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    })
    save_queue(queue)
    print(f"Added to queue: {Path(image_path).name}")


def list_queue():
    queue = load_queue()
    if not queue:
        print("Queue is empty")
        return
    for i, item in enumerate(queue):
        status = item.get("status", "pending")
        name = Path(item["image"]).name
        print(f"  [{i}] {status:8s} | {name} | {item['caption'][:40]}...")


def queue_all_images():
    """Add all generated travel images to the posting queue."""
    from generate_image import DESTINATIONS
    
    images = sorted(OUTPUT_DIR.glob("travel_*.jpg"))
    queue = load_queue()
    queued_images = {item["image"] for item in queue}
    
    added = 0
    for img in images:
        img_str = str(img)
        if img_str in queued_images:
            continue
        
        # Find matching destination
        dest_name = None
        for dest in DESTINATIONS:
            if f"travel_{dest}_" in img.name:
                dest_name = dest
                break
        
        if dest_name and dest_name in DESTINATIONS:
            caption = DESTINATIONS[dest_name]["caption"]
            add_to_queue(img_str, caption)
            added += 1
    
    print(f"\n📝 Added {added} images to queue. Total: {len(load_queue())}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python post_to_instagram.py queue-all   - Queue all generated images")
        print("  python post_to_instagram.py list        - List queue")
        print("  python post_to_instagram.py add <path> <caption>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "queue-all":
        queue_all_images()
    elif cmd == "list":
        list_queue()
    elif cmd == "add" and len(sys.argv) >= 4:
        add_to_queue(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
