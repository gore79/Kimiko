from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryCategory(str, Enum):
    IDENTITY = "identity"
    PREFERENCES = "preferences"
    FACTS = "facts"
    PROJECTS = "projects"
    HISTORY = "history"


# Categories that require explicit human approval before persistence
APPROVAL_REQUIRED = {
    MemoryCategory.PREFERENCES,
    MemoryCategory.FACTS,
}

# Categories Kimiko can write to directly
DIRECT_WRITE_ALLOWED = {
    MemoryCategory.PROJECTS,
    MemoryCategory.HISTORY,
}


@dataclass
class ApprovalInfo:
    required: bool
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None


@dataclass
class MemoryRecord:
    id: str
    category: MemoryCategory
    content: Dict[str, Any]
    source: str  # "user" | "kimiko" | "system"
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    approval: Optional[ApprovalInfo] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        if self.approval:
            d["approval"] = asdict(self.approval)
        return d

    @staticmethod
    def requires_approval(category: MemoryCategory) -> bool:
        return category in APPROVAL_REQUIRED

    @staticmethod
    def allows_direct_write(category: MemoryCategory) -> bool:
        return category in DIRECT_WRITE_ALLOWED
