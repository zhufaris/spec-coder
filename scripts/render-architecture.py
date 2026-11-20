#!/usr/bin/env python3
"""Render and verify the checked-in architecture PNG with Chromium."""
from __future__ import annotations

import argparse
import hashlib
import html as html_module
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "assets" / "spec-coder-architecture.html"
PNG = ROOT / "assets" / "spec-coder-architecture.png"
SOURCE_SHA_KEY = "spec-coder-source-sha256"
CAPTURE = (1400, 1000)
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunks(data: bytes):
    if not data.startswith(SIGNATURE):
        raise ValueError("not a PNG")
    offset = len(SIGNATURE)
    while offset < len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        yield kind, payload
        offset += 12 + length


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if not data.startswith(SIGNATURE) or data[12:16] != b"IHDR":
        raise ValueError("missing PNG IHDR")
    return struct.unpack(">II", data[16:24])


def png_text(path: Path) -> dict[str, str]:
    values = {}
    for kind, payload in _chunks(path.read_bytes()):
        if kind == b"tEXt" and b"\0" in payload:
            key, value = payload.split(b"\0", 1)
            values[key.decode("latin-1")] = value.decode("latin-1")
    return values


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))


def set_png_text(path: Path, key: str, value: str) -> None:
    chunks = list(_chunks(path.read_bytes()))
    kept = [
        (kind, payload)
        for kind, payload in chunks
        if not (kind == b"tEXt" and payload.split(b"\0", 1)[0] == key.encode("latin-1"))
    ]
    output = bytearray(SIGNATURE)
    for index, (kind, payload) in enumerate(kept):
        output.extend(_chunk(kind, payload))
        if index == 0:
            output.extend(_chunk(b"tEXt", key.encode("latin-1") + b"\0" + value.encode("latin-1")))
    path.write_bytes(output)


def _chromium_args(chromium: Path, cache: Path) -> list[str]:
    profile = cache / "architecture-renderer-profile"
    disk_cache = cache / "architecture-renderer-cache"
    profile.mkdir(parents=True, exist_ok=True)
    disk_cache.mkdir(parents=True, exist_ok=True)
    return [
        str(chromium), "--headless", "--no-sandbox", "--disable-dev-shm-usage",
        "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
        f"--window-size={CAPTURE[0]},{CAPTURE[1]}",
        f"--user-data-dir={profile}", f"--disk-cache-dir={disk_cache}",
    ]


def browser_geometry(chromium: Path, cache: Path, source_path: Path = HTML) -> dict:
    script = """
<script>
(() => {
  const box = element => {
    const r = element.getBoundingClientRect();
    return {left:r.left, top:r.top, right:r.right, bottom:r.bottom, width:r.width, height:r.height};
  };
  const geometry = {
    viewport:{width:innerWidth,height:innerHeight},
    document:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},
    main:box(document.querySelector('main')),
    svg:box(document.querySelector('svg'))
  };
  const fits = r => r.left >= 0 && r.top >= 0 && r.right <= innerWidth && r.bottom <= innerHeight;
  geometry.fits_capture = innerWidth === 1400 && innerHeight === 1000 && geometry.document.width <= innerWidth && geometry.document.height <= innerHeight && fits(geometry.main) && fits(geometry.svg);
  const pre = document.createElement('pre');
  pre.id = 'spec-coder-geometry';
  pre.textContent = JSON.stringify(geometry);
  document.body.replaceChildren(pre);
})();
</script>
"""
    source = source_path.read_text(encoding="utf-8").replace("</body>", script + "</body>")
    probe = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
            handle.write(source)
            probe = Path(handle.name)
        result = subprocess.run(
            _chromium_args(chromium, cache) + ["--dump-dom", probe.as_uri()],
            check=True, text=True, capture_output=True, timeout=30,
        )
    finally:
        if probe is not None:
            probe.unlink(missing_ok=True)
    match = re.search(r'<pre id="spec-coder-geometry">(.*?)</pre>', result.stdout, re.S)
    if not match:
        raise RuntimeError("Chromium geometry probe produced no result")
    return json.loads(html_module.unescape(match.group(1)))


def render(chromium: Path, cache: Path) -> dict:
    geometry = browser_geometry(chromium, cache)
    if not geometry["fits_capture"]:
        raise RuntimeError("page bounds exceed capture: " + json.dumps(geometry, sort_keys=True))
    subprocess.run(
        _chromium_args(chromium, cache) + [f"--screenshot={PNG}", HTML.as_uri()],
        check=True, text=True, capture_output=True, timeout=30,
    )
    set_png_text(PNG, SOURCE_SHA_KEY, hashlib.sha256(HTML.read_bytes()).hexdigest())
    return check(chromium, cache, geometry)


def check(chromium: Path, cache: Path, geometry=None) -> dict:
    geometry = geometry or browser_geometry(chromium, cache)
    expected = hashlib.sha256(HTML.read_bytes()).hexdigest()
    actual = png_text(PNG).get(SOURCE_SHA_KEY)
    dimensions = png_dimensions(PNG)
    synchronized = actual == expected
    if not geometry["fits_capture"] or dimensions != CAPTURE or not synchronized:
        raise RuntimeError(json.dumps({"geometry": geometry, "dimensions": dimensions, "source_synchronized": synchronized}, sort_keys=True))
    return {"fits_capture": True, "geometry": geometry, "png_dimensions": dimensions, "source_sha256": expected, "source_synchronized": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--render", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--browser-cache", type=Path, required=True)
    parser.add_argument("--chromium", type=Path, default=Path("/usr/bin/chromium"))
    args = parser.parse_args()
    if not args.chromium.is_file():
        parser.error("Chromium executable not found")
    summary = render(args.chromium, args.browser_cache) if args.render else check(args.chromium, args.browser_cache)
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
