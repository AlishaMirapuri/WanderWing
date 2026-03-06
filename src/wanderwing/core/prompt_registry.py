"""
Prompt Version Registry for WanderWing.

SHA256-based prompt version store with SQLite persistence.
Tracks prompt changes over time, supports diffs, and enables
eval-driven prompt development.

Standalone module — creates its own SQLAlchemy engine and does NOT
import wanderwing.db to avoid the email-validator dependency chain.

Usage:
    from wanderwing.core.prompt_registry import prompt_registry

    version = prompt_registry.register("intent_extraction", prompt_text)
    current = prompt_registry.get_current("intent_extraction")
    diff_str = prompt_registry.diff(hash_a, hash_b)
    versions = prompt_registry.register_from_files("src/wanderwing/agents/prompts")
"""

import difflib
import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import sessionmaker

from wanderwing.utils.config import get_settings

# ── Engine (standalone — avoids wanderwing.db import chain) ──────────────────

_settings = get_settings()
_engine = create_engine(
    _settings.database_url,
    connect_args={"check_same_thread": False} if _settings.is_sqlite else {},
)
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

# ── Table definition ──────────────────────────────────────────────────────────

_metadata = MetaData()

_versions_table = Table(
    "prompt_versions",
    _metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(255), nullable=False, index=True),
    Column("content_hash", String(64), nullable=False),
    Column("text", Text, nullable=False),
    Column("version_number", Integer, nullable=False),
    Column("registered_at", DateTime, nullable=False),
)

_metadata.create_all(_engine, checkfirst=True)

# ── Data type ─────────────────────────────────────────────────────────────────


@dataclass
class PromptVersion:
    name: str
    content_hash: str
    text: str
    version_number: int
    registered_at: datetime

    @property
    def hash_prefix(self) -> str:
        return self.content_hash[:8]

    @property
    def line_count(self) -> int:
        return len(self.text.splitlines())


# ── Registry ──────────────────────────────────────────────────────────────────


