import json
from pathlib import Path

ROOT = Path("annotation_data_blanked")
ROOT.mkdir(parents=True, exist_ok=True)

items = []

for j in sorted(ROOT.glob("*.json")):
    if j.name == "manifest.json":
        continue

    data = json.loads(j.read_text())
    game = data.get("Game", "Unknown")
    tier = data.get("tier")
    folder = f"{game.lower()}_tier{tier}" if tier is not None else game.lower()

    items.append({
        "name": j.name,
        "json_path": f"annotation_data_blanked/{j.name}",
        "game": game,
        "tier": tier,
        "folder": folder,
    })

manifest = {"files": items}
out = ROOT / "manifest.json"
out.write_text(json.dumps(manifest, indent=2))
print(f"✅ wrote {out} with {len(items)} entries")
