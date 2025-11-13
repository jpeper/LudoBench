// docs/viewer.js

// --- Helper: convert GitHub "blob" URLs to raw image URLs ---
// --- Helper: convert GitHub "blob" URLs to raw image URLs ---
function fixImageUrl(url) {
  if (!url) return null;

  // Already a raw link
  if (url.includes("raw.githubusercontent.com")) {
    return url;
  }

  // Match: https://github.com/<user>/<repo>/blob/<branch>/<path>
  const m = url.match(
    /^https:\/\/github\.com\/([^/]+)\/([^/]+)\/blob\/([^/]+)\/(.+)$/
  );
  if (m) {
    const [, user, repo, branch, path] = m;
    return `https://raw.githubusercontent.com/${user}/${repo}/${branch}/${path}`;
  }

  // Any other github.com URL → just add ?raw=1 as a fallback
  if (url.startsWith("https://github.com/") && !url.includes("?raw=1")) {
    return url + "?raw=1";
  }

  // Local or other URLs
  return url;
}


// --- Load manifest ---
async function loadManifest() {
  const url = "annotation_data_blanked/manifest.json";
  console.log("Fetching manifest from:", url);

  const res = await fetch(url);
  console.log("Manifest response status:", res.status, res.statusText);
  if (!res.ok) {
    throw new Error("HTTP " + res.status + " when fetching " + url);
  }

  let manifest;
  try {
    manifest = await res.json();
  } catch (e) {
    console.error("Failed to parse manifest JSON:", e);
    throw e;
  }

  console.log("Raw manifest JSON:", manifest);

  if (manifest && Array.isArray(manifest.files)) {
    return manifest.files;
  }
  if (Array.isArray(manifest)) {
    return manifest;
  }

  throw new Error("Manifest has wrong shape (expected {files:[...]} or [...])");
}

function buildFolderIndex(files) {
  const folders = new Set(["all"]);
  for (const f of files) {
    // We TRUST the folder field already in manifest.json
    if (f.folder) folders.add(f.folder);
  }
  return Array.from(folders);
}

function populateFolderSelect(folders) {
  const sel = document.getElementById("folderSelect");
  sel.innerHTML = "";
  folders.forEach((f) => {
    const opt = document.createElement("option");
    opt.value = f;
    opt.textContent = f;
    sel.appendChild(opt);
  });
}

function filterFilesByFolder(files, folder) {
  if (folder === "all") return files;
  return files.filter((f) => f.folder === folder);
}

function populateFileSelect(files) {
  const sel = document.getElementById("fileSelect");
  sel.innerHTML = "";
  files.forEach((f) => {
    const opt = document.createElement("option");
    opt.value = f.json_path;
    opt.textContent = f.name;
    sel.appendChild(opt);
  });
}

async function loadJson(path) {
  console.log("Fetching JSON:", path);
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error("HTTP " + res.status + " when fetching " + path);
  }
  return await res.json();
}

// --- Answer helpers ---
function normalizedAnswers(rawAnswer) {
  const tokens = String(rawAnswer || "")
    .split(/,|\/|\bor\b/i)
    .map((s) => s.trim())
    .filter(Boolean);
  const out = new Set();
  for (const t of tokens) out.add(t.toLowerCase());
  return out;
}

function isNumber(s) {
  if (s === "" || s == null) return false;
  return !Number.isNaN(Number(s));
}

// --- Rendering ---
function renderQuestion(data) {
  const game = data.Game ?? "?";
  const qid = data.ID ?? "?";
  const question = data.Question ?? "No question provided.";

  const card = document.getElementById("questionCard");
  card.innerHTML = `
    <h2>${game} <span class="id-tag">(ID ${qid})</span></h2>
    <p class="question-label">❓ Question:</p>
    <p class="question-text">${question}</p>
  `;

  const info = document.getElementById("answerInfo");
  info.textContent = "";
  info.className = "answer-info";
}

