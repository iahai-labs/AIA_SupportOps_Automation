# Phase 10.1 — Subpath Compatibility

SupportOps is intended to be published below:

`https://ai.iradhd.ir/supportops/`

This patch adds an explicit application root path and makes the demo UI build static, API, and
OpenAPI URLs from that base path rather than assuming the domain root.

## Production configuration

`docker-compose.prod.yml` now sets:

`ROOT_PATH=/supportops`

FastAPI receives the value through `root_path`.

The demo page receives the active request root path and exposes it to the browser as
`window.APP_BASE`. The JavaScript client then prefixes API calls with that base.

## Reverse proxy expectation

The host Nginx should forward `/supportops/` to the application on `127.0.0.1:8003`.

The deployment step should verify:

- `/supportops/demo`
- `/supportops/static/demo/style.css`
- `/supportops/static/demo/app.js`
- `/supportops/api/v1/...`
- `/supportops/docs`
- `/supportops/openapi.json`

before the public URL is considered release-ready.
