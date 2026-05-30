import os
from pathlib import Path

from scripts.kb_query import parse_frontmatter


def test_markdown_frontmatter():
    """Verify that all markdown files in docs/ have valid YAML frontmatter."""
    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    assert docs_dir.exists() and docs_dir.is_dir(), "docs/ directory must exist"

    md_files = []
    for root, _, files in os.walk(docs_dir):
        # Skip Obsidian config dir
        if ".obsidian" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                md_files.append(Path(root) / file)

    # We should have at least the core documents we modified
    assert len(md_files) > 0, "No markdown files found to validate"

    errors = []

    for file_path in md_files:
        rel_path = file_path.relative_to(docs_dir)

        # Core files that we demand to have frontmatter
        core_files = [
            "index.md",
            "knowledge_base.md",
            "glossary.md",
            "ai_guide.md",
            "ai/MASTER_CONTEXT.md",
        ]

        meta = parse_frontmatter(file_path)

        # If it is a core file or has any frontmatter start, validate it
        content = file_path.read_text(encoding="utf-8")
        has_fm = content.startswith("---")

        if str(rel_path) in core_files or has_fm:
            if not has_fm:
                errors.append(
                    f"docs/{rel_path} does not start with YAML frontmatter delimiters"
                )
                continue

            if not meta:
                errors.append(f"docs/{rel_path} has invalid or unparseable frontmatter")
                continue

            # Validate required fields
            if "title" not in meta or not meta["title"]:
                errors.append(f"docs/{rel_path} frontmatter is missing 'title'")
            if (
                "tags" not in meta
                or not isinstance(meta["tags"], list)
                or not meta["tags"]
            ):
                errors.append(f"docs/{rel_path} frontmatter lacks valid 'tags' list")
            if "summary" not in meta or not meta["summary"]:
                errors.append(f"docs/{rel_path} frontmatter is missing 'summary'")

    assert not errors, "\n".join(errors)
