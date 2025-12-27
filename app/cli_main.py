from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.version import __version__
from app.core.update_manager import UpdateManager
from app.update.models import FileChange, UpdateProposal

from app.memory.manager import MemoryManager
from app.memory.models import MemoryCategory

from app.core.runtime_status import get_runtime_status, to_human_readable as runtime_hr
from app.core.memory_status import get_memory_status, to_human_readable as memory_hr
from app.core.governance_status import get_governance_status, to_human_readable as governance_hr
from app.core.capabilities_status import get_capabilities_status, to_human_readable as capabilities_hr
from app.core.system_snapshot import (
    get_system_snapshot,
    to_human_readable as snapshot_hr,
    to_json as snapshot_json,
)
from app.core.diagnostics import run_diagnostics, diagnostics_to_json
from app.core.readiness import evaluate_readiness
from app.core.proposal_permissions import evaluate_proposal_permission
from app.core.proposal_drafting import (
    generate_proposal_draft,
    proposal_draft_to_json,
)


START_TIME = time.time()


@dataclass
class RuntimeState:
    repo_root: Path
    update_manager: UpdateManager
    memory_manager: MemoryManager


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _print_help() -> None:
    print(
        "Kimiko CLI (approval-based learning ENABLED)\n"
        "Commands:\n"
        "  help\n"
        "  version\n"
        "  snapshot [--json]\n"
        "  diagnostics [--json]\n"
        "  readiness\n"
        "  propose-check\n"
        "  propose-draft [--json]\n"
        "  status [runtime|memory|governance|capabilities]\n"
        "  quit | exit\n"
        "\n"
        "Update system:\n"
        "  update propose-demo\n"
        "  update list\n"
        "  update show <id>\n"
        "  update approve <id>\n"
        "  update reject <id> [note]\n"
        "  update apply <id>\n"
        "\n"
        "Memory system:\n"
        "  memory propose <facts|preferences> <reason> <json>\n"
        "  memory proposals\n"
        "  memory approve <id>\n"
        "  memory reject <id> [note]\n"
        "  memory list <identity|facts|preferences|projects|history>\n"
    )


def _cmd_version() -> None:
    print(f"Kimiko v{__version__}")


def _cmd_snapshot(state: RuntimeState, parts: list[str]) -> None:
    as_json = "--json" in parts

    snapshot = get_system_snapshot(
        start_time=START_TIME,
        update_manager=state.update_manager,
        memory_manager=state.memory_manager,
    )

    if as_json:
        print(json.dumps(snapshot_json(snapshot), indent=2))
    else:
        print(snapshot_hr(snapshot))


def _cmd_diagnostics(state: RuntimeState, parts: list[str]) -> None:
    as_json = "--json" in parts

    snapshot = get_system_snapshot(
        start_time=START_TIME,
        update_manager=state.update_manager,
        memory_manager=state.memory_manager,
    )

    report = run_diagnostics(snapshot)

    if as_json:
        print(json.dumps(diagnostics_to_json(report), indent=2))
        return

    print("System Diagnostics")
    print("==================")
    print(f"Overall Health: {report.overall}")
    print("")
    print("Subsystems:")

    for result in report.results:
        print(f"- {result.name}: {result.status}")

    print("")
    print(report.recommendation)


def _cmd_readiness(state: RuntimeState) -> None:
    snapshot = get_system_snapshot(
        start_time=START_TIME,
        update_manager=state.update_manager,
        memory_manager=state.memory_manager,
    )

    diagnostics = diagnostics_to_json(run_diagnostics(snapshot))

    report = evaluate_readiness(
        snapshot=snapshot_json(snapshot),
        diagnostics=diagnostics,
    )

    print("System Readiness")
    print("================")
    print(f"Ready for action: {'YES' if report.ready else 'NO'}")
    print(f"Status: {report.status}")
    print("")

    if report.reasons:
        if report.status == "BLOCKED":
            print("Blocking reasons:")
        else:
            print("Reasons:")
        for r in report.reasons:
            print(f"- {r}")
    else:
        print("No blocking conditions detected.")

    print("")
    print("Action remains blocked.")


