#!/usr/bin/env python3
# generate_lcm_quality.py — Генерация 180 карточек через LCM-LoRA
# РАБОЧАЯ ВЕРСИЯ для GTX 1650 4GB (без бага чёрных квадратов)
# Время: ~2-3 часа | VRAM: ~2.5 ГБ | Качество: 85-90%

import torch, os, json, time, sys
from datetime import datetime
from diffusers import StableDiffusionPipeline, LCMScheduler
from PIL import Image, ImageEnhance
from pathlib import Path

# 📝 Словарь: русское слово → английский промпт
WORDS = {
    "абрикос": "apricot fruit",
    "авоська": "string mesh shopping bag",
    "автобус": "city bus vehicle",
    "автомат": "submachine gun weapon",
    "автопилот": "airplane autopilot control panel",
    "ананас": "pineapple fruit",
    "апельсин": "orange citrus fruit",
    "бабочка": "colorful butterfly insect",
    "бак": "metal fuel tank",
    "банки": "glass jars with lids",
    "баночка": "small glass jar",
    "баранка": "ring-shaped bread bagel",
    "башмак": "leather boot shoe",
    "бык": "bull male cow",
    "веер": "folding hand fan",
    "велосипед": "bicycle bike",
    "велюр": "velour fabric texture swatch",
    "веник": "household broom",
    "весна": "spring season flowers blooming",
    "ветер": "wind blowing leaves",
    "вечер": "evening sunset sky",
    "вещь": "generic object item",
    "вилка": "metal dining fork",
    "вишня": "cherry fruit with stem",
    "волан": "badminton shuttlecock",
    "год": "calendar page showing year",
    "грач": "rook black bird",
    "гриб": "mushroom with cap",
    "дно": "bottom surface view",
    "дождь": "rain falling drops",
    "дом": "house building",
    "доска": "wooden plank board",
    "доски": "stack of wooden planks",
    "доспехи": "medieval knight armor",
    "дочь": "young girl daughter",
    "дым": "gray smoke wisps",
    "жук": "beetle insect",
    "зенит": "zenith sky overhead view",
    "змея": "snake coiled",
    "зонтик": "umbrella open",
    "зуб": "human tooth",
    "карандаш": "yellow pencil",
    "карман": "jeans pocket",
    "картошка": "potato tuber",
    "карусель": "merry-go-round carousel",
    "кит": "whale ocean animal",
    "клип": "metal paper clip",
    "ключ": "door key metal",
    "книга": "hardcover book",
    "книжка": "small paperback booklet",
    "ком": "snowball clump",
    "кони": "two horses standing",
    "конфеты": "assorted colorful candies",
    "коньки": "ice skates pair",
    "коробка": "cardboard box closed",
    "коробок": "matchbox with matches",
    "корочка": "bread crust slice",
    "коса": "long hair braid",
    "кот": "cat sitting",
    "кошка": "female cat",
    "краб": "crab sea animal",
    "крошка": "bread crumbs",
    "крупа": "buckwheat grains",
    "лак": "nail polish bottle",
    "лама": "llama animal",
    "лампа": "desk lamp lit",
    "лапа": "animal paw print",
    "лев": "lion male",
    "лес": "forest trees",
    "лето": "summer sunny day",
    "лис": "fox red",
    "лодка": "small rowing boat",
    "ложка": "metal spoon",
    "лото": "lotto bingo card",
    "лужа": "puddle water reflection",
    "лук": "onion vegetable",
    "луковица": "light bulb lamp",
    "люлька": "baby cradle hanging",
    "мак": "red poppy flower",
    "малина": "raspberry berry",
    "мама": "mother woman smiling",
    "мандарин": "mandarin orange fruit",
    "мантия": "wizard cloak robe",
    "маска": "theater mask",
    "машина": "car automobile",
    "меч": "medieval sword",
    "миска": "bowl for food",
    "мишка": "teddy bear plush",
    "мошка": "midge tiny fly",
    "мушка": "house fly insect",
    "мышка": "computer mouse",
    "мясо": "raw meat steak",
    "мяч": "soccer ball",
    "нос": "human nose profile",
    "папа": "father man smiling",
    "педаль": "bicycle pedal",
    "перец": "bell pepper vegetable",
    "перо": "white feather",
    "персик": "peach fruit",
    "перчик": "red chili pepper",
    "печка": "wood stove",
    "пират": "pirate with hat",
    "пирог": "fruit pie whole",
    "пирожное": "cupcake with frosting",
    "пирожок": "small baked pastry",
    "пища": "food plate",
    "плюшка": "sweet cinnamon bun",
    "повар": "chef with hat",
    "помидор": "tomato red",
    "помощник": "male assistant helper",
    "помощница": "female assistant helper",
    "прогулка": "person walking in park",
    "пруд": "small pond with water",
    "пружина": "metal spring coil",
    "прут": "thin tree branch twig",
    "птица": "bird flying",
    "птичка": "small songbird",
    "пуговица": "sewing button",
    "рак": "crayfish freshwater",
    "рама": "picture frame wooden",
    "река": "river flowing",
    "репа": "turnip root vegetable",
    "речка": "small stream river",
    "рога": "deer antlers",
    "роса": "morning dew on grass",
    "рот": "human mouth open",
    "рука": "human hand palm",
    "руль": "car steering wheel",
    "рыба": "fish swimming",
    "сало": "slice of pork fat",
    "сани": "wooden sled",
    "сапог": "tall leather boot",
    "сверло": "drill bit metal",
    "светильник": "wall lamp fixture",
    "светлячок": "glowing firefly",
    "светофор": "traffic light three colors",
    "свеча": "wax candle lit",
    "свечка": "small tea light candle",
    "сердце": "red heart shape",
    "сестра": "young girl sister",
    "сетка": "fishing net mesh",
    "сказка": "fairy tale storybook",
    "скакалка": "jump rope skipping",
    "скала": "rock cliff",
    "скалолаз": "person rock climbing",
    "скачка": "horse race galloping",
    "слон": "elephant large",
    "слоны": "group of elephants",
    "снег": "falling snowflakes",
    "снеговик": "snowman with carrot nose",
    "снежинка": "single snowflake crystal",
    "снежок": "hand-packed snowball",
    "собака": "dog sitting",
    "сова": "owl bird",
    "сок": "glass of orange juice",
    "сом": "catfish freshwater",
    "сорока": "magpie black and white bird",
    "сосна": "pine tree evergreen",
    "стол": "wooden table",
    "стук": "knocking hand on door",
    "стул": "wooden chair",
    "сук": "thick tree branch",
    "суп": "bowl of hot soup",
    "сыр": "wedge of yellow cheese",
    "телега": "wooden horse cart",
    "телескоп": "astronomical telescope",
    "телефон": "classic telephone handset",
    "телёнок": "baby calf",
    "точка": "black dot circle",
    "улица": "city street view",
    "фото": "photograph with frame",
    "хлеб": "loaf of bread",
    "череп": "human skull",
    "черепашка": "small turtle",
    "черника": "blueberry berries",
    "чернила": "ink bottle with quill",
    "экран": "computer monitor screen",
    "экскаватор": "yellow excavator construction",
    "эскалатор": "escalator stairs moving",
    "эскимо": "chocolate ice cream bar"
}

