# AI Lighting Architecture Patterns

**Source:** `docs/research/manual_research1.txt`  
**Parsed:** 2026-05-25

## The Oculizer Pattern

Oculizer is an open-source, music-reactive lighting automation system that demonstrates a clean architecture for AI-assisted lighting:

```
Real-Time System Audio Stream
    ↓
Feature Extraction (librosa: FFT, MFCCs, Spectral Centroid, RMS Energy)
    ↓
EfficientAT Deep Learning Audio Tagging
    ↓
Dimensionality Reduction & Semantic Clustering (scikit-learn: PCA & K-Means)
    ↓
Scene Prediction & Mapping Engine (matches detected audio mood to JSON profiles)
    ↓
Hardware Output Generation (Mel-Scaled FFT → DMX Values via PyDMXControl)
```

### Key Architectural Insight

The important pattern is not the specific model or library. It is the **separation between analysis, declarative scene intent, and protocol output**:

1. **Analysis layer** captures and classifies input (audio, video, environmental data).
2. **Scene intent layer** stores declarative JSON profiles that define how detected conditions map to lighting behavior.
3. **Output layer** renders scene state into DMX frames via Art-Net, sACN, or other protocols.

This separation allows an AI agent to adjust lighting behavior by rewriting a local JSON configuration file without touching the analysis or output code.

### Oculizer Scene Profile Example

```json
{
    "name": "deep_bass_pulse",
    "description": "Modulates fixture intensity based on sub-bass FFT bands",
    "type": "effect",
    "lights": [
        {
            "name": "beam_01",
            "type": "rgb",
            "modulator": "mfft",
            "mfft_range": [0, 5],
            "power_range": [1.0, 3.5],
            "brightness_range": [0.3, 1.0],
            "color": "blue"
        }
    ]
}
```

## MaestroDMX and the "AI Lighting Box" Reality

Devices like MaestroDMX claim to generate complete light shows in real time using AI, running on compact single-board computers (e.g., NanoPI Plus). However, technical analysis reveals:

- These systems do **not** execute complex, real-time deep learning models locally.
- Running a real-time LLM or generative video model with low latency requires high-performance hardware (80-core CPU or dedicated GPU), absent in these compact units.
- Instead, they rely on **reactive frequency algorithms** and **k-means clustering** to detect musical transitions, tempo shifts, and energy envelopes.
- These techniques are functionally similar to established, code-based audio analysis frameworks (like Oculizer).

The "AI" branding is marketing — the underlying technology is well-understood signal processing and clustering.

## The AI-Drafting Workflow

In professional production environments, AI integration is evolving into a hybrid **"AI-drafting"** workflow:

```
AI Audio & Visual Analysis (Motion, Color Tone, Energy, Context)
    ↓
Generates base cues & transitions
    ↓
Structured DMX Output Stream (piped to lighting software or console)
    ↓
Manual timing overrides & brand alignment by human designer
    ↓
Final Executable Show
```

### Why Hybrid, Not Full Automation

- Live performances require **absolute reliability** — unexpected lighting changes during a show are unacceptable.
- AI engines serve as **highly efficient programming assistants**, not replacements for human lighting directors.
- Designers must **review, edit, and lock down** AI-generated cue suggestions before performance.
- Machine-speed analysis dramatically accelerates the design phase, but human judgment ensures show quality and safety.

## Agent Backend Selection Criteria

When selecting a platform for AI-driven, agentic show control, evaluate across these dimensions:

| Dimension | Ideal for Agents | Poor for Agents |
|---|---|---|
| **Code-generation compatibility** | Simple string formatting, standard libraries | Proprietary syntax, high hallucination rates |
| **Bi-directional state reporting** | Native query/response (WebSocket, REST) | Requires scraping logs or parsing exports |
| **Licensing/hardware locks** | Open-source, no restrictions | Locked behind paid hardware or licenses |
| **Deployment complexity** | Self-contained script execution | Large application with GUI configuration |
| **Latency profile** | Direct protocol (Art-Net, sACN) | Console → OSC → Lua → command pipeline |

### Platform Assessment

| Platform | Agent Fit | Reasoning |
|---|---|---|
| **Python Bare-Metal (Art-Net/sACN)** | Excellent | Direct protocol control, inspectable frames, no console UI dependency |
| **QLC+ (WebSockets)** | Excellent | Plain-text command surface with query paths, open-source |
| **Chataigne (Middleware)** | Good | Stable translation layer; insulates agent from console-specific syntax |
| **grandMA3 onPC** | Low (until readback proven) | Fragile OSC setup, command context sensitivity, weak structured feedback |
| **Open Stage Control** | Medium | Browser UI + OSC/WebSocket bridge; not a lighting engine itself |
| **Obsidian ONYX** | Medium | OSC support but licensing restrictions and display bugs |
| **ChamSys MagicQ** | Low-Medium | Binary CREP protocol, hardware unlock requirements |

## Recommended Architecture for RayFlow

```
AI / Human Direction
        ↓
RayFlow show intent and fixture model (source of truth)
        ↓
Deterministic renderer
        ├──→ Art-Net adapter
        ├──→ sACN adapter
        ├──→ QLC+ WebSocket adapter
        ├──→ grandMA3 export / gated OSC adapter
        └──→ Middleware adapter (Chataigne)
```

The **renderer boundary** is critical. It prevents MA3 command syntax, QLC+ widget IDs, or Art-Net packet details from leaking into the AI-facing show design layer.
