"""atlas-killswitch — operational safety primitives for federal AI agents."""

from atlas_killswitch.core import KillSwitch, KillDecision, KillSwitchHaltedError
from atlas_killswitch.triggers import RuleBasedTrigger, RateLimitTrigger
from atlas_killswitch.actions import HaltAction, LogOnlyAction
from atlas_killswitch.audit import AuditLog, AuditEvent

__version__ = "0.1.0"

__all__ = [
    "KillSwitch",
    "KillDecision",
    "KillSwitchHaltedError",
    "RuleBasedTrigger",
    "RateLimitTrigger",
    "HaltAction",
    "LogOnlyAction",
    "AuditLog",
    "AuditEvent",
]
