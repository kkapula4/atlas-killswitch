"""Actions — what to do when a trigger fires."""

from atlas_killswitch.core import KillDecision, KillSwitchHaltedError


class HaltAction:
    """Halt agent execution immediately by raising KillSwitchHaltedError."""

    name = "halt"

    def execute(self, decision: KillDecision, context: dict) -> str:
        raise KillSwitchHaltedError(
            f"[atlas-killswitch] Halted by {decision.trigger_name}: {decision.reason}"
        )


class LogOnlyAction:
    """Log the trigger but let the agent continue. Useful for shadow-mode rollout."""

    name = "log-only"

    def execute(self, decision: KillDecision, context: dict) -> str:
        return self.name
