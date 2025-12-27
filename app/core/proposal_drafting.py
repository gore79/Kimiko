from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ProposalDraft:
    draft_id: str
    title: str
    timestamp: float
    justification: str
    governance_check: Dict[str, str]
    proposed_change: str
    risks: List[str]
    impact: str
    compliance: str


def generate_proposal_draft(
    *,
    snapshot: Dict,
    diagnostics: Dict,
    readiness: Dict,
    permission: Dict,
) -> ProposalDraft:
    """
    Generate a read-only proposal draft.

    Preconditions (enforced by caller):
    - readiness.status == READY
    - permission.allowed == True
    """

    draft_id = f"draft-{int(time.time())}"

    return ProposalDraft(
        draft_id=draft_id,
        title="Placeholder Proposal Draft",
        timestamp=time.time(),
        justification=(
            "This is a placeholder draft. "
            "No concrete proposal content has been generated yet."
        ),
        governance_check={
            "readiness": readiness.get("status", "UNKNOWN"),
            "permission": permission.get("status", "UNKNOWN"),
            "diagnostics": diagnostics.get("overall", "UNKNOWN"),
        },
        proposed_change=(
            "No change is proposed at this stage. "
            "This draft exists only to validate the drafting pipeline."
        ),
        risks=[
            "Draft content is placeholder only",
            "No real change described",
        ],
        impact="No impact. Draft-only validation.",
        compliance=(
            "This draft complies with Phase D½ invariants. "
            "It is informational only and has no effect unless explicitly approved."
        ),
    )
