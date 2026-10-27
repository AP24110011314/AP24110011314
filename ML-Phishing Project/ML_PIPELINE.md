# ML PIPELINE

## 1. Data
- Phishing: PhishTank (verified online), OpenPhish feed. Legit: Tranco top list (pin the list ID/date).
- Store `url, label, source, collected_at, registered_domain`.
- Clean: lowercase scheme/host, strip whitespace, drop duplicates, drop invalid URLs, drop URLs that appear with both labels.
- **Bias fix:** Tranco gives only domains. Build legit URLs with paths by crawling a few internal links from each sampled domain (respect robots.txt, rate limit) or add a public mixed dataset. Report the path-length distribution per class; run an ablation without path features.
- Target size: 50k+ per class if possible; keep class ratio documented (real world is ~99:1 legit, so also report metrics at a realistic prior).

## 2. Splits (important)
- Random stratified 70/15/15 (for comparison with prior work).
- **Zero-day split:** group by registered domain (GroupShuffleSplit) AND a time-based split (train on older feeds, test on newest weeks). This is the headline result.

## 3. Features (`feature_spec.json` is the source of truth)
Lexical: url_length, hostname_length, path_length, query_length, num_dots, num_hyphens, num_underscores, num_slashes, num_digits, digit_ratio, num_special_chars, has_at, has_ip_host, has_port, uses_https, num_subdomains, tld, tld_in_suspicious_list, has_punycode ("xn--"), has_double_slash_in_path, shannon_entropy_host, shannon_entropy_path, longest_token_len, num_query_params.
Brand/keyword: suspicious_keyword_count (login, verify, secure, account, update, bank, wallet...), brand_in_subdomain_or_path (brand appears but registered domain differs), min_levenshtein_to_brand_list (typosquatting), is_url_shortener.
Optional host features (training-time only, **not** in real-time path unless cached): domain age, DNS records. Skip for latency.
Encode TLD with a fixed top-N vocab + "other".

## 4. Models
1. RandomForest (n_estimators 300) and XGBoost (tuned with Optuna/RandomizedSearch, CV grouped by domain).
2. Char-CNN (PyTorch): vocab of printable ASCII + `<unk>`, len 200, Adam lr 1e-3, dropout 0.3, early stopping on val F1, batch 256.
3. Ensemble: stacker on validation predictions. Compare against simple average.

## 5. Evaluation
- Metrics: accuracy, precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, FPR at fixed recall.
- Tables: {RF, XGB, CNN, Hybrid} x {random split, domain-disjoint, time-based}.
- Ablations: no path features; no brand features; CNN-only on host vs full URL.
- Error analysis: top false positives/negatives; SHAP for XGB.
- Latency benchmark of ONNX models (p50/p95).
- Fix random seeds; log everything to `ml/reports/`.

## 6. Export
`export_onnx.py` produces `xgb.onnx`, `cnn.onnx`, `stacker.json`, `vocab.json`, `feature_spec.json` and a `golden_set.json` (URLs + expected scores) used by API tests.
