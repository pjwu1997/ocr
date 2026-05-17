const refs = {
  dropZone: document.getElementById("dropZone"),
  fileInput: document.getElementById("fileInput"),
  fileInfo: document.getElementById("fileInfo"),
  fileName: document.getElementById("fileName"),
  fileMeta: document.getElementById("fileMeta"),
  clearFileBtn: document.getElementById("clearFileBtn"),
  runBtn: document.getElementById("runBtn"),
  progressArea: document.getElementById("progressArea"),
  progressFill: document.getElementById("progressFill"),
  progressText: document.getElementById("progressText"),
  emptyState: document.getElementById("emptyState"),
  resultsArea: document.getElementById("resultsArea"),
  originalGallery: document.getElementById("originalGallery"),
  markdownBody: document.getElementById("markdownBody"),
  markdownRaw: document.getElementById("markdownRaw"),
  layoutGallery: document.getElementById("layoutGallery"),
  cropsGallery: document.getElementById("cropsGallery"),
  copyMdBtn: document.getElementById("copyMdBtn"),
  toggleRawBtn: document.getElementById("toggleRawBtn"),
  toast: document.getElementById("toast"),
  tabBtns: document.querySelectorAll(".tab-btn"),
  fieldsTableBody: document.getElementById("fieldsTableBody"),
  editReason: document.getElementById("editReason"),
  saveReviewBtn: document.getElementById("saveReviewBtn"),
  resultTabs: document.querySelectorAll(".result-tab"),
  singleView: document.getElementById("singleView"),
  rulesView: document.getElementById("rulesView"),
  historyView: document.getElementById("historyView"),
  docTypeSelect: document.getElementById("docTypeSelect"),
  detectedTypeBadge: document.getElementById("detectedTypeBadge"),
  rulesTableBody: document.getElementById("rulesTableBody"),
  addRuleBtn: document.getElementById("addRuleBtn"),
  historyTableBody: document.getElementById("historyTableBody"),
  detailBtn: document.getElementById("detailBtn"),
};

let selectedFile = null;
let rawMarkdown = "";
let showRaw = false;
let currentResultId = null;

// ── Helpers ──

function showToast(msg) {
  refs.toast.textContent = msg;
  refs.toast.classList.add("show");
  setTimeout(() => refs.toast.classList.remove("show"), 2000);
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1048576).toFixed(1) + " MB";
}

// ── Load rules into dropdown ──

let allRules = [];

async function loadRules() {
  try {
    const res = await fetch("/api/rules");
    if (!res.ok) return;
    allRules = await res.json();
    // Populate dropdown
    refs.docTypeSelect.innerHTML = '<option value="0">-- Select type --</option>';
    allRules.forEach((rule) => {
      const opt = document.createElement("option");
      opt.value = rule.id;
      opt.textContent = `${rule.welfare_item}. ${rule.category} — ${rule.doc_type}`;
      refs.docTypeSelect.appendChild(opt);
    });
  } catch (e) {
    console.error("Failed to load rules:", e);
  }
}

loadRules();

// ── File selection ──

function handleFile(file) {
  const ext = file.name.split(".").pop().toLowerCase();
  const allowed = ["pdf", "jpg", "jpeg", "png"];
  if (!allowed.includes(ext)) {
    showToast("Unsupported file type: ." + ext);
    return;
  }
  selectedFile = file;
  refs.fileName.textContent = file.name;
  refs.fileMeta.textContent = formatSize(file.size) + " — " + ext.toUpperCase();
  refs.fileInfo.style.display = "block";
  refs.dropZone.style.display = "none";
  refs.runBtn.disabled = false;
  refs.detailBtn.disabled = false;
}

refs.dropZone.addEventListener("click", () => refs.fileInput.click());

refs.fileInput.addEventListener("change", () => {
  if (refs.fileInput.files.length > 0) handleFile(refs.fileInput.files[0]);
});

refs.dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  refs.dropZone.classList.add("dragover");
});

refs.dropZone.addEventListener("dragleave", () => {
  refs.dropZone.classList.remove("dragover");
});

refs.dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  refs.dropZone.classList.remove("dragover");
  if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});

