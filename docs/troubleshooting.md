# Troubleshooting Guide

Quick reference for diagnosing and resolving common issues.

---

## Triage Matrix

| Issue Type | Route To | First Diagnostic | Common Fix |
|------------|----------|------------------|------------|
| Install/env errors | DevEx | Python version? UV installed? | `uv sync` |
| Import errors | DevEx | Check pyproject.toml | `uv sync` |
| Lint failures | DevEx | Run with --fix? | `uv run ruff check . --fix` |
| Test failures | Feature/Core | Run with -vv? | `uv run pytest -vv -k <pattern>` |
| Art-Net not working | ProtocolBridge | grandMA3 running? Correct universe? | Check Network Setup in MA3 |
| sACN not working | ProtocolBridge | Multicast enabled? Correct address? | Verify network interface |
| OSC connection fails | ProtocolBridge | OSC input enabled in MA3? Correct port? | Check In & Out / OSC |
| GDTF parse fails | FixtureEngineer | Valid .gdtf.zip file? | Re-download from gdtf-share.com |
| Fixture not responding | FixtureEngineer | Correct DMX address? Universe match? | Verify patch in MA3 |
| Visualizer blank | VisualizerDev | Fixtures have 3D geometry? | Try different fixture |
| Context drift | Any | Session log stale? | Clear + resume from logs |
| Stuck > 30min | Any | Documented blockers? | Create handoff packet |

---

## Common Issues

### Environment Issues

**Problem: `ModuleNotFoundError`**
```bash
# Solution: Sync dependencies
uv sync

# If still failing, check pyproject.toml dependencies
cat pyproject.toml | grep -A 10 "dependencies"
```

**Problem: `uv: command not found`**
```bash
# Solution: Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Problem: Python version mismatch**
```bash
# Solution: Check required version
python --version
# Should be >= 3.10
```

---

### Code Quality Issues

**Problem: Linting fails**
```bash
# Auto-fix most issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# View specific errors
uv run ruff check . --output-format=full
```

---

### Test Issues

**Problem: Tests fail locally**
```bash
# Run with verbose output
uv run pytest -vv

# Run specific test file
uv run pytest tests/test_bridge.py

# Run tests matching pattern
uv run pytest -k "test_artnet"

# Re-run last failed tests
uv run pytest --lf

# Show print statements
uv run pytest -s
```

**Problem: Tests pass locally but fail in CI**
```bash
# Check for:
# 1. Missing dependencies in pyproject.toml
# 2. Environment variables not set in CI
# 3. Different Python version
# 4. Timing/race conditions in protocol tests

# Reproduce CI environment locally
uv sync
uv run pytest
```

---

### Protocol Issues

**Problem: Art-Net packets not received by grandMA3**
```bash
# 1. Verify grandMA3 onPC is running
# 2. Confirm an Art-Net input row is enabled for the target local universe
# 3. Verify universe number matches (MA3 may use 1-based)
# 4. Use Wireshark to confirm packets are being sent:
#    wireshark -i lo0 -f "udp port 6454"
# 5. Check firewall isn't blocking port 6454
```

**Problem: sACN multicast not working**
```bash
# 1. Verify network interface supports multicast
# 2. Check multicast address calculation: 239.255.<hi>.<lo>
# 3. Try unicast mode instead of multicast
# 4. Verify grandMA3 sACN input is enabled
```

**Problem: OSC commands not executing**
```bash
# 1. Verify OSC input is enabled in grandMA3 In & Out / OSC
# 2. Check port number (default: 8000)
# 3. Test connection manually:
#    python -c "from pythonosc import udp_client; c = udp_client.UDPClient('127.0.0.1', 8000); c.send_message('/cmd', 'About')"
# 4. Check grandMA3 OSC settings for allowed IPs
# 5. Verify command syntax is valid MA3 command
```

**Problem: GDTF fixture fails to parse**
```bash
# 1. Verify file is a valid .gdtf.zip (it's a ZIP archive)
# 2. Check that Device.xml exists inside the zip
# 3. Re-download from gdtf-share.com
# 4. Try parsing a known-good fixture first
```

**Problem: Fixture doesn't respond in visualizer**
```bash
# 1. Verify fixture is patched in grandMA3
# 2. Check DMX address matches what RayFlow sends
# 3. Verify universe number matches
# 4. Try a simple fixture first (generic dimmer)
# 5. Check that the fixture has 3D geometry in GDTF
```

---

### Git Issues

**Problem: Accidentally on main branch**
```bash
# Stash your changes
git stash

# Create feature branch
git checkout -b feat/<name>

# Restore your changes
git stash pop
```

**Problem: Merge conflicts**
```bash
# Check which files have conflicts
git status

# Open conflicted files and resolve
# Look for <<<<<<< HEAD markers

# After resolving, mark as resolved
git add <resolved-files>
git commit
```

---

### Documentation Issues

**Problem: MkDocs build fails**
```bash
# Check for syntax errors in markdown
mkdocs build --strict

# Validate navigation in mkdocs.yml
cat mkdocs.yml

# Common issues:
# - Broken internal links
# - Missing files referenced in nav
# - YAML syntax errors
```

---

### Session Issues

**Problem: Context drift during long session**
1. Pause and create session log documenting progress
2. Clear chat history
3. Resume from session log + `.agent/CONTEXT.md`
4. Load only files needed for current task

**Problem: Lost track of what to do next**
1. Read last session log in `session_logs/`
2. Check `docs/implementation_schedule.md`
3. Review `.agent/CONTEXT.md` for current priorities

**Problem: Stuck for > 30 minutes**
1. Document blockers in session log
2. Create handoff packet with context
3. Flag for human review
4. Consider alternate approaches or escalate to different role

---

## Escalation Guidelines

### When to Escalate

- Security issues (credentials exposed, vulnerabilities)
- Breaking changes to public APIs or protocol implementations
- Unable to resolve after 2 serious attempts
- Conflicting requirements or ambiguous specs

### How to Escalate

1. **Document thoroughly** in session log:
   - What was attempted
   - Results/errors observed
   - Debugging steps taken
   - Current state of work

2. **Create handoff packet**:
   - Clear problem statement
   - Relevant file paths and line numbers
   - Expected vs actual behavior
   - Proposed solutions considered

3. **Flag for review**:
   - Tag in session log with `ESCALATION`
   - Update implementation schedule status
   - Notify via appropriate channel

---

## Prevention

### Avoid Common Pitfalls

1. **Always run health check before committing**
   ```bash
   uv run ruff format . && uv run ruff check . && uv run pytest
   ```

2. **Create session logs consistently**
   - Use `.agent/skills/end-session/SKILL.md`
   - Document decisions and blockers
   - Update implementation schedule

3. **Follow boot order when starting sessions**
   - AGENTS.md → README.md → .agent/CONTEXT.md
   - Review last 3-5 session logs
   - Plan before implementing

4. **Branch safety**
   - Check branch before starting: `git branch`
   - Never work directly on `main`
   - Create descriptive feature branch names

5. **Protocol verification**
   - Always verify Art-Net/sACN packets with network tools
   - Test OSC commands manually before automating
   - Validate GDTF files before parsing

---

## Getting Help

- **Documentation**: `docs/` directory
- **Session history**: `session_logs/` (last 3-5 logs)
- **Project context**: `.agent/CONTEXT.md`
- **Standards**: `docs/development_standards.md`
- **Checklists**: `docs/checklists.md`
- **Glossary**: `docs/glossary.md` — lighting industry terms

If you've exhausted these resources and still blocked, document the issue thoroughly and escalate.
