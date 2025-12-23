from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

from app.update.guardrails import validate_proposal, GuardrailViolation
from app.update.models import ProposalStatus, UpdateProposal


@dataclass
class ApplyResult:
    ok: bool
    message: str
    backup_dir: Path | None = None


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run_healthcheck() -> Tuple[bool, str]:
    try:
        cp = subprocess.run(
            ["python", "-m", "app.cli_main", "--health"],
            check=False,
            capture_output=True,
            text=True,
        )
        out = (cp.stdout or "") + (cp.stderr or "")
        if cp.returncode == 0:
            return True, out.strip()
        return False, out.strip() or f"Health check failed with code {cp.returncode}"
    except Exception as e:
        return False, f"Health check exception: {e}"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _backup_files(repo_root: Path, backup_dir: Path, files: List[str]) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    for rel in files:
        src = repo_root / rel
        dst = backup_dir / rel
        _ensure_parent(dst)
        if src.exists():
            shutil.copy2(src, dst)
        else:
            dst.write_text("", encoding="utf-8")


def _restore_backup(repo_root: Path, backup_dir: Path) -> None:
    for src in backup_dir.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(backup_dir)
        dst = repo_root / rel
        _ensure_parent(dst)
        content = src.read_bytes()
        dst.write_bytes(content)


def apply_proposal(repo_root: Path, backups_root: Path, proposal: UpdateProposal) -> ApplyResult:
    try:
        validate_proposal(proposal)
    except GuardrailViolation as e:
        return ApplyResult(False, f"Blocked by guardrails: {e}")

    if proposal.status != ProposalStatus.APPROVED:
        return ApplyResult(False, f"Proposal must be APPROVED before apply. Current: {proposal.status.value}")

    files_to_backup = sorted(set([*proposal.scope, *[c.file for c in proposal.changes]]))
    backup_dir = backups_root / f"{proposal.id}-{_utc_stamp()}"
    _backup_files(repo_root, backup_dir, files_to_backup)

    try:
        for ch in proposal.changes:
            path = repo_root / ch.file

            if ch.action == "delete":
                if path.exists():
                    path.unlink()
                continue

            _ensure_parent(path)
            path.write_text(ch.new_content or "", encoding="utf-8")

        ok, msg = _run_healthcheck()
        if not ok:
            _restore_backup(repo_root, backup_dir)
            return ApplyResult(False, f"Post-update health check failed; rolled back.\n{msg}", backup_dir=backup_dir)

        return ApplyResult(True, "Update applied successfully and health check passed.", backup_dir=backup_dir)

    except Exception as e:
        _restore_backup(repo_root, backup_dir)
        return ApplyResult(False, f"Apply failed with exception; rolled back. {e}", backup_dir=backup_dir)
