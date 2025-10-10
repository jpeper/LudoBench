# RulesBench Example Visualizer – Streamlit
# -------------------------------------------------
# Run with:
#   pip install streamlit requests pillow
#   streamlit run streamlit_app.py
# (Optionally pass a starting folder: streamlit run streamlit_app.py -- --folder ./my_examples)
# -------------------------------------------------

import argparse
import json
import os
import pathlib
import sys
from io import BytesIO
import re

import requests
import streamlit as st
from PIL import Image

# -----------------------------
# CLI args (so `--folder` works)
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--folder", default="examples", help="Directory containing the JSON examples")
cli_args, _ = parser.parse_known_args(sys.argv[1:])
folder_path = pathlib.Path(cli_args.folder)
# -----------------------------

if "json_buffer" not in st.session_state:
    st.session_state.json_buffer = ""

st.set_page_config(page_title="RulesBench Visualizer", layout="wide")
st.title("RulesBench Example Visualizer")

# Sidebar – choose / change folder
BASE_DIR = pathlib.Path(cli_args.folder)

# Find all subdirectories that contain JSON files
subfolders = [p for p in BASE_DIR.iterdir() if p.is_dir() and list(p.glob("*.json"))]

if not subfolders:
    st.sidebar.error(f"No JSON subfolders found under {BASE_DIR}")
    st.stop()

# Dropdown with folder names
selected_subfolder = st.sidebar.selectbox(
    "Choose JSON folder",
    [p.name for p in subfolders]
)

folder_path = BASE_DIR / selected_subfolder

json_files = sorted(folder_path.glob("*.json"))

if not json_files:
    st.warning(f"No *.json files found in {folder_path}")
    st.stop()
# Sidebar – choose example
file_options = [p.name for p in json_files]
selected_name = st.sidebar.selectbox("Choose example", file_options)
json_path = folder_path / selected_name

# Load JSON
try:
    data = json.loads(json_path.read_text(encoding="utf-8"))
except Exception as exc:
    st.error(f"Failed to parse {selected_name}: {exc}")
    st.stop()

# refresh buffer if we switched files ------------------
if st.session_state.get("current_file") != selected_name:
    st.session_state.current_file = selected_name
    st.session_state.json_buffer = json.dumps(
        data, indent=2, ensure_ascii=False
    )

# Layout
col_left, col_right = st.columns(2)

# -----------------------------
# Left question – JSON details + editor
with col_left:
    
   
    game = data.get('Game', '?')
    qid = data.get('ID', '?')
    question = data.get('Question', 'No question provided.')

    st.markdown(
        f"""
        <div style="
            background-color:rgba(255,255,255,0.05);
            border-radius:12px;
            padding:18px 20px;
            border:1px solid rgba(255,255,255,0.15);
            box-shadow:0 2px 6px rgba(0,0,0,0.25);
        ">
            <h3 style="margin-top:0; color:#FFFFFF;">
                 {game} <span style="font-size:0.8em; color:#BBBBBB;">(ID {qid})</span>
            </h3>
            <p style="font-size:18px; line-height:1.6; color:#EEEEEE;">
                <strong style="color:#FF6666;">❓ Question:</strong><br>
                {question}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    # --- Build accepted answers set from JSON ("Answer")
    raw_answer = str(data.get("Answer", "")).strip()
    # allow multiple forms like "2", "two" or "3/three", or "A, B"
    accepted = {
        token.strip().lower()
        for token in re.split(r",|/|\bor\b", raw_answer)
        if token.strip()
    }

    def _is_number(s: str):
        try:
            float(s)
            return True
        except Exception:
            return False

    user = st.text_input("Your answer", key=f"ans_{data.get('ID','')}")
    check = st.button("Check", key=f"check_{data.get('ID','')}")

    if check:
        norm = user.strip().lower()

        correct = False
        # text match (case-insensitive)
        if norm in accepted:
            correct = True
        # numeric match with tiny tolerance
        elif _is_number(norm):
            for a in accepted:
                if _is_number(a) and abs(float(a) - float(norm)) < 1e-9:
                    correct = True
                    break

        if correct:
            st.success("✅ Correct!")
        else:
            st.error("❌ Not quite. Try again.")

        with st.expander("Show solution / rationale"):
            st.markdown(f"**Expected:** {raw_answer or '—'}")
            st.markdown(f"**Rationale:** {data.get('Rationale','—')}")
# -----------------------------
# Right – image viewer (with simple caching)
with col_right:
    urls = data.get("game_state_url")

    if urls:
        # Normalize to list if it's a single string
        if isinstance(urls, str):
            urls = [urls]

        cache_dir = folder_path / "_image_cache"
        cache_dir.mkdir(exist_ok=True)

        for url in urls:
            img_file = cache_dir / pathlib.Path(url).name

            if not img_file.exists():
                try:
                    r = requests.get(url, timeout=10)
                    r.raise_for_status()
                    img_file.write_bytes(r.content)
                except Exception as exc:
                    st.error(f"Couldn't fetch image: {exc}")
                    continue

            if img_file.exists():
                try:
                    image = Image.open(img_file)
                    st.image(image, caption=f"Game state: {pathlib.Path(url).name}", width="stretch")
                    st.markdown(f"[🖼️ Open full image]({url})", unsafe_allow_html=True)
                except Exception as exc:
                    st.error(f"Failed to open cached image: {exc}")
    else:
        st.info("No `game_state_url` found in this JSON.")

# -----------------------------
# Debug raw view (optional)
# with st.expander("▶ Raw JSON object"):
#     st.json(data)
