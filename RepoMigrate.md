# 🤖 AI AGENT RUNBOOK: v2 Image Manifest Migration
> **Target Environment:** GitHub Repo (`open-word-images`) | **Runner:** Ubuntu Latest | **Local OS:** Windows (migration script only)  
> **Purpose:** Provide full context, architecture, step-by-step execution plan, and recovery procedures for Qwen-Code CLI to safely migrate from v1 flat manifest to v2 hierarchical system.

---

## 🎯 Objective
Replace the legacy flat `manifest.json` and scattered thumbnail/version logic with a scalable, multilingual, version-tracked system where:
1. Each image version stores its own generation prompt.
2. Multilingual words map to a single `concept`.
3. Thumbnails are organized in `thumbs/{size}/`.
4. Symlinks (`_latest`, `_best`) resolve to optimal versions.
5. GitHub Actions automatically versions, links, thumbs, and builds `manifest.json` on push.

---

## 📊 Current vs Target State

| Aspect | 🟥 Current (v1) | 🟩 Target (v2) |
|--------|----------------|----------------|
| **Manifest** | Flat array `[{word, version, path}]` | Hierarchical `concepts → styles → versions` |
| **Prompts** | Lost after generation | Stored per-version + fallback from `words.py` |
| **Languages** | Split by folder (`eng/`, `new/`) | Unified in `default/`, tracked via `words.language` |
| **Thumbnails** | `_latest_128.png` in style root | `thumbs/128/`, `thumbs/256/`, `thumbs/512/` |
| **Versioning** | Manual or basic CI rename | Auto `_vN` on push, `latest`/`best` symlinks |
| **Symlinks** | Created locally (Win issues) | Created in Linux CI runner only |

---

## 🧩 Architecture & Key Components

### 1. `.github/workflows/update-manifest-v2.yml`
- **Triggers:** `push` to `styles/**/*.png`, manual dispatch
- **Runs:** `scripts/process_images.py`
- **Actions:** Versions unversioned `.png` → `_vN`, creates `_latest`/`_best` symlinks, generates `thumbs/`, rebuilds `manifest.json`
- **Safety:** Uses `git-auto-commit-action` or standard `git push` with `[skip ci]`

### 2. `scripts/process_images.py` (CI Runner)
- Scans `styles/*/` for bare `.png` files (no `_vN`, `_latest`, `_best`)
- Determines `max_version` → creates `_v{N+1}.png`
- Reads `words.py` in same folder for prompt injection
- Generates 128/256/512 previews in `thumbs/`
- Outputs v2 `manifest.json` with `concepts`, `words`, `metadata`

### 3. `scripts/migrate_all.py` (Local Windows)
- **DO NOT RUN IN CI**
- Disables old workflow (`update-manifest.yml` → `.yml.disabled`)
- Merges `words.py` from `styles/new` & `styles/eng`
- Copies bare `.png` files to `styles/default/` in batches (80 files/commit)
- Pushes to trigger CI for each batch
- Deletes old folders after success

### 4. `manifest.json` (v2 Schema Snippet)
```json
{
  "version": "2.0",
  "updated": "ISO-8601",
  "concepts": {
    "cat": {
      "default_style": "default",
      "styles": {
        "default": {
          "latest": 2,
          "best": 2,
          "versions": [
            {
              "n": 1,
              "filename": "cat_v1.png",
              "prompt": "cat, sitting...",
              "path": "default/cat_v1.png",
              "previews": {"128": "default/thumbs/128/cat_v1.png"}
            }
          ]
        }
      }
    }
  },
  "words": {
    "cat": {"concept": "cat", "language": "eng", "pos": null},
    "кошка": {"concept": "cat", "language": "rus", "pos": null}
  },
  "metadata": {"total_concepts": 0, "total_versions": 0}
}
```

---

## 📋 Execution Steps (Sequential)

### 🔹 Step 0: Pre-flight Checks
```bash
git status
git branch --show-current
ls styles/eng/ styles/new/ .github/workflows/update-manifest.yml
```
✅ Ensure you're on `main`, no uncommitted changes, old workflow exists.

### 🔹 Step 1: Deploy New Infrastructure
1. Add files to repo:
    - `.github/workflows/update-manifest-v2.yml`
    - `scripts/process_images.py`
    - `scripts/migrate_all.py`
2. Commit & push:
   ```bash
   git add .github/workflows/update-manifest-v2.yml scripts/process_images.py scripts/migrate_all.py
   git commit -m "feat: add v2 manifest infrastructure & migration script"
   git push origin main
   ```