# 🎨 Промпт
BASE_PROMPT = "{word} icon for learning apps, flat vector style, thick black outline, white background, minimalist, no shading, primary colors red blue yellow green, educational clipart, isolated object, simple geometric shapes, clean lines, children illustration style, 2d vector art, sharp focus, high quality"
NEGATIVE = "photorealistic, shading, gradients, shadows, textures, text, letters, watermark, signature, blurry, deformed, complex background, people, faces, realistic, 3d render, photograph, noise, grain, extra details, low quality, worst quality"

# 🔧 Настройки: LCM-LoRA Quality для 4GB
OUTPUT_DIR = "cards"
RESOLUTION = 768       # Выше чем 512 = чётче контуры
STEPS = 8              # LCM работает за 4-8 шагов
GUIDANCE = 1.5         # Оптимально для LCM
SEED_BASE = 42
MAX_RETRIES = 2

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🔄 Прогресс
PROGRESS_FILE = "progress.json"
STATUS_FILE = "status.txt"
LOG_FILE = "generate.log"

done = {}
if Path(PROGRESS_FILE).exists():
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            done = json.load(f)
    except:
        pass

pending = [w for w in WORDS if w not in done]
total = len(WORDS)

# 📄 Логирование
def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

# 📄 Статус
def update_status(done_count, start_time):
    elapsed = (time.time() - start_time) / 60
    remaining = total - done_count
    avg_per_img = elapsed / max(done_count, 1)
    eta_min = remaining * avg_per_img

    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Генерация карточек (LCM-LoRA Quality)\n")
        f.write(f"========================================\n")
        f.write(f"Готово:   {done_count} / {total}\n")
        f.write(f"Осталось: {remaining}\n")
        f.write(f"Прошло:   {elapsed:.1f} мин\n")
        f.write(f"ETA:      {eta_min:.0f} мин (~{eta_min/60:.1f} ч)\n")
        f.write(f"Обновлено: {datetime.now().strftime('%H:%M:%S')}\n")