refs.clearFileBtn.addEventListener("click", () => {
  selectedFile = null;
  refs.fileInput.value = "";
  refs.fileInfo.style.display = "none";
  refs.dropZone.style.display = "block";
  refs.runBtn.disabled = true;
  refs.detailBtn.disabled = true;
});

// ── Mode switch ──

refs.tabBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    refs.tabBtns.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const mode = btn.dataset.mode;
    const aiocrView = document.getElementById("aiocrView");
    if (aiocrView) aiocrView.classList.toggle("active", mode === "aiocr");
    refs.singleView.classList.toggle("active", mode === "single");
    refs.rulesView.classList.toggle("active", mode === "rules");
    refs.historyView.classList.toggle("active", mode === "history");
    if (mode === "rules") loadRulesTable();
    if (mode === "history") loadHistory();
  });
});

// ── Result tabs ──

const allTabIds = ["tabOriginal", "tabFields", "tabMarkdown", "tabLayout", "tabCrops"];

refs.resultTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    refs.resultTabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    allTabIds.forEach((id) => document.getElementById(id).style.display = "none");
    const target = "tab" + tab.dataset.tab.charAt(0).toUpperCase() + tab.dataset.tab.slice(1);
    document.getElementById(target).style.display = "block";
  });
});

// ── Markdown toolbar ──

refs.copyMdBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(rawMarkdown).then(() => showToast("Copied to clipboard"));
});

refs.toggleRawBtn.addEventListener("click", () => {
  showRaw = !showRaw;
  refs.markdownBody.style.display = showRaw ? "none" : "block";
  refs.markdownRaw.style.display = showRaw ? "block" : "none";
  refs.toggleRawBtn.textContent = showRaw ? "Toggle Rendered" : "Toggle Raw";
});

// ── Fields review table ──

let currentFields = [];

function renderFieldsTable(fields) {
  currentFields = fields;
  refs.fieldsTableBody.innerHTML = "";
  fields.forEach((f, idx) => {
    const isNo = f.ai_value === "no";
    const isBoolField = f.ai_value === "是" || f.ai_value === "否";
    const row = document.createElement("div");
    row.className = "row row-field";
    let inputHtml;
    if (isBoolField) {
      const checked = f.ai_value === "是" ? "checked" : "";
      inputHtml = `<label class="checkbox-label"><input type="checkbox" class="review-checkbox" data-index="${idx}" ${checked} /> 是</label>`;
    } else {
      inputHtml = `<textarea class="review-textarea" data-index="${idx}" rows="1" placeholder="${isNo ? "no matching" : ""}">${isNo ? "" : f.ai_value}</textarea>`;
    }
    row.innerHTML = `
      <div class="field-label">${f.field}</div>
      <div class="ai-value${isNo ? " no-match" : ""}">${f.ai_value}</div>
      <div>${inputHtml}</div>
    `;
    refs.fieldsTableBody.appendChild(row);
  });
}

