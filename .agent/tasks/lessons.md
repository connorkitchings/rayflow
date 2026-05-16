# Lessons Learned

> Patterns and mistakes to avoid. Review at session start. Update after any correction.

---

## How to Use This File

1. **Review at session start** — Check for relevant lessons before starting work
2. **Add after corrections** — Whenever the user corrects you, capture the pattern
3. **Iterate ruthlessly** — Refine rules until the same mistake stops happening

---

## Correction Patterns

> Lessons from user corrections. Each entry captures the mistake, the rule to prevent it, and the date.

### [Date: 2026-05-15]

**Mistake:**
> Gave user manual MA3 clicking instructions ("look for this button, click that") instead of automating the setup. User got frustrated with "manual work."

**Root Cause:**
> Insufficient knowledge of MA3 onPC UI; MA Lighting docs were offline; .show file format is binary (blocked XML generation). Fell back to manual instructions as default, which is the wrong default for a CLI tool project.

**Rule Added:**
> **Automation-first for external tool integration.** If the tool can't be scripted, document the exact menu path once, then move on. Never make the user click through a multi-step UI process during a coding session. If a tool's docs are unavailable, research the binary/app structure before proposing file generation.

**Example:**
> Should have: (1) checked .show file format before proposing XML generation, (2) defaulted to tcpdump/loopback verification instead of MA3 visual verification, (3) treated MA3 config as one-time setup documented in a guide, not session-time work.

---

### [Date: 2026-05-15]

**Mistake:**
> Proposed generating XML show files without verifying the .show file format first. The format is binary (GMA3 header), not XML.

**Root Cause:**
> Assumed .show files were XML based on common practice (MA2 macros use XML). Didn't empiricially check before building a plan around it.

**Rule Added:**
> **Verify file format before proposing generation.** Read the first bytes of any target file format before designing code that produces it. `file <path>`, `xxd <path> | head -3`, and `head -c 50 <path>` take seconds.

**Example:**
> Should have: run `file` and `xxd` on the `.show` file FIRST, discovered it's binary, and pivoted to tcpdump + OSC approach immediately instead of proposing XML generation.

---

### [Date: YYYY-MM-DD]

**Mistake:**
> What went wrong (from user correction)

**Root Cause:**
> Why it happened

**Rule Added:**
> Specific rule to prevent this mistake

**Example:**
> What you should have done instead

---

### Template for New Entries

```markdown
### [Date: YYYY-MM-DD]

**Mistake:**
> [Brief description of what went wrong]

**Root Cause:**
> [Why it happened - be honest]

**Rule Added:**
> [Specific actionable rule]

**Example:**
> [What you should have done]
```

---

## Categories

### Code Quality
- [ ] Lazy fixes / temporary workarounds
- [ ] Missing tests
- [ ] Over-engineering
- [ ] Not considering edge cases

### Process
- [ ] Not planning before implementing
- [ ] Skipping verification
- [ ] Not asking clarifying questions
- [ ] Implementing without approval

### Context
- [ ] Not reading relevant docs first
- [ ] Missing important files
- [ ] Not checking recent session logs
- [ ] Ignoring existing patterns in codebase

### Communication
- [ ] Not explaining changes
- [ ] Making assumptions without checking
- [ ] Not providing options
- [ ] Missing handoff notes

---

## Review Checklist

Before each session, check:

- [ ] Read last 10 entries for relevant patterns
- [ ] Any new lessons since last session?
- [ ] Rules still make sense / haven't become outdated?

---

## Success Metrics

Track improvement over time:

- [ ] Fewer repeated mistakes
- [ ] Corrections decrease over time
- [ ] Rules are specific and actionable

---

## Links

- Principles: `.agent/PRINCIPLES.md`
- Start session: `.agent/skills/start-session/SKILL.md`
- End session: `.agent/skills/end-session/SKILL.md`

---

**Update this file after EVERY correction. The goal is to make the same mistake once.**
