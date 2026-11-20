import hashlib
import importlib.util
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "assets" / "spec-coder-architecture.html"
PNG = ROOT / "assets" / "spec-coder-architecture.png"
RENDERER = ROOT / "scripts" / "render-architecture.py"


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_architecture", RENDERER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ArchitectureAssetTests(unittest.TestCase):
    def test_renderer_tracks_html_digest_in_png(self):
        renderer = load_renderer()
        self.assertEqual(renderer.png_dimensions(PNG), (1400, 1000))
        expected = hashlib.sha256(HTML.read_bytes()).hexdigest()
        self.assertEqual(renderer.png_text(PNG)[renderer.SOURCE_SHA_KEY], expected)

    def test_live_browser_geometry_fits_capture(self):
        cache = os.environ.get("SPEC_CODER_BUILD_CACHE")
        if not cache:
            self.skipTest("set SPEC_CODER_BUILD_CACHE to run live Chromium geometry")
        before = (HTML.read_bytes(), PNG.read_bytes())
        result = subprocess.run(
            (
                sys.executable,
                "-B",
                str(RENDERER),
                "--check",
                "--browser-cache",
                cache,
                "--chromium",
                "/usr/bin/chromium",
            ),
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"fits_capture": true', result.stdout)
        self.assertEqual((HTML.read_bytes(), PNG.read_bytes()), before)

        renderer = load_renderer()
        legacy = """<!doctype html>
<style>
  body { margin: 0; padding: 32px; }
  main { width: 1320px; padding: 28px 36px 36px; border: 1px solid; }
</style>
<body><main><svg width="1320" height="760"></svg></main></body>
"""
        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8") as handle:
            handle.write(legacy)
            handle.flush()
            geometry = renderer.browser_geometry(
                Path("/usr/bin/chromium"), Path(cache), Path(handle.name)
            )
        self.assertFalse(geometry["fits_capture"])

    def test_png_header_is_the_documented_capture_size(self):
        data = PNG.read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", data[16:24]), (1400, 1000))


if __name__ == "__main__":
    unittest.main()