# 🎨 Пост-обработка
def post_process(img, target_size=1024):
    img = img.resize((target_size, target_size), Image.LANCZOS)
    img = ImageEnhance.Sharpness(img).enhance(1.3)
    bg = Image.new("RGB", (target_size, target_size), (255, 255, 255))
    bg.paste(img, (0, 0), img if img.mode == "RGBA" else None)
    return bg

# 🚀 Загрузка модели (LCM-LoRA — без бага чёрных квадратов)
log("=" * 60)
log("ЗАПУСК ГЕНЕРАЦИИ (LCM-LoRA Quality — 768×768, 8 шагов)")
log("=" * 60)
log(f"Всего слов: {total}")
log(f"Осталось: {len(pending)}")
log(f"Разрешение: {RESOLUTION}×{RESOLUTION}")
log(f"Шаги: {STEPS}")
log(f"Папка: {os.path.abspath(OUTPUT_DIR)}")
log("")
log("Загрузка модели (~2 мин)...")

try:
    # 🔑 КЛЮЧЕВОЕ: LCM-LoRA не имеет бага VAE на GTX 16xx
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float32,  # Всё в float32 — лечит NaN/Inf
        use_safetensors=True,
        safety_checker=None
    )

    # Добавляем LCM-LoRA
    pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5")
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    pipe.to("cuda")

    # 🔧 ФИКС для GTX 16xx: VAE в float32 — лечит NaN/Inf в декодере
    # Ставим ПОСЛЕ pipe.to("cuda"), чтобы типы совпали
    # ❌ НЕ используем cpu_offload — он ломает VAE на GTX 16xx
    pipe.enable_vae_slicing()
    # ❌ НЕ добавлять enable_attention_slicing() — ломает на GTX 16xx

    # 🔍 ТЕСТОВАЯ ГЕНЕРАЦИЯ (проверка перед запуском)
    log("🧪 Тестовая генерация (кот)...")
    test_img = pipe(
        prompt="cat sitting, flat vector style, thick black outline, white background",
        negative_prompt=NEGATIVE,
        width=RESOLUTION,
        height=RESOLUTION,
        num_inference_steps=STEPS,
        guidance_scale=GUIDANCE
    ).images[0]

    test_img.save("test_lcm_check.png")

    # Проверка на чёрный квадрат
    bbox = test_img.getbbox()
    extrema = test_img.getextrema()

    if bbox is None or (extrema[0] == (0, 0) and extrema[1] == (0, 0) and extrema[2] == (0, 0)):
        log("❌ ТЕСТОВАЯ КАРТИНКА ЧЁРНАЯ!")
        log("💡 Попробуйте: pip install --upgrade diffusers transformers")
        sys.exit(1)
    else:
        log(f"✅ Тест прошёл! Изображение: {test_img.size}, bbox={bbox}")

    torch.cuda.empty_cache()
    log("Модель готова!\n")

except Exception as e:
    log(f"❌ ОШИБКА загрузки модели: {type(e).__name__}: {e}")
    log("💡 Проверьте: pip install diffusers==0.24.0 huggingface_hub==0.19.4")
    sys.exit(1)

# 🔄 Основной цикл
start_total = time.time()
update_status(len(done), start_total)

log("▶️ НАЧАЛО ГЕНЕРАЦИИ\n")

