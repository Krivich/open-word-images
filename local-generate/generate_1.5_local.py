# generate_light.py
# Модель: SD 1.5 + LCM-LoRA | Разрешение: 512×512 | Шаги: 4 | Память: ~2.5 ГБ
# Для: GTX 1650 4GB, работает из РФ, бесплатно

import torch, os, json, time
from diffusers import StableDiffusionPipeline, LCMScheduler
from PIL import Image
from pathlib import Path

# 🎨 Промпты: 180 слов с уточнениями для flat-vector стиля
# Формат: "ключ_файла": "точный английский промпт"
WORDS = {
    "apricot": "apricot fruit, single object",
    "avoska": "string mesh bag, russian shopping bag, empty",
    "bus": "city bus, side view, simple",
    "automat": "submachine gun, simplified icon",  # или "vending machine" если нужен торговый автомат
    "autopilot": "steering wheel with auto symbol, icon",
    "pineapple": "pineapple fruit, whole",
    "orange": "orange fruit, whole with leaf",
    "butterfly": "butterfly insect, wings spread, symmetrical",
    "tank": "water tank, cylindrical, simple",
    "jars": "glass jars, two pieces, empty",
    "small_jar": "single small glass jar with lid",
    "bagel": "russian bagel baranka, ring shaped bread",
    "boot": "leather boot, side view",
    "bull": "bull animal, standing, simplified",
    "fan": "hand fan, folded, traditional",
    "bicycle": "bicycle, side view, simple line art",
    "velour": "velour fabric swatch, folded, texture hint",
    "broom": "household broom, wooden handle",
    "spring_season": "spring season symbol: flower + sun, icon",
    "wind": "wind symbol: curved lines + leaf, icon",
    "evening": "evening symbol: moon + stars, simple",
    "object": "generic object, cube shape, simple",
    "fork": "dining fork, side view",
    "cherry": "two cherries with stem, red",
    "shuttlecock": "badminton shuttlecock, feathered",
    "year": "calendar page showing number 1, icon",
    "rook_bird": "rook bird, black, standing",
    "mushroom": "mushroom with red cap and white dots",
    "bottom": "bottom surface, flat plane with shadow",
    "rain": "rain symbol: cloud + drops, icon",
    "house": "simple house, front view, chimney",
    "board": "wooden board, rectangular, plank",
    "boards": "three wooden planks stacked",
    "armor": "medieval knight armor, chest plate, icon",
    "daughter": "little girl silhouette, simple, no face details",
    "smoke": "smoke wisps, gray, abstract icon",
    "beetle": "ladybug beetle, red with black spots",
    "zenith": "zenith symbol: arrow pointing up to sun",
    "snake": "snake coiled, simple, no details",
    "umbrella": "umbrella, open, side view",
    "tooth": "human tooth, white, simple",
    "pencil": "yellow pencil with eraser, diagonal",
    "pocket": "shirt pocket, front view, with stitch",
    "potato": "potato tuber, brown, whole",
    "carousel": "carousel merry-go-round, simple, one horse",
    "whale": "whale, side view, spouting water",
    "paper_clip": "metal paper clip, silver, simple",
    "key": "door key, classic shape, metal",
    "book": "closed hardcover book, side view",
    "booklet": "small booklet, closed, simple",
    "clump": "clump of snow or earth, rounded",
    "horses": "two horses, simplified, side view",
    "candies": "three wrapped candies, colorful",
    "ice_skates": "pair of ice skates, white boots",
    "box": "cardboard box, closed, simple",
    "matchbox": "matchbox, closed, with striker strip",
    "crust": "slice of bread with crust, simple",
    "braid": "hair braid, three-strand, simple",
    "cat_male": "cat, sitting, simple outline",
    "cat_female": "cat with bow, sitting, simple",
    "crab": "crab, front view, claws up",
    "crumb": "bread crumb, small irregular shape",
    "cereal": "bowl of cereal grains, simple",
    "nail_polish": "nail polish bottle with brush",
    "llama": "llama animal, side view, fluffy",
    "lamp": "desk lamp, adjustable arm, simple",
    "paw": "animal paw print, four toes",
    "lion": "lion head, mane, simplified icon",
    "forest": "forest symbol: three pine trees",
    "summer": "summer symbol: sun + palm tree icon",
    "fox": "fox, sitting, bushy tail",
    "boat": "small rowboat, side view",
    "spoon": "table spoon, side view",
    "lotto": "lotto ball with number 7, simple",
    "puddle": "puddle of water, oval with reflection hint",
    "onion": "onion bulb, whole with roots",
    "light_bulb": "incandescent light bulb, classic shape",
    "cradle": "baby cradle, wooden, rocking",
    "poppy": "poppy flower, red petals, black center",
    "raspberry": "raspberry fruit, detailed drupelets",
    "mom": "woman silhouette with heart, simple",
    "mandarin": "mandarin orange with leaf, whole",
    "cloak": "wizard cloak with hood, draped",
    "mask": "theater mask, comedy/tragedy, simple",
    "car": "car, side view, simplified",
    "sword": "medieval sword, straight blade, simple",
    "bowl": "ceramic bowl, empty, top view",
    "teddy_bear": "teddy bear, sitting, simple",
    "midge": "tiny flying insect, simple dot+wings",
    "fly": "house fly insect, wings spread",
    "mouse": "mouse animal, side view, long tail",
    "meat": "piece of meat, steak shape, simple",
    "ball": "sports ball, spherical with seams",
    "nose": "human nose profile, simple outline",
    "dad": "man silhouette with tie, simple",
    "pedal": "bicycle pedal, side view",
    "pepper": "bell pepper, red, whole",
    "feather": "bird feather, white, detailed barbs",
    "peach": "peach fruit, with leaf, fuzzy hint",
    "chili": "red chili pepper, curved",
    "stove": "kitchen stove, four burners, simple",
    "pirate": "pirate hat with skull, icon",
    "pie": "whole pie in dish, crimped crust",
    "cupcake": "cupcake with swirl frosting, simple",
    "small_pie": "hand-held pie, empanada style",
    "food": "plate with fork+knife, icon",
    "bun": "sweet bun with raisins, rounded",
    "chef": "chef hat, tall white, icon",
    "tomato": "tomato, red, whole with stem",
    "assistant_m": "person with clipboard, male silhouette",
    "assistant_f": "person with clipboard, female silhouette",
    "walk": "walking person + tree, park icon",
    "pond": "small pond with reeds, oval",
    "spring_coil": "metal spring coil, compressed",
    "twig": "small twig with two leaves",
    "bird": "generic bird in flight, simple",
    "small_bird": "small bird perched, simple",
    "button": "sewing button, four holes, round",
    "crayfish": "crayfish, claws up, simplified",
    "frame": "picture frame, rectangular, empty",
    "river": "river winding through landscape, icon",
    "turnip": "turnip vegetable, purple top, white bottom",
    "small_river": "narrow stream, simple blue line",
    "horns": "pair of curved animal horns",
    "dew": "dew drops on grass blade, icon",
    "mouth": "human mouth, smiling, simple",
    "hand": "human hand, open palm, simple",
    "steering_wheel": "car steering wheel, circular",
    "fish": "fish, side view, simple fins",
    "pork_fat": "slice of salo pork fat, white with rind",
    "sled": "wooden sled, runners, simple",
    "high_boot": "knee-high boot, side view",
    "drill_bit": "metal drill bit, spiral, simple",
    "light_fixture": "ceiling light fixture, simple",
    "firefly": "firefly with glowing abdomen, night",
    "traffic_light": "traffic light, three circles vertical",
    "candle": "tall candle with flame, simple",
    "small_candle": "short candle, tealight style",
    "heart": "heart shape, classic, red",
    "sister": "two girls holding hands, silhouettes",
    "net": "fishing net, mesh pattern, simple",
    "fairy_tale": "open book with magic sparkles, icon",
    "jump_rope": "jump rope, mid-swing, simple",
    "cliff": "rock cliff, vertical face, simple",
    "climber": "rock climber on wall, silhouette",
    "horse_race": "horse jumping over hurdle, icon",
    "elephant": "elephant, side view, trunk up",
    "elephants": "two elephants, adult + baby",
    "snow": "snow symbol: snowflake + ground, icon",
    "snowman": "snowman with hat and scarf, simple",
    "snowflake": "snowflake, six-pointed, symmetrical",
    "snowball": "snowball, spherical with texture hint",
    "dog": "dog, sitting, friendly, simple",
    "owl": "owl, front view, big eyes, simple",
    "juice": "glass of juice with straw, orange",
    "catfish": "catfish, whiskers, side view",
    "magpie": "magpie bird, black and white",
    "pine_tree": "pine tree, triangular, simple",
    "table": "dining table, four legs, top view hint",
    "knock": "hand knocking on door, icon",
    "chair": "simple chair, four legs, backrest",
    "branch": "tree branch with two twigs",
    "soup": "bowl of soup with steam, simple",
    "cheese": "wedge of cheese with holes",
    "cart": "wooden cart, two wheels, simple",
    "telescope": "telescope on tripod, side view",
    "telephone": "retro telephone with dial, icon",
    "calf": "baby cow, standing, simple",
    "dot": "single black dot, centered",
    "street": "street with sidewalk, perspective lines",
    "photo": "photograph frame with landscape inside",
    "bread": "loaf of bread, sliced end visible",
    "skull": "human skull, front view, simplified",
    "turtle": "turtle, top view, shell pattern",
    "blueberry": "cluster of three blueberries",
    "ink": "ink bottle with quill pen, vintage",
    "screen": "computer screen, blank, simple",
    "excavator": "excavator vehicle, side view, arm up",
    "escalator": "escalator stairs, moving, side view",
    "ice_cream_bar": "ice cream bar on stick, chocolate coated"
}

