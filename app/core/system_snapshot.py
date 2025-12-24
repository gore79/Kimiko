from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any

from app.version import __version__
from app.core.runtime_status import get_runtime_status
from app.core.memory_status import get_memory_status
from app.core.governance_status import get_governance_status
from app.core.capabilities_status import get_capabilities_status
from app.memory.manager import MemoryManager
from app.core.update_manager import UpdateManager


# -----------------------------
# Structured Snapshot Model
# -----------------------------

@dataclass(frozen=True)
class SystemSnapshot:
    runtime: Dict[str, Any]
    memory: Dict[str, Any]
    governance: Dict[str, Any]
    capabilities: Dict[str, Any]


# -----------------------------
# Snapshot Construction
# -----------------------------

def get_system_snapshot(
    *,
    start_time: float,
    update_manager: UpdateManager,
    memory_manager: MemoryManager,
) -> SystemSnapshot:
    runtime_status = get_runtime_status(
        version=__version__,
        start_time=start_time,
    )

    memory_status = get_memory_status(memory_manager)
    governance_status = get_governance_status(update_manager, memory_manager)
    capabilities_status = get_capabilities_status()

    return SystemSnapshot(
        runtime={
            "version": runtime_status.version,
            "uptime_seconds": runtime_status.uptime_seconds,
            "python": runtime_status.python_version,
            "platform": runtime_status.platform,
        },
        memory={
            "backend": memory_status.backend,
            "counts": memory_status.counts,
            "pending_proposals": memory_status.pending_proposals,
        },
        governance={
            "pending_update_proposals": governance_status.pending_update_proposals,
            "pending_memory_proposals": governance_status.pending_memory_proposals,
            "approval_required_for": governance_status.approval_required_for,
            "last_approved_action": governance_status.last_approved_action,
        },
        capabilities={
            "enabled": capabilities_status.enabled,
            "disabled": capabilities_status.disabled,
            "planned": capabilities_status.planned,
        },
    )


# -----------------------------
# Renderers
# -----------------------------

def to_human_readable(snapshot: SystemSnapshot) -> str:
    lines: List[str] = []

    lines.extend([
        "System Snapshot",
        "===============",
        "",
        "Runtime",
        "-------",
        f"Version: {snapshot.runtime['version']}",
        f"Uptime (s): {snapshot.runtime['uptime_seconds']}",
        f"Python: {snapshot.runtime['python']}",
        f"Platform: {snapshot.runtime['platform']}",
        "",
        "Memory",
        "------",
        f"Backend: {snapshot.memory['backend']}",
    ])

    for k, v in snapshot.memory["counts"].items():
        lines.append(f"- {k}: {v}")

    lines.append(f"Pending proposals: {snapshot.memory['pending_proposals']}")
    lines.append("")
    lines.extend([
        "Governance",
        "----------",
        "Pending update proposals:",
    ])

    if snapshot.governance["pending_update_proposals"]:
        for pid in snapshot.governance["pending_update_proposals"]:
            lines.append(f"- {pid}")
    else:
        lines.append("(none)")

    lines.append("")
    lines.append("Pending memory proposals:")
    if snapshot.governance["pending_memory_proposals"]:
        for pid in snapshot.governance["pending_memory_proposals"]:
            lines.append(f"- {pid}")
    else:
        lines.append("(none)")

    lines.append("")
    lines.append("Approval required for:")
    for item in snapshot.governance["approval_required_for"]:
        lines.append(f"- {item}")

    lines.append("")
    if snapshot.governance["last_approved_action"]:
        lines.append(
            f"Last approved action: {snapshot.governance['last_approved_action']}"
        )
    else:
        lines.append("Last approved action: (none)")

    lines.extend([
        "",
        "Capabilities",
        "------------",
        "Enabled:",
    ])

    for c in snapshot.capabilities["enabled"]:
        lines.append(f"- {c}")

    lines.append("Disabled:")
    for c in snapshot.capabilities["disabled"]:
        lines.append(f"- {c}")

    lines.append("Planned:")
    for c in snapshot.capabilities["planned"]:
        lines.append(f"- {c}")

    return "\n".join(lines)


def to_json(snapshot: SystemSnapshot) -> Dict[str, Any]:
    """
    Pure machine-readable snapshot.
    No formatting. No side effects.
    """
    return {
        "runtime": snapshot.runtime,
        "memory": snapshot.memory,
        "governance": snapshot.governance,
        "capabilities": snapshot.capabilities,
    }
