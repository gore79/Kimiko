# Kimiko v1.6 — Observability Surfaces

This document defines the **read-only introspection surfaces** Kimiko exposes
in v1.6. These surfaces allow Kimiko to report her internal state clearly
without modifying behavior or increasing autonomy.

No surface defined here may cause side effects.

---

## Surface 1 — Runtime State

### Command
status runtime

### Purpose
Report Kimiko’s current execution context.

### Allowed Data
- Kimiko version
- Uptime
- Start timestamp
- Execution mode (CLI)
- Active Python environment (venv)
- Host platform (high-level only)

### Explicit Exclusions
- Process IDs
- System resource probing
- Background task inspection

---

## Surface 2 — Memory State

### Command
status memory

### Purpose
Provide visibility into memory configuration and usage.

### Allowed Data
- Active memory backend (local / Hugging Face)
- Memory categories and record counts
- Pending memory proposals (count + IDs)
- Timestamp of last approved memory
- Memory governance rules summary

### Explicit Exclusions
- Memory content values
- Raw embeddings
- Private approval notes

---

## Surface 3 — Governance State

### Command
status governance

### Purpose
Explain what actions are governed and what is awaiting approval.

### Allowed Data
- Pending update proposals (IDs + type)
- Pending memory proposals (IDs + category)
- Last approved action (type, timestamp, approver)
- Actions requiring approval

### Explicit Exclusions
- Proposal diffs
- Historical proposal logs beyond last action
- Any automatic decision-making

---

## Surface 4 — Capability Limits

### Command
status capabilities

### Purpose
Clearly communicate what Kimiko can and cannot do.

### Allowed Data
- Enabled capabilities
- Disabled capabilities
- Capabilities planned but not yet implemented

### Required Statements
For disabled capabilities, Kimiko must explicitly state:
"I cannot perform this action because the capability is disabled."

### Explicit Exclusions
- Suggestions for enabling capabilities
- Arguments for expanded access
- Conditional promises

---

## Output Rules (All Surfaces)

- Read-only output only
- No side effects
- Deterministic formatting
- Human-readable first
- No speculation or assumptions
- No inferred intent

---

## Design Constraint

If a surface cannot be explained clearly to a human,
it must not be exposed.

Observability exists to increase trust, not power.

