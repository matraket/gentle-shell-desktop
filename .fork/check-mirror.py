#!/usr/bin/env python3
"""Check that the Spanish mirror (docs-es/) matches the English corpus line by line.

Pairs: docs/**/*.md <-> docs-es/**/*.md (except docs/assets/mockup-v2/), and
CONTRIBUTING.md <-> docs-es/CONTRIBUTING.md. Each Spanish file starts with a
two-line header (a "> " note and a blank line), so Spanish line N+2 mirrors
English line N. Meaning is not checked; structure is.

Usage:
  check-mirror.py [--root DIR] [--changed-since REF]

--changed-since REF also requires every English line added, changed or deleted
since REF to have its Spanish counterpart changed in the same way, so a
correction cannot land in only one language. Exit 0 when everything matches.
"""
import argparse
import difflib
import posixpath
import re
import subprocess
import sys
from pathlib import Path

EXCLUDED = ("docs/assets/mockup-v2/",)
LABELS = ("Inference:", "UNVERIFIED:")
HEADER = 2

CODE_SPAN = re.compile(r"(`+)(.+?)\1")
LINK = re.compile(r"\]\(")
LINK_TARGET = re.compile(r"\]\(([^)\s]+)\)")
URL = re.compile(r"https?://[^\s)>`\]]+")
ANY_PINNED = re.compile(r"github\.com/[^/]+/[^/]+/blob/[0-9a-f]{40}/")
PINNED = re.compile(
    r"^https://github\.com/(matraket|Gentleman-Programming)/gentle-shell-desktop/blob/[0-9a-f]{40}/([^#?]+)"
)
LIST = re.compile(r"^(\s*)([-*+]|\d+\.)\s")
HEADING = re.compile(r"^(#{1,6})\s")


def pairs(root):
    out = {}
    for en in sorted((root / "docs").rglob("*.md")):
        rel = en.relative_to(root).as_posix()
        if rel.startswith(EXCLUDED):
            continue
        out[rel] = "docs-es/" + rel[len("docs/"):]
    out["CONTRIBUTING.md"] = "docs-es/CONTRIBUTING.md"
    return out


def kind(line, fenced):
    s = line.strip()
    if s.startswith("```"):
        return "fence"
    if fenced:
        return "code"
    if not s:
        return "blank"
    m = HEADING.match(line)
    if m:
        return "h%d" % len(m.group(1))
    if s.startswith("|"):
        return "table/%d" % CODE_SPAN.sub("", line).replace("\\|", "").count("|")
    m = LIST.match(line)
    if m:
        return "list/%d/%s" % (len(m.group(1)), "ol" if m.group(2)[0].isdigit() else "ul")
    if s.startswith(">"):
        return "quote"
    if s.startswith("<!--"):
        return "comment"
    return "text"


def link_paths(line, en_rel):
    """Repository paths of the relative links on an English line."""
    base = posixpath.dirname(en_rel)
    out = set()
    for target in LINK_TARGET.findall(line):
        if "://" in target or target.startswith("#"):
            continue
        out.add(posixpath.normpath(posixpath.join(base, target.split("#")[0])))
    return out


def facts(line):
    return {
        "code spans": sorted(m.group(2) for m in CODE_SPAN.finditer(line)),
        "labels": [line.count(label) for label in LABELS],
        "links": len(LINK.findall(line)),
    }


def url_errors(en_line, es_line, en_rel):
    """External URLs must match; a Spanish pinned blob URL must point at the
    file an English relative link on the same line points at."""
    en_urls = sorted(URL.findall(en_line))
    es_urls = []
    errors = []
    for url in URL.findall(es_line):
        if ANY_PINNED.search(url) and url not in en_urls:
            m = PINNED.match(url)
            if not m or m.group(2) not in link_paths(en_line, en_rel):
                errors.append("pinned URL %s does not match an English relative link" % url)
            continue
        es_urls.append(url)
    if sorted(es_urls) != en_urls:
        errors.append("urls differ: %r vs %r" % (en_urls, sorted(es_urls)))
    return errors


