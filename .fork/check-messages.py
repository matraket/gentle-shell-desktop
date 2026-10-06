#!/usr/bin/env python3
"""Reject commit messages with bare issue references (#12, fixes #3, (#20), GH-7).

These commits travel to Gentleman-Programming/gentle-shell-desktop, where a bare
#N or GH-N links to the upstream issue N, not to this fork's, and "closes GH-N"
could close it. Write owner/repo#N or a full URL instead.

Usage: check-messages.py <revision-range>   Exit 0 when no message has one.
"""
import re
import subprocess
import sys

BARE = re.compile(r"(?<![\w/.-])#\d+\b|\bGH-\d+\b", re.IGNORECASE)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    out = subprocess.run(
        ["git", "log", "--format=%H%x00%B%x01", sys.argv[1]],
        capture_output=True, text=True, check=True,
    ).stdout
    failures = 0
    for record in filter(None, (r.strip() for r in out.split("\x01"))):
        sha, body = record.split("\x00", 1)
        for match in BARE.finditer(body):
            print("%s: bare reference %s in: %s" % (sha[:7], match.group(0), body.splitlines()[0]))
            failures += 1
    print("%d bare references" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
