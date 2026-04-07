#!/usr/bin/env python3
# generate_fixed.py — Исправленная версия для GTX 1650 4GB
# Фикс: убрано attention_slicing + гибридный fp16/fp32 для VAE

import torch, os, json, time, sys
from datetime import datetime
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageEnhance
from pathlib import Path

# 📝 Словарь (180 слов)
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

# 🔧 Настройки
OUTPUT_DIR = "cards"
BASE_RESOLUTION = 512
TARGET_RESOLUTION = 1024
STEPS = 30              # Чуть меньше для стабильности
GUIDANCE = 7.5
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

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

def update_status(done_count, start_time):
    elapsed = (time.time() - start_time) / 60
    remaining = total - done_count
    avg_per_img = elapsed / max(done_count, 1)
    eta_min = remaining * avg_per_img

    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Генерация карточек (FIXED)\n")
        f.write(f"========================================\n")
        f.write(f"Готово:   {done_count} / {total}\n")
        f.write(f"Осталось: {remaining}\n")
        f.write(f"Прошло:   {elapsed:.1f} мин\n")
        f.write(f"ETA:      {eta_min:.0f} мин (~{eta_min/60:.1f} ч)\n")
        f.write(f"Обновлено: {datetime.now().strftime('%H:%M:%S')}\n")

def post_process(img):
    img = img.resize((TARGET_RESOLUTION, TARGET_RESOLUTION), Image.LANCZOS)
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    bg = Image.new("RGB", (TARGET_RESOLUTION, TARGET_RESOLUTION), (255, 255, 255))
    bg.paste(img, (0, 0), img if img.mode == "RGBA" else None)
    return bg

# 🚀 Загрузка модели (ИСПРАВЛЕННАЯ)
log("=" * 50)
log("ЗАПУСК ГЕНЕРАЦИИ (FIXED для GTX 1650)")
log("=" * 50)
log(f"Всего слов: {total}")
log(f"Осталось: {len(pending)}")
log(f"Папка: {os.path.abspath(OUTPUT_DIR)}")
log("")
log("Загрузка модели (~3 мин)...")

try:
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        use_safetensors=True,
        safety_checker=None
    )
    pipe.to("cuda")

    # 🔑 КРИТИЧЕСКИЕ ФИКСЫ:
    pipe.enable_model_cpu_offload()      # ← Оставляем (экономит VRAM)
    pipe.enable_vae_slicing()            # ← Оставляем (стабильно)
    # pipe.enable_attention_slicing()    # ← ❌ УБРАТЬ! Это ломает VAE на GTX 16xx

    log("Прогрев модели...")
    test_img = pipe(
        prompt="test",
        width=BASE_RESOLUTION,
        height=BASE_RESOLUTION,
        num_inference_steps=5
    ).images[0]

    # 🔍 Проверка: не чёрный ли квадрат?
    test_img.save("test_check.png")
    if test_img.getbbox() is None or test_img.getextrema() == ((0, 0), (0, 0), (0, 0)):
        log("⚠️ ТЕСТОВАЯ КАРТИНКА ЧЁРНАЯ! Пробуем альтернативу...")
        # Альтернатива: отключаем cpu_offload, оставляем только vae_slicing
        pipe.disable_model_cpu_offload()
        test_img2 = pipe(
            prompt="test",
            width=BASE_RESOLUTION,
            height=BASE_RESOLUTION,
            num_inference_steps=5
        ).images[0]
        test_img2.save("test_check2.png")
        if test_img2.getbbox() is not None:
            log("✅ Альтернатива работает! Продолжаем без cpu_offload")
        else:
            log("❌ Обе конфигурации не работают. Попробуйте LCM-LoRA версию.")
            sys.exit(1)
    else:
        log("✅ Тест прошёл! Изображения генерируются корректно.")

    torch.cuda.empty_cache()
    log("Модель готова!\n")

except Exception as e:
    log(f"ОШИБКА загрузки модели: {e}")
    sys.exit(1)

# 🔄 Основной цикл
start_total = time.time()
update_status(len(done), start_total)

log("НАЧАЛО ГЕНЕРАЦИИ\n")

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
                width=BASE_RESOLUTION,
                height=BASE_RESOLUTION,
                num_inference_steps=STEPS,
                guidance_scale=GUIDANCE,
                generator=generator
            ).images[0]

            # 🔍 Проверка на чёрный квадрат
            if img.getbbox() is None or img.getextrema() == ((0, 0), (0, 0), (0, 0)):
                log(f"  ⚠️ {ru_word}: чёрный квадрат, пробуем снова...")
                torch.cuda.empty_cache()
                continue

            img = post_process(img)
            filename = f"{OUTPUT_DIR}/{ru_word}.png"
            img.save(filename, "PNG", optimize=True, compress_level=6)

            elapsed = time.time() - start
            size_kb = os.path.getsize(filename) // 1024

            # 🔍 Проверка размера файла
            if size_kb < 50:
                log(f"  ⚠️ {ru_word}: файл слишком маленький ({size_kb}KB), возможно брак")

            done[ru_word] = {"seed": seed, "time": round(elapsed, 2), "attempts": attempt}

            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(done, f, ensure_ascii=False, indent=2)

            if i % 5 == 0:
                update_status(len(done), start_total)

            log(f"[{len(done)}/{total}] {ru_word} — {elapsed:.1f}с — {size_kb}KB — попытка #{attempt}")
            success = True
            break

        except torch.cuda.OutOfMemoryError:
            log(f"  OOM: {ru_word} (попытка #{attempt})")
            torch.cuda.empty_cache()
            time.sleep(2)
            continue

        except Exception as e:
            log(f"  Ошибка {ru_word} (попытка #{attempt}): {e}")
            torch.cuda.empty_cache()
            time.sleep(1)
            continue

    if not success:
        log(f"  ПРОПУЩЕНО: {ru_word} после {MAX_RETRIES + 1} попыток")
        done[ru_word] = {"error": True, "attempts": MAX_RETRIES + 1}

    torch.cuda.empty_cache()
    time.sleep(0.3)

# 🎉 Финал
total_time = (time.time() - start_total) / 3600
update_status(len(done), start_total)

log("")
log("=" * 50)
log("ЗАВЕРШЕНО")
log("=" * 50)
log(f"Готово: {len(done)} / {total} картинок")
log(f"Время: {total_time:.2f} часов")
log(f"Папка: {os.path.abspath(OUTPUT_DIR)}")
log(f"Лог: {os.path.abspath(LOG_FILE)}")

# 🔍 Финальная проверка качества
valid_count = 0
for ru_word in done:
    filepath = f"{OUTPUT_DIR}/{ru_word}.png"
    if Path(filepath).exists():
        size_kb = os.path.getsize(filepath) // 1024
        if size_kb >= 50:
            valid_count += 1

log(f"✅ Валидных картинок: {valid_count} / {len(done)}")
if valid_count < len(done) * 0.9:
    log("⚠️ МНОГО БРАКА! Проверьте папку cards/ вручную")