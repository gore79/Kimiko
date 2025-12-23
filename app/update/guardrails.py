from __future__ import annotations

from app.update.models import UpdateProposal


PROTECTED_PREFIXES = (
    "app/update/",        # bootstrap protection
    ".kimiko/",           # internal state is never self-modified
)

DISALLOWED_FILES = (
    "app/cli_main.py",    # entrypoint is protected in v1.5
)

ALLOWED_ACTIONS = {"create", "modify", "delete"}


class GuardrailViolation(Exception):
    pass


def _norm(p: str) -> str:
    return p.replace("\\", "/").lstrip("./")


def validate_proposal(proposal: UpdateProposal) -> None:
    # Must support rollback in v1.5
    if not proposal.rollback_supported:
        raise GuardrailViolation("rollback_supported must be true in v1.5")

    # Required fields
    if not proposal.summary.strip():
        raise GuardrailViolation("summary is required")
    if not proposal.reason.strip():
        raise GuardrailViolation("reason is required")
    if not proposal.scope:
        raise GuardrailViolation("scope must list affected files")

    # Scope checks
    for s in proposal.scope:
        ns = _norm(s)
        if any(ns.startswith(pref) for pref in PROTECTED_PREFIXES):
            raise GuardrailViolation(f"Scope touches protected area: {s}")
        if ns in DISALLOWED_FILES:
            raise GuardrailViolation(f"Scope touches disallowed file: {s}")

    # Change checks
    for ch in proposal.changes:
        nf = _norm(ch.file)

        if ch.action not in ALLOWED_ACTIONS:
            raise GuardrailViolation(f"Invalid action {ch.action} for {ch.file}")

        if any(nf.startswith(pref) for pref in PROTECTED_PREFIXES):
            raise GuardrailViolation(f"Change touches protected area: {ch.file}")
        if nf in DISALLOWED_FILES:
            raise GuardrailViolation(f"Change touches disallowed file: {ch.file}")

        if ch.action in ("create", "modify") and ch.new_content is None:
            raise GuardrailViolation(f"{ch.action} requires new_content for {ch.file}")