for i, ru_word in enumerate(pending, 1):
    en_word = WORDS[ru_word]
    prompt = BASE_PROMPT.format(word=en_word)

    success = False
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            seed = SEED_BASE + i + (attempt - 1) * 1000
            generator = torch.Generator("cuda").manual_seed(seed)

            start = time.time()
            img = pipe(
                prompt=prompt,
                negative_prompt=NEGATIVE,
                width=RESOLUTION,
                height=RESOLUTION,
                num_inference_steps=STEPS,
                guidance_scale=GUIDANCE,
                generator=generator
            ).images[0]

            # 🔍 Проверка на чёрный квадрат (на всякий случай)
            if img.getbbox() is None:
                log(f"  ⚠️ {ru_word}: пустое изображение, пробуем снова...")
                torch.cuda.empty_cache()
                continue

            img = post_process(img)
            filename = f"{OUTPUT_DIR}/{ru_word}.png"
            img.save(filename, "PNG", optimize=True, compress_level=6)

            elapsed = time.time() - start
            size_kb = os.path.getsize(filename) // 1024

            # 🔍 Проверка размера файла
            if size_kb < 50:
                log(f"  ⚠️ {ru_word}: файл маленький ({size_kb}KB), возможен брак")

            done[ru_word] = {"seed": seed, "time": round(elapsed, 2), "attempts": attempt}

            # 💾 Чекпоинт каждые 5 слов
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(done, f, ensure_ascii=False, indent=2)

            if i % 5 == 0:
                update_status(len(done), start_total)

            log(f"[{len(done)}/{total}] {ru_word:<15} — {elapsed:5.1f}с — {size_kb:4}KB — попытка #{attempt}")
            success = True
            break

        except torch.cuda.OutOfMemoryError:
            log(f"  💥 OOM: {ru_word} (попытка #{attempt})")
            torch.cuda.empty_cache()
            time.sleep(2)
            # Пробуем с меньшим разрешением
            if attempt == 1:
                log(f"  ↓ Пробую 512×512 для {ru_word}")
                try:
                    seed = SEED_BASE + i + 5000
                    generator = torch.Generator("cuda").manual_seed(seed)
                    img = pipe(
                        prompt=prompt,
                        negative_prompt=NEGATIVE,
                        width=512, height=512,
                        num_inference_steps=STEPS,
                        guidance_scale=GUIDANCE,
                        generator=generator
                    ).images[0]
                    img = post_process(img)
                    img.save(f"{OUTPUT_DIR}/{ru_word}.png", "PNG", optimize=True)
                    done[ru_word] = {"seed": seed, "time": round(time.time() - start, 2), "attempts": attempt, "fallback": "512px"}
                    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                        json.dump(done, f, ensure_ascii=False, indent=2)
                    log(f"  ✓ {ru_word} — сохранён в 512×512")
                    success = True
                    break
                except:
                    continue
            continue

        except Exception as e:
            log(f"  ⚠️ {ru_word} (попытка #{attempt}): {type(e).__name__}: {e}")
            torch.cuda.empty_cache()
            time.sleep(1)
            continue

    if not success:
        log(f"  ✗ ПРОПУЩЕНО: {ru_word} после {MAX_RETRIES + 1} попыток")
        done[ru_word] = {"error": True, "attempts": MAX_RETRIES + 1}
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(done, f, ensure_ascii=False, indent=2)

    # 🔑 Очистка памяти после каждой итерации
    torch.cuda.empty_cache()
    time.sleep(0.3)

# 🎉 Финал
total_time = (time.time() - start_total) / 3600
update_status(len(done), start_total)

log("")
log("=" * 60)
log("✅ ЗАВЕРШЕНО")
log("=" * 60)
log(f"Готово: {len(done)} / {total} картинок")
log(f"Время: {total_time:.2f} часов")
log(f"Папка: {os.path.abspath(OUTPUT_DIR)}")
log(f"Лог: {os.path.abspath(LOG_FILE)}")
log(f"Статус: {os.path.abspath(STATUS_FILE)}")

# 🔍 Финальная проверка качества
valid_count = 0
small_files = []
for ru_word in done:
    filepath = f"{OUTPUT_DIR}/{ru_word}.png"
    if Path(filepath).exists():
        size_kb = os.path.getsize(filepath) // 1024
        if size_kb >= 50:
            valid_count += 1
        else:
            small_files.append((ru_word, size_kb))

log(f"\n📊 ВАЛИДАЦИЯ:")
log(f"  ✅ Валидных картинок: {valid_count} / {len(done)}")
if small_files:
    log(f"  ⚠️ Маленькие файлы (<50KB): {len(small_files)}")
    for word, size in small_files[:5]:
        log(f"     - {word}: {size}KB")
if valid_count >= len(done) * 0.95:
    log(f"\n🎉 ОТЛИЧНО! {valid_count/len(done)*100:.0f}% картинок валидны")
else:
    log(f"\n⚠️ ВНИМАНИЕ: Только {valid_count/len(done)*100:.0f}% валидны. Проверьте папку вручную.")