def _cmd_propose_check(state: RuntimeState) -> None:
    snapshot = get_system_snapshot(
        start_time=START_TIME,
        update_manager=state.update_manager,
        memory_manager=state.memory_manager,
    )

    diagnostics = diagnostics_to_json(run_diagnostics(snapshot))
    readiness = {
        "status": evaluate_readiness(
            snapshot=snapshot_json(snapshot),
            diagnostics=diagnostics,
        ).status
    }

    report = evaluate_proposal_permission(
        readiness=readiness,
        diagnostics=diagnostics,
        snapshot=snapshot_json(snapshot),
    )

    print("Proposal Permission Check")
    print("=========================")
    print(f"Allowed to propose: {'YES' if report.allowed else 'NO'}")
    print(f"Status: {report.status}")
    print("")

    if report.reasons:
        print("Reasons:")
        for r in report.reasons:
            print(f"- {r}")

    print("")
    print("No proposal generated.")


def _cmd_propose_draft(state: RuntimeState, parts: list[str]) -> None:
    as_json = "--json" in parts

    snapshot_obj = get_system_snapshot(
        start_time=START_TIME,
        update_manager=state.update_manager,
        memory_manager=state.memory_manager,
    )
    snapshot = snapshot_json(snapshot_obj)

    diagnostics = diagnostics_to_json(run_diagnostics(snapshot_obj))

    readiness_report = evaluate_readiness(
        snapshot=snapshot,
        diagnostics=diagnostics,
    )

    permission = evaluate_proposal_permission(
        readiness={"status": readiness_report.status},
        diagnostics=diagnostics,
        snapshot=snapshot,
    )

    if not permission.allowed:
        print("Proposal Draft")
        print("==============")
        print("Draft generation denied.")
        print("")
        for r in permission.reasons:
            print(f"- {r}")
        print("")
        print("No draft generated.")
        return

    draft = generate_proposal_draft(
        snapshot=snapshot,
        diagnostics=diagnostics,
        readiness={"status": readiness_report.status},
        permission={
            "status": permission.status,
            "allowed": permission.allowed,
        },
    )

    if as_json:
        print(json.dumps(proposal_draft_to_json(draft), indent=2))
        return

    print("Proposal Draft — NOT SUBMITTED")
    print("==============================")
    print(f"Draft ID: {draft.draft_id}")
    print(f"Title: {draft.title}")
    print("")
    print("Justification:")
    print(draft.justification)
    print("")
    print("Governance Check:")
    for k, v in draft.governance_check.items():
        print(f"- {k}: {v}")
    print("")
    print("Proposed Change:")
    print(draft.proposed_change)
    print("")
    print("Risks & Unknowns:")
    for r in draft.risks:
        print(f"- {r}")
    print("")
    print("Impact:")
    print(draft.impact)
    print("")
    print("Compliance:")
    print(draft.compliance)
    print("")
    print("Disclaimer:")
    print(draft.disclaimer)


# ---------------- Status Commands ----------------

def _cmd_status(state: RuntimeState, parts: list[str]) -> None:
    if len(parts) == 1:
        print(
            "Status available. Try:\n"
            "  status runtime\n"
            "  status memory\n"
            "  status governance\n"
            "  status capabilities"
        )
        return

    sub = parts[1].lower()

    if sub == "runtime":
        rs = get_runtime_status(version=__version__, start_time=START_TIME)
        print(runtime_hr(rs))
        return

    if sub == "memory":
        ms = get_memory_status(state.memory_manager)
        print(memory_hr(ms))
        return

    if sub == "governance":
        gs = get_governance_status(state.update_manager, state.memory_manager)
        print(governance_hr(gs))
        return

    if sub == "capabilities":
        cs = get_capabilities_status()
        print(capabilities_hr(cs))
        return

    print("Unknown status command")


# ---------------- Update Commands ----------------

