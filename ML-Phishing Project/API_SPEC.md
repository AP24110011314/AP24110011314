# API SPEC

## POST /api/predict
Request
```json
{ "url": "http://secure-login.paypa1-verify.com/account?id=1" }
```
Response 200
```json
{
  "url": "...", "label": "phishing", "score": 0.97, "threshold": 0.85,
  "models": { "xgb": 0.95, "cnn": 0.98 },
  "reasons": ["Brand name 'paypal' imitated in domain", "Suspicious keywords: login, verify", "High hyphen count"],
  "latency_ms": 18, "model_version": "2026.10.1"
}
```
Errors: 400 (invalid/oversized URL), 429 (rate limit), 500 (inference error). Never echo stack traces.

## GET /api/health -> `{ "status": "ok", "model_version": "..." }`

## Implementation notes
- Load ONNX sessions once at module scope (cold-start safe); warm up with one dummy inference.
- Validate with `zod`; accept http/https only; max 2048 chars.
- `reasons` come from rule-based flags on features (cheap) or top SHAP-like contributions precomputed per feature.
- Rate limit by IP (in-memory/Upstash). CORS: allow only the extension origin (`chrome-extension://<id>`).
- Tests: parity with `golden_set.json`, schema tests, load test (autocannon) for p95.
- Deploy: Vercel can be tight for onnxruntime-node binaries; prefer Render/Railway/Fly Docker container.