refs.saveReviewBtn.addEventListener("click", async () => {
  if (!currentResultId) {
    showToast("No OCR result to save");
    return;
  }

  const reviewed = currentFields.map((f, idx) => {
    const checkbox = refs.fieldsTableBody.querySelector(`.review-checkbox[data-index="${idx}"]`);
    const textarea = refs.fieldsTableBody.querySelector(`.review-textarea[data-index="${idx}"]`);
    return {
      field: f.field,
      ai_value: f.ai_value,
      human_value: checkbox ? (checkbox.checked ? "是" : "否") : (textarea ? textarea.value : ""),
    };
  });
  const reason = refs.editReason.value;

  try {
    const res = await fetch(`/api/results/${currentResultId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fields: reviewed, edit_reason: reason }),
    });
    if (res.ok) {
      showToast("覆核內容已儲存");
    } else {
      showToast("Save failed");
    }
  } catch (e) {
    showToast("Save error: " + e.message);
  }
});

// ── Gallery with page nav ──

function renderGalleryWithNav(container, images) {
  container.innerHTML = "";
  if (images.length === 0) {
    container.innerHTML = '<p style="color:var(--muted);text-align:center;">No images</p>';
    return;
  }

  let currentPage = 0;

  function render() {
    container.innerHTML = "";

    if (images.length > 1) {
      const nav = document.createElement("div");
      nav.className = "page-nav";
      const prevBtn = document.createElement("button");
      prevBtn.textContent = "Prev";
      prevBtn.disabled = currentPage === 0;
      prevBtn.addEventListener("click", () => { currentPage--; render(); });
      const info = document.createElement("span");
      info.textContent = `Page ${currentPage + 1} / ${images.length}`;
      const nextBtn = document.createElement("button");
      nextBtn.textContent = "Next";
      nextBtn.disabled = currentPage === images.length - 1;
      nextBtn.addEventListener("click", () => { currentPage++; render(); });
      nav.appendChild(prevBtn);
      nav.appendChild(info);
      nav.appendChild(nextBtn);
      container.appendChild(nav);
    }

    const img = document.createElement("img");
    img.src = images[currentPage];
    img.alt = `Page ${currentPage + 1}`;
    container.appendChild(img);
  }

  render();
}

// ── Run OCR ──

refs.runBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  // Show progress
  refs.runBtn.disabled = true;
  refs.detailBtn.disabled = true;
  refs.progressArea.style.display = "block";
  refs.progressFill.className = "progress-fill indeterminate";
  refs.progressText.textContent = "Processing...";
  refs.emptyState.style.display = "none";
  refs.resultsArea.style.display = "none";

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("rule_id", refs.docTypeSelect.value);

  try {
    const res = await fetch("/api/ocr", { method: "POST", body: formData });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Server error" }));
      throw new Error(err.detail || "OCR failed");
    }

    const data = await res.json();

    // Save result ID for review
    currentResultId = data.result_id || null;

    // Progress done
    refs.progressFill.className = "progress-fill";
    refs.progressFill.style.width = "100%";
    refs.progressText.textContent = "Done!";

    // Render results
    renderGalleryWithNav(refs.originalGallery, data.original_pages || []);
    renderGalleryWithNav(refs.layoutGallery, data.layout_images || []);

    // Detected type badge
    if (data.detected_type) {
      refs.detectedTypeBadge.textContent = "Document: " + data.detected_type;
      refs.detectedTypeBadge.style.display = "inline-block";
    } else {
      refs.detectedTypeBadge.style.display = "none";
    }

    // Fields (dynamic based on rule)
    renderFieldsTable(data.extracted_fields || []);

    // Markdown
    rawMarkdown = data.markdown || "";
    refs.markdownRaw.textContent = rawMarkdown;
    refs.markdownBody.innerHTML = simpleMarkdownToHtml(rawMarkdown);

    // Crops
    refs.cropsGallery.innerHTML = "";
    (data.crop_images || []).forEach((crop) => {
      const card = document.createElement("div");
      card.className = "crop-card";
      card.innerHTML = `
        <img src="${crop.url}" alt="${crop.label}" />
        <div class="crop-label">${crop.label}</div>
      `;
      refs.cropsGallery.appendChild(card);
    });

    if ((data.crop_images || []).length === 0) {
      refs.cropsGallery.innerHTML = '<p style="color:var(--muted);text-align:center;grid-column:1/-1;">No cropped regions</p>';
    }

    // Show results, activate original tab
    refs.resultsArea.style.display = "block";
    refs.resultTabs.forEach((t) => t.classList.remove("active"));
    refs.resultTabs[0].classList.add("active");
    allTabIds.forEach((id) => document.getElementById(id).style.display = "none");
    document.getElementById("tabOriginal").style.display = "block";


    showToast("OCR completed successfully");
  } catch (err) {
    refs.progressFill.className = "progress-fill";
    refs.progressFill.style.width = "0%";
    refs.progressText.textContent = "Error: " + err.message;
    showToast("Error: " + err.message);
  } finally {
    refs.runBtn.disabled = false;
  refs.detailBtn.disabled = false;
    setTimeout(() => {
      refs.progressArea.style.display = "none";
      refs.progressFill.style.width = "0%";
    }, 3000);
  }
});

// ── Detail Mode (AsiaMath OCR – detail) ──

refs.detailBtn.addEventListener("click", async () => {
  console.log("Detail Mode clicked", { selectedFile: !!selectedFile, ruleId: refs.docTypeSelect.value });
  if (!selectedFile) return;

  refs.detailBtn.disabled = true;
  refs.runBtn.disabled = true;
  refs.progressArea.style.display = "block";
  refs.progressFill.className = "progress-fill indeterminate";
  refs.progressText.textContent = "Detail Mode processing...";
  refs.emptyState.style.display = "none";
  refs.resultsArea.style.display = "none";

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("rule_id", refs.docTypeSelect.value);

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 min timeout
    const res = await fetch("/api/ocr/detail", { method: "POST", body: formData, signal: controller.signal });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Server error" }));
      throw new Error(err.detail || "Detail mode failed");
    }

    const data = await res.json();
    currentResultId = data.result_id || null;

    refs.progressFill.className = "progress-fill";
    refs.progressFill.style.width = "100%";
    refs.progressText.textContent = "Done!";

    // Render results (same as Run OCR)
    renderGalleryWithNav(refs.originalGallery, data.original_pages || []);
    renderGalleryWithNav(refs.layoutGallery, data.layout_images || []);
    renderFieldsTable(data.extracted_fields || []);

    if (data.detected_type) {
      refs.detectedTypeBadge.textContent = "Document: " + data.detected_type;
      refs.detectedTypeBadge.style.display = "inline-block";
    } else {
      refs.detectedTypeBadge.style.display = "none";
    }

    rawMarkdown = data.markdown || "";
    refs.markdownRaw.textContent = rawMarkdown;
    refs.markdownBody.innerHTML = simpleMarkdownToHtml(rawMarkdown);

    refs.cropsGallery.innerHTML = '<p style="color:var(--muted);text-align:center;grid-column:1/-1;">Detail mode: no crops</p>';

    // Show results, switch to fields tab
    refs.resultsArea.style.display = "block";
    refs.resultTabs.forEach((t) => t.classList.remove("active"));
    refs.resultTabs[1].classList.add("active");
    allTabIds.forEach((id) => document.getElementById(id).style.display = "none");
    document.getElementById("tabFields").style.display = "block";

    showToast("Detail Mode completed");
  } catch (err) {
    console.error("Detail mode error:", err);
    refs.progressFill.className = "progress-fill";
    refs.progressFill.style.width = "0%";
    refs.progressText.textContent = "Error: " + err.message;
    showToast("Error: " + err.message);
    alert("Detail Mode Error: " + err.message);
  } finally {
    refs.detailBtn.disabled = false;
    refs.runBtn.disabled = false;
    setTimeout(() => {
      refs.progressArea.style.display = "none";
      refs.progressFill.style.width = "0%";
    }, 3000);
  }
});

// ── Rules Management ──

async function loadRulesTable() {
  try {
    const res = await fetch("/api/rules");
    if (!res.ok) return;
    const rules = await res.json();
    refs.rulesTableBody.innerHTML = "";
    rules.forEach((rule) => {
      const fields = rule.fields_json || [];
      const fieldTags = fields.map((f) => `<span class="field-tag">${f.name}</span>`).join("");
      const row = document.createElement("div");
      row.className = "row row-rule";
      row.innerHTML = `
        <div>${rule.welfare_item || ""}</div>
        <div>${rule.category}</div>
        <div>${rule.doc_type}</div>
        <div class="field-tags">${fieldTags || '<span style="color:var(--muted)">—</span>'}</div>
        <div class="row-actions">
          <button class="btn-icon" onclick="editRule(${rule.id})">Edit</button>
          <button class="btn-icon danger" onclick="deleteRule(${rule.id})">Del</button>
        </div>
      `;
      refs.rulesTableBody.appendChild(row);
    });
  } catch (e) {
    console.error("Failed to load rules:", e);
  }
}

refs.addRuleBtn.addEventListener("click", () => showRuleModal());

function showRuleModal(rule = null) {
  const isEdit = !!rule;
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";

  const fieldsStr = rule
    ? (rule.fields_json || []).map((f) => f.name).join("\n")
    : "";

  overlay.innerHTML = `
    <div class="modal-card">
      <h3>${isEdit ? "Edit Rule" : "Add Rule"}</h3>
      <label>Welfare Item #</label>
      <input id="modalWelfare" value="${rule?.welfare_item || ""}" />
      <label>Category</label>
      <input id="modalCategory" value="${rule?.category || ""}" />
      <label>Document Type</label>
      <input id="modalDocType" value="${rule?.doc_type || ""}" />
      <label>Fields (one per line)</label>
      <textarea id="modalFields" rows="6">${fieldsStr}</textarea>
      <label>Notes</label>
      <textarea id="modalNotes" rows="3">${rule?.notes || ""}</textarea>
      <div class="modal-actions">
        <button class="btn-ghost" id="modalCancel">Cancel</button>
        <button class="btn-primary" id="modalSave">${isEdit ? "Update" : "Create"}</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  overlay.querySelector("#modalCancel").addEventListener("click", () => overlay.remove());
  overlay.addEventListener("click", (e) => { if (e.target === overlay) overlay.remove(); });

  overlay.querySelector("#modalSave").addEventListener("click", async () => {
    const fieldNames = overlay.querySelector("#modalFields").value
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
    const fields = fieldNames.map((name) => ({ name, type: "text" }));

    const body = {
      welfare_item: overlay.querySelector("#modalWelfare").value,
      category: overlay.querySelector("#modalCategory").value,
      doc_type: overlay.querySelector("#modalDocType").value,
      fields_json: fields,
      notes: overlay.querySelector("#modalNotes").value,
    };

    const url = isEdit ? `/api/rules/${rule.id}` : "/api/rules";
    const method = isEdit ? "PUT" : "POST";

    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        overlay.remove();
        showToast(isEdit ? "Rule updated" : "Rule created");
        loadRulesTable();
        loadRules(); // refresh dropdown
      } else {
        showToast("Save failed");
      }
    } catch (e) {
      showToast("Error: " + e.message);
    }
  });
}

window.editRule = async function (id) {
  const res = await fetch("/api/rules");
  if (!res.ok) return;
  const rules = await res.json();
  const rule = rules.find((r) => r.id === id);
  if (rule) showRuleModal(rule);
};

window.deleteRule = async function (id) {
  if (!confirm("Delete this rule?")) return;
  try {
    const res = await fetch(`/api/rules/${id}`, { method: "DELETE" });
    if (res.ok) {
      showToast("Rule deleted");
      loadRulesTable();
      loadRules();
    }
  } catch (e) {
    showToast("Error: " + e.message);
  }
};

// ── History ──

async function loadHistory() {
  try {
    const res = await fetch("/api/results");
    if (!res.ok) return;
    const results = await res.json();
    refs.historyTableBody.innerHTML = "";
    if (results.length === 0) {
      refs.historyTableBody.innerHTML = '<div class="row row-history"><div style="grid-column:1/-1;color:var(--muted);text-align:center;">No results yet</div></div>';
      return;
    }
    results.forEach((r) => {
      const date = r.reviewed_at || r.created_at || "";
      const dateStr = date ? new Date(date).toLocaleString() : "";
      const row = document.createElement("div");
      row.className = "row row-history";
      row.innerHTML = `
        <div style="word-break:break-all">${r.filename}</div>
        <div>${r.detected_type || "—"}</div>
        <div><span class="status-badge ${r.status}">${r.status}</span></div>
        <div style="font-size:12px;color:var(--muted)">${dateStr}</div>
      `;
      refs.historyTableBody.appendChild(row);
    });
  } catch (e) {
    console.error("Failed to load history:", e);
  }
}

// ── Simple markdown → HTML ──

function simpleMarkdownToHtml(md) {
  if (!md) return '<p style="color:var(--muted);">No text detected</p>';

  let html = md;

  // Escape HTML
  html = html.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  // Tables
  html = html.replace(/^(\|.+\|)\n(\|[-| :]+\|)\n((?:\|.+\|\n?)*)/gm, (match, header, sep, body) => {
    const ths = header.split("|").filter(Boolean).map((c) => `<th>${c.trim()}</th>`).join("");
    const rows = body.trim().split("\n").map((row) => {
      const tds = row.split("|").filter(Boolean).map((c) => `<td>${c.trim()}</td>`).join("");
      return `<tr>${tds}</tr>`;
    }).join("");
    return `<table><thead><tr>${ths}</tr></thead><tbody>${rows}</tbody></table>`;
  });

  // Headers
  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

  // Bold / italic
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Line breaks → paragraphs
  html = html.split(/\n{2,}/).map((block) => {
    if (block.startsWith("<h") || block.startsWith("<table") || block.startsWith("<pre")) return block;
    return `<p>${block.replace(/\n/g, "<br>")}</p>`;
  }).join("\n");

  return html;
}

// ───────────────────────────────────────────────────────────────────
// AIOCR (v1) — flow-based multi-file analyze
// ───────────────────────────────────────────────────────────────────

const aiocr = {
  flowSelect: document.getElementById("aiocrFlowSelect"),
  caseId: document.getElementById("aiocrCaseId"),
  dropZone: document.getElementById("aiocrDropZone"),
  fileInput: document.getElementById("aiocrFileInput"),
  fileList: document.getElementById("aiocrFileList"),
  runBtn: document.getElementById("aiocrRunBtn"),
  progress: document.getElementById("aiocrProgress"),
  progressText: document.getElementById("aiocrProgressText"),
  empty: document.getElementById("aiocrEmpty"),
  results: document.getElementById("aiocrResults"),
  jobId: document.getElementById("aiocrJobId"),
  status: document.getElementById("aiocrStatus"),
  documents: document.getElementById("aiocrDocuments"),
  warnings: document.getElementById("aiocrWarnings"),
};

let aiocrFiles = [];

async function aiocrLoadFlows() {
  if (!aiocr.flowSelect) return;
  try {
    const res = await fetch("/v1/aiocr/flows");
    if (!res.ok) throw new Error("flows " + res.status);
    const data = await res.json();
    aiocr.flowSelect.innerHTML = "";
    Object.entries(data).forEach(([key, flow]) => {
      const opt = document.createElement("option");
      opt.value = key;
      opt.textContent = `${flow.label} (${key})`;
      aiocr.flowSelect.appendChild(opt);
    });
  } catch (e) {
    aiocr.flowSelect.innerHTML = '<option value="">Failed to load flows</option>';
    console.error(e);
  }
}
aiocrLoadFlows();

function aiocrRenderFileList() {
  aiocr.fileList.innerHTML = "";
  aiocrFiles.forEach((f, idx) => {
    const row = document.createElement("div");
    row.className = "aiocr-file-row";
    row.innerHTML = `
      <span class="aiocr-file-name">${f.name}</span>
      <span class="aiocr-file-meta">${formatSize(f.size)}</span>
      <button class="btn-ghost btn-sm" data-idx="${idx}">×</button>
    `;
    row.querySelector("button").addEventListener("click", () => {
      aiocrFiles.splice(idx, 1);
      aiocrRenderFileList();
      aiocr.runBtn.disabled = aiocrFiles.length === 0;
    });
    aiocr.fileList.appendChild(row);
  });
}

function aiocrAddFiles(fileList) {
  const allowed = ["pdf", "jpg", "jpeg", "png"];
  for (const f of fileList) {
    const ext = f.name.split(".").pop().toLowerCase();
    if (!allowed.includes(ext)) {
      showToast("Skipped unsupported: " + f.name);
      continue;
    }
    aiocrFiles.push(f);
  }
  aiocrRenderFileList();
  aiocr.runBtn.disabled = aiocrFiles.length === 0;
}

if (aiocr.dropZone) {
  aiocr.dropZone.addEventListener("click", () => aiocr.fileInput.click());
  aiocr.fileInput.addEventListener("change", () => aiocrAddFiles(aiocr.fileInput.files));
  aiocr.dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    aiocr.dropZone.classList.add("dragover");
  });
  aiocr.dropZone.addEventListener("dragleave", () => aiocr.dropZone.classList.remove("dragover"));
  aiocr.dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    aiocr.dropZone.classList.remove("dragover");
    aiocrAddFiles(e.dataTransfer.files);
  });
}

