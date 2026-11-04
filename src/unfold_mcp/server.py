"""Unfold MCP server: PDF, DOCX, PPTX and XLSX documents to Markdown."""
from __future__ import annotations

from typing import Annotated

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from . import files
from .client import PRODUCTS, call

PRODUCT = PRODUCTS["unfold"]
MAX_FILE = 10 * 1024 * 1024

server = MCPServer(
    "unfold",
    title="Unfold: documents to Markdown",
    instructions=(
        "Convert a PDF, Word (DOCX), PowerPoint (PPTX) or Excel (XLSX) document to Markdown, from a URL or a local "
        "file. Local files are uploaded to the Unfold API, processed in memory and not stored. "
        "Each call is one request on the user's Unfold plan."
    ),
    website_url="https://unfold.bytestay.pt",
)

READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=True)


@server.tool(annotations=READ_ONLY)
async def convert_document(
    url: Annotated[str | None, Field(description="Public http(s) URL of the document.")] = None,
    path: Annotated[str | None, Field(description="Local file to upload instead (up to 10 MB).")] = None,
    max_chars: Annotated[int, Field(ge=100, le=500_000, description="Cut the Markdown to this many characters.")]
    = 20_000,
) -> dict:
    """Convert one document to Markdown. Give either `url` or `path`. The format is detected from the content."""
    if bool(url) == bool(path):
        raise ToolError("Give exactly one of url or path.")
    if url:
        return await call(PRODUCT, "POST", "/v1/convert", json={"url": url, "max_chars": max_chars})
    name, content = files.read_bytes(path, MAX_FILE)
    return await call(PRODUCT, "POST", "/v1/convert", files={"file": (name, content)},
                      data={"max_chars": str(max_chars)})


def main() -> None:  # pragma: no cover - stdio entry point
    server.run("stdio")

if __name__ == "__main__":  # pragma: no cover
    main()
