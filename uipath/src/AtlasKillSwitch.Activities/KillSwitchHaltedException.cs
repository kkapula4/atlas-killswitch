using System;

namespace AtlasKillSwitch.Activities
{
    /// <summary>
    /// Thrown by <see cref="KillSwitchCheck"/> when a trigger fires and HaltOnTrigger is true.
    /// Catch this in UiPath Studio with a Try/Catch activity to handle gracefully.
    /// </summary>
    public sealed class KillSwitchHaltedException : Exception
    {
        public string? TriggerName { get; }
        public string? Reason { get; }
        public string? AuditEventId { get; }

        public KillSwitchHaltedException(string? triggerName, string? reason, string? auditEventId)
            : base($"[atlas-killswitch] Halted by {triggerName}: {reason}")
        {
            TriggerName = triggerName;
            Reason = reason;
            AuditEventId = auditEventId;
        }
    }
}