### 🔹 Step 2: Run Local Migration
```bash
python scripts/migrate_all.py
```
⚠️ **DO NOT INTERRUPT.** Script will:
1. Disable old workflow
2. Merge `words.py`
3. Push batches to `styles/default/`
4. Delete `eng/` & `new/`

### 🔹 Step 3: Monitor CI
1. Open GitHub → **Actions** tab
2. Watch for `Update Manifest & Thumbnails` runs
3. Verify each run succeeds (`✓ Auto-versioned`, `✓ Manifest built`)
4. If a run fails, check logs, fix, and re-push a dummy commit to retry.

### 🔹 Step 4: Post-Migration Validation
```bash
# Check structure
find styles/default -name "*.png" | head -20
ls -l styles/default/*_latest.png  # Should show symlinks

# Validate manifest
python3 -c "
import json
m = json.load(open('manifest.json'))
assert m.get('version') == '2.0'
assert len(m.get('concepts', {})) > 0
print(f'✅ Valid v2 manifest: {len(m[\"concepts\"])} concepts, {len(m[\"words\"])} words')
"
```

---

## ✅ Validation Checklist
- [ ] `.github/workflows/update-manifest.yml` is renamed to `.yml.disabled`
- [ ] `styles/eng/` and `styles/new/` are deleted via `git rm`
- [ ] `styles/default/` contains versioned files, symlinks, `thumbs/`, `words.py`
- [ ] `manifest.json` has `version: "2.0"`, hierarchical `concepts`, `words` map
- [ ] Symlinks resolve correctly (`readlink styles/default/cat_latest.png`)
- [ ] Thumbnails exist in `thumbs/128/`, `thumbs/256/`, `thumbs/512/`
- [ ] CI runs pass with `[skip ci]` on manifest commits
- [ ] No duplicate or orphaned `_latest_*` files in root

---

## 🆘 Troubleshooting & Recovery

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| **CI fails on `os.symlink`** | Windows runner or permission issue | Ensure `runs-on: ubuntu-latest`. Script has `shutil.copy2` fallback. |
| **Manifest missing prompts** | `words.py` syntax error or wrong encoding | Validate with `ast.literal_eval()`. Check UTF-8 encoding. |
| **Batch push stuck/rejected** | Git conflict or large payload | Run `git pull --rebase`, then `python scripts/migrate_all.py` again. |
| **Old workflow still triggers** | `.yml.disabled` not committed | `git add .github/workflows/*.yml.disabled && git commit && git push` |
| **Manifest structure invalid** | Parser bug in `process_images.py` | Run `python3 -m json.tool manifest.json > /dev/null`. Check indentation & trailing commas. |
| **Need full rollback** | Migration corrupted state | `git revert HEAD~3..HEAD` or `git reset --hard <pre-migration-commit>` |

---

## 🧹 Post-Migration Cleanup
Once validation passes:
```bash
# Remove legacy scripts & disabled workflow
git rm .github/workflows/update-manifest.yml.disabled
git rm scripts/gen_manifest.py scripts/generate_thumbnails.py
git rm scripts/migrate_all.py

git commit -m "chore: remove v1 scripts & cleanup after migration"
git push origin main

# Force clean CI run
gh workflow run update-manifest-v2.yml
```

---

## 📜 Agent Notes & Constraints
1. **NEVER run `migrate_all.py` in CI.** It's Windows-local only. CI must only run `process_images.py`.
2. **Symlinks are Linux-only.** GitHub runner creates them. Local Windows users should ignore symlink warnings.
3. **`words.py` format is strict.** Must be `words = { "key": "value", ... }`. No trailing commas, valid Python dict syntax.
4. **Manifest is overwritten on each CI run.** Do not manually edit `manifest.json` except for `alias_of` or `best` overrides.
5. **Thumbnails path format:** `{style}/thumbs/{size}/{word}_v{N}.png`. Update frontend if it expects old `_latest_128.png` paths.
6. **If CI loops:** Add `[skip ci]` to commit messages. Verify workflow triggers match only `styles/default/**/*.png` after migration.

---
📝 **Next Steps for Agent:**
1. Verify repo state
2. Deploy `update-manifest-v2.yml`, `process_images.py`, `migrate_all.py`
3. Run `python scripts/migrate_all.py`
4. Monitor Actions tab, validate JSON, cleanup legacy files
5. Report success or attach logs if rollback needed

✅ **Ready to execute.**