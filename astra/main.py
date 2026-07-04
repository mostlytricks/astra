"""ASTRA — Agent Skill Transfer & Registry App.

The filesystem is the registry: registry/<skill>/<version>/ holds the raw skill
folder (SKILL.md + optional assets). Every surface — the rendered page, the zip,
the install command — derives from that one folder. No second source of truth.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

import markdown
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry"

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

app = FastAPI(title="astra")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def skill_dir(name: str, version: str) -> Path:
    d = (REGISTRY / name / version).resolve()
    # guard against path traversal — the resolved dir must stay inside registry/
    if not d.is_dir() or REGISTRY.resolve() not in d.parents:
        raise HTTPException(status_code=404, detail=f"no skill {name}@{version}")
    if not (d / "SKILL.md").is_file():
        raise HTTPException(status_code=404, detail=f"{name}@{version} has no SKILL.md")
    return d


def parse_skill_text(text: str) -> tuple[dict[str, str], str]:
    """Split SKILL.md content into (frontmatter dict, markdown body). Tolerant:
    no frontmatter block means empty metadata, whole file is body."""
    meta: dict[str, str] = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]
            for line in parts[1].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
    return meta, body


def parse_skill_md(path: Path) -> tuple[dict[str, str], str]:
    return parse_skill_text(path.read_text(encoding="utf-8"))


def semver_key(v: str) -> list[int]:
    return [int(x) for x in v.split(".")] if SEMVER_RE.match(v) else [-1]


def list_registry() -> dict[str, list[str]]:
    """The catalog, derived live from the registry tree — name -> sorted versions."""
    out: dict[str, list[str]] = {}
    if REGISTRY.is_dir():
        for skill in sorted(p for p in REGISTRY.iterdir() if p.is_dir()):
            versions = [v.name for v in skill.iterdir()
                        if v.is_dir() and (v / "SKILL.md").is_file()]
            if versions:
                out[skill.name] = sorted(versions, key=semver_key)
    return out


def yank_marker(name: str, version: str) -> Path:
    """Sidecar path for a version's yank state. Lives *beside* the immutable
    version folder, never inside it — the published bytes never change; a yank
    is metadata about a version, not an edit to its content."""
    return REGISTRY / name / f"{version}.yanked"


def yanked_versions(name: str) -> dict[str, str]:
    """version -> reason for every yanked version of a skill (reason may be '')."""
    d = REGISTRY / name
    out: dict[str, str] = {}
    if d.is_dir():
        for p in d.glob("*.yanked"):
            if p.is_file():
                out[p.name[: -len(".yanked")]] = p.read_text(encoding="utf-8").strip()
    return out


def require_token(request: Request) -> None:
    """Curator gate shared by every write endpoint (publish, yank, unyank)."""
    token = os.environ.get("ASTRA_PUBLISH_TOKEN", "")
    if not token:
        raise HTTPException(403, "curator actions disabled: ASTRA_PUBLISH_TOKEN not set on server")
    if request.headers.get("x-astra-token") != token:
        raise HTTPException(401, "bad or missing X-Astra-Token header")


def catalog() -> list[dict]:
    """One row per skill for the index page and JSON API — derived live from the
    registry tree. `latest` is the newest *non-yanked* version (yank hides from
    latest); a fully-yanked skill falls back to its newest version, flagged."""
    items = []
    for name, versions in list_registry().items():
        yanked = yanked_versions(name)
        live = [v for v in versions if v not in yanked]
        latest = live[-1] if live else versions[-1]
        meta, _ = parse_skill_md(REGISTRY / name / latest / "SKILL.md")
        items.append({
            "name": name,
            "latest": latest,
            "versions": versions,
            "yanked": sorted(yanked, key=semver_key),
            "fully_yanked": not live,
            "description": meta.get("description", ""),
        })
    return items


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"skills": catalog()})


# ---------------------------------------------------------------------------
# JSON API — what the future catalog UI and the publish skill talk to
# ---------------------------------------------------------------------------

@app.get("/api/skills")
def api_skills():
    return {"skills": catalog()}


@app.get("/api/skills/{name}/latest")
def api_skill_latest(name: str):
    return api_skill(name, resolve_latest(name))


@app.get("/api/skills/{name}/{version}")
def api_skill(name: str, version: str):
    d = skill_dir(name, version)
    meta, _ = parse_skill_md(d / "SKILL.md")
    files = sorted(
        str(p.relative_to(d)).replace("\\", "/")
        for p in d.rglob("*") if p.is_file()
    )
    reasons = yanked_versions(name)
    return {
        "name": name, "version": version, "metadata": meta, "files": files,
        "yanked": version in reasons, "yank_reason": reasons.get(version, ""),
    }


@app.post("/api/publish", status_code=201)
async def api_publish(request: Request, name: str, version: str):
    """Curator-only ingest: raw zip body + ?name=&version=. The zip's contents
    become registry/<name>/<version>/ — after every wall below holds."""
    require_token(request)
    if not NAME_RE.match(name):
        raise HTTPException(400, f"skill name must be kebab-case: {name!r}")
    if not SEMVER_RE.match(version):
        raise HTTPException(400, f"version must be X.Y.Z: {version!r}")
    dest = REGISTRY / name / version
    if dest.exists():
        raise HTTPException(409, f"{name}@{version} already published — versions are immutable, bump instead")

    body = await request.body()
    try:
        zf = zipfile.ZipFile(io.BytesIO(body))
    except zipfile.BadZipFile:
        raise HTTPException(400, "request body is not a zip")
    entries = zf.namelist()
    for e in entries:
        if e.startswith("/") or ".." in e or ":" in e or "\\" in e:
            raise HTTPException(400, f"unsafe path in zip: {e!r}")
    if "SKILL.md" not in entries:
        raise HTTPException(400, "zip must contain SKILL.md at its root (zip the folder's contents, not the folder)")

    meta, _ = parse_skill_text(zf.read("SKILL.md").decode("utf-8"))
    if meta.get("name") != name:
        raise HTTPException(400, f"SKILL.md frontmatter name {meta.get('name')!r} != published name {name!r}")
    if not meta.get("description"):
        raise HTTPException(400, "SKILL.md frontmatter must carry a non-empty description")

    # extract to a temp dir inside the registry, then rename into place —
    # a half-written version folder must never be observable
    REGISTRY.mkdir(exist_ok=True)
    tmp = tempfile.mkdtemp(prefix=".publish-", dir=REGISTRY)
    try:
        zf.extractall(tmp)
        dest.parent.mkdir(parents=True, exist_ok=True)
        os.replace(tmp, dest)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return {"published": f"{name}@{version}", "page": f"/skills/{name}/{version}"}


@app.post("/api/yank")
async def api_yank(request: Request, name: str, version: str, reason: str = ""):
    """Curator-only withdrawal: hide a version from `latest` and flag it, without
    touching its bytes (pins keep working — this is yank, not delete). Reversible
    via unyank. Reason comes from ?reason= or, if absent, the raw request body."""
    require_token(request)
    skill_dir(name, version)  # 404 if the version doesn't exist
    if not reason:
        reason = (await request.body()).decode("utf-8", "replace").strip()
    yank_marker(name, version).write_text(reason, encoding="utf-8")
    return {"yanked": f"{name}@{version}", "reason": reason}


@app.post("/api/unyank")
def api_unyank(request: Request, name: str, version: str):
    """Reverse a yank — a yank is metadata, so restoring is just removing it."""
    require_token(request)
    marker = yank_marker(name, version)
    if not marker.is_file():
        raise HTTPException(404, f"{name}@{version} is not yanked")
    marker.unlink()
    return {"unyanked": f"{name}@{version}"}


def resolve_latest(name: str) -> str:
    """Newest *installable* version — yank hides a version from `latest`, so a
    saved latest-tracking command never resolves to a withdrawn release."""
    versions = list_registry().get(name)
    if not versions:
        raise HTTPException(status_code=404, detail=f"no skill named {name}")
    yanked = yanked_versions(name)
    live = [v for v in versions if v not in yanked]
    if not live:
        raise HTTPException(status_code=404, detail=f"all versions of {name} are yanked")
    return live[-1]


# "latest" alias routes — declared BEFORE the {version} routes so the literal
# path wins; a shared install command keeps working across version bumps
@app.get("/skills/{name}/latest", response_class=HTMLResponse)
def skill_page_latest(name: str):
    return RedirectResponse(f"/skills/{name}/{resolve_latest(name)}")


@app.get("/skills/{name}/latest/download")
def skill_download_latest(name: str):
    return skill_download(name, resolve_latest(name))


@app.get("/skills/{name}/{version}", response_class=HTMLResponse)
def skill_page(request: Request, name: str, version: str):
    d = skill_dir(name, version)
    meta, body = parse_skill_md(d / "SKILL.md")
    files = sorted(
        str(p.relative_to(d)).replace("\\", "/")
        for p in d.rglob("*") if p.is_file()
    )
    versions = list_registry().get(name, [version])
    reasons = yanked_versions(name)
    this_yanked = version in reasons
    live = [v for v in versions if v not in reasons]
    newest_live = live[-1] if live else None
    # a yanked version is never the install target for `latest`; it also can't
    # equal newest_live (it's excluded from `live`), so is_latest is False for it
    is_latest = version == newest_live
    base = str(request.base_url).rstrip("/")
    # the latest version's page hands out a latest-tracking command, so a
    # shared/saved paste keeps installing the newest release after bumps
    zip_url = f"{base}/skills/{name}/{'latest' if is_latest else version}/download"
    target = f"$env:USERPROFILE\\.claude\\skills\\{name}"
    install_cmd = (
        f'iwr {zip_url} -OutFile "$env:TEMP\\{name}.zip"; '
        f'Expand-Archive "$env:TEMP\\{name}.zip" "{target}" -Force; '
        f'del "$env:TEMP\\{name}.zip"'
    )
    return templates.TemplateResponse(request, "skill.html", {
        "name": meta.get("name", name),
        "version": version,
        "versions": versions,
        "yanked_versions": list(reasons),
        "yanked": this_yanked,
        "yank_reason": reasons.get(version, ""),
        "newest_live": newest_live,
        "is_latest": is_latest,
        "description": meta.get("description", ""),
        "body_html": markdown.markdown(body, extensions=["fenced_code", "tables"]),
        "files": files,
        "install_cmd": install_cmd,
        "install_check": f"/{meta.get('name', name)}",
        "download_url": f"/skills/{name}/{version}/download",
    })


@app.get("/skills/{name}/{version}/download")
def skill_download(name: str, version: str):
    d = skill_dir(name, version)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(d.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(d))
    buf.seek(0)
    filename = f"{name}-{version}.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
