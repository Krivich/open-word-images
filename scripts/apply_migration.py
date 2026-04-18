#!/usr/bin/env python3
"""
apply_migration.py - Applies manifest-migration.json to manifest.json

================================================================================
📖 MIGRATION FORMAT & RULES
================================================================================

This script applies a recursive diff (manifest-migration.json) to manifest.json.
Only explicitly specified paths are modified. Everything else remains untouched.

CORE RULES:
  • null          → Delete the key (if it exists)
  • {}            → Keep current value unchanged (no-op marker)
  • dict          → Recursively merge with the existing object
  • list          → Apply sparse patching (see array rules below)
  • primitive     → Replace existing value or create a new key
  • Missing path  → Ignored (no action taken)
  • Keys starting with "_" → Skipped (reserved for metadata like _manifest_hash)

📦 ARRAY PATCHING RULES:
  • {}            → Keep the element at this index unchanged
  • null          → Delete the element at this index
  • dict/value    → Replace the existing element or append to the end
  • Deletions are processed in reverse order to prevent index shifting.

🛡️ SAFETY & CONFLICT DETECTION:
  • Include "_manifest_hash": "<sha256>" in the migration root to verify
    the manifest hasn't changed since the diff was created.
  • Use --skip-hash-check to bypass verification in CI/debug environments.

================================================================================
🛠 USAGE (CLI)
================================================================================

  python apply_migration.py [OPTIONS]

    --dry-run           Show planned changes without writing to disk
    --skip-hash-check   Ignore manifest hash verification
    --base-dir <path>   Project root directory (default: parent of script)
    --verbose           Enable detailed operation logging

  Example:
    python scripts/apply_migration.py --dry-run --verbose
"""

import json
import sys
import hashlib
import argparse
from pathlib import Path
from typing import Optional


def deep_merge(target: dict, source: dict) -> None:
    """
    Recursively merges source dict into target dict in-place.
    - null values in source delete the corresponding key in target.
    - Nested dicts are merged recursively.
    - Keys starting with '_' are ignored.
    """
    for key, value in source.items():
        if key.startswith("_"):
            continue
        if value is None:
            target.pop(key, None)
        elif isinstance(value, dict) and isinstance(target.get(key), dict):
            deep_merge(target[key], value)
        else:
            target[key] = value


def patch_array(target: list, diff: list) -> list:
    """
    Applies sparse patching to an array.
    - {}    → Keep element at index
    - null  → Delete element at index
    - dict  → Recursively merge with existing element
    - other → Replace or append element
    """
    res = target.copy()

    # 1️⃣ Replace & Append
    for i, patch in enumerate(diff):
        if isinstance(patch, dict) and not patch:  # {} = keep
            continue
        if patch is None:
            continue  # Deletions handled in pass 2

        if isinstance(patch, dict) and i < len(res) and isinstance(res[i], dict):
            deep_merge(res[i], patch)
        elif i < len(res):
            res[i] = patch
        else:
            res.append(patch)

    # 2️⃣ Delete (reverse order to preserve indices)
    for i in range(len(diff) - 1, -1, -1):
        if diff[i] is None and i < len(res):
            res.pop(i)

    return res


def apply_diff(node: dict, diff: dict, log_func: Optional[callable] = None) -> int:
    """
    Recursively applies a diff object to a target node.
    Returns the number of modified keys.
    """
    changes = 0
    for key, value in diff.items():
        if key.startswith("_"):
            continue

        if value is None:
            if key in node:
                node.pop(key)
                log_func and log_func(f"  🗑 DELETE: {key}")
                changes += 1
        elif isinstance(value, dict):
            if key not in node:
                node[key] = {}
            elif not isinstance(node[key], dict):
                node[key] = {}  # Type conflict resolution
                log_func and log_func(f"  📦 INIT_DICT: {key}")
            changes += apply_diff(node[key], value, log_func)
        elif isinstance(value, list):
            if isinstance(node.get(key), list):
                node[key] = patch_array(node[key], value)
                log_func and log_func(f"  🔄 PATCH_ARRAY: {key} ({len(value)} ops)")
                changes += 1
            else:
                node[key] = value
                changes += 1
        else:
            if node.get(key) != value:
                node[key] = value
                log_func and log_func(f"  ✏️  SET: {key} = {repr(value)[:50]}")
                changes += 1
    return changes


def compute_file_hash(path: Path) -> str:
    """Computes SHA-256 hash of a file."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Applies manifest-migration.json to manifest.json")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing to disk")
    parser.add_argument("--skip-hash-check", action="store_true", help="Skip manifest hash verification")
    parser.add_argument("--base-dir", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--verbose", action="store_true", default=True)
    args = parser.parse_args()

    manifest_path = args.base_dir / "manifest.json"
    migration_path = args.base_dir / "manifest-migration.json"

    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    if not migration_path.exists():
        print("ℹ️  manifest-migration.json not found. Nothing to apply.")
        sys.exit(0)

    # Load files
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(migration_path, "r", encoding="utf-8") as f:
        migration = json.load(f)

    # Hash check for conflict detection
    if not args.skip_hash_check and "_manifest_hash" in migration:
        current_hash = compute_file_hash(manifest_path)
        if current_hash != migration["_manifest_hash"]:
            print("❌ HASH MISMATCH! Manifest changed since migration was created.", file=sys.stderr)
            print(f"   Expected: {migration['_manifest_hash']}")
            print(f"   Found:    {current_hash}")
            print("   Use --skip-hash-check or regenerate the migration.", file=sys.stderr)
            sys.exit(2)

    # Apply diff
    logger = lambda m: print(f"[MIGRATE] {m}") if args.verbose else None
    logger("📦 Loading and applying migration...")
    changes = apply_diff(manifest, migration, log_func=logger)

    if changes == 0:
        logger("✅ No changes detected.")
        if not args.dry_run:
            migration_path.unlink()
        sys.exit(0)

    # Save or dry-run
    if args.dry_run:
        logger("🔍 DRY RUN COMPLETE. Files NOT saved.")
    else:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
            f.write("\n")
        migration_path.unlink()
        logger(f"✅ Migration applied successfully ({changes} changes).")

    print("\n📊 Summary:")
    print(f"   Changes applied : {changes}")


if __name__ == "__main__":
    main()