# atlas-killswitch

> Open-source kill switch and human-oversight library for federal AI agents.
> First component of the **ATLAS Safety Stack** — operational safety primitives for U.S. federal AI deployments.
> UiPath-first launch. Platform-agnostic core.

## The gap this closes

In a May 2026 Market Connections survey of 200+ federal IT executives, only **29% of federal agencies reported documented "kill switch" procedures** for the AI agents they're deploying. More than half of federal agencies are now planning agentic AI pilots — a vast majority without the operational primitives needed to stop an agent when it goes wrong.

NIST, OWASP, and CSA have published the standards. Federal agencies don't need another framework. They need shippable, free, open-source tooling that closes the operational gap between what the standards require and what their teams can actually deploy on Monday morning.

`atlas-killswitch` is that tooling, for the first and most viscerally important gap.

## What it does (v1.0 scope)

A drop-in library you wrap around any agent invocation to give it a defensible kill layer.

- **Trigger types** — rule-based (output contains forbidden content), rate-limit (too many tool calls), anomaly (behavior outside trained baseline), manual (operator button), external (webhook from monitoring system).
- **Action types** — halt (immediate stop), suspend (pause for human approval), escalate (notify + continue), log-only.
- **Audit output** — every trigger, every action, every override — emitted in a standardized JSON schema designed for federal SIEM ingestion (Splunk, Sentinel, agency-specific).
- **Pluggable** — bring your own monitors, actions, and audit sinks.
- **Integrations** — first-class UiPath custom activity. Reference adapters for Claude, OpenAI, Bedrock, Azure OpenAI, and self-hosted Llama.

## Who it's for

- Federal RPA and AI teams standing up UiPath Maestro or any agentic platform
- Any federal agency required to demonstrate human-oversight controls for AI under OMB M-25-21
- Federal contractors and systems integrators supporting agency AI programs
- Any team that needs to put an agent in production and pass an Authorization to Operate review

## Why UiPath-first

The author's community is federal UiPath teams, and UiPath Maestro is being adopted across federal automation programs right now. The first integration ships as a UiPath custom activity so federal UiPath programs can drop it directly into existing workflows. The underlying library is platform-agnostic — because federal agencies run multiple AI vendors and shouldn't be locked to any of them.

## v0.1 scope — shipping in ~30 days

- Core `KillSwitch` Python class with pluggable triggers and actions
- One rule-based trigger (regex / keyword match on agent output)
- One rate-limit trigger (max-N tool calls per window)
- Halt and log-only actions
- Standardized JSON audit schema
- Stub UiPath custom activity
- Reference example wrapping a Claude agent and a UiPath Maestro agent

## Roadmap

- **v0.1** — Core library + one trigger + halt action + audit schema + UiPath stub
- **v0.2** — Anomaly trigger + suspend / human-in-loop action + first SIEM adapter
- **v0.3** — Compliance mapping (OMB M-25-21 + NIST AI RMF Manage function) + UiPath custom activity (production-ready)
- **v1.0** — Full integration set + reference deployments + documentation

## Why free

Released free and open-source for U.S. federal agencies, contractors, and the broader public-sector AI community. The author's career was built through federal automation programs; this is a way to give back while there is a real gap and a real moment.

## How to follow along

- Star the repo to get release notifications
- Issues labeled `design-partner` are open for federal teams interested in early collaboration
- LinkedIn: https://www.linkedin.com/in/karthik-kapula-a84109179/

## License

Apache 2.0 — intentionally permissive. Any federal agency, contractor, or systems integrator may fork, adapt, and deploy without restriction.

## The ATLAS Safety Stack

`atlas-killswitch` is the first component of a planned modular toolkit addressing operational gaps the EY 2026 Federal Trends Report and ServiceNow's Market Connections 2026 survey identified across federal AI programs. Future components: AI SBOM generator (CISA-aligned), AI use case inventory helper (OMB M-25-21 format), AI vendor liability contract template library, continuous authorization scaffolding.

Each component will ship as a standalone repo under the ATLAS Safety Stack umbrella. Use one, use all.

## Author

**Karthik Kapula** — 3x UiPath MVP · IEEE Senior Member · UiPath Dallas Chapter Leader

Built on public sources only. Personal work, not affiliated with or endorsed by any agency or employer.
