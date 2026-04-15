#!/usr/bin/env python3
"""
БЕЗОПАСНАЯ МИГРАЦИЯ v2 (SMART SYNC)
- Проверяет статус GitHub Actions через API
- Фоллбэк: детектит изменения от CI по контенту (симлинки, thumbs, manifest)
- Авто-определение ветки, микро-батчи, безопасный парсинг words.py
"""
import os, sys, re, ast, time, shutil, subprocess, json, urllib.request
from pathlib import Path

SRC_FOLDERS = [Path("styles/new"), Path("styles/eng")]
DST_DIR = Path("styles/default")
OLD_WF = Path(".github/workflows/update-manifest.yml_bak")
CI_TIMEOUT = 300  # 5 минут максимум
BATCH_SIZE = 50
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY", "Krivich/open-word-images")  # owner/repo

def git(args, check=True):
    cmd = ["git"] + args
    print(f"  🐢 {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 and check:
        print(f"  ❌ Git error: {res.stderr.strip()}")
        sys.exit(1)
    return res.stdout.strip()

def get_branch():
    return git(["rev-parse", "--abbrev-ref", "HEAD"])

def get_current_sha():
    return git(["rev-parse", "HEAD"])


def detect_ci_changes(before_files):
    """
    Детектит, принёс ли git pull изменения от CI.
    before_files: set of file paths before pull
    Returns: True если появились новые файлы (симлинки, thumbs, manifest)
    """
    # Ожидаемые артефакты CI
    ci_artifacts = []
    for root, dirs, files in os.walk("styles"):
        for f in files:
            if "_latest.png" in f or "_best.png" in f:
                ci_artifacts.append(os.path.join(root, f))
            if "thumbs" in root and f.endswith(".png"):
                ci_artifacts.append(os.path.join(root, f))

    if Path("manifest.json").exists():
        ci_artifacts.append("manifest.json")

    after_files = set(ci_artifacts)
    new_artifacts = after_files - before_files

    if new_artifacts:
        print(f"  ✅ CI-артефакты обнаружены: {len(new_artifacts)} новых файлов")
        return True
    return False

def check_github_actions_status(commit_sha, workflow_name="update-manifest-v2.yml"):
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{workflow_name}/runs?head_sha={commit_sha}&per_page=1"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token: req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            runs = data.get("workflow_runs", [])
            if not runs: return None
            run = runs[0]
            status, conclusion = run.get("status"), run.get("conclusion")
            if status == "completed":
                return conclusion == "success"
            return False
    except Exception as e:
        if "403" in str(e): return "RATE_LIMIT"
        return None

def wait_for_ci(commit_sha):
    branch = get_branch()
    print(f"  ⏳ Ожидание завершения CI для коммита {commit_sha[:7]}...")
    t0 = time.time()
    api_failed = False

    while time.time() - t0 < CI_TIMEOUT:
        # 1. API Check (отключаемся после 403)
        if not api_failed:
            api_res = check_github_actions_status(commit_sha)
            if api_res is True:
                git(["fetch", "origin", branch])
                git(["pull", "--rebase", "origin", branch])
                print("  ✅ CI завершён (подтверждено API). Синхронизировано.")
                return True
            elif api_res is False:
                time.sleep(5)
                continue
            elif api_res == "RATE_LIMIT":
                api_failed = True
                print("  ⚠️ GitHub API rate limit. Переключаюсь на Git-мониторинг...")

        # 2. Git Fallback: проверяем только изменения, не спамим пуллами
        git(["fetch", "origin", branch], check=False)
        local_sha = git(["rev-parse", "HEAD"])
        remote_sha = git(["rev-parse", f"origin/{branch}"], check=False)

        if local_sha != remote_sha:
            print("  🔄 Обнаружены новые коммиты на сервере. Забираю...")
            try:
                git(["pull", "--rebase", "origin", branch])
                # Проверяем, что CI действительно отработал (появились артефакты)
                if Path("manifest.json").exists() or any(Path("styles/default").glob("thumbs/*/*.png")):
                    print("  ✅ CI завершён (артефакты найдены). Готово.")
                    return True
                else:
                    print("  ⚠️ Сервер обновился, но артефактов CI пока нет. Жду...")
            except Exception as e:
                print(f"  ❌ Ошибка pull: {e}")
                input("Разрешите конфликты вручную и нажмите Enter...")
                return True

        # Тихий прогресс
        elapsed = int(time.time() - t0)
        if elapsed % 30 == 0 and elapsed > 0:
            print(f"  ⏳ Всё ещё ждём... ({elapsed}с прошло)")
        time.sleep(5)

    print(f"  ⚠️ Таймаут ({CI_TIMEOUT}с). Проверьте вкладку Actions.")
    return False

def parse_words_py(filepath):
    """Безопасный парсинг words.py с поддержкой комментариев и многострочных строк"""
    if not filepath.exists():
        return {}, ""

    content = filepath.read_text(encoding="utf-8")

    # Удаляем однострочные комментарии вне строк
    lines = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue  # Полностью комментарий
        # Убираем # только если он после закрывающей кавычки значения
        if "#" in line:
            # Простая эвристика: ищем паттерн "ключ": "значение" # комментарий
            m = re.match(r'(\s*"[^"]+"\s*:\s*"[^"]*")\s*(#.*)?$', line)
            if m:
                lines.append(m.group(1))
            else:
                lines.append(line)
        else:
            lines.append(line)

    clean = "\n".join(lines)

    # ЖАДНЫЙ режим для многострочного dict
    m = re.search(r'words\s*=\s*(\{.*\})', clean, re.DOTALL)
    if not m:
        print(f"  ⚠️ Не удалось найти words dict в {filepath}")
        return {}, ""

    try:
        words_dict = ast.literal_eval(m.group(1))
    except Exception as e:
        print(f"  ⚠️ Ошибка парсинга {filepath}: {e}")
        # Показываем фрагмент для отладки
        snippet = m.group(1)[:300] + "..." if len(m.group(1)) > 300 else m.group(1)
        print(f"  🔍 Фрагмент: {snippet}")
        return {}, ""

    # Сохраняем хвост файла (NEGATIVE, BASE_PROMPT и т.д.)
    tail = clean[m.end():].strip()
    return words_dict, tail

def prepare_words_py():
    target = DST_DIR / "words.py"
    merged = {}
    tail = ""

    for src in [Path("styles/new/words.py"), Path("styles/eng/words.py")]:
        if not src.exists(): continue
        words, src_tail = parse_words_py(src)
        merged.update(words)  # eng перезапишет new при коллизиях
        if src_tail: tail = src_tail

    lines = ["words = {"]
    for k, v in merged.items():
        # Экранируем кавычки и переносы в промптах
        safe_v = v.replace('"', '\\"').replace('\n', ' ').replace('\r', '')
        lines.append(f'    "{k}": "{safe_v}",')
    lines.append("}")
    if tail:
        lines.append(f"\n{tail}")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")

    print(f"  📝 Merged {len(merged)} prompts.")
    git(["add", str(target)])
    git(["commit", "-m", "chore: init default/words.py"])
    sha = get_current_sha()
    git(["push", "origin", get_branch()])
    wait_for_ci(sha)

def migrate_version(src_dir, ver):
    files = [f for f in src_dir.glob(f"*_v{ver}.png") if not f.is_symlink()]
    if not files: return

    files.sort(key=lambda x: x.name)

    for i in range(0, len(files), BATCH_SIZE):
        batch = files[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(files) + BATCH_SIZE - 1) // BATCH_SIZE

        copied = 0
        for src in batch:
            dst_name = re.sub(r'_v\d+\.png$', '.png', src.name)
            dst = DST_DIR / dst_name
            if dst.exists():
                continue
            shutil.copy2(src, dst)
            git(["add", str(dst)])
            copied += 1

        if copied == 0:
            continue

        git(["commit", "-m", f"migrate: {src_dir.name} v{ver} batch {batch_num}/{total_batches}"])
        sha = get_current_sha()
        git(["push", "origin", get_branch()])
        print(f"  🚀 v{ver} batch {batch_num} sent. Waiting CI...")
        wait_for_ci(sha)

def main():
    print("🛡️ МИГРАЦИЯ v2 (SMART SYNC)\n" + "="*40)
    DST_DIR.mkdir(parents=True, exist_ok=True)
    git(["config", "pull.rebase", "true"])
    branch = get_branch()
    print(f"📍 Branch: {branch}")
    print(f"🔗 Repo: {GITHUB_REPO}")

    # 1. Отключаем старый экшн
    if OLD_WF.exists():
        disabled = OLD_WF.with_suffix(".yml.disabled")
        OLD_WF.rename(disabled)
        git(["add", str(disabled)])
        git(["commit", "-m", "chore: disable old workflow"])
        sha = get_current_sha()
        git(["push", "origin", branch])
        wait_for_ci(sha)

    # 2. Готовим words.py
    if not (DST_DIR / "words.py").exists():
        print("\n📝 Подготовка words.py...")
        prepare_words_py()

    # 3. Цикл по папкам -> версиям
    for src in SRC_FOLDERS:
        if not src.exists():
            print(f"\n⚠️ {src} not found. Skip.")
            continue
        print(f"\n📂 === {src.name} ===")

        versions = set()
        for f in src.glob("*.png"):
            if f.is_symlink(): continue
            m = re.search(r'_v(\d+)\.png$', f.name)
            if m: versions.add(int(m.group(1)))

        if not versions:
            print("  ℹ️ No versions found.")
            continue

        for ver in sorted(versions):
            print(f"\n🔹 Version v{ver}")
            migrate_version(src, ver)

    # 4. Удаляем старые папки
    print("\n🧹 Cleaning up old folders...")
    for src in SRC_FOLDERS:
        if src.exists():
            shutil.rmtree(src)
            git(["rm", "-r", str(src)])
            git(["commit", "-m", f"chore: remove {src.name}"])
            sha = get_current_sha()
            git(["push", "origin", branch])
            wait_for_ci(sha)

    print("\n" + "="*40)
    print("🎉 MIGRATION COMPLETE!")
    print("📊 Check Actions tab for final green checks.")
    print("🗑️ You can now delete migrate_all.py and .yml.disabled")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Interrupted. State saved. Re-run to continue.")
    except Exception as e:
        print(f"\n❌ Critical: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)