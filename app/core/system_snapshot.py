from __future__ import annotations

from dataclasses import dataclass

from app.version import __version__
from app.core.runtime_status import get_runtime_status, to_human_readable as runtime_hr
from app.core.memory_status import get_memory_status, to_human_readable as memory_hr
from app.core.governance_status import get_governance_status, to_human_readable as governance_hr
from app.core.capabilities_status import get_capabilities_status, to_human_readable as capabilities_hr
from app.memory.manager import MemoryManager
from app.core.update_manager import UpdateManager


@dataclass(frozen=True)
class SystemSnapshot:
    runtime: str
    memory: str
    governance: str
    capabilities: str


def get_system_snapshot(
    *,
    start_time: float,
    update_manager: UpdateManager,
    memory_manager: MemoryManager,
) -> SystemSnapshot:
    runtime = runtime_hr(
        get_runtime_status(version=__version__, start_time=start_time)
    )
    memory = memory_hr(get_memory_status(memory_manager))
    governance = governance_hr(
        get_governance_status(update_manager, memory_manager)
    )
    capabilities = capabilities_hr(get_capabilities_status())

    return SystemSnapshot(
        runtime=runtime,
        memory=memory,
        governance=governance,
        capabilities=capabilities,
    )


def to_human_readable(snapshot: SystemSnapshot) -> str:
    return (
        "System Snapshot\n"
        "===============\n\n"
        f"{snapshot.runtime}\n\n"
        f"{snapshot.memory}\n\n"
        f"{snapshot.governance}\n\n"
        f"{snapshot.capabilities}"
    )