BASE_PROMPT = "{desc}, icon for learning apps, flat vector style, thick black outline 3px, white background, minimalist, no shading, primary colors red blue yellow green, educational clipart, isolated object, simple geometric shapes, clean lines, children illustration style"
NEGATIVE = "photorealistic, shading, gradients, shadows, textures, text, letters, watermark, blurry, deformed, complex background, people, faces, realistic, 3d, detailed, noisy"

# 🔧 Настройки
OUTPUT_DIR = "cards"
RESOLUTION = 512  # Если OOM — снизить до 384
STEPS = 4         # LCM работает за 4 шага!
GUIDANCE = 1.0    # Для LCM
SEED_BASE = 42

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🔄 Чекпоинт
PROGRESS_FILE = "progress.json"
done = set()
if Path(PROGRESS_FILE).exists():
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        done = set(json.load(f))
pending = [w for w in WORDS if w not in done]
print(f"📦 Осталось: {len(pending)} из {len(WORDS)} слов")

# 🚀 Загрузка модели
print("⏳ Загрузка модели (~2 мин)...")
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
    use_safetensors=True,
    safety_checker=None
)
pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5")
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
pipe.to("cuda")

# 🔑 Оптимизации для 4 ГБ
pipe.enable_model_cpu_offload()
pipe.enable_vae_slicing()
pipe.enable_attention_slicing()
print("✅ Модель готова!")

