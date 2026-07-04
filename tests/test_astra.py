"""System tests — boot the app against a temp registry and prove every wall."""

import io
import zipfile

import pytest
from fastapi.testclient import TestClient

import astra.main as main

SKILL_MD = """---
name: {name}
description: {description}
---

# {name}

A test skill body.
"""


def make_zip(files: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for path, content in files.items():
            zf.writestr(path, content)
    return buf.getvalue()


@pytest.fixture
def client(tmp_path, monkeypatch):
    reg = tmp_path / "registry"
    seed = reg / "demo" / "1.0.0"
    seed.mkdir(parents=True)
    (seed / "SKILL.md").write_text(
        SKILL_MD.format(name="demo", description="a seeded demo skill"),
        encoding="utf-8",
    )
    monkeypatch.setattr(main, "REGISTRY", reg)
    monkeypatch.setenv("ASTRA_PUBLISH_TOKEN", "sekrit")
    return TestClient(main.app)


def publish(client, name, version, zip_bytes, token="sekrit"):
    return client.post(
        f"/api/publish?name={name}&version={version}",
        content=zip_bytes,
        headers={"X-Astra-Token": token} if token else {},
    )


def yank(client, name, version, reason="", token="sekrit", verb="yank"):
    url = f"/api/{verb}?name={name}&version={version}"
    if reason:
        url += f"&reason={reason}"
    return client.post(url, headers={"X-Astra-Token": token} if token else {})


def seed_second_version(client, version="1.10.0", desc="v2 desc"):
    z = make_zip({"SKILL.md": SKILL_MD.format(name="demo", description=desc)})
    assert publish(client, "demo", version, z).status_code == 201


# --- read surfaces ---------------------------------------------------------

def test_catalog_lists_seeded_skill(client):
    data = client.get("/api/skills").json()
    assert data["skills"] == [{
        "name": "demo", "latest": "1.0.0", "versions": ["1.0.0"],
        "yanked": [], "fully_yanked": False,
        "description": "a seeded demo skill",
    }]


def test_metadata_endpoint(client):
    data = client.get("/api/skills/demo/1.0.0").json()
    assert data["metadata"]["name"] == "demo"
    assert data["files"] == ["SKILL.md"]


def test_catalog_page_renders(client):
    html = client.get("/").text
    assert "demo" in html
    assert "a seeded demo skill" in html
    assert "Search skills" in html


def test_detail_page_renders(client):
    html = client.get("/skills/demo/1.0.0").text
    assert "a seeded demo skill" in html
    assert "Expand-Archive" in html  # the install one-liner is on the page


def test_detail_page_has_install_verification(client):
    html = client.get("/skills/demo/1.0.0").text
    assert "did it install" in html.lower()       # the verification checklist
    assert "Restart Claude Code" in html          # the troubleshooting step
    assert "/demo" in html                         # the /name appears-as-command check


def test_download_roundtrip_is_byte_identical(client):
    r = client.get("/skills/demo/1.0.0/download")
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    disk = (main.REGISTRY / "demo" / "1.0.0" / "SKILL.md").read_bytes()
    assert zf.read("SKILL.md") == disk


def test_latest_alias_tracks_newest_version(client):
    # seed a second, newer version so latest has something to resolve
    z = make_zip({"SKILL.md": SKILL_MD.format(name="demo", description="v2 desc")})
    assert publish(client, "demo", "1.10.0", z).status_code == 201

    # page redirects to the newest version
    r = client.get("/skills/demo/latest")
    assert r.status_code == 200 and r.url.path.endswith("/demo/1.10.0")

    # download serves the newest bytes
    zf = zipfile.ZipFile(io.BytesIO(client.get("/skills/demo/latest/download").content))
    assert "v2 desc" in zf.read("SKILL.md").decode("utf-8")

    # API resolves too
    assert client.get("/api/skills/demo/latest").json()["version"] == "1.10.0"

    # the newest page hands out a latest-tracking command; older pages stay pinned
    assert "/skills/demo/latest/download" in client.get("/skills/demo/1.10.0").text
    old = client.get("/skills/demo/1.0.0").text
    assert "/skills/demo/1.0.0/download" in old and "pinned to v1.0.0" in old


def test_latest_alias_404s_for_unknown_skill(client):
    assert client.get("/skills/nope/latest").status_code == 404
    assert client.get("/api/skills/nope/latest").status_code == 404


def test_unknown_skill_404s(client):
    assert client.get("/skills/nope/1.0.0").status_code == 404
    assert client.get("/api/skills/nope/1.0.0").status_code == 404


# --- publish walls ---------------------------------------------------------

def test_publish_happy_path_then_served(client):
    z = make_zip({"SKILL.md": SKILL_MD.format(name="newbie", description="fresh skill")})
    r = publish(client, "newbie", "1.0.0", z)
    assert r.status_code == 201, r.text
    # immediately live on every surface
    assert (main.REGISTRY / "newbie" / "1.0.0" / "SKILL.md").is_file()
    names = [s["name"] for s in client.get("/api/skills").json()["skills"]]
    assert "newbie" in names
    assert client.get("/skills/newbie/1.0.0").status_code == 200


def test_publish_multi_file_and_version_sort(client):
    z = make_zip({
        "SKILL.md": SKILL_MD.format(name="demo", description="v2"),
        "scripts/helper.py": "print('hi')",
    })
    assert publish(client, "demo", "1.10.0", z).status_code == 201
    data = client.get("/api/skills").json()["skills"][0]
    assert data["latest"] == "1.10.0"  # semver sort, not string sort
    assert "scripts/helper.py" in client.get("/api/skills/demo/1.10.0").json()["files"]


def test_publish_rejects_bad_token(client):
    z = make_zip({"SKILL.md": SKILL_MD.format(name="x", description="d")})
    assert publish(client, "x", "1.0.0", z, token="wrong").status_code == 401
    assert publish(client, "x", "1.0.0", z, token=None).status_code == 401


def test_publish_disabled_without_server_token(client, monkeypatch):
    monkeypatch.delenv("ASTRA_PUBLISH_TOKEN")
    z = make_zip({"SKILL.md": SKILL_MD.format(name="x", description="d")})
    assert publish(client, "x", "1.0.0", z).status_code == 403


def test_publish_rejects_duplicate_version(client):
    z = make_zip({"SKILL.md": SKILL_MD.format(name="demo", description="d")})
    assert publish(client, "demo", "1.0.0", z).status_code == 409


def test_publish_rejects_missing_skill_md(client):
    z = make_zip({"README.md": "not a skill"})
    r = publish(client, "x", "1.0.0", z)
    assert r.status_code == 400
    assert "SKILL.md" in r.json()["detail"]


def test_publish_rejects_name_mismatch(client):
    z = make_zip({"SKILL.md": SKILL_MD.format(name="other", description="d")})
    assert publish(client, "x", "1.0.0", z).status_code == 400


def test_publish_rejects_bad_name_and_version(client):
    z = make_zip({"SKILL.md": SKILL_MD.format(name="Bad_Name", description="d")})
    assert publish(client, "Bad_Name", "1.0.0", z).status_code == 400
    z = make_zip({"SKILL.md": SKILL_MD.format(name="ok-name", description="d")})
    assert publish(client, "ok-name", "v1", z).status_code == 400


def test_publish_rejects_zip_slip(client):
    z = make_zip({
        "SKILL.md": SKILL_MD.format(name="evil", description="d"),
        "../outside.txt": "escaped!",
    })
    assert publish(client, "evil", "1.0.0", z).status_code == 400
    assert not (main.REGISTRY.parent / "outside.txt").exists()


def test_publish_rejects_non_zip_body(client):
    assert publish(client, "x", "1.0.0", b"just some text").status_code == 400


def test_publish_rejects_console_nonascii(client):
    # a script that prints non-ASCII would mojibake/crash on a cp949 console
    z = make_zip({
        "SKILL.md": SKILL_MD.format(name="hangul", description="d"),
        "run.py": "print('안녕')  # greets in Korean\n",
    })
    assert publish(client, "hangul", "1.0.0", z).status_code == 400


def test_publish_allows_warnings(client):
    # a non-stdlib import is a warning, not a wall — publish still succeeds
    z = make_zip({
        "SKILL.md": SKILL_MD.format(name="warned", description="d"),
        "run.py": "import os\nimport requests\nprint('ok')\n",
    })
    assert publish(client, "warned", "1.0.0", z).status_code == 201


# --- dry-run bundle validation --------------------------------------------

def validate(client, files):
    return client.post("/api/validate", content=make_zip(files)).json()


def test_validate_accepts_clean_bundle(client):
    body = validate(client, {
        "SKILL.md": SKILL_MD.format(name="clean", description="d"),
        "run.py": "import json\nprint('ok')\n",
    })
    assert body["ok"] is True and body["errors"] == 0


def test_validate_flags_console_nonascii_as_error(client):
    body = validate(client, {
        "SKILL.md": SKILL_MD.format(name="x", description="d"),
        "run.py": "print('안녕')\n",
    })
    assert body["ok"] is False
    assert any(f["code"] == "console-nonascii" for f in body["findings"])


def test_validate_warns_nonstdlib_import_but_stays_ok(client):
    body = validate(client, {
        "SKILL.md": SKILL_MD.format(name="y", description="d"),
        "run.py": "import requests\n",
    })
    assert body["ok"] is True  # warnings don't block
    assert any(f["code"] == "nonstdlib-import" for f in body["findings"])


def test_validate_rejects_path_traversal(client):
    body = validate(client, {
        "SKILL.md": SKILL_MD.format(name="z", description="d"),
        "../evil.txt": "escape",
    })
    assert body["ok"] is False
    assert any(f["code"] == "path-unsafe" for f in body["findings"])


def test_validate_exempts_skill_md_from_ascii(client):
    # SKILL.md renders as HTML, never prints — rich text is allowed
    md = SKILL_MD.format(name="rich", description="curated — versioned ✨")
    body = validate(client, {"SKILL.md": md})
    assert body["ok"] is True
    assert not any(f["code"] in ("console-nonascii", "nonascii") for f in body["findings"])
    assert publish(client, "rich", "1.0.0", make_zip({"SKILL.md": md})).status_code == 201


def test_validate_needs_no_token(client, monkeypatch):
    # authors self-check without the publish token — validate is a read-like lint
    monkeypatch.delenv("ASTRA_PUBLISH_TOKEN")
    body = client.post("/api/validate",
                       content=make_zip({"SKILL.md": SKILL_MD.format(name="a", description="d")})).json()
    assert body["ok"] is True


# --- yank / unyank ---------------------------------------------------------

def test_yank_hides_from_latest_but_keeps_pin_installable(client):
    seed_second_version(client)  # demo now has 1.0.0 + 1.10.0, latest = 1.10.0
    assert yank(client, "demo", "1.10.0", reason="broken build").status_code == 200

    # latest now resolves to the older live version everywhere
    assert client.get("/skills/demo/latest").url.path.endswith("/demo/1.0.0")
    assert client.get("/api/skills/demo/latest").json()["version"] == "1.0.0"
    assert client.get("/api/skills").json()["skills"][0]["latest"] == "1.0.0"

    # but the yanked version is NOT deleted — its pinned page + download still work
    assert client.get("/skills/demo/1.10.0").status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(client.get("/skills/demo/1.10.0/download").content))
    assert "v2 desc" in zf.read("SKILL.md").decode("utf-8")


