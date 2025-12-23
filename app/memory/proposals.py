from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from app.memory.models import MemoryCategory


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryProposalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    FAILED = "FAILED"


@dataclass
class MemoryProposal:
    id: str
    category: MemoryCategory
    content: Dict
    reason: str
    source: str  # "kimiko" | "user"
    status: MemoryProposalStatus = MemoryProposalStatus.PROPOSED
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    notes: str = ""

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["category"] = self.category.value
        d["status"] = self.status.value
        return d

    @staticmethod
    def from_dict(d: Dict) -> "MemoryProposal":
        return MemoryProposal(
            id=d["id"],
            category=MemoryCategory(d["category"]),
            content=d["content"],
            reason=d["reason"],
            source=d["source"],
            status=MemoryProposalStatus(d["status"]),
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            notes=d.get("notes", ""),
        )
