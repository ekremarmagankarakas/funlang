# FunLang Browser Playground

This folder is a static playground that runs the FunLang **interpreter** in the browser using Pyodide (Python compiled to WebAssembly).

It intentionally does **not** support LLVM compilation.

## Run locally

From the repo root:

```bash
python3 -m http.server
```

Then open:

- http://localhost:8000/web/

## Deploy

You can deploy the `web/` folder to any static host (GitHub Pages / Netlify / Vercel static / S3).

The Python runtime files are shipped under `web/py/` and loaded into Pyodide at runtime.
