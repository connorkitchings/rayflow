# Runbook

This runbook documents how to operate and troubleshoot RayFlow in its default state.

## Table of Contents

- [Monitoring](#monitoring)
- [Common Issues & Troubleshooting](#common-issues--troubleshooting)
- [grandMA3 onPC Operations](#grandma3-onpc-operations)
- [Contact & Escalation](#contact--escalation)

## Monitoring

- **CI Pipeline:** GitHub Actions workflow runs linting, security scans, and tests on every push/PR. Treat red builds as the primary health signal.
- **Structured Logs:** Application scripts log to stdout with timestamps and module names. Redirect output to files during longer runs for later analysis.
- **grandMA3 onPC:** Monitor the console's network and In & Out status to verify Art-Net, sACN, and OSC connections. Current RayFlow baseline is grandMA3 onPC 2.3.2.0.

## Common Issues & Troubleshooting

### Issue: `uv sync` fails or dependencies missing

**Symptoms:**
- `uv sync` exits with resolution errors or missing interpreter messages.

**Troubleshooting Steps:**
1. Verify Python 3.10+ is installed: `python3 --version`.
2. Clear the `.venv` (if created) and rerun `uv sync`.
3. On macOS, ensure `uv` binary is on the PATH (`which uv`).

**Resolution:**
Re-run `uv sync` after environment correction. Consult `pyproject.toml` to confirm dependency pins remain intact.

### Issue: Art-Net connection fails

**Symptoms:**
- DMX values sent from RayFlow don't reach grandMA3 onPC.
- No response in the 3D visualizer.

**Troubleshooting Steps:**
1. Ensure grandMA3 onPC is running and a show is loaded.
2. Confirm an Art-Net input row is enabled for the target local universe.
3. Verify universe number matches (MA3 may use 1-based universes).
4. Use Wireshark to confirm packets: `wireshark -i lo0 -f "udp port 6454"`.
5. Check macOS firewall isn't blocking port 6454.

**Resolution:**
Enable Art-Net in grandMA3 Network Setup, verify universe alignment, and ensure no firewall blocks.

### Issue: OSC commands not executing

**Symptoms:**
- RayFlow sends OSC commands but grandMA3 doesn't respond.

**Troubleshooting Steps:**
1. Verify OSC input is enabled in the In & Out / OSC configuration.
2. Check port number (default: 8000).
3. Verify allowed IP addresses include your Mac's IP.
4. Test with a simple command: `About`.

**Resolution:**
Enable OSC in grandMA3, verify port and IP settings, and ensure command syntax is valid.

### Issue: GDTF fixture fails to parse

**Symptoms:**
- RayFlow throws an error when loading a .gdtf.zip file.

**Troubleshooting Steps:**
1. Verify the file is a valid ZIP archive: `unzip -t <file.gdtf.zip>`.
2. Check that `Device.xml` exists inside the archive.
3. Re-download from gdtf-share.com if the file is corrupted.
4. Try parsing a known-good fixture first.

**Resolution:**
Replace corrupted GDTF file with a fresh download from gdtf-share.com.

### Issue: CI pipeline red due to lint/test failure

**Symptoms:**
- GitHub Actions job fails on `ruff` or `pytest`.

**Troubleshooting Steps:**
1. Reproduce locally with `uv run ruff format . && uv run ruff check .` and `uv run pytest -vv`.
2. Apply fixes or update tests to meet expectations.
3. Push changes; confirm pipeline passes.

**Resolution:**
Keep local checks green before pushing to avoid repeated CI failures.

## grandMA3 onPC Operations

### Starting a Session

1. Launch grandMA3 onPC
2. Open or create a show
3. Verify network and In & Out settings for Art-Net, sACN, and OSC
4. Open the 3D visualizer

### Stopping a Session

1. Save the show: `Store Show`
2. Close the 3D visualizer
3. Exit grandMA3 onPC
4. Note any changes made for the session log

### Backup a Show

1. Go to `Backup` → `Save Backup`
2. Choose a location outside the repo (e.g., `~/Documents/MA3 Backups/`)
3. Name with date: `rayflow_practice_2026-05-15.ma3backup`

### Import MVR File

1. Go to `Import` → `MVR`
2. Select the `.mvr` file from `data/shows/`
3. Verify fixtures appear in the 3D visualizer

### Record Visualizer Output

1. Open the 3D visualizer
2. Go to `Setup` → `Recording` → `Screen Capture`
3. Set format (MP4) and resolution (1920x1080)
4. Start recording, play the sequence, stop when done

## Contact & Escalation

- **Primary Maintainer:** Connor Kitchings (`connorkitchings` on GitHub).
- **Escalation Path:** If encountering issues beyond the current scope, open an issue in the repository with detailed logs and session context.