def compare(en_rel, en_text, es_text):
    en = en_text.split("\n")
    es = es_text.replace("\r\n", "\n").split("\n")
    if len(es) < HEADER or not es[0].startswith("> ") or es[1].strip():
        return ["header: line 1 must be a '> ' note and line 2 blank"]
    body = es[HEADER:]
    if len(body) != len(en):
        hint = ""
        if abs(len(body) - len(en)) == 1 and (en[-1] == "" or body[-1] == ""):
            hint = " (check the trailing newline)"
        return ["line count: English %d, Spanish %d (expected English + %d)%s" % (len(en), len(es), HEADER, hint)]
    errors = []
    fenced = False
    for i, (a, b) in enumerate(zip(en, body), start=1):
        where = "EN %d / ES %d" % (i, i + HEADER)
        ka, kb = kind(a, fenced), kind(b, fenced)
        if ka != kb:
            errors.append("%s: line kind %s vs %s" % (where, ka, kb))
        elif ka in ("code", "fence"):
            if a != b:
                errors.append("%s: code block lines must be identical" % where)
        else:
            fa, fb = facts(a), facts(b)
            for key in fa:
                if fa[key] != fb[key]:
                    errors.append("%s: %s differ: %r vs %r" % (where, key, fa[key], fb[key]))
            errors.extend("%s: %s" % (where, e) for e in url_errors(a, b, en_rel))
        if ka == "fence":
            fenced = not fenced
    if fenced:
        errors.append("unclosed code block at the end of the English file")
    return errors


def git_show(root, ref, path):
    r = subprocess.run(["git", "-C", str(root), "show", "%s:%s" % (ref, path)],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def change_points(old, new):
    """Changed line indices in `new`, and the `new` positions where lines were deleted."""
    changed, deleted = set(), set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag in ("replace", "insert"):
            changed.update(range(j1, j2))
        if tag in ("replace", "delete"):
            deleted.add(j1)
    return changed, deleted


def changed_errors(root, ref, en_rel, es_rel, en_text, es_text):
    en_old = git_show(root, ref, en_rel)
    es_old = git_show(root, ref, es_rel)
    en_new, es_new = en_text.split("\n"), es_text.replace("\r\n", "\n").split("\n")
    en_changed, en_deleted = change_points([] if en_old is None else en_old.split("\n"), en_new)
    if es_old is None:
        es_changed, es_deleted = set(range(len(es_new))), set()
    else:
        es_changed, es_deleted = change_points(es_old.replace("\r\n", "\n").split("\n"), es_new)
    errors = []
    for j in sorted(en_changed):
        if j + HEADER not in es_changed:
            errors.append("EN %d changed since %s but ES %d did not" % (j + 1, ref, j + 1 + HEADER))
    for j in sorted(en_deleted):
        if j + HEADER not in es_deleted and j + HEADER not in es_changed:
            errors.append("EN lines deleted before EN %d since %s but not before ES %d" % (j + 1, ref, j + 1 + HEADER))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--changed-since", metavar="REF")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    expected = pairs(root)
    failures = 0
    for en_rel, es_rel in expected.items():
        en_path, es_path = root / en_rel, root / es_rel
        if not es_path.is_file():
            print("MISSING %s (mirror of %s)" % (es_rel, en_rel))
            failures += 1
            continue
        en_text = en_path.read_text(encoding="utf-8")
        es_text = es_path.read_text(encoding="utf-8")
        problems = compare(en_rel, en_text, es_text)
        if args.changed_since and not problems:
            problems = changed_errors(root, args.changed_since, en_rel, es_rel, en_text, es_text)
        for problem in problems:
            print("%s: %s" % (es_rel, problem))
            failures += 1
    for es in sorted((root / "docs-es").rglob("*.md")):
        rel = es.relative_to(root).as_posix()
        if rel not in expected.values():
            print("ORPHAN %s (no English source)" % rel)
            failures += 1
    print("%d pairs checked, %d problems" % (len(expected), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