function aiocrConfidenceClass(c) {
  if (c >= 0.85) return "conf-high";
  if (c >= 0.60) return "conf-mid";
  return "conf-low";
}

function aiocrRenderDocuments(documents) {
  aiocr.documents.innerHTML = "";
  if (!documents || documents.length === 0) {
    aiocr.documents.innerHTML = '<p style="color:var(--muted);text-align:center;">No documents processed</p>';
    return;
  }
  documents.forEach((doc) => {
    const card = document.createElement("div");
    card.className = "aiocr-doc-card";
    const t = doc.doc_type;
    const tConfClass = aiocrConfidenceClass(t.confidence);
    const fieldsHtml = (doc.fields || []).map((f) => {
      const cls = aiocrConfidenceClass(f.confidence);
      const reviewFlag = f.needs_review
        ? '<span class="needs-review-flag">needs review</span>'
        : "";
      const alt = f.normalized_value && f.normalized_value !== f.value
        ? `<div class="aiocr-normalized">→ ${f.normalized_value}</div>`
        : "";
      const val = f.value
        ? `<span class="aiocr-field-value">${escapeHtml(f.value)}</span>`
        : '<span class="aiocr-field-empty">(empty)</span>';
      return `
        <div class="aiocr-field-row ${cls}">
          <div class="aiocr-field-key">
            <div class="aiocr-field-label">${escapeHtml(f.label)}</div>
            <div class="aiocr-field-keyname">${escapeHtml(f.key)}</div>
          </div>
          <div class="aiocr-field-val">
            ${val}
            ${alt}
          </div>
          <div class="aiocr-field-conf">
            <span class="conf-pill ${cls}">${(f.confidence * 100).toFixed(0)}%</span>
            ${reviewFlag}
          </div>
        </div>
      `;
    }).join("");
    card.innerHTML = `
      <div class="aiocr-doc-head">
        <div>
          <div class="aiocr-doc-filename">${escapeHtml(doc.file_name)}</div>
          <div class="aiocr-doc-id">${doc.document_id}</div>
        </div>
        <div class="aiocr-doc-type">
          <span class="type-badge">${escapeHtml(t.label)}</span>
          <span class="conf-pill ${tConfClass}">${(t.confidence * 100).toFixed(0)}%</span>
          <div class="aiocr-doc-typecode">${t.code}</div>
        </div>
      </div>
      <div class="aiocr-fields">${fieldsHtml}</div>
    `;
    aiocr.documents.appendChild(card);
  });
}

