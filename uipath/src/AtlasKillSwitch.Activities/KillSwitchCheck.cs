using System;
using System.Activities;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Text.Json;

namespace AtlasKillSwitch.Activities
{
    [DisplayName("KillSwitch Check")]
    [Description("Evaluates agent input/output against atlas-killswitch triggers. " +
                 "Throws KillSwitchHaltedException when a trigger fires (configurable).")]
    public sealed class KillSwitchCheck : CodeActivity
    {
        // ── Input ────────────────────────────────────────────────────────────

        [Category("Input")]
        [RequiredArgument]
        [DisplayName("Agent Input")]
        public InArgument<string> AgentInput { get; set; } = default!;

        [Category("Input")]
        [RequiredArgument]
        [DisplayName("Agent Output")]
        public InArgument<string> AgentOutput { get; set; } = default!;

        // ── Context ──────────────────────────────────────────────────────────

        [Category("Context")]
        [DisplayName("Agent ID")]
        public InArgument<string> AgentId { get; set; } = new InArgument<string>("");

        [Category("Context")]
        [DisplayName("Use Case")]
        public InArgument<string> UseCase { get; set; } = new InArgument<string>("");

        [Category("Context")]
        [DisplayName("Agency")]
        public InArgument<string> Agency { get; set; } = new InArgument<string>("");

        // ── Triggers ─────────────────────────────────────────────────────────

        [Category("Triggers")]
        [DisplayName("Forbidden Patterns (comma-separated regex)")]
        public InArgument<string> ForbiddenPatterns { get; set; } = new InArgument<string>("");

        [Category("Triggers")]
        [DisplayName("Max Invocations Per Window (0 = disabled)")]
        public InArgument<int> MaxInvocationsPerWindow { get; set; } = new InArgument<int>(0);

        [Category("Triggers")]
        [DisplayName("Window Seconds")]
        public InArgument<int> WindowSeconds { get; set; } = new InArgument<int>(60);

        // ── Audit ────────────────────────────────────────────────────────────

        [Category("Audit")]
        [DisplayName("Audit Sink Path (.jsonl)")]
        public InArgument<string> AuditSinkPath { get; set; } = new InArgument<string>("");

        // ── Behavior ─────────────────────────────────────────────────────────

        [Category("Behavior")]
        [DisplayName("Halt On Trigger")]
        [DefaultValue(true)]
        public InArgument<bool> HaltOnTrigger { get; set; } = new InArgument<bool>(true);

        [Category("Behavior")]
        [DisplayName("Python Executable")]
        [DefaultValue("python")]
        public InArgument<string> PythonExecutable { get; set; } = new InArgument<string>("python");

        // ── Output ───────────────────────────────────────────────────────────

        [Category("Output")]
        [DisplayName("Triggered")]
        public OutArgument<bool> Triggered { get; set; } = new OutArgument<bool>();

        [Category("Output")]
        [DisplayName("Trigger Name")]
        public OutArgument<string> TriggerName { get; set; } = new OutArgument<string>();

        [Category("Output")]
        [DisplayName("Reason")]
        public OutArgument<string> Reason { get; set; } = new OutArgument<string>();

        [Category("Output")]
        [DisplayName("Audit Event ID")]
        public OutArgument<string> AuditEventId { get; set; } = new OutArgument<string>();

        // ── Execute ──────────────────────────────────────────────────────────

        protected override void Execute(CodeActivityContext context)
        {
            var payload = new
            {
                agent_input = AgentInput.Get(context),
                agent_output = AgentOutput.Get(context),
                context = new
                {
                    agent_id = AgentId.Get(context),
                    use_case = UseCase.Get(context),
                    agency = Agency.Get(context),
                },
                forbidden_patterns = ParsePatterns(ForbiddenPatterns.Get(context)),
                max_invocations = MaxInvocationsPerWindow.Get(context),
                window_seconds = WindowSeconds.Get(context) > 0 ? WindowSeconds.Get(context) : 60,
                audit_sink = string.IsNullOrWhiteSpace(AuditSinkPath.Get(context))
                    ? null
                    : AuditSinkPath.Get(context),
            };

            var bridgePath = Path.Combine(
                Path.GetDirectoryName(typeof(KillSwitchCheck).Assembly.Location)!,
                "bridge", "ks_bridge.py");

            var result = RunBridge(
                PythonExecutable.Get(context) ?? "python",
                bridgePath,
                JsonSerializer.Serialize(payload));

            Triggered.Set(context, result.Triggered);
            TriggerName.Set(context, result.TriggerName ?? "");
            Reason.Set(context, result.Reason ?? "");
            AuditEventId.Set(context, result.AuditEventId ?? "");

            if (result.Triggered && HaltOnTrigger.Get(context))
                throw new KillSwitchHaltedException(result.TriggerName, result.Reason, result.AuditEventId);
        }

        private static string[] ParsePatterns(string? raw)
        {
            if (string.IsNullOrWhiteSpace(raw)) return Array.Empty<string>();
            return raw.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
        }

        private static KillSwitchResult RunBridge(string pythonExe, string bridgePath, string payloadJson)
        {
            using var proc = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = pythonExe,
                    Arguments = $"\"{bridgePath}\"",
                    UseShellExecute = false,
                    RedirectStandardInput = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    StandardInputEncoding = Encoding.UTF8,
                    StandardOutputEncoding = Encoding.UTF8,
                    CreateNoWindow = true,
                }
            };

            proc.Start();
            proc.StandardInput.Write(payloadJson);
            proc.StandardInput.Close();

            var stdout = proc.StandardOutput.ReadToEnd().Trim();
            var stderr = proc.StandardError.ReadToEnd().Trim();
            proc.WaitForExit();

            if (string.IsNullOrEmpty(stdout))
                throw new InvalidOperationException(
                    $"[atlas-killswitch] Bridge produced no output (exit {proc.ExitCode}): {stderr}");

            return JsonSerializer.Deserialize<KillSwitchResult>(stdout,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true })
                ?? throw new InvalidOperationException("[atlas-killswitch] Bridge returned null result.");
        }
    }
}
