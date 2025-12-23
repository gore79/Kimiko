from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.update.models import UpdateProposal


class ProposalStore:
    """
    File-based proposal store.
    One JSON file per proposal under .kimiko/proposals/<id>.json
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, proposal_id: str) -> Path:
        return self.base_dir / f"{proposal_id}.json"

    def save(self, proposal: UpdateProposal) -> None:
        path = self._path(proposal.id)
        path.write_text(
            json.dumps(proposal.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self, proposal_id: str) -> UpdateProposal:
        path = self._path(proposal_id)
        if not path.exists():
            raise FileNotFoundError(f"Proposal not found: {proposal_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return UpdateProposal.from_dict(data)

    def list_ids(self) -> List[str]:
        if not self.base_dir.exists():
            return []
        return sorted(p.stem for p in self.base_dir.glob("*.json"))

    def list(self) -> List[UpdateProposal]:
        items: List[UpdateProposal] = []
        for pid in self.list_ids():
            try:
                items.append(self.load(pid))
            except Exception:
                # Corrupted proposal files are skipped, not fatal
                continue
        return items

    def exists(self, proposal_id: str) -> bool:
        return self._path(proposal_id).exists()
