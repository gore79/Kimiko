from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List

from app.update.engine import apply_proposal
from app.update.models import ProposalStatus, UpdateProposal
from app.update.store import ProposalStore


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class UpdateManager:
    """
    v1.5 contract enforcer:
    - Proposals are stored on disk
    - Approval is explicit
    - Apply is transactional + rollback
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.state_dir = repo_root / ".kimiko"
        self.proposals_dir = self.state_dir / "proposals"
        self.backups_dir = self.state_dir / "backups"
        self.store = ProposalStore(self.proposals_dir)

        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)

    # --- Query operations ---
    def list(self) -> List[UpdateProposal]:
        return self.store.list()

    def load(self, proposal_id: str) -> UpdateProposal:
        return self.store.load(proposal_id)

    # --- Mutations ---
    def propose(self, proposal: UpdateProposal) -> None:
        proposal.updated_at = _now_iso()
        self.store.save(proposal)

    def approve(self, proposal_id: str) -> UpdateProposal:
        p = self.load(proposal_id)
        if p.status in (ProposalStatus.REJECTED, ProposalStatus.APPLIED):
            raise ValueError(f"Cannot approve proposal in status: {p.status.value}")
        p.status = ProposalStatus.APPROVED
        p.updated_at = _now_iso()
        self.store.save(p)
        return p

    def reject(self, proposal_id: str, notes: str = "") -> UpdateProposal:
        p = self.load(proposal_id)
        if p.status == ProposalStatus.APPLIED:
            raise ValueError("Cannot reject an already applied proposal.")
        p.status = ProposalStatus.REJECTED
        p.notes = notes.strip()
        p.updated_at = _now_iso()
        self.store.save(p)
        return p

    def apply(self, proposal_id: str) -> str:
        p = self.load(proposal_id)
        res = apply_proposal(self.repo_root, self.backups_dir, p)
        if res.ok:
            p.status = ProposalStatus.APPLIED
            p.updated_at = _now_iso()
            self.store.save(p)
        else:
            p.status = ProposalStatus.FAILED
            p.notes = (p.notes + "\n" + res.message).strip()
            p.updated_at = _now_iso()
            self.store.save(p)
        return res.message