function aiocrRenderWarnings(warnings) {
  aiocr.warnings.innerHTML = "";
  if (!warnings || warnings.length === 0) return;
  const box = document.createElement("div");
  box.className = "aiocr-warnings";
  box.innerHTML =
    "<h4>Warnings</h4>" +
    warnings.map((w) => `<div class="aiocr-warning">[${w.code}] ${escapeHtml(w.message || "")}</div>`).join("");
  aiocr.warnings.appendChild(box);
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

if (aiocr.runBtn) {
  aiocr.runBtn.addEventListener("click", async () => {
    if (aiocrFiles.length === 0) return;
    const flowKey = aiocr.flowSelect.value;
    if (!flowKey) {
      showToast("Select a flow first");
      return;
    }
    const caseId = aiocr.caseId.value.trim() || "CASE-" + new Date().toISOString().slice(0, 10);

    aiocr.runBtn.disabled = true;
    aiocr.progress.style.display = "block";
    aiocr.progressText.textContent = "Analyzing… (AsiaMath OCR ensemble per file)";
    aiocr.empty.style.display = "none";
    aiocr.results.style.display = "none";

    const fd = new FormData();
    fd.append("case_id", caseId);
    fd.append("flow_key", flowKey);
    const manifest = aiocrFiles.map((f, i) => ({
      file_id: `FILE-${String(i + 1).padStart(3, "0")}`,
      file_name: f.name,
    }));
    fd.append("file_manifest", JSON.stringify(manifest));
    aiocrFiles.forEach((f) => fd.append("files", f));

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 900000); // 15 min
      const res = await fetch("/v1/aiocr/analyze", { method: "POST", body: fd, signal: controller.signal });
      clearTimeout(timeoutId);
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Server error" }));
        throw new Error(err.detail || err.error?.message || "Analyze failed");
      }
      const data = await res.json();
      aiocr.jobId.textContent = data.job_id;
      aiocr.status.textContent = data.status;
      aiocr.status.className = "aiocr-status status-" + data.status;
      aiocrRenderDocuments(data.documents);
      aiocrRenderWarnings(data.warnings);
      aiocr.results.style.display = "block";
      showToast(`Analyze ${data.status} — ${(data.documents || []).length} doc(s)`);
    } catch (e) {
      showToast("Error: " + e.message);
      console.error(e);
    } finally {
      aiocr.runBtn.disabled = false;
      aiocr.progress.style.display = "none";
    }
  });
}
