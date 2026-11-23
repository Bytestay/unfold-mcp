
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from unfold_mcp import server as unfold

SPEC_V1 = "openapi: 3.0.3\ninfo: {title: t, version: '1'}\npaths: {}\n"
SPEC_V2 = "openapi: 3.0.3\ninfo: {title: t, version: '2'}\npaths: {}\n"


async def test_server_lists_its_tools():
    listed = await unfold.server.list_tools()
    assert {t.name for t in listed} == {"convert_document"}
    for t in listed:
        assert t.description
        assert t.annotations.read_only_hint is True and t.annotations.destructive_hint is False
        assert t.annotations.idempotent_hint is True and t.annotations.open_world_hint is True


async def test_unfold_url_and_file(api, tmp_path):
    await unfold.convert_document(url="https://e.x/a.pdf")
    assert api.last_json() == {"url": "https://e.x/a.pdf", "max_chars": 20_000}
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF-1.4 x")
    await unfold.convert_document(path=str(pdf), max_chars=300)
    body = api.last.content
    assert b'name="file"; filename="a.pdf"' in body and b"%PDF-1.4 x" in body and b'name="max_chars"' in body
    for kwargs in ({}, {"url": "https://e.x/a.pdf", "path": str(pdf)}):
        with pytest.raises(ToolError, match="exactly one"):
            await unfold.convert_document(**kwargs)


async def test_unfold_file_limits(api, tmp_path):
    big = tmp_path / "big.pdf"
    big.write_bytes(b"0" * (unfold.MAX_FILE + 1))
    with pytest.raises(ToolError, match="limit is"):
        await unfold.convert_document(path=str(big))
    with pytest.raises(ToolError, match="No such file"):
        await unfold.convert_document(path=str(tmp_path / "missing.pdf"))


def _docx(path):
    import zipfile
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", "<x/>")


async def test_path_outside_root_is_refused(api, tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    (tmp_path / "secret.pdf").write_bytes(b"%PDF-1.4")
    monkeypatch.chdir(root)
    for path in ("../secret.pdf", str(tmp_path / "secret.pdf")):
        with pytest.raises(ToolError, match="outside the allowed folder"):
            await unfold.convert_document(path=path)
    (root / "a.pdf").symlink_to(tmp_path / "secret.pdf")
    with pytest.raises(ToolError, match="outside the allowed folder"):
        await unfold.convert_document(path="a.pdf")
    assert not api.requests


async def test_wrong_extension_and_magic_are_refused(api, tmp_path):
    (tmp_path / "id_rsa").write_text("x")
    with pytest.raises(ToolError, match="not an allowed file type"):
        await unfold.convert_document(path="id_rsa")
    (tmp_path / "fake.pdf").write_text("not a pdf")
    (tmp_path / "fake.docx").write_text("not a zip")
    _docx(tmp_path / "wrong.xlsx")
    for name in ("fake.pdf", "fake.docx", "wrong.xlsx"):
        with pytest.raises(ToolError, match="does not look like"):
            await unfold.convert_document(path=name)
    assert not api.requests


async def test_docx_and_explicit_root(api, tmp_path, monkeypatch):
    other = tmp_path / "other"
    other.mkdir()
    _docx(other / "a.docx")
    monkeypatch.setenv("UNFOLD_MCP_ROOT", str(other))
    await unfold.convert_document(path="a.docx")
    assert b'filename="a.docx"' in api.last.content
