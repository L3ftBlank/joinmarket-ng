#!/usr/bin/env python3
"""
Generate changelog entries from conventional commits.

This script parses git commit messages following the Conventional Commits spec
(https://www.conventionalcommits.org/) and generates changelog entries in the
Keep a Changelog format.

Usage:
    python scripts/generate_changelog.py                    # Since last tag
    python scripts/generate_changelog.py --since 0.11.0     # Since specific tag
    python scripts/generate_changelog.py --preview          # Preview without modifying
    python scripts/generate_changelog.py --update           # Update CHANGELOG.md

Conventional Commit Types -> Changelog Categories:
    feat:     Added
    fix:      Fixed
    perf:     Improved
    security: Security
    docs:     (skipped - documentation only)
    style:    (skipped - formatting only)
    refactor: Changed
    test:     (skipped - tests only)
    build:    (skipped - build system only)
    ci:       (skipped - CI only)
    chore:    (skipped - maintenance only)

Breaking changes (commits with BREAKING CHANGE: or !) are highlighted.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CHANGELOG = PROJECT_ROOT / "CHANGELOG.md"

# Map conventional commit types to changelog categories
TYPE_TO_CATEGORY = {
    "feat": "Added",
    "fix": "Fixed",
    "perf": "Improved",
    "security": "Security",
    "refactor": "Changed",
}

# Types to skip (don't include in changelog)
SKIP_TYPES = {"docs", "style", "test", "build", "ci", "chore", "release"}

# Regex patterns
CONVENTIONAL_COMMIT_PATTERN = re.compile(
    r"^(?P<type>\w+)"  # Type
    r"(?:\((?P<scope>[^)]+)\))?"  # Optional scope
    r"(?P<breaking>!)?"  # Optional breaking change indicator
    r":\s*"  # Colon separator
    r"(?P<description>.+)$"  # Description
)

BREAKING_CHANGE_PATTERN = re.compile(
    r"BREAKING[ -]CHANGE:\s*(.+)", re.IGNORECASE | re.MULTILINE
)


@dataclass
class Commit:
    """Represents a parsed commit."""

    hash: str
    type: str
    scope: str | None
    description: str
    body: str
    is_breaking: bool
    breaking_description: str | None


def run_git_command(args: list[str]) -> str:
    """Run a git command and return output."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        check=True,
    )
    return result.stdout.strip()


def get_latest_tag() -> str | None:
    """Get the most recent git tag."""
    try:
        return run_git_command(["describe", "--tags", "--abbrev=0"])
    except subprocess.CalledProcessError:
        return None


def get_commits_since(since_ref: str | None = None) -> list[Commit]:
    """Get all commits since a reference (tag or commit), parsing conventional format."""
    # Build git log command
    # Format: hash, subject, body separated by special delimiter
    delimiter = "---COMMIT_DELIMITER---"
    format_str = f"%H%n%s%n%b{delimiter}"

    if since_ref:
        ref_range = f"{since_ref}..HEAD"
    else:
        ref_range = "HEAD"

    try:
        output = run_git_command(["log", ref_range, f"--format={format_str}"])
    except subprocess.CalledProcessError:
        return []

    commits = []
    for commit_text in output.split(delimiter):
        commit_text = commit_text.strip()
        if not commit_text:
            continue

        lines = commit_text.split("\n", 2)
        if len(lines) < 2:
            continue

        commit_hash = lines[0]
        subject = lines[1]
        body = lines[2] if len(lines) > 2 else ""

        # Parse conventional commit format
        match = CONVENTIONAL_COMMIT_PATTERN.match(subject)
        if not match:
            continue  # Skip non-conventional commits

        commit_type = match.group("type").lower()
        scope = match.group("scope")
        description = match.group("description")
        is_breaking = bool(match.group("breaking"))

        # Check for BREAKING CHANGE in body
        breaking_description = None
        breaking_match = BREAKING_CHANGE_PATTERN.search(body)
        if breaking_match:
            is_breaking = True
            breaking_description = breaking_match.group(1).strip()

        commits.append(
            Commit(
                hash=commit_hash[:8],
                type=commit_type,
                scope=scope,
                description=description,
                body=body,
                is_breaking=is_breaking,
                breaking_description=breaking_description,
            )
        )

    return commits


