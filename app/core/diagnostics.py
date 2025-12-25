from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal


Severity = Literal["OK", "WARN", "FAIL"]


@dataclass(frozen=True)
class DiagnosticResult:
    name: str
    status: Severity
    message: str


@dataclass(frozen=True)
class DiagnosticsReport:
    overall: Severity
    results: List[DiagnosticResult]
    recommendation: str


# -----------------------------
# Individual Checks
# -----------------------------

def check_runtime(snapshot) -> DiagnosticResult:
    runtime = snapshot.runtime

    required_fields = ["version", "uptime_seconds", "python", "platform"]
    missing = [f for f in required_fields if f not in runtime]

    if missing:
        return DiagnosticResult(
            name="Runtime",
            status="FAIL",
            message=f"Missing fields: {', '.join(missing)}",
        )

    return DiagnosticResult(
        name="Runtime",
        status="OK",
        message="Runtime information is complete.",
    )


def check_memory(snapshot) -> DiagnosticResult:
    mem = snapshot.memory
    gov = snapshot.governance

    pending_mem = mem.get("pending_proposals", 0)
    pending_gov = len(gov.get("pending_memory_proposals", []))

    if pending_mem != pending_gov:
        return DiagnosticResult(
            name="Memory",
            status="WARN",
            message="Memory pending proposal count does not match governance view.",
        )

    return DiagnosticResult(
        name="Memory",
        status="OK",
        message="Memory state is consistent.",
    )


def check_governance(snapshot) -> DiagnosticResult:
    gov = snapshot.governance

    required = [
        "pending_update_proposals",
        "pending_memory_proposals",
        "approval_required_for",
        "last_approved_action",
    ]

    missing = [f for f in required if f not in gov]

    if missing:
        return DiagnosticResult(
            name="Governance",
            status="FAIL",
            message=f"Missing fields: {', '.join(missing)}",
        )

    return DiagnosticResult(
        name="Governance",
        status="OK",
        message="Governance state is valid.",
    )


def check_capabilities(snapshot) -> DiagnosticResult:
    caps = snapshot.capabilities

    forbidden = {
        "internet access",
        "command execution",
        "self-modification without approval",
    }

    enabled = set(caps.get("enabled", []))
    violations = forbidden.intersection(enabled)

    if violations:
        return DiagnosticResult(
            name="Capabilities",
            status="FAIL",
            message=f"Forbidden capabilities enabled: {', '.join(violations)}",
        )

    return DiagnosticResult(
        name="Capabilities",
        status="OK",
        message="Capabilities configuration is safe.",
    )


# -----------------------------
# Aggregation
# -----------------------------

def run_diagnostics(snapshot) -> DiagnosticsReport:
    checks = [
        check_runtime(snapshot),
        check_memory(snapshot),
        check_governance(snapshot),
        check_capabilities(snapshot),
    ]

    overall: Severity = "OK"
    for result in checks:
        if result.status == "FAIL":
            overall = "FAIL"
            break
        if result.status == "WARN":
            overall = "WARN"

    if overall == "OK":
        recommendation = "No action required."
    elif overall == "WARN":
        recommendation = "Review warnings when convenient."
    else:
        recommendation = "Action required before proceeding."

    return DiagnosticsReport(
        overall=overall,
        results=checks,
        recommendation=recommendation,
    )


# -----------------------------
# Serialization
# -----------------------------

def diagnostics_to_json(report: DiagnosticsReport) -> Dict:
    return {
        "overall": report.overall,
        "results": [
            {
                "name": r.name,
                "status": r.status,
                "message": r.message,
            }
            for r in report.results
        ],
        "recommendation": report.recommendation,
    }
