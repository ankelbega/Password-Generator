"use strict";

const byId = (id) => document.getElementById(id);
const HISTORY_KEY = "password-generator-history-v1";
const THEME_KEY = "password-generator-theme-v1";
let generatedItems = [];
let analysisTimer = null;

function setTheme(theme) {
  if (theme === "light" || theme === "dark") document.documentElement.dataset.theme = theme;
  else delete document.documentElement.dataset.theme;
  const dark = theme === "dark" || (!theme && window.matchMedia("(prefers-color-scheme: dark)").matches);
  byId("theme-label").textContent = dark ? "Tema e çelët" : "Tema e errët";
  byId("theme-icon").textContent = dark ? "☀" : "☾";
  byId("theme-toggle").setAttribute("aria-pressed", String(dark));
}

function readHistory() {
  try {
    const value = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    return Array.isArray(value) ? value.filter((item) => typeof item === "string").slice(0, 20) : [];
  } catch (_error) { return []; }
}

function saveToHistory(password) {
  const history = [password, ...readHistory().filter((item) => item !== password)].slice(0, 20);
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify(history)); } catch (_error) { /* storage may be disabled */ }
  renderHistory();
}

function renderHistory() {
  const container = byId("history-list");
  container.replaceChildren();
  const history = readHistory();
  if (!history.length) {
    const empty = document.createElement("p");
    empty.className = "history-empty";
    empty.textContent = "Fjalëkalimet e gjeneruara do të shfaqen këtu.";
    container.append(empty);
    return;
  }
  history.forEach((password) => {
    const row = document.createElement("div");
    row.className = "history-item";
    const text = document.createElement("span");
    text.className = "generated-password masked";
    text.textContent = password;
    text.title = "Kliko Shfaq për ta parë";
    const reveal = document.createElement("button");
    reveal.type = "button";
    reveal.className = "small-button history-reveal";
    reveal.textContent = "Shfaq";
    reveal.setAttribute("aria-label", "Shfaq ose fshih fjalëkalimin e historikut");
    reveal.addEventListener("click", () => {
      const hidden = text.classList.toggle("masked");
      reveal.textContent = hidden ? "Shfaq" : "Fshih";
    });
    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "small-button";
    copy.textContent = "Kopjo";
    copy.addEventListener("click", () => copyPassword(password, copy));
    row.append(text, reveal, copy);
    container.append(row);
  });
}

function selectedModeOptions(mode) {
  if (mode === "passphrase") {
    return {
      words: Number(byId("words").value), separator: byId("separator").value,
      capitalize: byId("capitalize").value,
      add_number: byId("add-number").checked, add_symbol: byId("add-symbol").checked,
    };
  }
  if (mode === "pin") {
    return {
      length: Number(byId("pin-length").value), no_repeat: byId("pin-no-repeat").checked,
      no_sequences: byId("pin-no-sequences").checked, no_all_same: byId("pin-no-same").checked,
    };
  }
  return {
    length: Number(byId("length").value), use_lower: byId("use-lower").checked,
    use_upper: byId("use-upper").checked, use_digits: byId("use-digits").checked,
    use_symbols: byId("use-symbols").checked, exclude_similar: byId("exclude-similar").checked,
    no_repeat: byId("no-repeat").checked,
  };
}

