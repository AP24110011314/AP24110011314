# ARCHITECTURE

## Components
1. **ml/** (Python): data collection, features, training, evaluation, ONNX export.
2. **api/** (Next.js, TypeScript): serves ONNX models via `onnxruntime-node`.
3. **extension/** (Chrome MV3, JS/TS): service worker + warning page + popup.

## Flow
```
Tab navigates -> background service worker (webNavigation.onBeforeNavigate, frame 0)
  -> normalise URL, check allowlist + cache
  -> POST /api/predict {url}
       -> validate -> extract features (TS) -> XGB/RF (ONNX) -> char-CNN (ONNX)
       -> ensemble -> {label, score, reasons}
  <- verdict
  -> if phishing & score >= threshold: redirect tab to warning.html?target=<url>
  -> else: set badge (green / grey)
```

## Model design
- Branch A: handcrafted features -> XGBoost (and RF baseline).
- Branch B: URL chars -> embedding(64) -> Conv1D(k=3,5,7, 128 filters) -> global max pool -> Dense -> sigmoid. Max length 200, pad/truncate.
- Ensemble: logistic-regression stacker over [p_xgb, p_cnn] trained on a held-out validation fold (fallback: 0.5/0.5 weighted average).
- Threshold chosen on validation set to hit target precision (>= 0.98).

## Serving decision
Train in Python, export to ONNX (`skl2onnx`/`onnxmltools` for tree models, `torch.onnx` for CNN). Serve in Node with `onnxruntime-node`.
**Critical:** feature extraction exists in both Python (training) and TypeScript (serving). Keep a shared `feature_spec.json` and a **parity test**: 1,000 URLs must produce identical feature vectors (tolerance 1e-6) in both languages. Fallback option if parity is painful: serve with a Python FastAPI microservice and keep Next.js only as a thin proxy.

## Repository layout
```
phish-detector/
  AGENTS.md  PRD.md  ARCHITECTURE.md  ML_PIPELINE.md  API_SPEC.md  EXTENSION_SPEC.md  TASKS.md
  ml/
    data/{raw,processed}/  notebooks/  src/{collect,features,train_tree,train_cnn,ensemble,evaluate,export_onnx}.py
    feature_spec.json  requirements.txt
  api/
    app/api/predict/route.ts  lib/{features.ts,tokenizer.ts,models.ts,ensemble.ts}
    models/{xgb.onnx,cnn.onnx,stacker.json,vocab.json}  tests/
  extension/
    manifest.json  background.js  warning.html  warning.js  popup.html  popup.js  options.html
```

## Privacy & security
Strip query/fragment before sending (configurable). No auth tokens. Rate limit 60 req/min/IP. No URL logging by default. Extension permissions minimal: `webNavigation`, `storage`, `tabs`, host permission for API only.
