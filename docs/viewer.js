// -----------------------
// Manifest loader
// -----------------------
async function loadManifest() {
  const url = "manifest.json";
  console.log("Loading manifest:", url);
  
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to load manifest: " + res.status);

  const manifest = await res.json();
  return manifest.files;
}

// -----------------------
// Folder handling
// -----------------------
function buildFolderIndex(files) {
  const set = new Set();
  for (const f of files) set.add(f.folder);
  return Array.from(set).sort();
}

function populateFolderSelect(folders) {
  const sel = document.getElementById("folderSelect");
  sel.innerHTML = "";
  for (const f of folders) {
    const opt = document.createElement("option");
    opt.textContent = f;
    opt.value = f;
    sel.appendChild(opt);
  }
}

function filterFiles(files, folder) {
  return files.filter(f => f.folder === folder);
}

function populateFileSelect(files) {
  const sel = document.getElementById("fileSelect");
  sel.innerHTML = "";
  for (const f of files) {
    const opt = document.createElement("option");
    opt.value = f.json_path;
    opt.textContent = f.name;
    sel.appendChild(opt);
  }
}

// -----------------------
// Load one JSON annotation
// -----------------------
async function loadJson(path) {
  console.log("Loading JSON:", path);
  const res = await fetch(path);
  if (!res.ok) throw new Error("Error loading " + path);
  return await res.json();
}

// -----------------------
// Rendering question + answer
// -----------------------
function normalizedAnswers(raw) {
  return new Set(
    String(raw || "")
      .split(/,|\/|\bor\b/i)
      .map(s => s.trim().toLowerCase())
      .filter(Boolean)
  );
}

function isNumber(s) {
  return s !== "" && !Number.isNaN(Number(s));
}

function renderQuestion(data) {
  const card = document.getElementById("questionCard");
  card.innerHTML = `
    <h2>${data.Game} <span class="id-tag">(ID ${data.ID})</span></h2>
    <p class="question-label">❓ Question:</p>
    <p class="question-text">${data.Question}</p>
  `;

  const info = document.getElementById("answerInfo");
  info.textContent = "";
  info.className = "answer-info";
}

function attachAnswerLogic(data) {
  const raw = String(data.Answer || "").trim();
  const accepted = normalizedAnswers(raw);

  const input = document.getElementById("answerInput");
  const button = document.getElementById("checkButton");
  const info = document.getElementById("answerInfo");

  const sol = document.getElementById("solutionText");
  sol.innerHTML = `
      <strong>Expected:</strong> ${raw || "—"}<br>
      <strong>Rationale:</strong> ${data.Rationale || "—"}
    `;

  button.onclick = () => {
    const user = input.value.trim().toLowerCase();
    let ok = false;

    if (accepted.has(user)) ok = true;
    else if (isNumber(user)) {
      for (const a of accepted)
        if (isNumber(a) && Math.abs(Number(a) - Number(user)) < 1e-9)
          ok = true;
    }

    info.textContent = ok ? "✅ Correct!" : "❌ Not quite. Try again.";
    info.className = "answer-info " + (ok ? "correct" : "wrong");
  };
}

// -----------------------
// Render image (LOCAL)
// -----------------------
function renderImage(data) {
  const imgContainer = document.getElementById("imageContainer");
  const img = document.getElementById("gameImage");
  const caption = document.getElementById("imageCaption");
  const link = document.getElementById("imageLink");

  let url = data.game_state_url;
  if (!url) {
    imgContainer.classList.add("hidden");
    return;
  }
  if (Array.isArray(url)) url = url[0];

  const fileName = url.split("/").pop();

  const folder = data.Game.toLowerCase().replace(/\s+/g, "_");

  const localPath = `images/${folder}/${fileName}`;

  console.log("Image:", localPath);

  imgContainer.classList.remove("hidden");
  img.src = localPath;
  caption.textContent = fileName;
  link.href = localPath;

  img.onerror = () => {
    caption.textContent = "Image failed to load: " + localPath;
  };
}

// prev and next scroller 
// ---------------------------------------------------------
// FIXED: Previous / Next navigation (fully working)
// ---------------------------------------------------------
let GLOBAL_FILES = [];
let GLOBAL_CURRENT_FOLDER = "";
let loadAndRenderRef = null;

function goRelative(offset) {
  const fileSelect = document.getElementById("fileSelect");

  const options = Array.from(fileSelect.options);
  if (options.length === 0) return;

  const values = options.map(o => o.value);
  const current = fileSelect.value;
  let idx = values.indexOf(current);

  if (idx === -1) return;

  let next = idx + offset;
  if (next < 0) next = values.length - 1;
  if (next >= values.length) next = 0;

  const nextPath = values[next];
  fileSelect.value = nextPath;

  if (loadAndRenderRef) loadAndRenderRef(nextPath);
}

document.getElementById("prevBtn").onclick = () => goRelative(-1);
document.getElementById("nextBtn").onclick = () => goRelative(1);


// -----------------------
// Initialize viewer
// -----------------------
// -----------------------
// Initialize viewer
// -----------------------
(async function init() {
  const questionCard = document.getElementById("questionCard");

  try {
    const files = await loadManifest();
    GLOBAL_FILES = files;                     // <-- make files visible to arrows

    const folders = buildFolderIndex(files);
    populateFolderSelect(folders);

    const folderSel = document.getElementById("folderSelect");
    const fileSel = document.getElementById("fileSelect");

    async function loadAndRender(path) {
      const data = await loadJson(path);
      renderQuestion(data);
      attachAnswerLogic(data);
      renderImage(data);
    }

    // Expose loadAndRender to arrows
    loadAndRenderRef = loadAndRender;         // <-- required for prev/next

    function refresh() {
      GLOBAL_CURRENT_FOLDER = folderSel.value; // <-- track folder for arrows
      const filtered = filterFiles(files, GLOBAL_CURRENT_FOLDER);
      populateFileSelect(filtered);

      if (filtered.length > 0)
        loadAndRender(filtered[0].json_path);
    }

    folderSel.onchange = refresh;
    fileSel.onchange = () => loadAndRender(fileSel.value);

    // initial load
    folderSel.value = folders[0];
    refresh();

  } catch (err) {
    console.error(err);
    questionCard.innerHTML = `<p style="color:#f55;">Init error: ${err}</p>`;
  }
})();
