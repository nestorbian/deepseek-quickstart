## Purpose

Practical, focused guidance for an AI coding agent to be immediately productive in this repo. Keep edits minimal and code-local unless asked to add features.

## Big picture

- This is a tiny MCP (Model Context Protocol) server implemented in `weather.py`. The module exposes a FastMCP instance named `mcp = FastMCP("weather")` and two primary tools: `get_alerts(state: str)` and `get_forecast(latitude: float, longitude: float)`.
- It calls the U.S. National Weather Service (NWS) API (base URL `https://api.weather.gov`) via an async helper `make_nws_request(url)` and returns human-readable strings for the caller (typically an LLM).

## Key files to inspect

- `weather.py` — single-file app. Important symbols: `mcp`, `NWS_API_BASE`, `USER_AGENT`, `make_nws_request`, `format_alert`, `get_alerts`, `get_forecast`.
- `pyproject.toml` — declares Python >=3.13 and deps: `httpx`, `mcp[cli]`.
- `main.py` — trivial entry point (not used by MCP tooling).

## How to run (developer workflows)

- Preferred: use the MCP CLI (installed from `mcp[cli]`). From project root:

	mcp run --module weather:mcp --port 8000

	This imports `mcp` from `weather.py` and serves an HTTP MCP endpoint. The CLI is the canonical way to run an MCP server in this project.

- Alternate / local debug: run the module directly. This starts the MCP server on stdio (useful for local model integrations):

	python weather.py


## Project-specific conventions & patterns

- Async only: network calls use `httpx.AsyncClient` and all I/O-facing tools are `async def`.
- Tools are simple: each `@mcp.tool()` returns a formatted string (not raw JSON). Keep that contract when changing behavior.
- Centralized request helper: `make_nws_request(url)` returns parsed JSON on success or `None` on any error. Callers must check for falsy return values and handle them by returning a short, user-facing message.
- NWS API usage patterns:
	- Alerts: GET {NWS_API_BASE}/alerts/active/area/{state}
	- Forecast: GET {NWS_API_BASE}/points/{lat},{lon} → use returned `properties.forecast` URL to fetch periods
- Headers: the code sets `User-Agent = USER_AGENT` and `Accept: application/geo+json`. Preserve those when adding HTTP requests.

## Examples (copyable snippets for code edits)

- Formatting alerts (existing helper): `format_alert(feature)` expects NWS feature JSON and uses `feature['properties']` safely with .get().
- Checking responses:

	data = await make_nws_request(url)
	if not data:
			return "无法获取..."

- Forecast tool flow (existing):
	1) GET /points/{lat},{lon}
	2) extract `properties.forecast`
	3) GET forecast URL and read `properties.periods` (take first 5 periods)

## Integration points & external dependencies

- External API: https://api.weather.gov (NWS). No API key required but calls must include a reasonable User-Agent.
- Run-time dependency: `httpx` for async HTTP + `mcp` for the server. See `pyproject.toml` for versions.

## Editing guidance and safe refactors

- Small changes to `weather.py` are fine; keep the exported symbol `mcp` and any `@mcp.tool()` signatures stable unless you update the runner or callers.
- If adding new network calls, reuse `make_nws_request` and preserve headers/timeouts.
- Keep return type of tools as plain strings (unless you intentionally change the contract and update callers/tests).

## What not to change without approval

- Don't change communication style: the app expects to be called as an MCP tool (stdio or via MCP CLI). Changing transport or `mcp` name will break integrations.
- Don't remove the `User-Agent` header — NWS requires it for polite API use.

## Quick checklist for PRs by an AI agent

1. Keep edits focused to necessary files (usually `weather.py`).
2. Preserve `mcp` export and `@mcp.tool()` signatures unless asked otherwise.
3. Run the server locally via `mcp run --module weather:mcp --port 8000` or `python weather.py` for stdio testing.
4. Ensure `make_nws_request()` is used for HTTP requests and callers handle None returns.

---

If anything here is unclear or you want the instructions expanded (more examples, tests to add, or a VS Code debug recipe), tell me which sections to extend.
