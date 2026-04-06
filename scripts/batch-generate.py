#!/usr/bin/env python3
"""
Batch generator for open-word-images
For "good samaritans" who want to generate multiple images at once
"""

import json
import os
import requests
from openai import OpenAI

def main():
    print("🎨 open-word-images Batch Generator")
    print("=" * 40)

    api_token = input("Enter OpenAI API token: ").strip()
    style = input("Style (flat/pixel/sketch) [flat]: ").strip() or "flat"
    batch_size = int(input("How many words to generate? [10]: ").strip() or "10")

    client = OpenAI(api_key=api_token)

    # Load dictionary
    try:
        with open('dictionary.json', 'r') as f:
            dictionary = json.load(f)
        print(f"✅ Loaded {len(dictionary)} words from dictionary")
    except:
        print("❌ dictionary.json not found")
        return

    # Load manifest
    try:
        with open('manifest.json', 'r') as f:
            manifest = json.load(f)
        existing = set(img['word'] for img in manifest)
        print(f"✅ {len(existing)} words already have images")
    except:
        existing = set()
        print("⚠️ No manifest.json found")

    # Find missing words
    missing = [w[0] for w in dictionary if w[0] not in existing][:batch_size]
    print(f"🎯 Will generate {len(missing)} missing words")

    # Load style prompt
    try:
        with open(f'styles/{style}/STYLE_PROMPT.md', 'r') as f:
            prompt_text = f.read()
        base_prompt = prompt_text.split('```')[1].strip() if '```' in prompt_text else prompt_text
    except:
        base_prompt = f"[OBJECT] icon, flat vector style, thick black outline, white background"

    # Generate
    os.makedirs(f'styles/{style}', exist_ok=True)

    for word in missing:
        print(f"\n Generating: {word}...")
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=f"{word} icon, {base_prompt}",
                size="1024x1024",
                n=1
            )
            image_url = response.data[0].url
            img_data = requests.get(image_url).content

            filename = f'styles/{style}/{word}_v1.png'
            with open(filename, 'wb') as f:
                f.write(img_data)

            print(f"✅ Saved: {filename}")
        except Exception as e:
            print(f"❌ Failed: {e}")

    print("\n🎉 Done! Commit and push to update manifest.json")

if __name__ == "__main__":
    main()
