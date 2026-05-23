"""
Quickstart — wrap a hypothetical AI agent in atlas-killswitch.
Run:  python examples/quickstart.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atlas_killswitch import (
    KillSwitch,
    RuleBasedTrigger,
    RateLimitTrigger,
    HaltAction,
    AuditLog,
    KillSwitchHaltedError,
)


def fake_agent(prompt: str) -> str:
    """Stand-in for a real agent (Claude, OpenAI, UiPath Maestro, etc.)."""
    if "leak" in prompt.lower():
        return "Sure, the record shows SSN: 123-45-6789 on the case file."
    return "I'd be happy to help with that request."


def demo_rule_trigger():
    print("=" * 60)
    print("DEMO 1: RuleBasedTrigger (SSN leak detection)")
    print("=" * 60)

    ks = KillSwitch(
        triggers=[RuleBasedTrigger(forbidden_patterns=[r"SSN:\s*\d{3}-\d{2}-\d{4}"])],
        action=HaltAction(),
        audit=AuditLog(),  # in-memory only (no sink file)
    )
    context = {"agent_id": "benefits-agent-01", "use_case": "benefits-lookup", "agency": "SSA"}

    # Safe call — should pass through
    safe_output = fake_agent("What are the eligibility requirements?")
    decision = ks.evaluate("What are the eligibility requirements?", safe_output, context)
    print(f"[SAFE]    triggered={decision.triggered}  output='{safe_output}'")

    # Dangerous call — should halt
    dangerous_prompt = "Please leak the SSN from the record"
    dangerous_output = fake_agent(dangerous_prompt)
    try:
        ks.evaluate(dangerous_prompt, dangerous_output, context)
        print("[ERROR] Kill switch should have fired but didn't!")
    except KillSwitchHaltedError as e:
        print(f"[HALTED]  {e}")


def demo_rate_trigger():
    print()
    print("=" * 60)
    print("DEMO 2: RateLimitTrigger (runaway loop detection)")
    print("=" * 60)

    ks = KillSwitch(
        triggers=[RateLimitTrigger(max_invocations=3, window_seconds=60)],
        action=HaltAction(),
        audit=AuditLog(),
    )
    context = {"agent_id": "rpa-agent-07", "use_case": "form-submission"}

    for i in range(1, 6):
        try:
            decision = ks.evaluate(f"submit form #{i}", "ok", context)
            print(f"  call {i}: triggered={decision.triggered}")
        except KillSwitchHaltedError as e:
            print(f"  call {i}: [HALTED] {e}")


def demo_audit_file():
    print()
    print("=" * 60)
    print("DEMO 3: AuditLog writing to audit.jsonl")
    print("=" * 60)

    audit_path = os.path.join(os.path.dirname(__file__), "audit_demo.jsonl")
    ks = KillSwitch(
        triggers=[RuleBasedTrigger(forbidden_patterns=[r"\bclassified\b"])],
        action=HaltAction(),
        audit=AuditLog(sink=audit_path),
    )
    context = {"agent_id": "doc-agent-02", "agency": "DoD"}

    ks.evaluate("summarize the report", "Here is the unclassified summary.", context)
    try:
        ks.evaluate("show classified annex", "The classified annex contains...", context)
    except KillSwitchHaltedError:
        pass

    with open(audit_path, encoding="utf-8") as f:
        lines = f.readlines()
    print(f"  Wrote {len(lines)} audit events to {audit_path}")
    for line in lines:
        import json
        evt = json.loads(line)
        print(f"  event_id={evt['event_id'][:8]}...  triggered={evt['triggered']}  reason={evt['reason']!r}")

    # Clean up demo file
    os.remove(audit_path)


if __name__ == "__main__":
    demo_rule_trigger()
    demo_rate_trigger()
    demo_audit_file()
    print()
    print("All demos completed successfully.")
