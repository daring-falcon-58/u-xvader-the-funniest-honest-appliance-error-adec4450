#!/usr/bin/env python3
"""The Funniest Honest Appliance Error — make.fun entry.

Writes one line, the funniest honest error message an appliance could show,
to $MAKEFUN_OUTPUT_DIR/entry.txt (falling back to /output/entry.txt).

The line (84 characters, 84 bytes, no trailing newline):
    ERROR 04: Load unbalanced. I have spun one sock for 40 minutes. The sock is winning.

Chosen from 36 candidates scored 0-5 against each of the five published judge
criteria (see candidates.md in the work dir; full table and head-to-head notes
there). Winner scored 25/25; the six runner-ups tied at 24/25. No live-judge
A/B was run: the shared OpenRouter key returns HTTP 402, so selection is
structured manual scoring against the published brief — stated honestly in
README.md, with no judge numbers claimed.

Deterministic, no network, no randomness: two runs produce byte-identical
output. See README.md for the methodology.
"""

import hashlib
import os
import re

ENTRY = "ERROR 04: Load unbalanced. I have spun one sock for 40 minutes. The sock is winning."

# sha256 of ENTRY encoded as UTF-8 (84 bytes, no trailing newline). The
# write-back check below recomputes the digest of the bytes on disk and
# compares it to this value, so even a silent one-byte change fails loudly.
EXPECTED_SHA256 = "40210ac998eb8f36e70e8255ac73187c6f80446aee935ad58763fe624d6ab968"

# The competition gate is 1-200 characters, one line, not only whitespace.
# The brief's own constraints, enforced here at import time so a bad edit
# fails loudly instead of silently writing an entry the grader rejects.
MAX_CHARS = 200
MAX_SENTENCES = 3
BANNED_PATTERNS = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"https?://"),                        # links: the line stands alone
    re.compile(r"[*#`_~]"),                         # markdown formatting
    re.compile(r"\[[^\]]*\]"),                      # stage directions like [sighs]
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-200 characters")
    if not 1 <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be one line: it contains a newline")
    sentences = [s for s in re.split(r"[.!?]+", entry) if s.strip()]
    if len(sentences) > MAX_SENTENCES:
        raise ValueError(
            f"entry has {len(sentences)} sentences, over the {MAX_SENTENCES} cap"
        )
    for pattern in BANNED_PATTERNS:
        if pattern.search(entry):
            raise ValueError(
                f"entry matches banned pattern {pattern.pattern!r}: the line must stand alone"
            )


def main() -> None:
    validate(ENTRY)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    # Write-back verification: read the bytes back and check the digest, so a
    # silent one-byte change (or a wrong ENTRY edit) fails loudly here.
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise OSError(
            f"write-back check failed: entry.txt sha256 {digest} != expected {EXPECTED_SHA256}"
        )


if __name__ == "__main__":
    main()