function attachAnswerLogic(data) {
  const rawAnswer = String(data.Answer ?? "").trim();
  const accepted = normalizedAnswers(rawAnswer);

  const input = document.getElementById("answerInput");
  const button = document.getElementById("checkButton");
  const info = document.getElementById("answerInfo");
  const sol = document.getElementById("solutionText");

  sol.innerHTML = `
    <strong>Expected:</strong> ${rawAnswer || "—"}<br>
    <strong>Rationale:</strong> ${data.Rationale ?? "—"}
  `;

  button.onclick = () => {
    const user = input.value.trim();
    const norm = user.toLowerCase();

    let correct = false;
    if (accepted.has(norm)) {
      correct = true;
    } else if (isNumber(norm)) {
      for (const a of accepted) {
        if (isNumber(a) && Math.abs(Number(a) - Number(norm)) < 1e-9) {
          correct = true;
          break;
        }
      }
    }

    if (correct) {
      info.textContent = "✅ Correct!";
      info.className = "answer-info correct";
    } else {
      info.textContent = "❌ Not quite. Try again.";
      info.className = "answer-info wrong";
    }
  };
}


function renderImage(data) {
  const imgContainer = document.getElementById("imageContainer");
  const imgEl = document.getElementById("gameImage");
  const captionEl = document.getElementById("imageCaption");
  const linkEl = document.getElementById("imageLink");

  let url = data.game_state_url;
  if (!url) {
    imgContainer.classList.add("hidden");
    return;
  }

  // If JSON has a list of URLs, take the first one
  if (Array.isArray(url)) {
    url = url[0];
  }

  // Extract JUST the file name (e.g., "t4_1.png")
  const fileName = url.split("/").pop();

  /**
   * Determine folder based on Game field.
   * e.g. "Res Arcana" -> "res_arcana"
   * e.g. "pax_ren" stays "pax_ren"
   */
  let folder = data.Game.toLowerCase().replace(/\s+/g, "_");

  // Build local path under docs/images/
  const localPath = `images/${folder}/${fileName}`;

  console.log("Loading LOCAL image:", localPath);

  imgContainer.classList.remove("hidden");
  imgEl.src = localPath;
  captionEl.textContent = fileName;
  linkEl.href = localPath;

  imgEl.onerror = () => {
    captionEl.textContent = "Image failed to load: " + localPath;
    console.error("IMAGE LOAD FAILED:", localPath);
  };
}

function renderImage(data) {
  const imgContainer = document.getElementById("imageContainer");
  const imgEl = document.getElementById("gameImage");
  const captionEl = document.getElementById("imageCaption");
  const linkEl = document.getElementById("imageLink");

  let url = data.game_state_url;
  if (!url) {
    imgContainer.classList.add("hidden");
    return;
  }

  // If JSON has a list of URLs, take the first one
  if (Array.isArray(url)) {
    url = url[0];
  }

  // Extract JUST the file name (e.g., "t4_1.png")
  const fileName = url.split("/").pop();

  /**
   * Determine folder based on Game field.
   * e.g. "Res Arcana" -> "res_arcana"
   * e.g. "pax_ren" stays "pax_ren"
   */
  let folder = data.Game.toLowerCase().replace(/\s+/g, "_");

  // Build local path under docs/images/
  const localPath = `images/${folder}/${fileName}`;

  console.log("Loading LOCAL image:", localPath);

  imgContainer.classList.remove("hidden");
  imgEl.src = localPath;
  captionEl.textContent = fileName;
  linkEl.href = localPath;

  imgEl.onerror = () => {
    captionEl.textContent = "Image failed to load: " + localPath;
    console.error("IMAGE LOAD FAILED:", localPath);
  };
}



// --- Main init ---
(async function init() {
  const questionCard = document.getElementById("questionCard");

  try {
    const files = await loadManifest();  // <--- if this throws we show message below

    const folders = buildFolderIndex(files);
    populateFolderSelect(folders);

    const folderSelect = document.getElementById("folderSelect");
    const fileSelect = document.getElementById("fileSelect");

    async function loadAndRender(path) {
      const data = await loadJson(path);
      renderQuestion(data);
      attachAnswerLogic(data);
      renderImage(data);
    }

    function refreshFileList() {
      const folder = folderSelect.value;
      const visible = filterFilesByFolder(files, folder);
      populateFileSelect(visible);
      if (visible.length > 0) {
        loadAndRender(visible[0].json_path);
      }
    }

    folderSelect.onchange = refreshFileList;
    fileSelect.onchange = () => loadAndRender(fileSelect.value);

    // Initial population
    refreshFileList();
  } catch (err) {
    console.error("Init error:", err);
    questionCard.innerHTML =
      `<p style="color:#f55;">Failed to load manifest or examples: ${err}</p>`;
  }
})();
