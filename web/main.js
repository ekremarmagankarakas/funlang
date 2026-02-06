const $ = (id) => document.getElementById(id);

const statusEl = $("status");
const statusTextEl = statusEl.querySelector(".statusText");

const configEl = $("config");
const codeEl = $("code");
const outEl = $("output");
const runBtn = $("run");
const trimBtn = $("format");
const clearBtn = $("clearOut");
const loadExampleBtn = $("loadExample");

const EXAMPLES = {
  default: `fun greet(name) {
    return "Hello, " + name;
};

print(greet("FunLang"));
`,
  turkish: `fonksiyon selamla(isim) {
    dondur "Merhaba, " + isim;
};

yazdir(selamla("FunLang"));
`,
  spanish: `funcion saludar(nombre) {
    devolver "Hola, " + nombre;
};

imprimir(saludar("FunLang"));
`,
  emoji: `🎯 greet(name) {
    ↩️ "Hello, " + name;
};

print(greet("FunLang"));
`,
};

function setStatus(kind, text) {
  statusEl.classList.remove("ready", "error");
  if (kind) statusEl.classList.add(kind);
  statusTextEl.textContent = text;
}

function appendOutput(s) {
  outEl.textContent += s;
  outEl.scrollTop = outEl.scrollHeight;
}

function setControlsEnabled(enabled) {
  configEl.disabled = !enabled;
  runBtn.disabled = !enabled;
  trimBtn.disabled = !enabled;
  clearBtn.disabled = !enabled;
  loadExampleBtn.disabled = !enabled;
}

async function loadText(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Fetch failed: ${res.status} ${res.statusText} (${url})`);
  }
  return await res.text();
}

async function loadJSON(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Fetch failed: ${res.status} ${res.statusText} (${url})`);
  }
  return await res.json();
}

function getConfigPath(configKey) {
  if (!configKey || configKey === "default") return null;
  return `/app/configs/${configKey}.json`;
}

async function boot() {
  setControlsEnabled(false);
  outEl.textContent = "";
  codeEl.value = EXAMPLES.default;
  codeEl.focus();

  if (typeof loadPyodide !== "function") {
    setStatus("error", "Pyodide not found (CDN blocked?)");
    return;
  }

  setStatus(null, "Loading Pyodide…");
  const pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.1/full/",
  });

  setStatus(null, "Loading FunLang sources…");
  const manifest = await loadJSON("./py/manifest.json");
  pyodide.FS.mkdirTree("/app");
  pyodide.FS.mkdirTree("/app/src");
  pyodide.FS.mkdirTree("/app/configs");

  for (const entry of manifest.files) {
    const srcUrl = `./py/${entry}`;
    const destPath = `/app/${entry}`;
    const txt = await loadText(srcUrl);
    pyodide.FS.mkdirTree(destPath.split("/").slice(0, -1).join("/"));
    pyodide.FS.writeFile(destPath, txt, { encoding: "utf8" });
  }

  await pyodide.runPythonAsync(`
import sys
if "/app" not in sys.path:
    sys.path.insert(0, "/app")
`);

  setStatus(null, "Initializing runner…");
  await pyodide.runPythonAsync(`
from funlang_runner import eval_funlang
`);

  function runOnce() {
    const configKey = configEl.value;
    const configPath = getConfigPath(configKey);
    const source = codeEl.value;

    runBtn.disabled = true;
    runBtn.textContent = "Running…";
    appendOutput(`\n> run (${configKey})\n`);

    pyodide.globals.set("__funlang_source", source);
    pyodide.globals.set("__funlang_config_path", configPath);

    return pyodide
      .runPythonAsync(`eval_funlang(__funlang_source, __funlang_config_path)`)
      .then((pyResult) => {
        const r = pyResult.toJs({ dict_converter: Object.fromEntries });

        if (r.stdout) appendOutput(r.stdout);
        if (r.error) {
          appendOutput(`\n[error]\n${r.error}\n`);
        } else if (r.result !== null && r.result !== undefined && r.result !== "") {
          appendOutput(`\n[result] ${r.result}\n`);
        }
      })
      .catch((e) => {
        appendOutput(`\n[pyodide error]\n${String(e)}\n`);
      })
      .finally(() => {
        runBtn.textContent = "Run";
        runBtn.disabled = false;
      });
  }

  runBtn.addEventListener("click", () => void runOnce());
  codeEl.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      void runOnce();
    }
  });

  clearBtn.addEventListener("click", () => {
    outEl.textContent = "";
  });

  trimBtn.addEventListener("click", () => {
    codeEl.value = codeEl.value
      .split("\n")
      .map((l) => l.replace(/\s+$/g, ""))
      .join("\n")
      .replace(/^\n+/, "")
      .replace(/\n+$/, "\n");
  });

  loadExampleBtn.addEventListener("click", () => {
    const k = configEl.value;
    codeEl.value = EXAMPLES[k] ?? EXAMPLES.default;
    codeEl.focus();
  });

  configEl.addEventListener("change", () => {
    // Keep user code; just hint via status.
    const k = configEl.value;
    setStatus("ready", `Ready (config: ${k})`);
  });

  setControlsEnabled(true);
  setStatus("ready", "Ready");
}

boot().catch((e) => {
  setControlsEnabled(false);
  setStatus("error", "Boot failed");
  appendOutput(`\n[boot error]\n${String(e)}\n`);
});
