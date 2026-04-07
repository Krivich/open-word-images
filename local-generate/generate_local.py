# generate_local.py — генерация карточек русских слов через SDXL
# Оптимизировано для GTX 1650 4GB VRAM

import torch, os, json
from diffusers import StableDiffusionXLPipeline
from PIL import Image, ImageOps
from pathlib import Path

# 📝 Русские слова → английский перевод для SDXL
WORDS = {
    "абрикос": "apricot", "авоська": "mesh bag", "автобус": "bus",
    "автомат": "machine gun", "автопилот": "autopilot", "ананас": "pineapple",
    "апельсин": "orange", "бабочка": "butterfly", "бак": "tank",
    "банки": "jars", "баночка": "small jar", "баранка": "bagel",
    "башмак": "boot", "бык": "bull", "веер": "fan",
    "велосипед": "bicycle", "велюр": "velour fabric", "веник": "broom",
    "весна": "spring season", "ветер": "wind", "вечер": "evening",
    "вещь": "thing object", "вилка": "fork", "вишня": "cherry",
    "волан": "shuttlecock", "год": "calendar year", "грач": "rook bird",
    "гриб": "mushroom", "дно": "bottom", "дождь": "rain",
    "дом": "house", "доска": "board", "доски": "boards",
    "доспехи": "armor", "дочь": "daughter", "дым": "smoke",
    "жук": "beetle", "зенит": "zenith", "змея": "snake",
    "зонтик": "umbrella", "зуб": "tooth", "карандаш": "pencil",
    "карман": "pocket", "картошка": "potato", "карусель": "carousel",
    "кит": "whale", "клип": "paper clip", "ключ": "key",
    "книга": "book", "книжка": "booklet", "ком": "clump lump",
    "кони": "horses", "конфеты": "candies", "коньки": "ice skates",
    "коробка": "box", "коробок": "matchbox", "корочка": "crust",
    "коса": "braid", "кот": "male cat", "кошка": "cat",
    "краб": "crab", "крошка": "crumb", "крупа": "groats cereal",
    "лак": "nail polish", "лама": "llama", "лампа": "lamp",
    "лапа": "paw", "лев": "lion", "лес": "forest",
    "лето": "summer", "лис": "fox", "лодка": "boat",
    "ложка": "spoon", "лото": "lotto", "лужа": "puddle",
    "лук": "onion", "луковица": "light bulb", "люлька": "cradle",
    "мак": "poppy flower", "малина": "raspberry", "мама": "mom",
    "мандарин": "mandarin", "мантия": "cloak", "маска": "mask",
    "машина": "car", "меч": "sword", "миска": "bowl",
    "мишка": "teddy bear", "мошка": "midge gnat", "мушка": "fly insect",
    "мышка": "mouse", "мясо": "meat", "мяч": "ball",
    "нос": "nose", "папа": "dad", "педаль": "pedal",
    "перец": "pepper", "перо": "feather", "персик": "peach fruit",
    "перчик": "chili pepper", "печка": "stove oven", "пират": "pirate",
    "пирог": "pie", "пирожное": "pastry cake", "пирожок": "small pie",
    "пища": "food", "плюшка": "sweet bun", "повар": "cook chef",
    "помидор": "tomato", "помощник": "assistant helper male",
    "помощница": "assistant helper female", "прогулка": "walk stroll",
    "пруд": "pond", "пружина": "spring coil", "прут": "twig rod",
    "птица": "bird", "птичка": "small bird", "пуговица": "button",
    "рак": "crayfish", "рама": "frame", "река": "river",
    "репа": "turnip", "речка": "small river", "рога": "horns",
    "роса": "dew drops", "рот": "mouth", "рука": "arm hand",
    "руль": "steering wheel", "рыба": "fish", "сало": "fat lard",
    "сани": "sled", "сапог": "high boot", "сверло": "drill bit",
    "светильник": "light fixture", "светлячок": "firefly", "светофор": "traffic light",
    "свеча": "candle", "свечка": "small candle", "сердце": "heart",
    "сестра": "sister", "сетка": "net mesh", "сказка": "fairy tale",
    "скакалка": "jump rope", "скала": "cliff rock", "скалолаз": "rock climber",
    "скачка": "horse race jump", "слон": "elephant", "слоны": "elephants",
    "снег": "snow", "снеговик": "snowman", "снежинка": "snowflake",
    "снежок": "snowball", "собака": "dog", "сова": "owl",
    "сок": "juice", "сом": "catfish", "сорока": "magpie bird",
    "сосна": "pine tree", "стол": "table", "стук": "knock tap",
    "стул": "chair", "сук": "tree branch", "суп": "soup",
    "сыр": "cheese", "телега": "cart wagon", "телескоп": "telescope",
    "телефон": "telephone", "телёнок": "calf", "точка": "dot point",
    "улица": "street", "фото": "photo", "хлеб": "bread",
    "череп": "skull", "черепашка": "turtle", "черника": "blueberry",
    "чернила": "ink", "экран": "screen", "экскаватор": "excavator",
    "эскалатор": "escalator", "эскимо": "ice cream bar"
}

PROMPT = "{word} icon for learning apps, flat vector style, thick black outline, white background, minimalist, no shading, primary colors red blue yellow green, educational clipart, isolated object, simple geometric shapes, clean lines, children illustration style"
NEGATIVE = "photorealistic, shading, gradients, shadows, textures, text, letters, watermark, blurry, deformed, complex background, people, faces"

OUTPUT_DIR = "cards"
RESOLUTION = 512
STEPS = 20
SEED = 42

os.makedirs(OUTPUT_DIR, exist_ok=True)

PROGRESS_FILE = "progress.json"
done = set()
if Path(PROGRESS_FILE).exists():
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        done = set(json.load(f))

pending = [w for w in WORDS if w not in done]
print(f"Осталось: {len(pending)} из {len(WORDS)} слов")

print("Загрузка модели...")
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
)
pipe.enable_model_cpu_offload()
pipe.enable_vae_slicing()
pipe.enable_attention_slicing()
print("Модель готова!")

for i, ru_word in enumerate(pending, 1):
    en_word = WORDS[ru_word]
    try:
        generator = torch.Generator("cuda").manual_seed(SEED + i)
        
        img = pipe(
            prompt=PROMPT.format(word=en_word),
            negative_prompt=NEGATIVE,
            width=RESOLUTION,
            height=RESOLUTION,
            num_inference_steps=STEPS,
            guidance_scale=7.5,
            generator=generator
        ).images[0]
        
        bg = Image.new("RGB", (RESOLUTION, RESOLUTION), (255, 255, 255))
        bg.paste(img, (0, 0), img if img.mode == "RGBA" else None)
        
        filename = f"{OUTPUT_DIR}/{ru_word}.png"
        bg.save(filename, "PNG", optimize=True)
        done.add(ru_word)
        
        if i % 10 == 0:
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(list(done), f, ensure_ascii=False)
        
        size_kb = os.path.getsize(filename) // 1024
        print(f"[{len(done)}/{len(WORDS)}] OK {ru_word} ({en_word}) — {size_kb} KB")
        
    except torch.cuda.OutOfMemoryError:
        print(f"OOM: {ru_word}, пропускаю")
        torch.cuda.empty_cache()
        continue
    except Exception as e:
        print(f"ERR {ru_word}: {e}")
        continue

with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
    json.dump(list(done), f, ensure_ascii=False)
print(f"Готово! {len(done)} картинок в '{OUTPUT_DIR}'")
