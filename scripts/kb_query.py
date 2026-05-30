#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path

# Try to import yaml, but define a fallback parser if it isn't installed
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def parse_frontmatter_fallback(content: str) -> dict:
    """Fallback frontmatter parser when PyYAML is not available."""
    metadata = {}
    # Match frontmatter block at start of file
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
    if not match:
        return metadata

    yaml_lines = match.group(1).splitlines()
    current_key = None
    list_accumulator = []

    for line in yaml_lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Check for list items
        if line_stripped.startswith("-") and current_key:
            item = line_stripped[1:].strip().strip('"').strip("'")
            list_accumulator.append(item)
            metadata[current_key] = list_accumulator
            continue

        if ":" in line:
            # Save previous list if any
            if current_key and list_accumulator:
                metadata[current_key] = list_accumulator
                list_accumulator = []

            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()

            # Check for inline list e.g. [a, b, c]
            if val.startswith("[") and val.endswith("]"):
                val_list = [
                    v.strip().strip('"').strip("'") for v in val[1:-1].split(",")
                ]
                metadata[key] = val_list
                current_key = None
            elif not val:
                current_key = key
                list_accumulator = []
            else:
                metadata[key] = val.strip('"').strip("'")
                current_key = None

    if current_key and list_accumulator:
        metadata[current_key] = list_accumulator

    return metadata


def parse_frontmatter(file_path: Path) -> dict:
    """Parses frontmatter from a markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return {}

    if not content.startswith("---"):
        return {}

    if HAS_YAML:
        try:
            match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
            if match:
                data = yaml.safe_load(match.group(1))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass  # Fall back to regex parser if safe_load fails for any reason

    return parse_frontmatter_fallback(content)


def scan_vault(docs_dir: Path) -> list:
    """Scans the vault directory recursively and returns all markdown metadata."""
    results = []
    for root, _, files in os.walk(docs_dir):
        # Skip Obsidian internal directory
        if ".obsidian" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(docs_dir)
                meta = parse_frontmatter(file_path)

                # Ensure structure
                title = meta.get("title", file_path.stem)
                tags = meta.get("tags", [])
                if isinstance(tags, str):
                    tags = [tags]
                tags = [t.strip() for t in tags]

                results.append(
                    {
                        "file": str(rel_path),
                        "absolute_path": str(file_path),
                        "title": title,
                        "tags": tags,
                        "summary": meta.get("summary", ""),
                        "related": meta.get("related", []),
                    }
                )
    return results


def cmd_list_tags(args, docs_dir: Path):
    vault = scan_vault(docs_dir)
    tag_counts = {}
    for doc in vault:
        for tag in doc["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if not tag_counts:
        print("No tags found in the knowledge base.")
        return

    print(f"{'Tag':<30} {'Count':<5}")
    print("-" * 36)
    for tag, count in sorted(tag_counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"{tag:<30} {count:<5}")


def cmd_search(args, docs_dir: Path):
    vault = scan_vault(docs_dir)
    results = []

    for doc in vault:
        match = True

        # Check tag filter
        if args.tag:
            if args.tag not in doc["tags"]:
                match = False

        # Check query match (in title, tags, or summary)
        if match and args.query:
            q = args.query.lower()
            text_pool = (
                f"{doc['title']} {' '.join(doc['tags'])} {doc['summary']}".lower()
            )
            if q not in text_pool:
                match = False

        if match:
            results.append(doc)

    if not results:
        print("No matching files found.")
        return

    print(f"Found {len(results)} matching files:\n")
    for doc in results:
        print(f"[{doc['title']}] (docs/{doc['file']})")
        if doc["tags"]:
            print(f"  Tags: {', '.join(doc['tags'])}")
        if doc["summary"]:
            print(f"  Summary: {doc['summary']}")
        print()


def cmd_view(args, docs_dir: Path):
    file_path = docs_dir / args.filepath
    if not file_path.exists() or not file_path.is_file():
        # Try exact search in name
        vault = scan_vault(docs_dir)
        matching = [d for d in vault if args.filepath.lower() in d["file"].lower()]
        if not matching:
            print(f"File not found: {args.filepath}")
            sys.exit(1)
        elif len(matching) > 1:
            print("Multiple files matched. Please select one:")
            for m in matching:
                print(f"  docs/{m['file']}")
            sys.exit(1)
        else:
            file_path = Path(matching[0]["absolute_path"])

    meta = parse_frontmatter(file_path)
    title = meta.get("title", file_path.stem)
    tags = meta.get("tags", [])
    summary = meta.get("summary", "No summary provided.")
    related = meta.get("related", [])

    print(f"Title:   {title}")
    print(f"Path:    docs/{file_path.relative_to(docs_dir)}")
    print(f"Tags:    {', '.join(tags) if tags else 'None'}")
    print(f"Summary: {summary}")
    if related:
        print("Related:")
        for r in related:
            print(f"  - {r}")
    print("\n" + "=" * 40 + "\n")

    # Print content after frontmatter
    content = file_path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n.*?\r?\n---\r?\n(.*)", content, re.DOTALL)
    body = match.group(1) if match else content
    # Print up to 40 lines of body for preview
    lines = body.strip().splitlines()
    for line in lines[:40]:
        print(line)
    if len(lines) > 40:
        print(f"\n... [{len(lines) - 40} more lines. Use a viewer to read fully.]")


def main():
    # Base directory logic: look for git repo root or current working dir docs directory
    script_dir = Path(__file__).resolve().parent
    docs_dir = script_dir.parent / "docs"
    if not docs_dir.exists():
        docs_dir = Path(os.getcwd()) / "docs"
    if not docs_dir.exists():
        print("Error: Could not locate 'docs/' directory.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Query utility for RayFlow Obsidian Knowledge Base."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-tags
    subparsers.add_parser(
        "list-tags", help="List all unique tags in the knowledge base."
    )

    # search
    search_parser = subparsers.add_parser("search", help="Search knowledge base files.")
    search_parser.add_argument("--tag", help="Filter files by tag.")
    search_parser.add_argument(
        "--query", help="Keyword search in title, tags, and summary."
    )

    # view
    view_parser = subparsers.add_parser(
        "view", help="View file metadata and content preview."
    )
    view_parser.add_argument(
        "filepath", help="Relative path or partial name of the markdown file."
    )

    args = parser.parse_args()

    if args.command == "list-tags":
        cmd_list_tags(args, docs_dir)
    elif args.command == "search":
        cmd_search(args, docs_dir)
    elif args.command == "view":
        cmd_view(args, docs_dir)


if __name__ == "__main__":
    main()
