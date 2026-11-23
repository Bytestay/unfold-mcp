"""Reading local files for tools that accept a path instead of the content.

A path is only read when, after resolving symlinks, it sits inside the root (the environment variable
UNFOLD_MCP_ROOT, or the current working directory when it is not set) and has an allowed extension.
"""
from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

ROOT_ENV = "UNFOLD_MCP_ROOT"
ALLOWED_TEXT = ".pdf, .docx, .pptx, .xlsx"
_ZIP_DIR = {".docx": "word/", ".pptx": "ppt/", ".xlsx": "xl/"}


def root() -> Path:
    return Path(os.environ.get(ROOT_ENV) or Path.cwd()).expanduser().resolve()


def _allowed(name: str) -> bool:
    return Path(name).suffix.lower() in (".pdf", *_ZIP_DIR)


def resolve(path: str) -> Path:
    base = root()
    given = Path(path).expanduser()
    p = (given if given.is_absolute() else base / given).resolve()
    if not p.is_relative_to(base):
        raise ToolError(f"{path} is outside the allowed folder {base} (set {ROOT_ENV} to allow another one).")
    if not p.is_file():
        raise ToolError(f"No such file: {path} (relative paths start from {base}).")
    if not _allowed(p.name):
        raise ToolError(f"{p.name} is not an allowed file type: {ALLOWED_TEXT}.")
    return p


def read_bytes(path: str, max_bytes: int) -> tuple[str, bytes]:
    p = resolve(path)
    size = p.stat().st_size
    if size > max_bytes:
        raise ToolError(f"{p} is {size:,} bytes; the limit is {max_bytes:,}.")
    data = p.read_bytes()
    _check_magic(p.name, data)
    return p.name, data


def _check_magic(name: str, data: bytes) -> None:
    suffix = Path(name).suffix.lower()
    if suffix == ".pdf":
        ok = data.startswith(b"%PDF-")
    else:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                ok = any(n.startswith(_ZIP_DIR[suffix]) for n in z.namelist())
        except zipfile.BadZipFile:
            ok = False
    if not ok:
        raise ToolError(f"{name} does not look like a real {suffix} file (content does not match the extension).")
