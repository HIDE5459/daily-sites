#!/usr/bin/env python3
"""Leonardo AI image generation for Instagram AI Traveler.
Uses Flux Dev model for photorealistic single-person portraits."""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Load API key
env_path = Path(__file__).parent / ".env"
for line in env_path.read_text().strip().split("\n"):
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip()

API_KEY = os.environ["LEONARDO_API_KEY"]
BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Flux Dev model ID - best for photorealistic portraits
MODEL_ID = "b2614463-296c-462a-9586-aafdb8f00e36"

OUTPUT_DIR = Path(__file__).parent.parent.parent / "instagram" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Base character: consistent description
CHAR = (
    "head and shoulders portrait photograph of one beautiful 25 year old "
    "Japanese woman with long straight black hair, warm natural smile, "
)

STYLE = (
    ", professional travel portrait photography, Canon 85mm f1.2 lens, "
    "extremely shallow depth of field, golden hour warm sunlight, "
    "photorealistic, one person only in frame, film grain"
)

NEG = "two people, multiple, duplicate, group, cartoon, anime, deformed, blurry, watermark, text"

DESTINATIONS = {
    "santorini": {
        "scene": "soft bokeh background showing Santorini Greece blue domes and white buildings, wearing white linen sundress",
        "caption": "🇬🇷 サントリーニ島の青と白の世界\nこの景色、永遠に見ていられる… ☀️\n\n#Santorini #Greece #AITravel #バーチャル旅行 #サントリーニ #地中海 #絶景 #旅スタグラム",
    },
    "paris": {
        "scene": "standing near Eiffel Tower in Paris with autumn trees, wearing beige trench coat and beret, romantic Parisian atmosphere",
        "caption": "🗼 パリの秋、エッフェル塔と\n風が気持ちいい季節 🍂\n\n#Paris #EiffelTower #AITravel #バーチャル旅行 #パリ旅行 #秋旅 #旅スタグラム",
    },
    "kyoto": {
        "scene": "walking through bamboo grove in Kyoto Japan, dappled sunlight, wearing casual kimono-style top, serene peaceful atmosphere",
        "caption": "🎋 京都・嵐山の竹林\n静寂に包まれる特別な空間 ✨\n\n#Kyoto #Japan #AITravel #バーチャル旅行 #京都 #嵐山 #竹林 #和の心",
    },
    "newyork": {
        "scene": "Times Square New York City at night in background, neon lights bokeh, wearing leather jacket, vibrant urban energy",
        "caption": "🗽 ニューヨーク、タイムズスクエアの夜 🌃\n眠らない街のエネルギー！\n\n#NYC #TimesSquare #AITravel #バーチャル旅行 #ニューヨーク #夜景",
    },
    "bali": {
        "scene": "at Gates of Heaven temple Bali with lush green mountains, wearing bohemian outfit with flowers in hair, misty morning",
        "caption": "🌺 バリ島・天国の門 🙏\n朝霧の中、神聖な空気に包まれて\n\n#Bali #Indonesia #AITravel #バーチャル旅行 #バリ島 #天国の門",
    },
    "iceland": {
        "scene": "Northern Lights aurora borealis in Iceland sky behind her, wearing warm parka and beanie, snowy landscape, magical night",
        "caption": "🌌 アイスランドのオーロラ ✨\n人生で一度は見たかった景色…\n\n#Iceland #NorthernLights #Aurora #AITravel #バーチャル旅行 #オーロラ",
    },
    "dubai": {
        "scene": "Dubai skyline with Burj Khalifa in background, rooftop terrace, wearing elegant evening dress, sunset golden hour",
        "caption": "🏙️ ドバイの夕暮れ 🌅\nブルジュ・ハリファの圧倒的スケール\n\n#Dubai #BurjKhalifa #AITravel #バーチャル旅行 #ドバイ #夕焼け",
    },
    "machupicchu": {
        "scene": "Machu Picchu ruins in Peru with misty mountains behind, wearing hiking outfit with backpack, early morning light",
        "caption": "🏔️ マチュピチュ、朝霧の天空の城 🇵🇪\n息を呑む絶景…\n\n#MachuPicchu #Peru #AITravel #バーチャル旅行 #マチュピチュ #世界遺産",
    },
    "maldives": {
        "scene": "crystal clear turquoise water of Maldives, overwater bungalow in background, wearing bikini top and sarong, tropical paradise",
        "caption": "🏝️ モルディブの透き通る海 🐠\n楽園ってこういうことか…\n\n#Maldives #Paradise #AITravel #バーチャル旅行 #モルディブ #リゾート",
    },
    "london": {
        "scene": "Big Ben and London Bridge in background, rainy day with umbrella, wearing classic trench coat, moody atmospheric London",
        "caption": "🇬🇧 ロンドンの雨の日もまた素敵 ☂️\nビッグベンと一緒に\n\n#London #BigBen #AITravel #バーチャル旅行 #ロンドン #雨の日",
    },
}


def generate_image(destination: str) -> dict:
    """Generate a travel portrait and return {path, caption}."""
    if destination not in DESTINATIONS:
        print(f"Unknown: {destination}. Available: {', '.join(DESTINATIONS.keys())}")
        sys.exit(1)

    dest = DESTINATIONS[destination]
    prompt = CHAR + dest["scene"] + STYLE

    payload = {
        "prompt": prompt,
        "negative_prompt": NEG,
        "modelId": MODEL_ID,
        "width": 832,
        "height": 1216,
        "num_images": 1,
    }

    # Generate
    resp = requests.post(f"{BASE_URL}/generations", headers=HEADERS, json=payload)
    resp.raise_for_status()
    gen_id = resp.json()["sdGenerationJob"]["generationId"]
    cost = resp.json()["sdGenerationJob"].get("cost", {})
    print(f"🌍 {destination} - Gen ID: {gen_id} (cost: {cost})")

    # Wait
    for i in range(30):
        time.sleep(5)
        r = requests.get(f"{BASE_URL}/generations/{gen_id}", headers=HEADERS)
        gen = r.json()["generations_by_pk"]
        status = gen.get("status")
        if status == "COMPLETE":
            images = gen.get("generated_images", [])
            if not images:
                raise RuntimeError("No images")
            url = images[0]["url"]
            dl = requests.get(url)
            filename = f"travel_{destination}_{int(time.time())}.jpg"
            path = OUTPUT_DIR / filename
            path.write_bytes(dl.content)
            # Save caption
            (OUTPUT_DIR / f"travel_{destination}_{int(time.time())}.txt").write_text(dest["caption"])
            print(f"✅ {destination}: {path.name} ({len(dl.content)} bytes)")
            return {"path": str(path), "caption": dest["caption"], "url": url}
        elif status == "FAILED":
            raise RuntimeError(f"Generation failed")
    raise TimeoutError("Timed out")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_image.py <destination|--all|--list>")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "--list":
        for d in DESTINATIONS:
            print(f"  {d}")
    elif arg == "--all":
        results = []
        for d in DESTINATIONS:
            try:
                result = generate_image(d)
                results.append(result)
            except Exception as e:
                print(f"❌ {d}: {e}")
            time.sleep(3)
        print(f"\n🎉 Generated {len(results)}/{len(DESTINATIONS)} images")
    else:
        result = generate_image(arg)
        print(f"📝 Caption:\n{result['caption']}")
