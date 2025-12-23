from __future__ import annotations

import platform
import sys
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeStatus:
    version: str
    uptime_seconds: int
    python_version: str
    platform: str
    execution_mode: str


def get_runtime_status(version: str, start_time: float) -> RuntimeStatus:
    uptime = int(time.time() - start_time)

    return RuntimeStatus(
        version=version,
        uptime_seconds=uptime,
        python_version=sys.version.split()[0],
        platform=platform.system(),
        execution_mode="CLI",
    )


def to_human_readable(rs: RuntimeStatus) -> str:
    h, rem = divmod(rs.uptime_seconds, 3600)
    m, s = divmod(rem, 60)

    if h:
        uptime_str = f"{h}h {m}m {s}s"
    elif m:
        uptime_str = f"{m}m {s}s"
    else:
        uptime_str = f"{s}s"

    return (
        "Runtime Status\n"
        "--------------\n"
        f"Version: {rs.version}\n"
        f"Uptime: {uptime_str}\n"
        f"Python: {rs.python_version}\n"
        f"Platform: {rs.platform}\n"
        f"Mode: {rs.execution_mode}"
    )
