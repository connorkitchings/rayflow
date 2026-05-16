# Development Standards & Workflow

This document provides comprehensive standards, workflows, and best practices for development in RayFlow.

## Core Principles

- **Keep It Lean:** Focus on a few core, high-signal documents
- **Short Sprints:** Maintain momentum with weekly or bi-weekly cycles
- **Context Discipline:** Only provide relevant documents to focus AI collaboration
- **User-Centric:** Test with real fixtures and real songs early and often
- **AI as Co-Pilot:** Use AI for generation, review, and ideation, but always validate its output
- **Continuous Documentation:** Documentation preserves context and decisions

## Development Workflow

### Branch Strategy

- **Main Branch:** `main` — Production-ready code only
- **Feature Branches:** `feat/description` — Individual features or fixes
- **Hotfix Branches:** `hotfix/description` — Critical production fixes

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes following coding standards
3. Run pre-commit checklist (see [Checklists](./checklists.md))
4. Submit pull request with clear description
5. Complete code review process
6. Run pre-merge checklist
7. Merge to `main` after approval

## Code Quality Standards

### Python Standards

- **Version:** Python 3.10+
- **Formatting:** Use `ruff` for linting, formatting, and import sorting
- **Type Hints:** All function signatures must include type hints
- **Docstrings:** Use Google-style docstrings for all public modules, classes, and functions
- **Testing:** Use `pytest` with comprehensive test coverage

### Code Structure

Python files should follow this order:

1. Shebang (if applicable)
2. Module-level docstring
3. Imports (Standard Library, Third-Party, Local Application)
4. Constants
5. Functions and classes
6. `if __name__ == "__main__":` block for executable scripts

### Protocol Testing Standards

When implementing lighting protocols (Art-Net, sACN, OSC):

- **Unit tests:** Test packet construction, parsing, and validation
- **Integration tests:** Test end-to-end communication with grandMA3 onPC
- **Network verification:** Use Wireshark/tcpdump to verify packet format
- **Edge cases:** Test universe overflow, invalid addresses, malformed packets

### Code Review Guidelines

#### First Pass: Understanding the Change

- **Clarity of Purpose:** Clear PR title and description
- **Related Issue:** Change linked to specific task/issue
- **Scope:** Reasonable scope, not trying to do too many things

#### Code Quality and Style

- **Readability:** Easy to understand with clear variable/function names
- **Style Guide:** Adheres to project style (ruff formatting/linting)
- **Comments:** Well-commented, especially in complex areas (protocol implementations)
- **Simplicity (KISS):** Not unnecessarily complex
- **Don't Repeat Yourself (DRY):** No duplicated code

#### Functionality and Correctness

- **Logic:** Sound logic that correctly solves the problem
- **Edge Cases:** Handles edge cases gracefully (universe overflow, invalid GDTF)
- **Error Handling:** Robust error handling, doesn't fail silently
- **Security:** No security vulnerabilities, network safety considered

#### Testing

- **Test Coverage:** New tests cover changes with adequate coverage
- **Test Quality:** Well-written, understandable tests
- **Test Types:** Unit tests for logic, integration tests for protocol workflows
- **Performance:** No significant performance regressions

## Quality Gates & Automation

### Pre-Commit Hooks

Automated checks run before each commit:

- Code formatting (ruff)
- Linting (ruff)
- Type checking (mypy)
- Security scanning (bandit)

### Continuous Integration

All pull requests trigger:

- Automated testing suite
- Code coverage reporting
- Security vulnerability scanning
- Documentation building

## Documentation Standards

### Markdown Guidelines

- Use clear, descriptive headings
- Include table of contents for long documents
- Link to related documents using relative paths
- Keep lines under 100 characters
- Use code blocks with appropriate language tags

### Guide Documentation

All guides in `docs/guides/` should follow this structure:

1. **Purpose:** What the guide accomplishes
2. **Prerequisites:** What you need before starting
3. **Steps:** Numbered, actionable steps
4. **Verification:** How to confirm it worked
5. **Troubleshooting:** Common issues and solutions
6. **Next Steps:** Where to go from here

## Deployment & Operations

### Environment Management

- **Development:** Local development with grandMA3 onPC running locally
- **Testing:** Test against grandMA3 onPC with sample fixtures
- **Production:** Not applicable (personal practice tool)

### Monitoring & Observability

- Application logging with structured output
- Error tracking for protocol failures
- Session logs for development history
