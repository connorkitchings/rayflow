# Agent Playbook

This playbook maintains the evolving knowledge, strategic constraints, and execution patterns for RayFlow. It acts as the dynamic memory for the Agentic Context Engineering (ACE) framework.

## [RULES]
1. **Branch Protection**: NEVER commit directly to `main`. Always check `git branch` and create a feature branch.
2. **Session Persistence**: Every session must conclude with a documented log in `session_logs/`.
3. **Mandatory Health Checks**: Code must pass `uv run ruff check .` and `uv run pytest` before any commit.
4. **Secret Zero**: Never hardcode credentials. Always utilize environment variables.
5. **Test Coverage Policy**: Every new feature requires tests. Every bug fix requires a regression test.
6. **Test Queries First**: Define representative test queries before coding to bound scope and clarify requirements.
7. **Architecture Before Code**: Always produce an architecture document first, even if you have a solution in mind. Use it to challenge and refine the AI's design.
8. **Challenge Over-Engineering**: Question every complexity addition. Simplicity is a strategic choice, not a limitation.
9. **Human Validates Before Implementation**: Explicit human checkpoint before proceeding to code generation.
10. **Protocol Verification**: Always verify Art-Net/sACN packets with network tools (Wireshark, tcpdump) before marking protocol work complete.
11. **grandMA3 Version Pinning**: Before giving grandMA3 onPC UI instructions, verify the installed app version and use the matching MA manual version. Current local baseline is grandMA3 onPC 2.3.2.0.
12. **Capture Before Generating MA3 XML**: Before implementing any MA3 import/export XML generator, first capture a real MA3 export with the target objects and events. Treat local MA3-exported XML as source-of-truth and document any fields RayFlow intentionally omits.
13. **Disposable Show First**: Before sending live mutating MA3 commands, verify the active show is disposable by observing the UI or confirming a new `.show` file was created. Do not trust `SaveShow As` syntax alone.
14. **Command Acceptance Before MA3 Mutation**: Before running live MA3 mutation probes, send a low-risk OSC `/cmd` command that must produce observable export evidence. UDP listener presence alone does not prove command acceptance.
15. **Reset MA3 Command Destination**: MA3 `/cmd` commands inherit the visible command-line destination such as `Fixture`. Prepend `ChangeDestination Root` before generated MA3 probe/export/show commands.

## [STRATEGIES]
1. **Start Simple**: Begin with basic Art-Net sender, then add receiver, then sACN, then OSC. Each step verified before next.
2. **GDTF First**: Load real fixtures from gdtf-share.com early — don't mock fixture data longer than necessary.
3. **grandMA3 onPC as Source of Truth**: When in doubt about protocol behavior, test against grandMA3 onPC directly.
4. **AI-as-Interface**: RayFlow's primary interface is through AI coding tools. Design data models and contracts to be AI-readable and AI-modifiable. The human directs; the AI translates to MA3 commands.
5. **Continuous Context Maintenance**: Regularly run health checks and session handoff routines to ensure that the context files accurately reflect the current state of the architecture.
6. **Automation-First MA3 Guidance**: Treat MA3 UI configuration as setup state to verify, not repeated manual work for the user. Prefer commands, exported files, tcpdump/Wireshark checks, or small RayFlow helpers before asking for click-through steps.
7. **Context-First AI**: Always provide the AI with the full rig definition, fixture capabilities, and current show state before requesting changes. See `docs/ai_interaction_contract.md`.
8. **MCP Follows Verified Control**: Do not build MCP tools for MA3 programming until the underlying MA3 operation has command, export/readback, or observation proof. MCP should expose known capabilities, not hide unresolved console-control gaps.
9. **API-First Control Loop**: Keep RayFlow's core agent workflow on deterministic, structured interfaces such as RayFlow show data, QLC+ WebSockets, Art-Net, or sACN. Treat grandMA3 as a professional compatibility/export target until MA3 mutation and readback are repeatably proven.

