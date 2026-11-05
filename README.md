# Unfold MCP server

<!-- mcp-name: io.github.bytestay/unfold-mcp -->

[![M8ven Score](https://m8ven.ai/badge/mcp/hybridforgelab/unfold-mcp?variant=verified)](https://m8ven.ai/mcp/hybridforgelab/unfold-mcp?s=readme)
[![CI](https://github.com/bytestay/unfold-mcp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/bytestay/unfold-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/bytestay-unfold-mcp)](https://pypi.org/project/bytestay-unfold-mcp/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/bytestay-unfold-mcp/)
[![License: MIT](https://img.shields.io/github/license/bytestay/unfold-mcp)](LICENSE)

Give your AI agent the content of PDF, Word (DOCX), PowerPoint (PPTX) and Excel (XLSX) documents as Markdown, from a URL or a local file.

The server is open source (MIT). It calls the [Unfold API](https://unfold.bytestay.pt), which is paid, with a free plan.

- You use **your own key, from RapidAPI or api.market**.
- Every tool call is one request on your plan.
- The free Basic plan has 15 requests a month, with a hard limit, so it never runs up a bill.

## 1. Get a key

| marketplace | |
|---|---|
| RapidAPI | [plans](https://rapidapi.com/bytestay-bytestay-default/api/unfold-document-to-markdown-api/pricing) |
| api.market | [store](https://api.market/store/bytestay/unfold) |

## 2. Add the server to your MCP client

The server runs locally over stdio with [uv](https://docs.astral.sh/uv/). Put your key in its environment.

**JSON configuration** (Claude Desktop, Cursor, VS Code and most clients):

```json
{
  "mcpServers": {
    "unfold": {
      "command": "uvx",
      "args": ["--from", "bytestay-unfold-mcp", "unfold-mcp"],
      "env": { "RAPIDAPI_KEY": "your-rapidapi-key" }
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add unfold --env RAPIDAPI_KEY=your-rapidapi-key -- uvx --from bytestay-unfold-mcp unfold-mcp
```

### Environment

| variable | meaning |
|---|---|
| `RAPIDAPI_KEY` | your RapidAPI key |
| `API_MARKET_KEY` | your api.market key, used when `RAPIDAPI_KEY` is not set |
| `HFL_MARKETPLACE` | `rapidapi` or `apimarket`, when both keys are set |

Without a key the server still starts. The first tool call then explains where to get one.

Also listed on Glama:

[![unfold-mcp on Glama](https://glama.ai/mcp/servers/hybridforgelab/unfold-mcp/badge)](https://glama.ai/mcp/servers/hybridforgelab/unfold-mcp)

## 3. Tools

| tool | what it does |
|---|---|
| `convert_document(url=… \| path=…, max_chars=20000)` | converts one document to Markdown; give a public URL, or a local file to upload |

The format is detected from the content.

Every tool returns the API's JSON response.

- When the marketplace reports it, `quota_remaining` is added: the requests left on your plan this month.
- Errors are explained in plain words, with what to do next:
  - key refused, with the link to subscribe;
  - quota reached, with the plans;
  - input the API couldn't process, with the API's reason.

## Privacy

- Local files are read only when a tool is given their path. They are sent to the API for that one request.
- The API processes inputs in memory and doesn't store them. See the [privacy policy](https://unfold.bytestay.pt/privacy.html).
- Your key is only sent to the marketplace you chose.

## Limits

- Local files up to 10 MB.
- Markdown up to 500,000 characters.
- The server needs Python 3.10+ (uv installs it for you).

## Development

```bash
uv venv && uv pip install -e ".[dev]"
.venv/bin/pytest            # unit tests, no network; 100% coverage required
.venv/bin/ruff check src tests scripts
```

`scripts/e2e_stdio.py unfold` runs the server over stdio, as a client would, and calls its tools against the real API. It needs `RAPIDAPI_KEY` or `API_MARKET_KEY`.

## Licence

MIT. Unfold itself is a paid API with a free plan, run by [ByteStay](https://bytestay.pt).
