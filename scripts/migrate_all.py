#!/usr/bin/env python3
"""
АВТОМАТИЧЕСКАЯ МИГРАЦИЯ v2
Запускается ОДИН РАЗ. Делает всё сама:
1. Отключает старый GitHub Action
2. Внедряет новый экшн и процессор
3. Мержит words.py из обеих папок
4. Копирует картинки батчами, коммитит и пушит
5. Ждёт CI между батчами
6. Удаляет старые папки
"""
import os, sys, re, ast, time, shutil, subprocess
from pathlib import Path

# 📍 НАСТРОЙКИ
STYLES_NEW = Path("styles/new")
STYLES_ENG   = Path("styles/eng")
STYLES_DEF   = Path("styles/default")
OLD_WF       = Path(".github/workflows/update-manifest.yml")
NEW_WF       = Path(".github/workflows/update-manifest-v2.yml")
PROC_SCRIPT  = Path("scripts/process_images.py")
BATCH_SIZE   = 80          # Файлов за коммит
CI_WAIT      = 6           # Секунд паузы между пушами

def git(args):
    """Безопасный вызов git (работает на Win + кириллица)"""
    cmd = ["git"] + args
    print(f"  🐢 {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def safe_commit_and_push(msg):
    git(["commit", "-m", msg])
    git(["push", "origin", "main"])
    print(f"  ✅ Pushed: {msg}")

def merge_words_py():
    """Мержит слова из new/ и eng/ в default/words.py"""
    merged = {}
    # Порядок важен: new перезаписывается eng при коллизиях (eng новее)
    for src in [STYLES_NEW / "words.py", STYLES_ENG / "words.py"]:
        if not src.exists(): continue
        try:
            m = re.search(r'words\s*=\s*(\{.*?\})', src.read_text(encoding="utf-8"), re.DOTALL)
            if m: merged.update(ast.literal_eval(m.group(1)))
        except Exception as e: print(f"  ⚠️ Пропуск {src}: {e}")

    # Формируем чистый файл
    lines = ["words = {"]
    for k, v in merged.items():
        lines.append(f'    "{k}": "{v}",')
    lines.append("}")

    # Дописываем хвост (NEGATIVE, BASE_PROMPT) из eng
    if (STYLES_ENG / "words.py").exists():
        tail = re.search(r'\}\s*(.*)', (STYLES_ENG / "words.py").read_text(encoding="utf-8"), re.DOTALL)
        if tail: lines.append(tail.group(1).strip())
    elif (STYLES_NEW / "words.py").exists():
        tail = re.search(r'\}\s*(.*)', (STYLES_NEW / "words.py").read_text(encoding="utf-8"), re.DOTALL)
        if tail: lines.append(tail.group(1).strip())

    target = STYLES_DEF / "words.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    git(["add", str(target)])
    safe_commit_and_push("chore: merge words.py prompts")

def migrate_folder(src_dir, batch_offset):
    if not src_dir.exists(): return 0
    # Только "чистые" PNG без версий и служебных суффиксов
    files = [f for f in src_dir.glob("*.png")
             if not f.is_symlink() and "_v" not in f.name
             and "_latest" not in f.name and "_best" not in f.name]
    if not files: return 0

    total = len(files)
    batches = (total // BATCH_SIZE) + (1 if total % BATCH_SIZE else 0)
    print(f"\n📦 {src_dir.name}: {total} файлов → ~{batches} батчей")

    for i in range(0, total, BATCH_SIZE):
        batch = files[i:i+BATCH_SIZE]
        b_num = batch_offset + (i // BATCH_SIZE)
        print(f"  📤 Батч {b_num}...")

        for f in batch:
            dest = STYLES_DEF / f.name
            if not dest.exists():  # Защита от затирания
                shutil.copy2(f, dest)

        git(["add", str(STYLES_DEF / "*.png")])
        git(["add", str(STYLES_DEF / "words.py")])
        safe_commit_and_push(f"migrate: {src_dir.name} batch {b_num}")

        if i + BATCH_SIZE < total:
            print(f"  ⏳ Пауза {CI_WAIT}с для стабильности CI...")
            time.sleep(CI_WAIT)
    return batches

def main():
    print("🚀 ЗАПУСК АВТОМИГРАЦИИ v2\n" + "="*40)

    # 0. Проверка пререквизитов
    if not NEW_WF.exists() or not PROC_SCRIPT.exists():
        print("❌ Положите в репозиторий update-manifest-v2.yml и process_images.py перед запуском!")
        sys.exit(1)

    print("1️⃣ Отключаю старый workflow...")
    if OLD_WF.exists():
        old_disabled = OLD_WF.with_suffix(".yml.disabled")
        OLD_WF.rename(old_disabled)
        git(["add", str(old_disabled)])
        safe_commit_and_push("chore: disable old v1 workflow")
    else:
        print("  ℹ️ Старый workflow уже отсутствует.")

    print("2️⃣ Внедряю новую инфраструктуру...")
    git(["add", str(NEW_WF), str(PROC_SCRIPT)])
    safe_commit_and_push("chore: add v2 workflow & image processor")

    print("3️⃣ Мержу промпты и создаю styles/default/...")
    STYLES_DEF.mkdir(parents=True, exist_ok=True)
    merge_words_py()

    print("4️⃣ Начинаю батч-миграцию картинок...")
    total_batches = 0
    # Сначала русские (были раньше), потом английские
    total_batches += migrate_folder(STYLES_NEW, 1)
    time.sleep(CI_WAIT + 2) # Дать CI догнать
    total_batches += migrate_folder(STYLES_ENG, total_batches + 1)

    print("5️⃣ Удаляю старые папки...")
    for d in [STYLES_NEW, STYLES_ENG]:
        if d.exists():
            shutil.rmtree(d)
            git(["rm", "-r", str(d)])
            safe_commit_and_push(f"chore: remove obsolete {d.name} folder")

    print("\n" + "="*40)
    print("🎉 МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
    print("💡 GitHub Actions сейчас обрабатывает последние коммиты.")
    print("📊 Через 2-5 минут появится manifest.json v2, симлинки и превью в thumbs/.")
    print("🔍 Проверьте вкладку Actions на зелёные галочки.")
    print("🗑️ Можно удалить scripts/migrate_all.py и старый .disabled workflow.")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка Git: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)