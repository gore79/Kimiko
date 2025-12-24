from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.memory.manager import MemoryManager
from app.memory.models import MemoryCategory


@dataclass(frozen=True)
class MemoryStatus:
    backend: str
    counts: Dict[str, int]
    pending_proposals: int


def get_memory_status(mm: MemoryManager) -> MemoryStatus:
    # Determine backend type (local vs HF)
    backend = mm.store.__class__.__name__

    # Count stored memory records by category
    counts: Dict[str, int] = {}
    for category in MemoryCategory:
        try:
            items = mm.list_memory(category)
            counts[category.value] = len(items)
        except Exception:
            counts[category.value] = 0

    # Count ONLY proposals that are truly pending (PROPOSED)
    pending = 0
    for proposal in mm.list_proposals():
        status = getattr(proposal.status, "value", None)
        if status == "PROPOSED":
            pending += 1

    return MemoryStatus(
        backend=backend,
        counts=counts,
        pending_proposals=pending,
    )


def to_human_readable(ms: MemoryStatus) -> str:
    lines = [
        "Memory Status",
        "-------------",
        f"Backend: {ms.backend}",
        "",
        "Record counts:",
    ]

    for k, v in ms.counts.items():
        lines.append(f"- {k}: {v}")

    lines.append("")
    lines.append(f"Pending memory proposals: {ms.pending_proposals}")

    return "\n".join(lines)
