# UiPath integration — atlas-killswitch

> v0.1 stub. A UiPath custom activity that wraps the `atlas-killswitch` Python library so federal UiPath workflows can call the kill switch as a first-class Studio activity.

## What this gives you

A drop-in **`KillSwitchCheck`** activity for UiPath Studio. Place it before any agentic step (an LLM call, an autonomous tool invocation, a Maestro agent task) and the workflow will:

1. Evaluate the agent's input/output against the configured triggers (rule-based, rate-limit)
2. Halt the workflow if a trigger fires
3. Write a federal-grade JSON audit event to disk for SIEM ingestion

No changes to your existing UiPath project structure. No new infrastructure. Apache 2.0.

## v0.1 scope

This v0.1 is a **stub** — meaning the interface is defined and the activity is wired, but the actual production-grade signing, NuGet packaging, and UiPath Marketplace publishing come in v0.2. Right now this lets:

- A UiPath developer see exactly how the activity will work
- A federal RPA team review the activity contract and provide design-partner feedback
- Anyone clone the repo, open the .csproj in Visual Studio, and build the activity package locally

## How the activity works (interface)

### Input arguments

| Property | Type | Required | Description |
|---|---|---|---|
| `AgentInput` | `String` | ✓ | The prompt / instruction sent to the agent |
| `AgentOutput` | `String` | ✓ | The response produced by the agent |
| `AgentId` | `String` | | Identifier for the agent (written to audit log) |
| `UseCase` | `String` | | Use-case label, e.g. `"benefits-lookup"` |
| `Agency` | `String` | | Agency name, e.g. `"SSA"`, `"DoD"` |
| `ForbiddenPatterns` | `String` | | Comma-separated regex patterns that must not appear in output |
| `MaxInvocationsPerWindow` | `Int32` | | Max invocations allowed per rolling window (0 = disabled) |
| `WindowSeconds` | `Int32` | | Rolling window length in seconds (default 60) |
| `AuditSinkPath` | `String` | | Path to append-only `.jsonl` audit file; leave blank to skip |
| `HaltOnTrigger` | `Boolean` | | Throw `KillSwitchHaltedException` when a trigger fires (default `True`) |
| `PythonExecutable` | `String` | | Python interpreter to invoke (default `"python"`) |

### Output arguments

| Property | Type | Description |
|---|---|---|
| `Triggered` | `Boolean` | Whether any trigger fired |
| `TriggerName` | `String` | Name of the trigger class that fired (`null` if clean) |
| `Reason` | `String` | Human-readable reason (`null` if clean) |
| `AuditEventId` | `String` | UUID of the written audit event |

### Workflow placement

```
┌─────────────────────────────────────────┐
│  Sequence                               │
│                                         │
│  ① Invoke LLM / Maestro agent task      │
│     → store result in agentOutput       │
│                                         │
│  ② KillSwitchCheck  ◄── ADD HERE        │
│     AgentInput   = originalPrompt       │
│     AgentOutput  = agentOutput          │
│     AuditSinkPath = "C:\audit\ks.jsonl" │
│     HaltOnTrigger = True                │
│                                         │
│  ③ Continue downstream workflow steps   │
└─────────────────────────────────────────┘
```

When `HaltOnTrigger = True` the activity throws `KillSwitchHaltedException`, which UiPath surfaces as a workflow fault. Add a **Try/Catch** with `KillSwitchHaltedException` to handle it gracefully (notify, escalate, close the case).

## File layout

```
uipath/
  README.md                          ← this file
  AtlasKillSwitchActivities.sln      ← Visual Studio solution
  src/
    AtlasKillSwitch.Activities/
      AtlasKillSwitch.Activities.csproj
      KillSwitchCheck.cs             ← the activity itself
      KillSwitchHaltedException.cs   ← exception type
      KillSwitchResult.cs            ← bridge response model
  bridge/
    ks_bridge.py                     ← Python subprocess bridge
```

## Building locally (Visual Studio)

1. Install [Visual Studio 2022](https://visualstudio.microsoft.com/) with **.NET desktop development**
2. Open `AtlasKillSwitchActivities.sln`
3. Restore NuGet packages → **Build → Release**
4. Output: `src/AtlasKillSwitch.Activities/bin/Release/net461/`
5. In UiPath Studio: **Manage Packages → Local → point at that folder**

## How the bridge works

The C# activity serializes all inputs to JSON and pipes them to `bridge/ks_bridge.py` via stdin. The bridge imports `atlas_killswitch`, runs the evaluation, and writes a JSON result to stdout. The activity parses stdout and sets output arguments. Exit code ≠ 0 with empty stdout surfaces as a workflow exception.

The bridge must be deployed alongside the compiled `.dll` (the `.csproj` copies it automatically via a `<Content>` item).

## Roadmap

| Version | Scope |
|---|---|
| v0.1 | Activity stub — interface defined, build works, no production hardening |
| v0.2 | NuGet signing, Marketplace listing, CI pipeline, rate-limit state persisted to disk |
| v0.3 | Native .NET trigger evaluation (eliminates Python subprocess dependency) |
