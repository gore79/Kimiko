from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CapabilitiesStatus:
    enabled: List[str]
    disabled: List[str]
    planned: List[str]


def get_capabilities_status() -> CapabilitiesStatus:
    # v1.6 is strictly read-only + introspection
    enabled = [
        "read-only introspection",
        "governed memory (proposal + approval)",
        "self-update proposals (approval required)",
    ]

    disabled = [
        "internet access",
        "file system writes",
        "command execution",
        "agent creation",
        "background tasks",
        "self-modification without approval",
    ]

    planned = [
        "passive tools (read-only)",
        "active tools (permissioned)",
        "controlled internet access",
        "agent spawning (queen-bee model)",
    ]

    return CapabilitiesStatus(
        enabled=enabled,
        disabled=disabled,
        planned=planned,
    )


def to_human_readable(cs: CapabilitiesStatus) -> str:
    lines = [
        "Capabilities Status",
        "-------------------",
        "",
        "Enabled capabilities:",
    ]

    for item in cs.enabled:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("Disabled capabilities:")
    for item in cs.disabled:
        lines.append(f"- {item} (disabled)")

    lines.append("")
    lines.append("Planned (not yet implemented):")
    for item in cs.planned:
        lines.append(f"- {item}")

    return "\n".join(lines)
