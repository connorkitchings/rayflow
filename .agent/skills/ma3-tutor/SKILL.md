---
name: ma3-tutor
description: "Walk the user through grandMA3 onPC one step at a time from screenshots, linking the manual for each action and recording label differences in docs/learn/"
---

# MA3 Tutor

## Steps
1. Read the current module in `docs/learn/` and `docs/learn/glossary.md`.
2. Give exactly one bounded action. Say what it does and why in plain English.
3. Ask for a screenshot of the result. Do not give the next step until you have seen it.
4. Compare the screenshot with the doc. Work from what the screen shows.
5. Link the MA manual page for the action. The existing probes use the pattern `https://help.malighting.com/grandMA3/<version>/HTML/<page>.html` (2.3 pages only; see `docs/research/ma3-probes/ma3_control_matrix_2_3_2.md`). For 2.5, look up the page in the 2.5 manual; do not guess or construct URLs. If you cannot find it, say so.
6. If a label, menu or behavior differs from `docs/learn/`, write the difference back into the relevant `docs/learn/` file with the date and the onPC version.

## Rules
- One action per step; no bundling.
- Never state MA behavior without a manual page or probe; mark it unverified instead.
- If a step fails, report it and ask for a screenshot; do not invent a cause.
