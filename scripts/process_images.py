#!/usr/bin/env python3
"""
GitHub Action Script (v3): Incremental Manifest Update & Versioning.
- Версионирует новые PNG в разрешённых стилях (по умолчанию только 'default')
- Генерирует превью в thumbs/{size}/
- ОБНОВЛЯЕТ manifest.json инкрементально (не пересоздаёт с нуля)
- НЕ создаёт и не трогает симлинки (передано в отдельный workflow)
- Сохраняет: best, status, planned_prompt, lang, words metadata и кастомные поля
"""
import os, re, json, ast
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

SIZES = [128, 256, 512]
STYLES_ROOT = Path("styles")
MANIFEST_FILE = Path("manifest.json")

# 🛑 Ограничение стиля. Поставьте None для обработки всех папок
ALLOWED_STYLES = ["default"]

def is_allowed_style(style_name: str) -> bool:
    if ALLOWED_STYLES is None: return True
    return style_name in ALLOWED_STYLES

def parse_words_py(style_dir: Path) -> dict:
    """Парсит words.py для получения промптов."""
    prompts = {}
    wp = style_dir / "words.py"
    if not wp.exists(): return prompts
    try:
        content = wp.read_text(encoding="utf-8")
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
    """Пропускает версии, симлинки и превьюшки."""
    return any(s in name for s in ["_v", "_latest", "_best", "_128", "_256", "_512"])

def process_new_images():
    """Версионирует новые картинки и генерирует превью. Симлинки НЕ создаёт."""
    new_files_found = False
    for style_dir in STYLES_ROOT.iterdir():
        if not style_dir.is_dir() or style_dir.name.startswith("."): continue
        if not is_allowed_style(style_dir.name): continue

        thumbs_base = style_dir / "thumbs"
        for src in style_dir.glob("*.png"):
            if src.is_symlink(): continue
            if "thumbs" in src.parts or "latest" in src.parts or "best" in src.parts: continue
            if is_skip_file(src.name): continue

            word = src.stem
            max_v = 0
            for f in style_dir.glob(f"{word}_v*.png"):
                if f.is_symlink(): continue
                match = re.match(rf"{re.escape(word)}_v(\d+)\.png$", f.name)
                if match: max_v = max(max_v, int(match.group(1)))

            new_v = max_v + 1
            dest = style_dir / f"{word}_v{new_v}.png"
            src.rename(dest)
            print(f"  📁 {style_dir.name}/{src.name} -> {dest.name}")
            new_files_found = True

            # Генерация превью
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

def update_manifest():
    """Загружает существующий манифест и аккуратно вплетает новые данные."""
    if MANIFEST_FILE.exists():
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load manifest: {e}. Starting fresh.")
            manifest = {}
    else:
        manifest = {}

    manifest.setdefault("version", "2.0")
    manifest.setdefault("concepts", {})
    manifest.setdefault("words", {})
    manifest.setdefault("styles", {})
    manifest.setdefault("metadata", {})

    total_versions = 0

    for style_dir in STYLES_ROOT.iterdir():
        if not style_dir.is_dir() or style_dir.name.startswith("."): continue
        if not is_allowed_style(style_dir.name): continue

        style_name = style_dir.name
        prompts = parse_words_py(style_dir)
        style_files = {}  # word -> [(v, path)]

        for f in style_dir.glob("*_v*.png"):
            if f.is_symlink(): continue
            if "thumbs" in f.parts or "latest" in f.parts or "best" in f.parts: continue
            m = re.match(r"(.+?)_v(\d+)\.png$", f.name)
            if m:
                word, v = m.group(1), int(m.group(2))
                style_files.setdefault(word, []).append((v, f))

        for word, vers in style_files.items():
            vers.sort(key=lambda x: x[0])
            max_v = vers[-1][0]

            # Инициализация концепта (только если отсутствует)
            if word not in manifest["concepts"]:
                manifest["concepts"][word] = {"default_style": style_name, "styles": {}}

            concept = manifest["concepts"][word]
            if not concept.get("default_style"):
                concept["default_style"] = style_name

            # Инициализация блока стиля (сохраняет best, status, planned_prompt и др.)
            if style_name not in concept["styles"]:
                concept["styles"][style_name] = {
                    "latest": None,
                    "best": None,
                    "status": "ready",
                    "versions": []
                }

            style_data = concept["styles"][style_name]
            style_data["latest"] = max_v  # latest всегда синхронизируется с диском

            # Безопасное слияние версий
            existing_versions = {v["n"]: v for v in style_data.get("versions", [])}

            for v_num, v_file in vers:
                if v_num not in existing_versions:
                    existing_versions[v_num] = {
                        "n": v_num,
                        "filename": v_file.name,
                        "path": f"{style_name}/{v_file.name}",
                        "prompt": prompts.get(word, "") if v_num == max_v else "",
                        "created": datetime.fromtimestamp(v_file.stat().st_mtime, tz=timezone.utc).isoformat(),
                        "previews": {}
                    }
                else:
                    ev = existing_versions[v_num]
                    ev["filename"] = v_file.name
                    ev["path"] = f"{style_name}/{v_file.name}"
                    if not ev.get("prompt") and v_num == max_v:
                        ev["prompt"] = prompts.get(word, "")
                    if "created" not in ev:
                        ev["created"] = datetime.fromtimestamp(v_file.stat().st_mtime, tz=timezone.utc).isoformat()

                # Пересчёт превью на основе файлов в папке
                previews = {}
                for s in SIZES:
                    p = style_dir / "thumbs" / str(s) / f"{word}_v{v_num}.png"
                    if p.exists():
                        previews[str(s)] = f"{style_name}/thumbs/{s}/{word}_v{v_num}.png"
                existing_versions[v_num]["previews"] = previews

            style_data["versions"] = sorted(existing_versions.values(), key=lambda x: x["n"])
            total_versions += len(style_data["versions"])

            # Добавление в words ТОЛЬКО если отсутствует (сохраняет lang, freq, cefr, alias_of, note)
            if word not in manifest["words"]:
                lang = "eng" if style_name in ("eng", "flat") else ("rus" if "new" in style_name else style_name)
                manifest["words"][word] = {"concept": word, "language": lang, "pos": None}

    # Обновление метаданных (сохраняет languages, styles_used, pending_concepts, build_engine)
    manifest["metadata"]["total_concepts"] = len(manifest["concepts"])
    manifest["metadata"]["total_versions"] = total_versions
    now_iso = datetime.now(timezone.utc).isoformat()
    manifest["metadata"]["last_build"] = now_iso
    manifest["updated"] = now_iso

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"📝 Manifest synced: {len(manifest['concepts'])} concepts, {total_versions} versions.")

def main():
    print("🚀 Starting manifest processor v3 (INCREMENTAL + NO SYMLINKS)...")
    process_new_images()
    # Запускаем всегда, чтобы подхватить изменения words.py и сохранить структуру
    update_manifest()
    print("✅ Done.")

if __name__ == "__main__":
    main()