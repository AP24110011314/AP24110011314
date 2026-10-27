# AGENTS.md — Instructions for OpenCode

## Project
Real-time phishing URL detector: Python ML pipeline -> ONNX models -> Next.js API -> Chrome MV3 extension. Read `PRD.md`, `ARCHITECTURE.md`, `ML_PIPELINE.md`, `API_SPEC.md`, `EXTENSION_SPEC.md`, `TASKS.md` before coding.

## Working rules
1. Work through `TASKS.md` in order, one task at a time; tick it off and commit with a clear message.
2. Before each task, state the plan in 3-5 lines; after it, run the tests and show results.
3. Never fabricate metrics. All numbers in reports must come from scripts in `ml/reports/`.
4. Prevent leakage: split by registered domain and time; never fit scalers/vocab on test data.
5. `ml/feature_spec.json` is the single source of truth for features. Any change requires updating both Python and TypeScript and the parity test.
6. Keep secrets out of git; use `.env` and `.env.example`.
7. Privacy: never log full URLs by default; strip query strings before sending from the extension.

## Stack & conventions
- Python 3.11, pandas, scikit-learn, xgboost, torch, onnx, onnxruntime, tldextract, pytest, ruff.
- Node 20, Next.js (App Router), TypeScript strict, zod, onnxruntime-node, vitest.
- Extension: plain JS or TS, MV3, no remote code, minimal permissions.
- Seeds fixed (42). Notebooks for exploration only; reusable logic lives in `ml/src/`.

## Commands
- `cd ml && pip install -r requirements.txt && pytest`
- `cd api && npm i && npm run dev` / `npm test`
- Load extension: chrome://extensions -> Developer mode -> Load unpacked -> `extension/`

## Definition of done (per task)
Code runs, tests pass, docs updated, no TODOs left silently, commit made.

## Ask before
Adding new heavy dependencies, changing the model architecture, or scraping beyond rate limits / robots.txt.