# 🔄 Генерация
for i, word_key in enumerate(pending, 1):
    desc = WORDS[word_key]
    prompt = BASE_PROMPT.format(desc=desc)

    try:
        generator = torch.Generator("cuda").manual_seed(SEED_BASE + i)
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

        elapsed = time.time() - start

        # Белый фон
        bg = Image.new("RGB", (RESOLUTION, RESOLUTION), (255, 255, 255))
        bg.paste(img, (0, 0), img if img.mode == "RGBA" else None)

        filename = f"{OUTPUT_DIR}/{word_key}.png"
        bg.save(filename, "PNG", optimize=True)
        done.add(word_key)

        if i % 10 == 0:
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(list(done), f, ensure_ascii=False)

        size_kb = os.path.getsize(filename) // 1024
        print(f"[{len(done)}/{len(WORDS)}] ✓ {word_key} | {elapsed:.1f}с | {size_kb}KB")

    except torch.cuda.OutOfMemoryError:
        print(f"⚠️ OOM: {word_key}, пробую 384×384...")
        torch.cuda.empty_cache()
        try:
            img = pipe(
                prompt=prompt,
                negative_prompt=NEGATIVE,
                width=384, height=384,
                num_inference_steps=STEPS,
                guidance_scale=GUIDANCE,
                generator=torch.Generator("cuda").manual_seed(SEED_BASE + i + 1000)
            ).images[0]
            bg = Image.new("RGB", (384, 384), (255, 255, 255))
            bg.paste(img, (0, 0), img if img.mode == "RGBA" else None)
            bg = bg.resize((RESOLUTION, RESOLUTION), Image.LANCZOS)
            bg.save(f"{OUTPUT_DIR}/{word_key}.png", "PNG", optimize=True)
            done.add(word_key)
            print(f"  └─ ✓ пересгенерировано в 384×384 → апскейл")
        except Exception as e2:
            print(f"  └─ ✗ Пропускаю: {e2}")
        continue
    except Exception as e:
        print(f"⚠️ {word_key}: {e}")
        continue

with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
    json.dump(list(done), f, ensure_ascii=False)
print(f"\n🎉 Готово! {len(done)} картинок в '{OUTPUT_DIR}'")