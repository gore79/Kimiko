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
