using System.Text.Json.Serialization;

namespace AtlasKillSwitch.Activities
{
    internal sealed class KillSwitchResult
    {
        [JsonPropertyName("triggered")]
        public bool Triggered { get; set; }

        [JsonPropertyName("trigger_name")]
        public string? TriggerName { get; set; }

        [JsonPropertyName("reason")]
        public string? Reason { get; set; }

        [JsonPropertyName("audit_event_id")]
        public string? AuditEventId { get; set; }
    }
}
