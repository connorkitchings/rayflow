# Agentic Show Control Architectures

**Source:** `docs/research/manual_research.txt`  
**Date parsed:** 2026-05-23  
**Purpose:** Convert the manual research note into a readable research packet and compare its recommendations with RayFlow's current grandMA3-centered direction.

## Executive Summary

The manual research argues that terminal-based AI agents work best when the lighting stack exposes deterministic, structured, scriptable interfaces. By that standard, grandMA3 onPC is powerful but high-friction: OSC `/cmd` can mutate state, but setup is fragile, command context matters, feedback is weak, and fixture import/patch workflows are not reliably command-line-first.

The strongest near-term architecture for RayFlow is not "AI drives grandMA3 directly." It is:

1. RayFlow owns the show model, rig model, cue intent, and fixture capability mapping.
2. A deterministic control backend renders those abstractions into QLC+ WebSocket commands, Art-Net, or sACN.
3. grandMA3 remains supported as an export, playback, and professional-console compatibility target, but not the primary agent execution loop until readback and mutation paths are proven.

This conclusion matches the recent live-probe experience: the work was slowed by MA3 OSC configuration, inherited command destinations, disposable-show isolation, and MVR import behavior. Those are solvable integration problems, but they are not the best foundation for an agent-first MVP.

## Files

- [01 - grandMA3 Agent Friction](01-grandma3-agent-friction.md)
- [02 - API-First Alternatives](02-api-first-alternatives.md)
- [03 - Comparative Synthesis](03-comparative-synthesis.md)
- [04 - RayFlow Direction Review](04-rayflow-direction-review.md)

## Decision Framing

Use grandMA3 when the deliverable must land in a professional MA ecosystem. Use QLC+, Art-Net, or sACN when the deliverable must be easy for terminal agents to generate, test, inspect, and iterate.

RayFlow should therefore make its internal representation console-independent and treat console adapters as outputs, not as the source of truth.
