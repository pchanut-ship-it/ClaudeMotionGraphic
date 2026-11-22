#!/usr/bin/env python3
"""Static checks for a Thai classroom touch game (single HTML file).

Usage:
    python3 check_static.py path/to/index.html

Checks:
  * external resources: only Google Fonts (fonts.googleapis.com / fonts.gstatic.com)
  * JavaScript written in ES5 (no arrow functions, template literals, let/const,
    classes, optional chaining, nullish coalescing, async/await, modern helpers)
  * CSS avoids features missing on old Smart-TV browsers
  * no speech synthesis (the game must not model pronunciation)
  * a full ES5 parse with acorn when Node.js + acorn are available
Exit code 1 when any check fails.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile


def strip_js_comments(js):
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", js)


def strip_css_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


JS_RULES = [
    ("optional chaining ?.", r"\?\.(?!\d)"),
    ("nullish coalescing ??", r"\?\?"),
    ("arrow function =>", r"=>"),
    ("template literal `", r"`"),
    ("let/const", r"\b(let|const)\s+[A-Za-z_$]"),
    ("class declaration", r"\bclass\s+[A-Z][A-Za-z0-9_]*\s*[{(e]"),
    ("async/await", r"\b(async\s+function|await\s+[A-Za-z_$(])"),
    ("Array.from", r"\bArray\.from\("),
    ("Array/String .includes()", r"\.includes\("),
    ("Array .find()/.findIndex()", r"\.find(Index)?\("),
    ("Object.assign", r"\bObject\.assign\("),
    ("Element.closest()", r"\.closest\("),
    ("Element.remove()", r"\.remove\(\)"),
    ("NodeList.forEach", r"querySelectorAll\([^)]*\)\.forEach"),
    ("speech synthesis", r"speechSynthesis|SpeechSynthesisUtterance"),
]

CSS_RULES = [
    ("light-dark()", r"light-dark\("),
    (":has()", r":has\("),
    (":is()/:where()", r":(is|where)\("),
    ("inset property", r"[;{\s]inset\s*:"),
    ("aspect-ratio property", r"[;{\s]aspect-ratio\s*:"),
    ("flex/grid gap", r"[;{\s](row-|column-)?gap\s*:"),
    ("min()/max()/clamp()", r"(?<![-\w])(min|max|clamp)\("),
    ("color-mix()", r"color-mix\("),
    ("@container", r"@container"),
]

ALLOWED_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")


def find_acorn():
    """Return a path to an installed acorn package, or None."""
    candidates = []
    npm = shutil.which("npm")
    if npm:
        try:
            root = subprocess.run([npm, "root", "-g"], capture_output=True, text=True, timeout=20).stdout.strip()
            if root:
                candidates.append(os.path.join(root, "acorn"))
        except Exception:
            pass
    candidates += ["/opt/node-tools/node_modules/acorn", "/usr/lib/node_modules/acorn",
                   "/usr/local/lib/node_modules/acorn", os.path.join(os.getcwd(), "node_modules", "acorn")]
    for c in candidates:
        if os.path.isfile(os.path.join(c, "package.json")):
            return c
    return None


def es5_parse(js):
    node = shutil.which("node")
    if not node:
        return None, "skipped (node not found)"
    acorn = find_acorn()
    if not acorn:
        return None, "skipped (acorn not installed; `npm i -g acorn` enables this check)"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(js)
        path = f.name
    code = ("const a=require(%r);const s=require('fs').readFileSync(%r,'utf8');"
            "try{a.parse(s,{ecmaVersion:5});console.log('ok')}catch(e){console.log('ERR '+e.message);process.exit(1)}"
            % (acorn, path))
    r = subprocess.run([node, "-e", code], capture_output=True, text=True)
    os.unlink(path)
    out = (r.stdout + r.stderr).strip()
    return r.returncode == 0, out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    html = open(path, encoding="utf-8").read()
    failures = 0

    def report(ok, label, detail=""):
        nonlocal failures
        if not ok:
            failures += 1
        print(("PASS " if ok else "FAIL ") + label + (("  " + detail) if detail else ""))

    # inline scripts and styles
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, flags=re.S | re.I)
    styles = re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S | re.I)
    js = strip_js_comments("\n".join(scripts))
    css = strip_css_comments("\n".join(styles))
    report(bool(scripts), "inline <script> present")

    # external resources
    ext = re.findall(r"""(?:src|href)\s*=\s*["'](https?://[^"']+)""", html, flags=re.I)
    ext += re.findall(r"""url\(\s*["']?(https?://[^)"']+)""", css)
    bad = sorted({u for u in ext if not any(h in u for h in ALLOWED_HOSTS)})
    report(not bad, "external resources limited to Google Fonts", ", ".join(bad[:5]))
    ext_scripts = re.findall(r"<script[^>]*\bsrc=", html, flags=re.I)
    report(not ext_scripts, "no external <script src>")

    for label, pattern in JS_RULES:
        hits = re.findall(pattern, js)
        report(not hits, "JS: no " + label, ("%d hit(s)" % len(hits)) if hits else "")
    for label, pattern in CSS_RULES:
        hits = re.findall(pattern, css)
        report(not hits, "CSS: no " + label, ("%d hit(s)" % len(hits)) if hits else "")

    ok, detail = es5_parse("\n".join(scripts))
    if ok is None:
        print("SKIP ES5 parse  " + detail)
    else:
        report(ok, "ES5 parse (acorn, ecmaVersion 5)", "" if ok else detail)

    # soft hints (not failures)
    if "localStorage" in js and not re.search(r"try\s*\{[^}]*localStorage", js, flags=re.S):
        print("WARN localStorage used outside try/catch?")
    if re.search(r"AudioContext", js) and "webkitAudioContext" not in js:
        print("WARN AudioContext without webkitAudioContext fallback")
    print("\n%s: %d failure(s)" % (os.path.basename(path), failures))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
