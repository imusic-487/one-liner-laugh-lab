#!/usr/bin/env python3
"""One-Liner Laugh Lab entry: write one funny line to /output/entry.txt.

Reads line.txt (the entry, exactly as submitted) and copies it byte for
byte to /output/entry.txt, after checking the gate: UTF-8 text, 1-200
characters, not only white space, a single line. The output is then
re-read and compared byte for byte, so a failed write is reported
instead of silently passing.
"""

import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "line.txt"
DEST = Path("/output/entry.txt")
MIN_CHARS = 1
MAX_CHARS = 200


def read_entry(source: Path) -> tuple[bytes, str]:
    """Read the entry file, returning (raw bytes, decoded text)."""
    try:
        raw = source.read_bytes()
    except FileNotFoundError:
        raise ValueError(f"entry file not found: {source}") from None
    except OSError as exc:
        raise ValueError(f"cannot read entry file {source}: {exc}") from None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"line.txt is not valid UTF-8: {exc}") from None
    if text.startswith("\ufeff"):
        raise ValueError(
            "line.txt starts with a UTF-8 byte-order mark, "
            "which would count as an extra character"
        )
    return raw, text


def validate(text: str) -> None:
    """Check the entry against the competition gate, raising ValueError."""
    if not MIN_CHARS <= len(text) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(text)} characters, must be "
            f"{MIN_CHARS}-{MAX_CHARS}"
        )
    if not text.strip():
        raise ValueError("entry is only white space")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")


def first_difference(a: bytes, b: bytes) -> int:
    """Index of the first byte where a and b differ, or the shorter length."""
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


def write_and_verify(raw: bytes, dest: Path) -> None:
    """Write raw bytes to dest, then re-read and verify them byte for byte."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        written = dest.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot write {dest}: {exc}") from None
    if written != raw:
        off = first_difference(written, raw)
        raise ValueError(
            f"verify failed: {dest} differs at byte {off} "
            f"(wrote {len(written)} bytes, expected {len(raw)})"
        )


def main() -> int:
    try:
        raw, text = read_entry(SOURCE)
        validate(text)
        write_and_verify(raw, DEST)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"wrote {len(text)} characters ({len(raw)} bytes) to {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
