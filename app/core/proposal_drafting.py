from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class ProposalDraft:
    draft_id: str
    title: str
    timestamp: float
    label: str
    justification: str
    governance_check: Dict[str, str]
    proposed_change: str
    risks: List[str]
    impact: str
    compliance: str
    disclaimer: str


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

    now = time.time()

    return ProposalDraft(
        draft_id=f"draft-{int(now)}",
        title="Placeholder Proposal Draft",
        timestamp=now,
        label="DRAFT — NOT SUBMITTED",
        justification=(
            "This draft exists to validate the governed proposal drafting pipeline. "
            "No concrete change is proposed."
        ),
        governance_check={
            "readiness": readiness.get("status", "UNKNOWN"),
            "permission": permission.get("status", "UNKNOWN"),
            "diagnostics": diagnostics.get("overall", "UNKNOWN"),
        },
        proposed_change=(
            "No change proposed. This is a structural draft only."
        ),
        risks=[
            "Draft content is placeholder only",
            "No real system change described",
        ],
        impact="No impact. Review-only draft.",
        compliance=(
            "Complies with Phase D½ system invariants and Phase E1 draft contract."
        ),
        disclaimer=(
            "This proposal is informational only. "
            "It has no effect unless explicitly approved and applied by a human."
        ),
    )


def proposal_draft_to_json(draft: ProposalDraft) -> Dict:
    """
    Convert a ProposalDraft to a JSON-serializable dict.
    """
    return asdict(draft)
