from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Dict


ProposalPermissionStatus = Literal["ALLOWED", "DENIED"]


@dataclass(frozen=True)
class ProposalPermissionReport:
    allowed: bool
    status: ProposalPermissionStatus
    reasons: List[str]


def evaluate_proposal_permission(
    *,
    readiness: Dict,
    diagnostics: Dict,
    snapshot: Dict,
) -> ProposalPermissionReport:
    reasons: List[str] = []

    # -----------------------------
    # Gate 1 — Readiness
    # -----------------------------
    if readiness.get("status") != "READY":
        reasons.append("Readiness status is not READY")

    if reasons:
        return ProposalPermissionReport(
            allowed=False,
            status="DENIED",
            reasons=reasons,
        )

    # -----------------------------
    # Gate 2 — Diagnostics
    # -----------------------------
    if diagnostics.get("overall") != "OK":
        return ProposalPermissionReport(
            allowed=False,
            status="DENIED",
            reasons=["Diagnostics status is not OK"],
        )

    # -----------------------------
    # Gate 3 — Governance Cleanliness
    # -----------------------------
    governance = snapshot.get("governance", {})

    if governance.get("pending_update_proposals"):
        return ProposalPermissionReport(
            allowed=False,
            status="DENIED",
            reasons=["Pending update proposals exist"],
        )

    if governance.get("pending_memory_proposals"):
        return ProposalPermissionReport(
            allowed=False,
            status="DENIED",
            reasons=["Pending memory proposals exist"],
        )

    # -----------------------------
    # Gate 4 — Human Context (Stub)
    # -----------------------------
    # Future: explicit proposal window or user request
    # For now, this gate always passes

    # -----------------------------
    # ALLOWED
    # -----------------------------
    return ProposalPermissionReport(
        allowed=True,
        status="ALLOWED",
        reasons=["All proposal permission gates passed"],
    )
