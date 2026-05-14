"""Local file storage for manuscript attachments.

A thin backend that writes bytes under a configured root directory.
Placeholder attachment records bypass storage entirely.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from app.config import settings


_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def safe_filename(name: str | None) -> str:
    if not name:
        return "file"
    cleaned = _SAFE.sub("-", name).strip("-")
    return cleaned or "file"


@dataclass
class StoredFile:
    storage_key: str
    size_bytes: int
    sha256: str


class LocalFileStorage:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / key

    def path_for(self, key: str) -> Path:
        return self._path(key)

    def exists(self, key: str) -> bool:
        if key.startswith("placeholder:"):
            return False
        return self._path(key).is_file()

    def write(self, key: str, stream: BinaryIO) -> StoredFile:
        target = self._path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        with target.open("wb") as fh:
            while chunk := stream.read(64 * 1024):
                size += len(chunk)
                digest.update(chunk)
                fh.write(chunk)
        return StoredFile(storage_key=key, size_bytes=size, sha256=digest.hexdigest())

    def delete(self, key: str) -> None:
        if key.startswith("placeholder:"):
            return
        path = self._path(key)
        if path.is_file():
            path.unlink()


_storage: LocalFileStorage | None = None


def get_storage() -> LocalFileStorage:
    """Module-level cached storage backend, configured from settings."""
    global _storage
    if _storage is None:
        _storage = LocalFileStorage(settings.storage_path)
    return _storage
