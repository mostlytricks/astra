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


# --- read surfaces ---------------------------------------------------------

def test_catalog_lists_seeded_skill(client):
    data = client.get("/api/skills").json()
    assert data["skills"] == [{
        "name": "demo", "latest": "1.0.0", "versions": ["1.0.0"],
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
