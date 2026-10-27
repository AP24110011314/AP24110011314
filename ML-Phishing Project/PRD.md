# PRD — Real-Time Phishing URL Detection (ML + Chrome Extension)

## 1. Problem
Blacklist-based protection only blocks phishing sites after they are reported. Zero-day phishing URLs slip through. We need detection from the URL string alone, in real time, in the browser.

## 2. Goals
- G1: Classify a URL as phishing/legitimate without any blacklist lookup.
- G2: Hybrid model (handcrafted features + character-level CNN) that generalises to unseen domains.
- G3: Chrome extension (Manifest V3) that warns the user before they interact with the page.
- G4: End-to-end latency (extension -> API -> verdict) p95 < 300 ms.
- G5: Reproducible comparative study: feature-based vs text-based vs hybrid.

## 3. Non-Goals
- Page-content / screenshot / DOM analysis (future work).
- Mobile browsers, Firefox/Safari (future work).
- Storing user browsing history.

## 4. Users
- Everyday browser user: wants a clear warning, minimal friction.
- Researcher/evaluator (us): needs metrics, ablations, reproducible notebooks.

## 5. Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| FR1 | Collect phishing URLs (PhishTank, OpenPhish) and legit URLs (Tranco) with dedup + labelling | P0 |
| FR2 | Extract >= 25 lexical/host features per URL (see ML_PIPELINE.md) | P0 |
| FR3 | Train RandomForest + XGBoost baselines | P0 |
| FR4 | Train char-level CNN on raw URL | P0 |
| FR5 | Hybrid ensemble (stacking/weighted average) | P0 |
| FR6 | Evaluate accuracy/precision/recall/F1/ROC-AUC + zero-day split | P0 |
| FR7 | Inference API `POST /api/predict` returning label, score, reasons | P0 |
| FR8 | Extension checks each top-frame navigation and shows warning page/banner | P0 |
| FR9 | Extension: allowlist, "proceed anyway", on/off toggle | P1 |
| FR10 | Local cache of verdicts (TTL) to cut latency/API calls | P1 |
| FR11 | Explainability: top 3 contributing signals shown in the warning | P2 |
| FR12 | Feedback button "report false positive" (stores URL only, opt-in) | P2 |

## 6. Non-Functional Requirements
- Latency p95 < 300 ms; model inference < 50 ms.
- Privacy: only the URL (query string stripped by default) leaves the browser; no cookies, no user ID; HTTPS only; no persistent logs of URLs unless user opts in.
- Reliability: if API is down, extension fails open (no block) and shows a neutral "unchecked" badge.
- Security: CORS restricted, rate limiting, input validation (max URL length 2048).
- Model size: ONNX artefacts < 20 MB total.

## 7. Success Metrics
- Hybrid F1 >= 0.97 on random split; >= 0.93 on domain-disjoint/time-based "zero-day" split.
- False-positive rate on top-10k legit domains < 1%.
- Hybrid beats best single model by >= 1 pt F1 on zero-day split (otherwise report honestly).

## 8. Key Risks
| Risk | Mitigation |
|------|-----------|
| Dataset bias: Tranco = bare homepages, phishing = deep paths, so the model learns "has path = phish" | Sample legit URLs with paths/queries (crawl links from Tranco sites, or use a public mixed dataset); ablate path features |
| Data leakage across train/test (same domain, near-duplicate URLs) | Split by registered domain and by time |
| JS vs Python feature mismatch at inference | Single source of truth + parity test suite (ARCHITECTURE.md) |
| Attackers adapt (e.g. long benign-looking domains) | Document as limitation; retrain pipeline scripted |
| High false positives hurt trust | Threshold tuned for precision; allowlist; show confidence |

## 9. Milestones
M1 data + EDA -> M2 features + baselines -> M3 CNN -> M4 hybrid + evaluation -> M5 API -> M6 extension -> M7 testing, paper draft.

## 10. Deliverables
Trained models (ONNX), Next.js API, Chrome extension, notebooks, evaluation report, paper draft, demo video.