def _handle_update(state: RuntimeState, parts: list[str]) -> None:
    um = state.update_manager

    if len(parts) < 2:
        print("Usage: update <subcommand>")
        return

    sub = parts[1].lower()

    if sub == "list":
        items = um.list()
        if not items:
            print("(no proposals)")
            return
        for p in items:
            print(f"- {p.id} [{p.status.value}] {p.summary}")
        return

    if sub == "show":
        if len(parts) < 3:
            print("Usage: update show <id>")
            return
        print(um.load(parts[2]))
        return

    if sub == "approve":
        if len(parts) < 3:
            print("Usage: update approve <id>")
            return
        um.approve(parts[2])
        print("Approved.")
        return

    if sub == "reject":
        if len(parts) < 3:
            print("Usage: update reject <id> [note]")
            return
        note = " ".join(parts[3:]) if len(parts) > 3 else ""
        um.reject(parts[2], note)
        print("Rejected.")
        return

    if sub == "apply":
        if len(parts) < 3:
            print("Usage: update apply <id>")
            return
        print(um.apply(parts[2]))
        return

    if sub == "propose-demo":
        p = UpdateProposal(
            id=f"update-{int(time.time())}",
            type="self-update",
            scope=["app/version.py"],
            summary="Demo patch bump",
            reason="Verify update system",
            changes=[
                FileChange(
                    file="app/version.py",
                    action="modify",
                    description="Patch bump",
                    new_content='__version__ = "1.5.2"\n',
                )
            ],
        )
        um.propose(p)
        print(f"Proposed {p.id}")
        return

    print("Unknown update command")


# ---------------- Memory Commands ----------------

def _handle_memory(state: RuntimeState, parts: list[str]) -> None:
    mm = state.memory_manager

    if len(parts) < 2:
        print("Usage: memory <subcommand>")
        return

    sub = parts[1].lower()

    try:
        if sub == "proposals":
            items = mm.list_proposals()
            if not items:
                print("(no memory proposals)")
                return
            for p in items:
                print(f"- {p.id} [{p.status.value}] {p.category.value}: {p.reason}")
            return

        if sub == "propose":
            if len(parts) < 5:
                print("Usage: memory propose <facts|preferences> <reason> <json>")
                return
            category = MemoryCategory(parts[2])
            reason = parts[3]
            content = json.loads(" ".join(parts[4:]))
            p = mm.propose(category, content, reason)
            print(f"Proposed memory {p.id}")
            return

        if sub == "approve":
            if len(parts) < 3:
                print("Usage: memory approve <id>")
                return
            p = mm.approve(parts[2], approved_by="Brandon")
            print(f"Approved and stored memory from proposal {p.id}")
            return

        if sub == "reject":
            if len(parts) < 3:
                print("Usage: memory reject <id> [note]")
                return
            note = " ".join(parts[3:]) if len(parts) > 3 else ""
            mm.reject(parts[2], note)
            print("Rejected.")
            return

        if sub == "list":
            if len(parts) < 3:
                print("Usage: memory list <category>")
                return
            category = MemoryCategory(parts[2])
            items = mm.list_memory(category)
            if not items:
                print("(empty)")
                return
            for r in items:
                print(f"- {r.id} {r.content}")
            return

        print("Unknown memory command")

    except FileNotFoundError as e:
        print(str(e))
    except Exception as e:
        print(f"Memory error: {e}")


# ---------------- Main Loop ----------------

def repl() -> None:
    repo = _repo_root()
    state = RuntimeState(
        repo_root=repo,
        update_manager=UpdateManager(repo),
        memory_manager=MemoryManager(repo),
    )

    print("\nKimiko CLI (approval-based learning ENABLED)")
    print("Type 'help' for commands. Ctrl+C or 'quit' to exit.\n")

    while True:
        try:
            raw = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        if cmd in ("quit", "exit"):
            print("Goodbye.")
            return
        if cmd == "help":
            _print_help()
            continue
        if cmd == "version":
            _cmd_version()
            continue
        if cmd == "snapshot":
            _cmd_snapshot(state, parts)
            continue
        if cmd == "diagnostics":
            _cmd_diagnostics(state, parts)
            continue
        if cmd == "readiness":
            _cmd_readiness(state)
            continue
        if cmd == "propose-check":
            _cmd_propose_check(state)
            continue
        if cmd == "propose-draft":
            _cmd_propose_draft(state, parts)
            continue
        if cmd == "status":
            _cmd_status(state, parts)
            continue
        if cmd == "update":
            _handle_update(state, parts)
            continue
        if cmd == "memory":
            _handle_memory(state, parts)
            continue

        print("Unknown command. Type 'help'.")


def healthcheck() -> int:
    repo = _repo_root()
    _ = UpdateManager(repo)
    _ = MemoryManager(repo)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--health", action="store_true")
    args, _ = parser.parse_known_args(argv)

    if args.health:
        return healthcheck()

    repl()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
