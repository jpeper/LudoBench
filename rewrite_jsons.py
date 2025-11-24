#!/usr/bin/env python3
import os, json, re

BASE = "annotation_data"    # top-level annotation folder
IMG_ROOT = "gamestates/images"
JSON_ROOT = "gamestates/json"

# Extract filename from any URL
URL_EXTRACT = re.compile(r".*/([^/?]+)(?:\?.*)?$")

def convert_to_local(url, prefix, game_folder):
    """Convert GitHub or remote URL → local relative path."""
    if isinstance(url, list):
        return [convert_to_local(u, prefix, game_folder) for u in url]

    if not isinstance(url, str) or not url.strip():
        return url

    m = URL_EXTRACT.match(url)
    if not m:
        return url

    filename = m.group(1)
    return f"{prefix}/{game_folder}/{filename}"


def sanitize_json(path):
    with open(path, "r") as f:
        data = json.load(f)

    # Determine destination folder name from Game
    game = data.get("Game", "")
    game_folder = game.lower().replace(" ", "_")

    # Fix all game_state_url entries
    if "game_state_url" in data:
        data["game_state_url"] = convert_to_local(
            data["game_state_url"], IMG_ROOT, game_folder
        )

    # Fix / convert json_game_state_url instead of blanking it
    if "json_game_state_url" in data:
        data["json_game_state_url"] = convert_to_local(
            data["json_game_state_url"], JSON_ROOT, game_folder
        )

    # Remove Rationale content but keep key (double-blind)
    if "Rationale" in data:
        data["Rationale"] = ""

    # Write sanitized JSON back
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    print("✔ Sanitized:", path)


def walk_all():
    for root, _, files in os.walk(BASE):
        for f in files:
            if f.endswith(".json"):
                sanitize_json(os.path.join(root, f))


if __name__ == "__main__":
    walk_all()
    print("\n all JSON files sanitized successfully!")
