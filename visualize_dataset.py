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
# Left – JSON details + editor
with col_left:
    st.header(f"{data.get('Game','?')} (ID {data.get('ID','?')})")
    st.markdown(f"**Question:** {data.get('Question','')}")
    # (skip answer/rationale here to encourage blind editing)

    with st.form("json_editor", clear_on_submit=False):
        st.session_state.json_buffer = st.text_area(
            "Edit JSON below ⤵",
            value=(
                st.session_state.json_buffer
                or json.dumps(data, indent=2, ensure_ascii=False)
            ),
            height=400,
            key="editor_text",
        )
        submitted = st.form_submit_button("💾 Save JSON", type="primary")

    if submitted:
        with st.spinner("Saving…"):
            try:
                parsed = json.loads(st.session_state.json_buffer)
                json_path.write_text(
                    json.dumps(parsed, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                data = parsed           # refresh preview
                st.success("Saved!")
            except json.JSONDecodeError as err:
                st.error(f"Invalid JSON: {err}")

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
                    st.image(image, caption=f"Game state: {pathlib.Path(url).name}", use_column_width=True)
                    st.markdown(f"[🖼️ Open full image]({url})", unsafe_allow_html=True)
                except Exception as exc:
                    st.error(f"Failed to open cached image: {exc}")
    else:
        st.info("No `game_state_url` found in this JSON.")

# -----------------------------
# Debug raw view (optional)
with st.expander("▶ Raw JSON object"):
    st.json(data)