## [SUCCESS_PATTERNS]
- **Incremental Protocol Testing**: Send one DMX value, verify it arrives, then expand to full universe.
- **GDTF Parsing**: Start with simple dimmer-only fixtures, then add moving lights with pan/tilt/color.
- **OSC Command Verification**: Send `About` command first to verify grandMA3 connection before complex macros.
- **Human-AI Collaboration Loop**: Prompt → Generate → Review → Feedback → Iterate. Human remains the final arbiter at every phase.
- **Evidence-First Backend Output**: Backend output adapters must return structured evidence and explicitly mark degraded proof such as `send-call-only`; do not treat "command sent" as equivalent to observed state.
- **Receiver Lifecycle for Protocol Proof**: Start capture receivers before sending live Art-Net/sACN frames, and stop them immediately after capture. Lingering UDP receivers can steal later loopback packets and create false mismatches.
- **Proposal-First Authoring**: Cue authoring helpers should return structured plans by default and require explicit apply gates before writing show YAML. Keep live backend output in separate `--execute` commands.
- **Renderer Families Before Authoring Families**: Add GDTF-backed renderer support for an attribute family before generating that family from high-level authoring helpers. Manual cue attributes can lead; deterministic authoring should follow proven render behavior.
- **Trigonometric Movement Mapping**: Map time-based movement paths (sine, circle, figure-8) to standard position attribute strings (like `pan` and `tilt`) before rendering, allowing them to route through GDTF mapping and 16-bit encoding.

## [REVIEW AGENTS]

### Agent Roster (Priority Order)

| # | Agent | Purpose | Trigger |
|---|-------|---------|---------|
| 1 | Planning Orchestrator | Scope, requirements, test queries | Start of any new task |
| 2 | Architecture Reviewer | Design patterns, SOLID, scalability | After planning, before code |
| 3 | Security Reviewer | Secrets, auth, injection, exposure | Before commits with security impact |
| 4 | Over-Engineering Detector | Complexity, unnecessary abstraction | During code review |
| 5 | Edge Case Challenger | Breaking scenarios, failure modes | After architecture design |
| 6 | Protocol Reviewer | Art-Net/sACN/OSC correctness | Protocol implementation changes |
| 7 | Testing Reviewer | Coverage, test quality, edge cases | Before any PR |
| 8 | Performance Reviewer | Bottlenecks, scaling, latency | Before release |
| 9 | Modularity Reviewer | Separation of concerns, coupling | Code organization concerns |
| 10 | Abstraction Reviewer | Interface design, encapsulation | Interface design changes |

### How to Invoke a Review Agent

1. **Select the appropriate agent** from the roster above
2. **Copy the prompt** from `.agent/VIBE_CRITIQUE_PROMPTS.md`
3. **Fill in the context** with your specific situation
4. **Submit to AI** for review
5. **Save output** to `.agent/reviews/YYYY-MM-DD/N - [Agent] Review.md`

### When to Run Reviews

**Always run:**
- Planning Orchestrator: New features/projects
- Architecture Reviewer: Significant design decisions
- Protocol Reviewer: Any Art-Net/sACN/OSC implementation

**Run as needed:**
- Edge Case Challenger: After architecture design
- Over-Engineering Detector: Code that feels complex
- Testing Reviewer: Before PR if coverage concerns
- Performance Reviewer: Before release
- Modularity/Abstraction Reviewers: Refactoring work

### Review Output Location

All review outputs go to:
```
.agent/reviews/YYYY-MM-DD/N - [Agent Name] Review.md
```

See `.agent/reviews/TEMPLATE.md` for output format.

### Review Status Indicators

- ✅ Pass: No issues found
- ⚠️ Warn: Minor issues, consider fixing
- ❌ Fail: Blocking issues, must fix
- ℹ️ Info: Informational, no action required