class PromptRegistry:
    """
    Stores and retrieves prompt versions by SHA256 hash.

    All methods are thread-safe: each call opens and closes its own session.
    """

    def register(self, name: str, text: str) -> PromptVersion:
        """
        Register a prompt version.

        Deduplicates by (name, content_hash) — re-registering the same text
        for the same prompt name returns the existing version without creating
        a new row. Version numbers auto-increment per prompt name.

        Args:
            name: Logical prompt identifier (e.g., "intent_extraction_v2")
            text: Full prompt text

        Returns:
            PromptVersion (new or existing if text unchanged)
        """
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        db = _SessionLocal()
        try:
            # Deduplication: same (name, hash) → return existing
            existing = (
                db.execute(
                    select(_versions_table).where(
                        (_versions_table.c.name == name)
                        & (_versions_table.c.content_hash == content_hash)
                    )
                )
                .mappings()
                .first()
            )

            if existing:
                return PromptVersion(
                    name=existing["name"],
                    content_hash=existing["content_hash"],
                    text=existing["text"],
                    version_number=existing["version_number"],
                    registered_at=existing["registered_at"],
                )

            # Auto-increment version number per prompt name
            latest_version = db.execute(
                select(_versions_table.c.version_number)
                .where(_versions_table.c.name == name)
                .order_by(_versions_table.c.version_number.desc())
                .limit(1)
            ).scalar()
            version_number = (latest_version or 0) + 1

            now = datetime.utcnow()
            db.execute(
                _versions_table.insert().values(
                    name=name,
                    content_hash=content_hash,
                    text=text,
                    version_number=version_number,
                    registered_at=now,
                )
            )
            db.commit()

            return PromptVersion(
                name=name,
                content_hash=content_hash,
                text=text,
                version_number=version_number,
                registered_at=now,
            )
        finally:
            db.close()

    def get_current(self, name: str) -> Optional[PromptVersion]:
        """
        Return the most recent version of a prompt by name, or None.
        """
        db = _SessionLocal()
        try:
            row = (
                db.execute(
                    select(_versions_table)
                    .where(_versions_table.c.name == name)
                    .order_by(_versions_table.c.version_number.desc())
                    .limit(1)
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            return PromptVersion(
                name=row["name"],
                content_hash=row["content_hash"],
                text=row["text"],
                version_number=row["version_number"],
                registered_at=row["registered_at"],
            )
        finally:
            db.close()

    def get_history(self, name: str) -> list[PromptVersion]:
        """
        Return all versions of a prompt, oldest first.
        """
        db = _SessionLocal()
        try:
            rows = (
                db.execute(
                    select(_versions_table)
                    .where(_versions_table.c.name == name)
                    .order_by(_versions_table.c.version_number)
                )
                .mappings()
                .all()
            )
            return [
                PromptVersion(
                    name=r["name"],
                    content_hash=r["content_hash"],
                    text=r["text"],
                    version_number=r["version_number"],
                    registered_at=r["registered_at"],
                )
                for r in rows
            ]
        finally:
            db.close()

    def get_by_hash(self, content_hash: str) -> Optional[PromptVersion]:
        """
        Look up a prompt version by its full SHA256 hash.
        """
        db = _SessionLocal()
        try:
            row = (
                db.execute(
                    select(_versions_table).where(
                        _versions_table.c.content_hash == content_hash
                    )
                )
                .mappings()
                .first()
            )
            if row is None:
                return None
            return PromptVersion(
                name=row["name"],
                content_hash=row["content_hash"],
                text=row["text"],
                version_number=row["version_number"],
                registered_at=row["registered_at"],
            )
        finally:
            db.close()

    def list_all(self) -> list[PromptVersion]:
        """
        Return all registered prompt versions across all prompt names, newest first.
        """
        db = _SessionLocal()
        try:
            rows = (
                db.execute(
                    select(_versions_table).order_by(
                        _versions_table.c.registered_at.desc()
                    )
                )
                .mappings()
                .all()
            )
            return [
                PromptVersion(
                    name=r["name"],
                    content_hash=r["content_hash"],
                    text=r["text"],
                    version_number=r["version_number"],
                    registered_at=r["registered_at"],
                )
                for r in rows
            ]
        finally:
            db.close()

    def diff(self, hash_a: str, hash_b: str) -> str:
        """
        Return a unified diff string between two prompt versions.

        Returns an empty string if either hash is not found or if the texts
        are identical.
        """
        v_a = self.get_by_hash(hash_a)
        v_b = self.get_by_hash(hash_b)
        if v_a is None or v_b is None:
            return ""
        lines_a = v_a.text.splitlines(keepends=True)
        lines_b = v_b.text.splitlines(keepends=True)
        return "".join(
            difflib.unified_diff(
                lines_a,
                lines_b,
                fromfile=f"{v_a.name} v{v_a.version_number} ({v_a.hash_prefix})",
                tofile=f"{v_b.name} v{v_b.version_number} ({v_b.hash_prefix})",
            )
        )

    def register_from_files(self, prompts_dir: str) -> list[PromptVersion]:
        """
        Scan a directory for *.txt prompt files and register each one.

        Uses the filename stem (without extension) as the prompt name.
        Skips __init__.txt and similar non-prompt files.

        Args:
            prompts_dir: Path to directory containing .txt prompt files

        Returns:
            List of registered PromptVersion objects (new or existing)
        """
        path = Path(prompts_dir)
        versions = []
        for txt_file in sorted(path.glob("*.txt")):
            if txt_file.stem.startswith("_"):
                continue
            name = txt_file.stem
            text = txt_file.read_text(encoding="utf-8")
            version = self.register(name, text)
            versions.append(version)
        return versions


# Module-level singleton
prompt_registry = PromptRegistry()
