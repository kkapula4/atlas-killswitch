"""
ks_bridge.py — stdin/stdout bridge between the UiPath C# activity and atlas-killswitch.

Protocol:
  stdin  → JSON payload (see fields below)
  stdout → JSON result  {"triggered", "trigger_name", "reason", "audit_event_id"}
  exit 0 always; errors are surfaced in the JSON so C# can raise a clean exception.

Note: each UiPath Robot invocation spawns a new process, so RateLimitTrigger state
resets per-call. Persistent rate limiting across calls is a v0.2 feature (state on disk).
"""
import sys
import json
import os

# Allow running from any working directory — resolve the repo root relative to this file.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _REPO_ROOT)

from atlas_killswitch import (
    KillSwitch,
    RuleBasedTrigger,
    RateLimitTrigger,
    LogOnlyAction,
    AuditLog,
    KillDecision,
    AuditEvent,
)


class _CapturingAuditLog(AuditLog):
    """Thin subclass that stores the last recorded event so we can return its event_id."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_event: AuditEvent | None = None

    def record(self, *args, **kwargs) -> AuditEvent:
        self.last_event = super().record(*args, **kwargs)
        return self.last_event


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read())

        agent_input: str = payload.get("agent_input", "")
        agent_output: str = payload.get("agent_output", "")
        ctx: dict = payload.get("context", {})
        forbidden: list = payload.get("forbidden_patterns", [])
        max_inv: int = payload.get("max_invocations", 0)
        window_sec: int = payload.get("window_seconds", 60)
        audit_sink: str | None = payload.get("audit_sink") or None

        triggers = []
        if forbidden:
            triggers.append(RuleBasedTrigger(forbidden_patterns=forbidden))
        if max_inv > 0:
            triggers.append(RateLimitTrigger(max_invocations=max_inv, window_seconds=window_sec))

        if not triggers:
            _respond(False, None, None, None)
            return

        audit = _CapturingAuditLog(sink=audit_sink)
        ks = KillSwitch(triggers=triggers, action=LogOnlyAction(), audit=audit)
        decision: KillDecision = ks.evaluate(agent_input, agent_output, ctx)

        event_id = audit.last_event.event_id if audit.last_event else None
        _respond(decision.triggered, decision.trigger_name, decision.reason, event_id)

    except Exception as exc:
        _respond(False, None, f"bridge error: {exc}", None)
        sys.exit(1)


def _respond(triggered: bool, trigger_name, reason, audit_event_id) -> None:
    print(json.dumps({
        "triggered": triggered,
        "trigger_name": trigger_name,
        "reason": reason,
        "audit_event_id": audit_event_id,
    }))


if __name__ == "__main__":
    main()