def test_yank_marks_api_and_page(client):
    seed_second_version(client)
    yank(client, "demo", "1.10.0", reason="oops")
    meta = client.get("/api/skills/demo/1.10.0").json()
    assert meta["yanked"] is True and meta["yank_reason"] == "oops"
    assert client.get("/api/skills").json()["skills"][0]["yanked"] == ["1.10.0"]

    page = client.get("/skills/demo/1.10.0").text
    assert "withdrawn" in page and "oops" in page
    assert "/skills/demo/1.10.0/download" in page  # pinned, not latest-tracking


def test_yank_leaves_published_bytes_untouched(client):
    before = (main.REGISTRY / "demo" / "1.0.0" / "SKILL.md").read_bytes()
    yank(client, "demo", "1.0.0")
    after = (main.REGISTRY / "demo" / "1.0.0" / "SKILL.md").read_bytes()
    assert before == after  # immutability: yank is a sidecar, never an edit


def test_fully_yanked_skill_shows_withdrawn_but_still_listed(client):
    yank(client, "demo", "1.0.0")  # the only version
    item = client.get("/api/skills").json()["skills"][0]
    assert item["fully_yanked"] is True and item["latest"] == "1.0.0"
    assert "withdrawn" in client.get("/").text
    # latest alias 404s — nothing installable via latest
    assert client.get("/skills/demo/latest").status_code == 404


def test_unyank_restores(client):
    seed_second_version(client)
    yank(client, "demo", "1.10.0")
    assert client.get("/api/skills/demo/latest").json()["version"] == "1.0.0"
    assert yank(client, "demo", "1.10.0", verb="unyank").status_code == 200
    assert client.get("/api/skills/demo/latest").json()["version"] == "1.10.0"


def test_yank_requires_token(client):
    assert yank(client, "demo", "1.0.0", token="wrong").status_code == 401
    assert yank(client, "demo", "1.0.0", token=None).status_code == 401


def test_yank_404s_for_unknown_version(client):
    assert yank(client, "demo", "9.9.9").status_code == 404
    assert yank(client, "nope", "1.0.0").status_code == 404


def test_unyank_404s_when_not_yanked(client):
    assert yank(client, "demo", "1.0.0", verb="unyank").status_code == 404
