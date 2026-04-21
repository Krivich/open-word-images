#!/usr/bin/env python3
"""
GitHub Action Script (FIXED): Versions new images in styles/default only.
- ИГНОРИРУЕТ все папки кроме 'default' (до завершения миграции)
- Безопасно пропускает старые превью (_latest_*, _best_*, _vN)
- Генерирует превью в thumbs/{size}/
- Строит manifest v2
"""
import os, re, json, ast, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

SIZES = [128, 256, 512]
STYLES_ROOT = Path("styles")
MANIFEST_FILE = Path("manifest.json")

# 🛑 ЖЕСТКОЕ ОГРАНИЧЕНИЕ: Обрабатываем ТОЛЬКО default
# После миграции поменяйте на None, чтобы включить все стили
ALLOWED_STYLES = ["default"]

def is_allowed_style(style_name: str) -> bool:
    if ALLOWED_STYLES is None: return True
    return style_name in ALLOWED_STYLES

def parse_words_py(style_dir: Path) -> dict:
    """Parse words.py to extract prompts."""
    prompts = {}
    wp = style_dir / "words.py"
    if not wp.exists(): return prompts
    try:
        content = wp.read_text(encoding="utf-8")
        # Удаляем # комментарии, но не трогаем строки
        lines = []
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"): continue
            if "#" in line:
                m = re.match(r'(\s*"[^"]+"\s*:\s*"[^"]*")\s*(#.*)?$', line)
                lines.append(m.group(1) if m else line)
            else:
                lines.append(line)
        clean = "\n".join(lines)
        m = re.search(r'=\s*(\{.*\})', clean, re.DOTALL)
        if m: prompts = ast.literal_eval(m.group(1))
    except Exception as e:
        print(f"  ⚠️ words.py parse error in {style_dir.name}: {e}")
    return prompts

def is_skip_file(name: str) -> bool:
    """Пропускает версии, симлинки и старые превьюшки v1"""
    if any(s in name for s in ["_v", "_latest", "_best", "_128", "_256", "_512"]):
        return True
    return False

def process_new_images():
    """Find unversioned PNGs in ALLOWED styles, version them, update symlinks, generate thumbs."""
    new_files_found = False

    for style_dir in STYLES_ROOT.iterdir():
        if not style_dir.is_dir() or style_dir.name.startswith("."): continue
        if not is_allowed_style(style_dir.name): continue  # 🛑 SKIP

        prompts = parse_words_py(style_dir)
        thumbs_base = style_dir / "thumbs"

        for src in style_dir.glob("*.png"):
            if src.is_symlink(): continue
            if "thumbs" in src.parts: continue
            if is_skip_file(src.name): continue

            word = src.stem
            # Find max version
            max_v = 0
            for f in style_dir.glob(f"{word}_v*.png"):
                if f.is_symlink(): continue
                match = re.match(rf"{re.escape(word)}_v(\d+)\.png$", f.name)
                if match: max_v = max(max_v, int(match.group(1)))

            new_v = max_v + 1
            dest = style_dir / f"{word}_v{new_v}.png"

            # 1. Rename
            src.rename(dest)
            print(f"  📁 {style_dir.name}/{src.name} -> {dest.name}")
            new_files_found = True

            # 2. Symlinks
            latest_ln = style_dir / f"{word}_latest.png"
            best_ln   = style_dir / f"{word}_best.png"
            for ln in (latest_ln, best_ln):
                if ln.exists() or ln.is_symlink(): ln.unlink()
            latest_ln.symlink_to(dest.name)
            best_ln.symlink_to(dest.name)

            # 3. Thumbnails
            for size in SIZES:
                out_dir = thumbs_base / str(size)
                out_dir.mkdir(parents=True, exist_ok=True)
                out_file = out_dir / f"{word}_v{new_v}.png"

                if out_file.exists() and out_file.stat().st_mtime >= dest.stat().st_mtime:
                    continue

                try:
                    img = Image.open(dest).convert("RGBA")
                    img.thumbnail((size, size), Image.LANCZOS)
                    img.save(out_file, "PNG", optimize=True)
                except Exception as e:
                    print(f"  ⚠️ Thumb error {word}_{size}: {e}")

    return new_files_found

def build_manifest():
    """Scan ALLOWED styles and build manifest.json v2.0"""
    manifest = {
        "version": "2.0",
        "updated": datetime.now(timezone.utc).isoformat(),
        "concepts": {},
        "words": {},
        "metadata": {"total_concepts": 0, "total_versions": 0}
    }

    for style_dir in STYLES_ROOT.iterdir():
        if not style_dir.is_dir() or style_dir.name.startswith("."): continue
        if not is_allowed_style(style_dir.name): continue  # 🛑 SKIP

        style_name = style_dir.name
        prompts = parse_words_py(style_dir)

        versions_map = {}
        for f in style_dir.glob("*_v*.png"):
            if f.is_symlink(): continue
            m = re.match(r"(.+?)_v(\d+)\.png$", f.name)
            if m:
                word, v = m.group(1), int(m.group(2))
                versions_map.setdefault(word, []).append((v, f))

        for word, vers in versions_map.items():
            vers.sort(key=lambda x: x[0])
            max_v = vers[-1][0]

            if word not in manifest["concepts"]:
                manifest["concepts"][word] = {"default_style": style_name, "styles": {}}

            ver_list = []
            for v_num, v_file in vers:
                previews = {}
                for s in SIZES:
                    p = style_dir / "thumbs" / str(s) / f"{word}_v{v_num}.png"
                    if p.exists():
                        previews[str(s)] = f"{style_name}/thumbs/{s}/{word}_v{v_num}.png"

                # Промпт берем только для latest версии, остальные можно оставить пустыми или заполнить по желанию
                prompt = prompts.get(word, "") if v_num == max_v else ""

                ver_list.append({
                    "n": v_num,
                    "filename": v_file.name,
                    "path": f"{style_name}/{v_file.name}",
                    "prompt": prompt,
                    "created": datetime.fromtimestamp(v_file.stat().st_mtime, tz=timezone.utc).isoformat(),
                    "previews": previews
                })

            manifest["concepts"][word]["styles"][style_name] = {
                "latest": max_v,
                "versions": ver_list
            }

            lang = "eng" if style_name in ("eng", "flat") else ("rus" if "new" in style_name else style_name)
            manifest["words"][word] = {"concept": word, "language": lang, "pos": None}

    manifest["metadata"]["total_concepts"] = len(manifest["concepts"])
    manifest["metadata"]["total_versions"] = sum(
        len(s["versions"]) for c in manifest["concepts"].values() for s in c["styles"].values()
    )

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"📝 Manifest built: {manifest['metadata']['total_concepts']} concepts, {manifest['metadata']['total_versions']} versions.")

def main():
    print("🚀 Starting manifest processor v2 (RESTRICTED TO DEFAULT)...")
    changed = process_new_images()
    if changed or not MANIFEST_FILE.exists():
        build_manifest()
    else:
        print("✨ No new images. Manifest up to date.")
    print("✅ Done.")

if __name__ == "__main__":
    main()