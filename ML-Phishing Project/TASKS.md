# TASKS (work in order; tick when done; commit per task)

## Phase 0 — Setup
- [ ] Create repo layout from ARCHITECTURE.md, `.gitignore`, Python venv, `ml/requirements.txt`, Node project.
## Phase 1 — Data
- [ ] `collect.py`: download PhishTank/OpenPhish/Tranco, save raw with timestamps.
- [ ] Build legit URLs with paths (see ML_PIPELINE.md bias fix).
- [ ] Clean, dedupe, add `registered_domain` (tldextract), write `processed/dataset.parquet`.
- [ ] EDA notebook: class balance, length distributions, per-class path stats.
## Phase 2 — Features + baselines
- [ ] `features.py` + `feature_spec.json`; unit tests on 20 hand-made URLs.
- [ ] Train RF + XGB, grouped CV, save metrics.
## Phase 3 — Char-CNN
- [ ] Tokenizer + vocab, PyTorch model, training loop with early stopping.
## Phase 4 — Hybrid + evaluation
- [ ] Stacker, threshold selection, full results tables (3 splits), ablations, SHAP, plots.
- [ ] Export ONNX + `golden_set.json`.
## Phase 5 — API
- [ ] `features.ts` + parity test against Python; tokenizer.ts; ONNX inference; `/api/predict`, `/api/health`.
- [ ] Validation, rate limit, CORS, tests, Dockerfile, deploy.
## Phase 6 — Extension
- [ ] manifest, background logic, warning page, popup/options, cache, fail-open.
- [ ] Manual test matrix: known phishing (PhishTank test), top legit sites, offline API, allowlist.
## Phase 7 — Wrap-up
- [ ] Latency benchmark, README with setup + demo GIF, evaluation report, paper outline.
