---
name: ld-research
description: "Template and sourcing rules for lighting-designer profiles in docs/research/concert-lds/"
---

# LD Research

Profiles live in `docs/research/concert-lds/NN-<name>.md`.

## Template
```markdown
# <Designer name>

## Sources
1. <Title> - <URL> - accessed YYYY-MM-DD

## Verified facts
- <Fact> [1]

## Signature looks
- <Look>: what it is, when it is used [n]

## Copyable on a small rig
3-5 techniques doable with 4 movers + 8 washes, each with how to do it and [n].

## Unverified or removed
- <Claim that could not be sourced, or was dropped, and why>
```

## Sourcing rules for adding a new LD
1. Find at least two independent sources (interviews, credited show pages, trade press). Record URL and access date.
2. Every fact in Verified facts carries a `[n]` pointing at a listed source. A fact without a source goes in Unverified or removed.
3. Do not infer techniques from photos or from fixtures alone unless a source states it.
4. Copyable techniques must fit 4 movers + 8 washes (`docs/learn/starter-rig.md`); drop the rest.
5. Never invent quotes, show credits or URLs. Fetch the page; if it cannot be read, do not cite it.
6. Mention the new profile in `docs/design/style-guide.md` only if it changes the guide.
