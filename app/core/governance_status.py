from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.core.update_manager import UpdateManager
from app.memory.manager import MemoryManager


@dataclass(frozen=True)
class GovernanceStatus:
    pending_update_proposals: List[str]
    pending_memory_proposals: List[str]
    approval_required_for: List[str]
    last_approved_action: Optional[str]


def get_governance_status(
    um: UpdateManager, mm: MemoryManager
) -> GovernanceStatus:
    # Pending update proposals
    updates = [
        p.id for p in um.list()
        if p.status.value == "PROPOSED"
    ]

    # Pending memory proposals
    memories = [
        p.id for p in mm.list_proposals()
        if p.status.value == "PROPOSED"
    ]

    approval_required_for = [
        "self-update",
        "self-upgrade",
        "memory write",
    ]

    # Best-effort last approved action
    last_action = None
    approved_updates = [
        p for p in um.list()
        if p.status.value == "APPROVED"
    ]
    if approved_updates:
        approved_updates.sort(key=lambda p: p.created_at)
        last = approved_updates[-1]
        last_action = f"update {last.id}"

    return GovernanceStatus(
        pending_update_proposals=updates,
        pending_memory_proposals=memories,
        approval_required_for=approval_required_for,
        last_approved_action=last_action,
    )


def to_human_readable(gs: GovernanceStatus) -> str:
    lines = [
        "Governance Status",
        "-----------------",
        "",
        "Pending update proposals:",
    ]

    if gs.pending_update_proposals:
        for pid in gs.pending_update_proposals:
            lines.append(f"- {pid}")
    else:
        lines.append("(none)")

    lines.append("")
    lines.append("Pending memory proposals:")
    if gs.pending_memory_proposals:
        for pid in gs.pending_memory_proposals:
            lines.append(f"- {pid}")
    else:
        lines.append("(none)")

    lines.append("")
    lines.append("Approval required for:")
    for item in gs.approval_required_for:
        lines.append(f"- {item}")

    lines.append("")
    if gs.last_approved_action:
        lines.append(f"Last approved action: {gs.last_approved_action}")
    else:
        lines.append("Last approved action: (none)")

    return "\n".join(lines)
