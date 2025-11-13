#!/usr/bin/env python3
import os, json

ROOT = "annotation_data"
OUT = "manifest.json"

entries = []

for folder in sorted(os.listdir(ROOT)):
    full_folder = os.path.join(ROOT, folder)
    if not os.path.isdir(full_folder):
        continue

    # infer game name from folder
    #   res_arcana_tier1 → Res Arcana
    #   pax_ren_tier2 → Pax Ren
    game = folder.split("_tier")[0].replace("_", " ").title()

    for fname in sorted(os.listdir(full_folder)):
        if not fname.endswith(".json"):
            continue

        json_path = f"annotation_data/{folder}/{fname}"

        entries.append({
            "name": fname,
            "folder": folder,
            "game": game,
            "json_path": json_path
        })

manifest = {"files": entries}

with open(OUT, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Created {OUT} with {len(entries)} JSON entries.")
