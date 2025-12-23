from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.memory.proposals import MemoryProposal


class MemoryProposalStore:
    """
    File-based store for memory proposals.
    Stored under .kimiko/memory/proposals/<id>.json
    """

    def __init__(self, repo_root: Path) -> None:
        self.base_dir = repo_root / ".kimiko" / "memory" / "proposals"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, proposal_id: str) -> Path:
        return self.base_dir / f"{proposal_id}.json"

    def save(self, proposal: MemoryProposal) -> None:
        self._path(proposal.id).write_text(
            json.dumps(proposal.to_dict(), indent=2),
            encoding="utf-8",
        )

    def load(self, proposal_id: str) -> MemoryProposal:
        path = self._path(proposal_id)
        if not path.exists():
            raise FileNotFoundError(f"Memory proposal not found: {proposal_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return MemoryProposal.from_dict(data)

    def list(self) -> List[MemoryProposal]:
        proposals: List[MemoryProposal] = []
        for p in self.base_dir.glob("*.json"):
            try:
                proposals.append(
                    MemoryProposal.from_dict(
                        json.loads(p.read_text(encoding="utf-8"))
                    )
                )
            except Exception:
                continue
        return proposals
