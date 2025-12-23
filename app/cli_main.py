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


START_TIME = time.time()


@dataclass
class RuntimeState:
    repo_root: Path
    update_manager: UpdateManager
    memory_manager: MemoryManager


def _uptime_str() -> str:
    seconds = int(time.time() - START_TIME)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _print_help() -> None:
    print(
        "Kimiko CLI (approval-based learning ENABLED)\n"
        "Commands:\n"
        "  help\n"
        "  version\n"
        "  status\n"
        "  uptime\n"
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


def _cmd_status() -> None:
    print("I’m running normally and everything looks good.")


def _cmd_uptime() -> None:
    print(f"I’ve been running for {_uptime_str()}.")


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
            _cmd_status()
            continue
        if cmd == "uptime":
            _cmd_uptime()
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
