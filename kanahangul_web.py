#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple web UI for kanahangul.py (standard library only).
- Imports kanahangul.py for conversion functions.
- Serves an HTML5 form with dropdowns + textareas.

Run:
  python kanahangul_web.py
Then open:
  http://127.0.0.1:8000
"""

from __future__ import annotations

import html
import sys
from pathlib import Path
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


# Ensure we can import kanahangul.py from the same directory as this script
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import kanahangul  # noqa: E402


def _h(s: str) -> str:
    return html.escape(s or "", quote=True)


def render_page(
    *,
    action: str = "kana_to_hangul",
    mode: str = "simple",
    profile: str = "default",
    long_vowels: str = "",
    text_in: str = "",
    text_out: str = "",
    error: str = "",
) -> str:
    profiles = sorted(getattr(kanahangul, "KANA_TO_HANGUL_PROFILES", {}).keys()) or ["default"]
    modes = ["simple", "tense", "double_vowel", "tense_double"]

    profile_options = "\n".join(
        f'<option value="{_h(p)}" {"selected" if p == profile else ""}>{_h(p)}</option>'
        for p in profiles
    )
    mode_options = "\n".join(
        f'<option value="{_h(m)}" {"selected" if m == mode else ""}>{_h(m)}</option>'
        for m in modes
    )

    action_options = "\n".join(
        [
            f'<option value="kana_to_hangul" {"selected" if action=="kana_to_hangul" else ""}>Kana → Hangul</option>',
            f'<option value="hangul_to_hiragana" {"selected" if action=="hangul_to_hiragana" else ""}>Hangul → Hiragana</option>',
            f'<option value="hangul_to_katakana" {"selected" if action=="hangul_to_katakana" else ""}>Hangul → Katakana</option>',
        ]
    )

    lv_options = "\n".join(
        [
            f'<option value="" {"selected" if long_vowels=="" else ""}>(no collapse)</option>',
            f'<option value="ー" {"selected" if long_vowels=="ー" else ""}>collapse to ー</option>',
        ]
    )

    err_html = f'<div class="error">{_h(error)}</div>' if error else ""

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kana ↔ Hangul Web Converter</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }}
    .row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    @media (max-width: 900px) {{ .row {{ grid-template-columns: 1fr; }} }}
    textarea {{ width: 100%; min-height: 220px; padding: 10px; font-size: 16px; }}
    select, button {{ padding: 8px 10px; font-size: 14px; }}
    .controls {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: end; margin: 12px 0 16px; }}
    label {{ display: grid; gap: 6px; font-size: 13px; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 14px; }}
    .error {{ color: #b00020; margin: 8px 0; }}
    .hint {{ color: #555; font-size: 13px; margin-top: 6px; line-height: 1.35; }}
    .muted {{ color: #666; font-size: 13px; }}
  </style>
</head>
<body>
  <h1>Kana ↔ Hangul Web Converter</h1>
  <p class="muted">Powered by <code>kanahangul.py</code> (imported from the same folder).</p>

  <form method="post" accept-charset="UTF-8">
    <div class="controls">
      <label>
        Conversion
        <select name="action">
          {action_options}
        </select>
      </label>

      <label>
        Kana→Hangul mode
        <select name="mode">
          {mode_options}
        </select>
      </label>

      <label>
        Hangul profile
        <select name="profile">
          {profile_options}
        </select>
      </label>

      <label>
        Katakana long vowels
        <select name="long_vowels">
          {lv_options}
        </select>
      </label>

      <button type="submit">Convert</button>
    </div>

    {err_html}

    <div class="row">
      <div class="card">
        <h3>Input</h3>
        <textarea name="input" spellcheck="false">{_h(text_in)}</textarea>
        <div class="hint">
          Kana→Hangul: tense modes handle small っ/ッ; double_vowel modes treat ー as an extra vowel syllable.<br/>
          Hangul→Katakana: “collapse to ー” merges duplicated vowel-only syllables into ー (if supported by your module).
        </div>
      </div>

      <div class="card">
        <h3>Output</h3>
        <textarea readonly spellcheck="false">{_h(text_out)}</textarea>
      </div>
    </div>
  </form>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send_html(self, page: str, status: int = 200) -> None:
        data = page.encode("utf-8", errors="replace")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        page = render_page()
        self._send_html(page)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        form = parse_qs(raw, keep_blank_values=True)

        action = (form.get("action", ["kana_to_hangul"])[0] or "kana_to_hangul").strip()
        mode = (form.get("mode", ["simple"])[0] or "simple").strip()
        profile = (form.get("profile", ["default"])[0] or "default").strip()
        long_vowels = (form.get("long_vowels", [""])[0] or "").strip()
        text_in = form.get("input", [""])[0]

        text_out = ""
        error = ""

        try:
            if action == "kana_to_hangul":
                # kanahangul.kana_to_hangul_text(text, mode="simple", hangul_profile="default")
                text_out = kanahangul.kana_to_hangul_text(text_in, mode=mode, hangul_profile=profile)

            elif action == "hangul_to_hiragana":
                # kanahangul.hangul_to_hiragana_text(text)
                text_out = kanahangul.hangul_to_hiragana_text(text_in)

            elif action == "hangul_to_katakana":
                # kanahangul.hangul_to_katakana_text(text, long_vowels=None or "ー")
                lv = "ー" if long_vowels == "ー" else None
                text_out = kanahangul.hangul_to_katakana_text(text_in, long_vowels=lv)

            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            error = f"{type(e).__name__}: {e}"

        page = render_page(
            action=action,
            mode=mode,
            profile=profile,
            long_vowels=long_vowels,
            text_in=text_in,
            text_out=text_out,
            error=error,
        )
        self._send_html(page)


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Serving on http://{host}:{port}  (Ctrl+C to stop)")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
