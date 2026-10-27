# CHROME EXTENSION SPEC (Manifest V3)

## manifest.json (essentials)
- `manifest_version: 3`, permissions: `webNavigation`, `storage`, `tabs`; `host_permissions`: API origin only.
- `background.service_worker: background.js`; `action.default_popup: popup.html`; `web_accessible_resources`: `warning.html`.

## Behaviour
1. `chrome.webNavigation.onBeforeNavigate` (frameId 0, http/https only).
2. Skip if extension disabled, host in allowlist, or scheme is chrome://, file://, localhost.
3. Normalise URL (strip query/fragment by default), look up `chrome.storage.session` cache (TTL 10 min).
4. `fetch(API/predict)` with 2 s timeout via AbortController. On failure: fail open, grey badge.
5. If `label == phishing` -> `chrome.tabs.update(tabId, {url: warning.html?target=...&score=...})`.
6. Warning page: clear red UI, shows reasons, buttons **Go back to safety** and **Proceed anyway** (adds temporary allow for that host).
7. Badge: green = safe, red = phishing, grey = unchecked.
8. Popup: toggle on/off, current verdict, "Report false positive", allowlist manager (in options page).

## Notes
- MV3 service workers sleep; keep all state in `chrome.storage`, not globals.
- Never inject content scripts for this MVP; keeps permissions small and review easy.
- Load unpacked via `chrome://extensions` for demo; Chrome Web Store publishing is optional.
