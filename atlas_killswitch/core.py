"""Core KillSwitch orchestration."""

from dataclasses import dataclass
from typing import Any, Optional, List


@dataclass
class KillDecision:
    """The outcome of evaluating an agent invocation against all triggers."""
    triggered: bool
    trigger_name: Optional[str] = None
    reason: Optional[str] = None
    action_taken: Optional[str] = None


class KillSwitchHaltedError(Exception):
    """Raised when the kill switch halts an agent invocation."""
    pass


class KillSwitch:
    """
    Wrap an agent invocation to add a defensible kill layer.

    Example:
        ks = KillSwitch(
            triggers=[RuleBasedTrigger(forbidden_patterns=[r"SSN:"])],
            action=HaltAction(),
            audit=AuditLog(sink="audit.jsonl"),
        )
        decision = ks.evaluate(agent_input, agent_output, context={"agent_id": "uc-01"})
    """

    def __init__(self, triggers, action, audit=None):
        self.triggers: List = triggers if isinstance(triggers, list) else [triggers]
        self.action = action
        self.audit = audit

    def evaluate(self, agent_input: Any, agent_output: Any, context: Optional[dict] = None) -> KillDecision:
        context = context or {}
        for trigger in self.triggers:
            fired, reason = trigger.check(agent_input, agent_output, context)
            if fired:
                decision = KillDecision(
                    triggered=True,
                    trigger_name=trigger.__class__.__name__,
                    reason=reason,
                )
                if self.audit:
                    self.audit.record(decision, agent_input, agent_output, context)
                # Action runs last because HaltAction raises an exception.
                action_name = self.action.execute(decision, context)
                decision.action_taken = action_name
                return decision

        decision = KillDecision(triggered=False)
        if self.audit:
            self.audit.record(decision, agent_input, agent_output, context)
        return decision
