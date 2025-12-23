from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Literal, Optional


class ProposalStatus(str, Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    FAILED = "FAILED"


RiskLevel = Literal["low", "medium", "high"]
UpdateType = Literal["self-update", "self-upgrade"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class FileChange:
    file: str
    action: Literal["create", "modify", "delete"]
    description: str
    # Full-content replacement for v1.5 (simple + safe)
    new_content: Optional[str] = None


@dataclass
class UpdateProposal:
    id: str
    type: UpdateType
    scope: List[str]
    summary: str
    reason: str
    risk_level: RiskLevel = "low"
    requires_restart: bool = True
    rollback_supported: bool = True
    status: ProposalStatus = ProposalStatus.PROPOSED
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    changes: List[FileChange] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @staticmethod
    def from_dict(d: Dict) -> "UpdateProposal":
        return UpdateProposal(
            id=d["id"],
            type=d["type"],
            scope=list(d.get("scope", [])),
            summary=d.get("summary", ""),
            reason=d.get("reason", ""),
            risk_level=d.get("risk_level", "low"),
            requires_restart=bool(d.get("requires_restart", True)),
            rollback_supported=bool(d.get("rollback_supported", True)),
            status=ProposalStatus(d.get("status", "PROPOSED")),
            created_at=d.get("created_at", _now_iso()),
            updated_at=d.get("updated_at", _now_iso()),
            changes=[
                FileChange(
                    file=c["file"],
                    action=c["action"],
                    description=c.get("description", ""),
                    new_content=c.get("new_content"),
                )
                for c in d.get("changes", [])
            ],
            notes=d.get("notes", ""),
        )
