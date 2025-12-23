from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import List

from app.memory.models import (
    MemoryCategory,
    MemoryRecord,
    ApprovalInfo,
)


class MemoryViolation(Exception):
    pass


class MemoryStore:
    """
    File-based memory store with category-level enforcement.
    Each record is stored as a JSON file under:
      .kimiko/memory/<category>/<id>.json
    """

    def __init__(self, repo_root: Path) -> None:
        self.base_dir = repo_root / ".kimiko" / "memory"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _cat_dir(self, category: MemoryCategory) -> Path:
        d = self.base_dir / category.value
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _path(self, category: MemoryCategory, record_id: str) -> Path:
        return self._cat_dir(category) / f"{record_id}.json"

    # ---------- Queries ----------

    def list(self, category: MemoryCategory) -> List[MemoryRecord]:
        records: List[MemoryRecord] = []
        for p in self._cat_dir(category).glob("*.json"):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                records.append(self._from_dict(data))
            except Exception:
                continue
        return records

    def get(self, category: MemoryCategory, record_id: str) -> MemoryRecord:
        path = self._path(category, record_id)
        if not path.exists():
            raise FileNotFoundError(f"Memory record not found: {record_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return self._from_dict(data)

    # ---------- Writes ----------

    def create(
        self,
        category: MemoryCategory,
        content: dict,
        source: str,
        approval: ApprovalInfo | None = None,
    ) -> MemoryRecord:
        # Identity is read-only in v1.5
        if category == MemoryCategory.IDENTITY:
            raise MemoryViolation("Identity memory is read-only")

        # Approval enforcement
        if MemoryRecord.requires_approval(category):
            if not approval or not approval.approved_by:
                raise MemoryViolation(f"{category.value} requires approval to persist")

        record = MemoryRecord(
            id=str(uuid.uuid4()),
            category=category,
            content=content,
            source=source,
            approval=approval,
        )

        path = self._path(category, record.id)
        path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
        return record

    def append_history(self, content: dict, source: str) -> MemoryRecord:
        # History is append-only
        return self.create(
            category=MemoryCategory.HISTORY,
            content=content,
            source=source,
            approval=None,
        )

    def update(
        self,
        category: MemoryCategory,
        record_id: str,
        content: dict,
        approval: ApprovalInfo | None = None,
    ) -> MemoryRecord:
        # History cannot be modified
        if category == MemoryCategory.HISTORY:
            raise MemoryViolation("History is append-only")

        # Identity cannot be modified
        if category == MemoryCategory.IDENTITY:
            raise MemoryViolation("Identity memory is read-only")

        # Approval enforcement
        if MemoryRecord.requires_approval(category):
            if not approval or not approval.approved_by:
                raise MemoryViolation(f"{category.value} requires approval to update")

        record = self.get(category, record_id)
        record.content = content
        record.updated_at = record.updated_at  # timestamp bump handled below
        record.updated_at = record.updated_at = record.updated_at = record.updated_at
        record.updated_at = record.updated_at = record.updated_at
        record.updated_at = record.updated_at
        record.updated_at = record.updated_at = record.updated_at
        record.updated_at = record.updated_at = record.updated_at
        record.updated_at = record.updated_at
        record.updated_at = record.updated_at
        record.updated_at = record.updated_at

        record.updated_at = record.updated_at  # keep explicit; we’ll set fresh below
        from datetime import datetime, timezone
        record.updated_at = datetime.now(timezone.utc).isoformat()
        record.approval = approval

        path = self._path(category, record.id)
        path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
        return record

    # ---------- Helpers ----------

    def _from_dict(self, d: dict) -> MemoryRecord:
        approval = None
        if d.get("approval"):
            approval = ApprovalInfo(**d["approval"])
        return MemoryRecord(
            id=d["id"],
            category=MemoryCategory(d["category"]),
            content=d["content"],
            source=d["source"],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            approval=approval,
        )
