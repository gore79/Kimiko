from __future__ import annotations

import time
from pathlib import Path
from typing import List

from app.memory.models import (
    MemoryCategory,
    ApprovalInfo,
)
from app.memory.store import MemoryStore, MemoryViolation
from app.memory.proposals import MemoryProposal, MemoryProposalStatus
from app.memory.proposal_store import MemoryProposalStore


class MemoryManager:
    """
    v1.5 Memory enforcement layer.
    Implements:
      - Proposal → approval → persistence for facts/preferences
      - Direct-write for projects
      - Append-only history
      - Read-only identity
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.store = MemoryStore(repo_root)
        self.proposals = MemoryProposalStore(repo_root)

    # ---------- Proposals ----------

    def propose(
        self,
        category: MemoryCategory,
        content: dict,
        reason: str,
        source: str = "kimiko",
    ) -> MemoryProposal:
        if not MemoryCategory(category):
            raise ValueError("Invalid memory category")

        if category not in (MemoryCategory.FACTS, MemoryCategory.PREFERENCES):
            raise MemoryViolation(
                f"{category.value} does not accept proposals in v1.5"
            )

        proposal = MemoryProposal(
            id=f"mem-{int(time.time())}",
            category=category,
            content=content,
            reason=reason,
            source=source,
        )
        self.proposals.save(proposal)
        return proposal

    def list_proposals(self) -> List[MemoryProposal]:
        return self.proposals.list()

    def approve(self, proposal_id: str, approved_by: str) -> MemoryProposal:
        p = self.proposals.load(proposal_id)
        p.status = MemoryProposalStatus.APPROVED
        p.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.proposals.save(p)

        approval = ApprovalInfo(
            required=True,
            approved_by=approved_by,
            approved_at=p.updated_at,
        )

        # Persist into memory store
        self.store.create(
            category=p.category,
            content=p.content,
            source=p.source,
            approval=approval,
        )

        p.status = MemoryProposalStatus.APPLIED
        self.proposals.save(p)
        return p

    def reject(self, proposal_id: str, notes: str = "") -> MemoryProposal:
        p = self.proposals.load(proposal_id)
        p.status = MemoryProposalStatus.REJECTED
        p.notes = notes
        p.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.proposals.save(p)
        return p

    # ---------- Direct memory writes ----------

    def write_project(self, content: dict, source: str = "kimiko"):
        return self.store.create(
            category=MemoryCategory.PROJECTS,
            content=content,
            source=source,
            approval=None,
        )

    def append_history(self, content: dict, source: str = "system"):
        return self.store.append_history(
            content=content,
            source=source,
        )

    # ---------- Reads ----------

    def list_memory(self, category: MemoryCategory):
        return self.store.list(category)