def parse_body_bullets(body: str) -> list[str]:
    """Extract bullet points from commit body.

    Supports:
    - Lines starting with '- ' or '* '
    - Numbered lists like '1. ', '2. '
    - Continuation lines (indented or following a bullet)
    """
    if not body.strip():
        return []

    bullets: list[str] = []
    current_bullet: list[str] = []

    for line in body.split("\n"):
        stripped = line.strip()

        # Skip empty lines between bullets
        if not stripped:
            if current_bullet:
                bullets.append(" ".join(current_bullet))
                current_bullet = []
            continue

        # Skip BREAKING CHANGE lines (handled separately)
        if stripped.upper().startswith(
            "BREAKING CHANGE:"
        ) or stripped.upper().startswith("BREAKING-CHANGE:"):
            continue

        # Check if this is a new bullet point
        is_bullet = (
            stripped.startswith("- ")
            or stripped.startswith("* ")
            or re.match(r"^\d+\.\s", stripped)
        )

        if is_bullet:
            # Save previous bullet if exists
            if current_bullet:
                bullets.append(" ".join(current_bullet))

            # Start new bullet (remove bullet marker)
            if stripped.startswith("- ") or stripped.startswith("* "):
                current_bullet = [stripped[2:]]
            else:
                # Numbered list - remove "N. " prefix
                current_bullet = [re.sub(r"^\d+\.\s*", "", stripped)]
        elif current_bullet:
            # Continuation of previous bullet
            current_bullet.append(stripped)
        # else: ignore lines before first bullet

    # Don't forget the last bullet
    if current_bullet:
        bullets.append(" ".join(current_bullet))

    return bullets


def format_changelog_entry(commit: Commit) -> str:
    """Format a single commit as a changelog entry.

    Format:
    - **Scope**: Description (hash)
      - Body bullet 1
      - Body bullet 2
    """
    lines = []

    # Build the main entry line
    parts = []

    # Add scope prefix if present
    if commit.scope:
        parts.append(f"**{commit.scope.title()}**:")

    # Add description (capitalize first letter)
    desc = commit.description[0].upper() + commit.description[1:]
    parts.append(desc)

    entry = " ".join(parts)

    # Add breaking change notice
    if commit.is_breaking:
        if commit.breaking_description:
            entry = f"**BREAKING**: {entry} - {commit.breaking_description}"
        else:
            entry = f"**BREAKING**: {entry}"

    # Add commit hash reference
    entry = f"{entry} ({commit.hash})"

    lines.append(f"- {entry}")

    # Add body bullets as sub-items
    body_bullets = parse_body_bullets(commit.body)
    for bullet in body_bullets:
        lines.append(f"  - {bullet}")

    return "\n".join(lines)


def generate_changelog_section(commits: list[Commit]) -> str:
    """Generate a changelog section from commits."""
    # Group commits by category
    categories: dict[str, list[Commit]] = defaultdict(list)
    breaking_changes: list[Commit] = []

    for commit in commits:
        # Skip certain types
        if commit.type in SKIP_TYPES:
            continue

        # Map type to category
        category = TYPE_TO_CATEGORY.get(commit.type)
        if not category:
            continue

        categories[category].append(commit)

        # Track breaking changes separately
        if commit.is_breaking:
            breaking_changes.append(commit)

    # Generate output
    lines = []

    # Order: Breaking Changes first, then standard categories
    category_order = ["Added", "Changed", "Fixed", "Security", "Improved"]

    for category in category_order:
        if category not in categories:
            continue

        lines.append(f"### {category}")
        lines.append("")
        for commit in categories[category]:
            lines.append(format_changelog_entry(commit))
        lines.append("")

    return "\n".join(lines).rstrip()


def update_changelog(new_content: str) -> None:
    """Update CHANGELOG.md with new content under [Unreleased]."""
    if not CHANGELOG.exists():
        print(f"Error: {CHANGELOG} not found")
        sys.exit(1)

    content = CHANGELOG.read_text()

    # Find the [Unreleased] section and insert content after it
    unreleased_pattern = r"(## \[Unreleased\]\n)"
    replacement = f"\\1\n{new_content}\n"

    new_changelog = re.sub(unreleased_pattern, replacement, content, count=1)

    if new_changelog == content:
        print("Warning: Could not find [Unreleased] section in CHANGELOG.md")
        return

    CHANGELOG.write_text(new_changelog)
    print(f"Updated {CHANGELOG}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate changelog entries from conventional commits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--since",
        help="Generate changelog since this tag/ref (default: last tag)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview changelog entries without modifying files",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update CHANGELOG.md with generated entries",
    )

    args = parser.parse_args()

    # Determine the reference point
    since_ref = args.since
    if not since_ref:
        since_ref = get_latest_tag()
        if since_ref:
            print(f"Generating changelog since tag: {since_ref}")
        else:
            print("No tags found, generating changelog from all commits")

    # Get commits
    commits = get_commits_since(since_ref)

    if not commits:
        print("No conventional commits found")
        return

    # Filter out skipped types for reporting
    relevant_commits = [c for c in commits if c.type not in SKIP_TYPES]
    print(
        f"Found {len(commits)} commits, {len(relevant_commits)} relevant for changelog"
    )

    # Generate changelog section
    changelog_section = generate_changelog_section(commits)

    if not changelog_section.strip():
        print("No changelog entries generated (all commits may be skipped types)")
        return

    print("\n" + "=" * 60)
    print("Generated Changelog Entries:")
    print("=" * 60)
    print(changelog_section)
    print("=" * 60 + "\n")

    if args.update:
        update_changelog(changelog_section)
    elif not args.preview:
        print("Use --update to write to CHANGELOG.md, or --preview to just view")


if __name__ == "__main__":
    main()
