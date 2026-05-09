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
  historyView: document.getElementById("historyView"),
};

let selectedFile = null;
let rawMarkdown = "";
let showRaw = false;

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
});

// ── Mode switch ──

refs.tabBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    refs.tabBtns.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    if (btn.dataset.mode === "single") {
      refs.singleView.classList.add("active");
      refs.historyView.classList.remove("active");
    } else {
      refs.singleView.classList.remove("active");
      refs.historyView.classList.add("active");
    }
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

// ── 公文 fields review table ──

let currentFields = [];

function renderFieldsTable(fields) {
  currentFields = fields;
  refs.fieldsTableBody.innerHTML = "";
  fields.forEach((f, idx) => {
    const isNo = f.ai_value === "no";
    const isFineCheck = f.field === "是否包含「罰款」關鍵字";
    const row = document.createElement("div");
    row.className = "row row-field";
    let inputHtml;
    if (isFineCheck) {
      const checked = f.ai_value === "是" ? "checked" : "";
      inputHtml = `<label class="checkbox-label"><input type="checkbox" class="review-checkbox" data-index="${idx}" ${checked} /> 是</label>`;
    } else {
      inputHtml = `<textarea class="review-textarea" data-index="${idx}" rows="1" placeholder="${isNo ? "no matching" : ""}">${isNo ? "" : f.ai_value}</textarea>`;
    }
    row.innerHTML = `
      <div class="field-label">${f.field}</div>
      <div class="ai-value${isNo ? " no-match" : ""}">${isFineCheck ? (f.ai_value === "是" ? "是" : "否") : f.ai_value}</div>
      <div>${inputHtml}</div>
    `;
    refs.fieldsTableBody.appendChild(row);
  });
}

refs.saveReviewBtn.addEventListener("click", () => {
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
  console.log("Review saved:", { fields: reviewed, reason });
  showToast("覆核內容已儲存");
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
  refs.progressArea.style.display = "block";
  refs.progressFill.className = "progress-fill indeterminate";
  refs.progressText.textContent = "Processing...";
  refs.emptyState.style.display = "none";
  refs.resultsArea.style.display = "none";

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res = await fetch("/api/ocr", { method: "POST", body: formData });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Server error" }));
      throw new Error(err.detail || "OCR failed");
    }

    const data = await res.json();

    // Progress done
    refs.progressFill.className = "progress-fill";
    refs.progressFill.style.width = "100%";
    refs.progressText.textContent = "Done!";

    // Render results
    renderGalleryWithNav(refs.originalGallery, data.original_pages || []);
    renderGalleryWithNav(refs.layoutGallery, data.layout_images || []);

    // 公文 fields
    renderFieldsTable(data.gongwen_fields || []);

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
    setTimeout(() => {
      refs.progressArea.style.display = "none";
      refs.progressFill.style.width = "0%";
    }, 3000);
  }
});

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
