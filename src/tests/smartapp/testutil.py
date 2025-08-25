# vim: set ft=python ts=4 sw=4 expandtab:

"""
Unit test utilities.
"""

from pathlib import Path


def load_file(path: Path) -> str:
    """Load text of a single file as a string."""
    return path.read_text(encoding="utf-8")


def load_dir(path: Path) -> dict[str, str]:
    """Load text of all files in a directory into a dict."""
    return {f.name: f.read_text(encoding="utf-8") for f in path.iterdir() if f.is_file()}