async function generatePasswords() {
  const status = byId("generate-status");
  const button = byId("generate-button");
  status.textContent = "";
  button.disabled = true;
  const mode = byId("mode").value;
  const body = { mode, count: Number(byId("count").value), ...selectedModeOptions(mode) };
  try {
    const response = await fetch("/api/generate", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
      cache: "no-store",
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Gjenerimi dështoi.");
    generatedItems = data.passwords.map((password) => ({ password, revealed: false }));
    renderGenerated(data.passwords, data.entropy_bits);
    data.passwords.forEach(saveToHistory);
  } catch (error) {
    status.textContent = error.message || "Nuk u lidh dot me shërbimin lokal.";
  } finally { button.disabled = false; }
}

function renderGenerated(passwords, entropy) {
  const container = byId("generated-list");
  container.replaceChildren();
  passwords.forEach((password, index) => {
    const row = document.createElement("div");
    row.className = "generated-item";
    const text = document.createElement("span");
    text.className = "generated-password masked";
    text.textContent = password;
    const reveal = document.createElement("button");
    reveal.type = "button"; reveal.className = "icon-button"; reveal.textContent = "Shfaq";
    reveal.setAttribute("aria-label", "Shfaq ose fshih fjalëkalimin");
    reveal.setAttribute("aria-pressed", "false");
    reveal.addEventListener("click", () => {
      const shown = text.classList.toggle("masked") === false;
      reveal.textContent = shown ? "Fshih" : "Shfaq";
      reveal.setAttribute("aria-pressed", String(shown));
    });
    const copy = document.createElement("button");
    copy.type = "button"; copy.className = "icon-button"; copy.textContent = "Kopjo";
    copy.addEventListener("click", () => copyPassword(password, copy));
    row.append(text, reveal, copy);
    container.append(row);
    generatedItems[index].element = text;
  });
  const summary = document.createElement("p");
  summary.className = "field-note";
  summary.textContent = `Entropia e përafërt: ${entropy} bit${passwords.length > 1 ? " për secilin" : ""}.`;
  container.append(summary);
}

async function copyPassword(password, button) {
  const previous = button.textContent;
  try {
    await navigator.clipboard.writeText(password);
    button.textContent = "U kopjua";
    window.setTimeout(() => { button.textContent = previous; }, 2200);
    window.setTimeout(async () => {
      try {
        if (await navigator.clipboard.readText() === password) await navigator.clipboard.writeText("");
      } catch (_error) { /* clipboard read/clear is permission-dependent */ }
    }, 30000);
  } catch (_error) {
    button.textContent = "Kopjimi dështoi";
    window.setTimeout(() => { button.textContent = previous; }, 2500);
  }
}

function escapeHtml(value) {
  const replacements = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  return String(value).replace(/[&<>"']/g, (char) => replacements[char]);
}

function renderAnalysis(data) {
  const container = byId("analysis-result");
  const category = data.score <= 20 ? "weak" : data.score <= 40 ? "weak" : data.score <= 60 ? "mid" : data.score <= 80 ? "strong" : "very-strong";
  const penaltyHtml = data.penalties.length
    ? data.penalties.map((item) => `<li>${escapeHtml(item.detail)} (${item.points})</li>`).join("")
    : "<li>Nuk u gjetën modele të njohura dobësie.</li>";
  const suggestionHtml = data.suggestions.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  const crack = data.crack_time;
  container.innerHTML = `
    <div class="analysis-top"><span class="analysis-level">${escapeHtml(data.level)}</span><span class="analysis-score">${data.score} / 100</span></div>
    <div class="strength-track" role="meter" aria-label="Forca e fjalëkalimit" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${data.score}"><div class="strength-fill level-${category}" style="width:${data.score}%"></div></div>
    <div class="metrics">
      <div class="metric"><strong>${data.entropy_bits} bit</strong><span>Entropia</span></div>
      <div class="metric"><strong>${data.length}</strong><span>Karaktere</span></div>
      <div class="metric"><strong>${escapeHtml(crack.offline_fast_hash)}</strong><span>Thyerje offline e shpejtë</span></div>
    </div>
    <div class="analysis-details"><section><h3>Vërejtje</h3><ul>${penaltyHtml}</ul></section><section><h3>Sugjerime</h3><ul>${suggestionHtml}</ul></section></div>
    <details class="crack-details"><summary>Shfaq kohët e vlerësuara të thyerjes</summary><ul>
      <li>Online, me kufizim: ${escapeHtml(crack.online_throttled)}</li><li>Online, pa kufizim: ${escapeHtml(crack.online_fast)}</li>
      <li>Offline, hash i ngadaltë: ${escapeHtml(crack.offline_slow_hash)}</li><li>Offline, hash i shpejtë: ${escapeHtml(crack.offline_fast_hash)}</li>
    </ul></details>`;
}

function scheduleAnalysis() {
  window.clearTimeout(analysisTimer);
  analysisTimer = window.setTimeout(async () => {
    const password = byId("check-password").value;
    if (!password) {
      byId("analysis-result").innerHTML = '<div class="empty-analysis">Fillo të shkruash për të parë analizën.</div>';
      return;
    }
    try {
      const response = await fetch("/api/analyze", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }), cache: "no-store",
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Analiza dështoi.");
      renderAnalysis(data);
    } catch (error) {
      byId("analysis-result").textContent = error.message || "Analiza dështoi.";
    }
  }, 300);
}

function activateTab(tab) {
  const generate = tab === "tab-generate";
  for (const [buttonId, panelId, active] of [
    ["tab-generate", "panel-generate", generate], ["tab-check", "panel-check", !generate],
  ]) {
    const button = byId(buttonId);
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", String(active));
    button.tabIndex = active ? 0 : -1;
    byId(panelId).hidden = !active;
  }
}

byId("mode").addEventListener("change", () => {
  byId("random-options").hidden = byId("mode").value !== "random";
  byId("phrase-options").hidden = byId("mode").value !== "passphrase";
  byId("pin-options").hidden = byId("mode").value !== "pin";
});
byId("length").addEventListener("input", () => { byId("length-value").value = byId("length").value; });
byId("pin-length").addEventListener("input", () => { byId("pin-length-value").value = byId("pin-length").value; });
byId("generate-button").addEventListener("click", generatePasswords);
byId("check-password").addEventListener("input", scheduleAnalysis);
byId("tab-generate").addEventListener("click", () => activateTab("tab-generate"));
byId("tab-check").addEventListener("click", () => activateTab("tab-check"));
document.querySelectorAll('[role="tab"]').forEach((tab) => tab.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
    event.preventDefault();
    const next = tab.id === "tab-generate" ? "tab-check" : "tab-generate";
    activateTab(next); byId(next).focus();
  }
}));
byId("toggle-check-password").addEventListener("click", (event) => {
  const input = byId("check-password");
  const shown = input.type === "password";
  input.type = shown ? "text" : "password";
  event.currentTarget.setAttribute("aria-pressed", String(shown));
  event.currentTarget.setAttribute("aria-label", shown ? "Fshih fjalëkalimin" : "Shfaq fjalëkalimin");
});
byId("clear-history").addEventListener("click", () => {
  try { localStorage.clear(); } catch (_error) { /* clearing is best effort in restricted contexts */ }
  renderHistory();
});
byId("theme-toggle").addEventListener("click", () => {
  const current = document.documentElement.dataset.theme || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const next = current === "dark" ? "light" : "dark";
  try { localStorage.setItem(THEME_KEY, next); } catch (_error) { /* optional preference */ }
  setTheme(next);
});

try { setTheme(localStorage.getItem(THEME_KEY)); } catch (_error) { setTheme(null); }
renderHistory();
