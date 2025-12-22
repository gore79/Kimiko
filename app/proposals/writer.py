from datetime import datetime
from pathlib import Path


PROPOSALS_DIR = Path(__file__).parent


def write_proposal(
    title: str,
    description: str,
    affected_files: list[str],
    reason: str,
) -> Path:
    """
    Write a proposal to disk.
    This does NOT execute anything.
    It only records an idea for review.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = title.lower().replace(" ", "_")
    filename = f"{timestamp}_{safe_title}.txt"
    path = PROPOSALS_DIR / filename

    content = [
        f"TITLE: {title}",
        "",
        f"TIMESTAMP: {timestamp}",
        "",
        "DESCRIPTION:",
        description,
        "",
        "AFFECTED FILES:",
        *[f"- {f}" for f in affected_files],
        "",
        "REASON:",
        reason,
        "",
        "STATUS: PENDING APPROVAL",
    ]

    path.write_text("\n".join(content), encoding="utf-8")
    return path
