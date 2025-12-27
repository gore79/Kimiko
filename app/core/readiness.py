from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Dict


ReadinessStatus = Literal["READY", "NOT_READY", "BLOCKED"]


@dataclass(frozen=True)
class ReadinessReport:
    ready: bool
    status: ReadinessStatus
    reasons: List[str]


FORBIDDEN_CAPABILITIES = {
    "internet access",
    "command execution",
    "self-modification without approval",
}


def evaluate_readiness(
    *,
    snapshot: Dict,
    diagnostics: Dict,
) -> ReadinessReport:
    reasons: List[str] = []

    # -----------------------------
    # Gate 1 — Governance (BLOCKED)
    # -----------------------------
    governance = snapshot.get("governance", {})

    if governance.get("pending_update_proposals"):
        reasons.append("Pending update proposals exist")

    if governance.get("pending_memory_proposals"):
        reasons.append("Pending memory proposals exist")

    if governance.get("approval_required_for"):
        reasons.append("Governance approval required")

    if reasons:
        return ReadinessReport(
            ready=False,
            status="BLOCKED",
            reasons=reasons,
        )

    # -----------------------------
    # Gate 2 — Capability Safety (BLOCKED)
    # -----------------------------
    capabilities = snapshot.get("capabilities", {})
    enabled = set(capabilities.get("enabled", []))
    violations = FORBIDDEN_CAPABILITIES.intersection(enabled)

    if violations:
        return ReadinessReport(
            ready=False,
            status="BLOCKED",
            reasons=[f"Forbidden capability enabled: {v}" for v in violations],
        )

    # -----------------------------
    # Gate 3 — Diagnostics (NOT_READY)
    # -----------------------------
    if diagnostics.get("overall") != "OK":
        return ReadinessReport(
            ready=False,
            status="NOT_READY",
            reasons=["Diagnostics status is not OK"],
        )

    # -----------------------------
    # READY
    # -----------------------------
    return ReadinessReport(
        ready=True,
        status="READY",
        reasons=["All readiness gates passed"],
    )
