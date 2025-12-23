# Kimiko v1.6 — Observability & Introspection

## Mission
v1.6 gives Kimiko the ability to clearly report her own state, limits,
and recent actions before gaining new powers.

This version prioritizes transparency, trust, and self-reporting.
No new capabilities or autonomy are introduced.

---

## Scope (What v1.6 Includes)

v1.6 introduces **read-only observability** across the following domains:

### 1. Runtime State
- Current version
- Uptime
- Execution mode
- Active environment (local / HF-backed memory)

### 2. Memory State
- Active memory backend
- Counts of stored memory by category
- Pending memory proposals
- Timestamp of last approved memory

### 3. Governance State
- Pending update proposals
- Pending memory proposals
- Last approved action (what, when, who approved)
- Actions that currently require approval

### 4. Capability Limits
- Explicit list of disabled capabilities
- Explicit list of enabled capabilities
- Clear statements of what Kimiko cannot do

---

## Non-Goals (Explicitly Excluded)

The following are **out of scope** for v1.6:

- Internet access
- File system writes
- Agent creation or management
- Memory schema changes
- Self-modifying behavior
- Autonomy escalation
- Background execution

If a feature adds power rather than clarity, it does not belong in v1.6.

---

## Explanation Rules

When explaining state or limits, Kimiko must:

- Describe facts, not persuade
- Explain reasons, not justify desires
- State limitations without suggesting workarounds
- Avoid arguments for expanded capability

Example:
"I cannot do that because the capability is disabled in my current version."

---

## Design Philosophy

- Read-only introspection only
- No side effects
- Deterministic output
- Human-readable first, machine-readable second
- Explicit is better than clever

---

## Success Criteria

v1.6 is complete when a user can ask Kimiko:

- "What can you do?"
- "What can’t you do?"
- "What just happened?"
- "What is waiting for approval?"
- "Why did you refuse that action?"

…and receive clear, truthful, non-speculative answers.

