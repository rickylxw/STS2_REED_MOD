"""
批量生成遗物/药水/能力图标 - 使用 curl 调用内置 text_to_image API
"""
import subprocess
import time
import os
import sys
import re
from urllib.parse import quote

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_API = "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image"
REQUEST_INTERVAL = 2.0

ICON_STYLE = "game icon art, centered composition on dark background, glowing magical fire effect, semi-realistic digital painting, warm orange-red-amber palette, clean icon design, no text, no person, no human, no animal, no creature, no character"

RELICS = [
    ("ScaleFlameCharm", "An ancient charm amulet made of dragon flame scales, glowing orange scale-shaped pendant radiating protective fire energy, cracked scale patterns with ember glow between them, game relic icon, dark background"),
    ("RelicOfTheDragon", "An ancient dragon relic artifact, glowing dragon-eye gemstone radiating power, dragon-fire essence crystal, orange-red glowing gem on stone pedestal, game relic icon, dark background"),
    ("ReedsSpearhead", "A spearhead-shaped relic forged from reed and flame, glowing spear tip artifact radiating scorching energy, orange-red metal spearhead with ember cracks, game relic icon, dark background"),
    ("HeartOfEmbers", "A glowing heart-shaped relic made of solidified embers, ember heart artifact radiating warmth, cracked heart with orange glowing core, game relic icon, dark background"),
    ("FlameOfVictoria", "A crown-shaped flame relic, Victoria's flame crown artifact, golden-orange fire crown radiating power, regal flame crest, game relic icon, dark background"),
    ("AshenCore", "A core-shaped relic made of compressed ash and ember, dark ash sphere with glowing orange cracks, compacted ash energy core, game relic icon, dark background"),
]

POTIONS = [
    ("DragonFlamePotion", "A potion bottle filled with swirling dragon flame liquid, glowing orange-red fire essence in glass vial, ember particles floating in the liquid, capped bottle radiating heat, game potion icon, dark background"),
]

POWERS = [
    ("Ash", "A swirling mass of grey ash particles, ash counter icon, grey ash cloud with faint orange embers, game power icon, dark background"),
    ("AshRecoveryPower", "Ash particles swirling in a healing circle, recovering energy from ash, green-orange ash healing aura, game power icon, dark background"),
    ("CalamityBreath", "A dark calamity miasma spreading, dark purple-orange toxic breath cloud, ominous disaster fog, game power icon, dark background"),
    ("DragonsLegacyPower", "An ancient dragon power symbol, dragon fire heritage crest, growing strength emblem with orange flame, game power icon, dark background"),
    ("EmberSpread", "Embers spreading outward from a central point, spreading fire particles radiating, ember dispersion pattern, game power icon, dark background"),
    ("EternalEmberPower", "An eternal ember radiating infinite power, supreme glowing ember core, all-encompassing ash aura, game power icon, dark background"),
    ("EverflamePower", "An everlasting flame that never extinguishes, perpetual fire feeding on scorch, unquenchable orange flame, game power icon, dark background"),
    ("FlameShadowForm", "A flame shadow form symbol, dark fire silhouette, ember and shadow fusion emblem, game power icon, dark background"),
    ("Scorch", "A burning scorch effect, intense orange flame burning debuff, scorching fire damage symbol, game power icon, dark background"),
    ("ScorchCounter", "A scorch counter symbol, controlled burn, orange flame in a containment circle, game power icon, dark background"),
    ("ScorchImmunity", "A scorch immunity shield, flame being blocked by a barrier, protective dome blocking orange fire, game power icon, dark background"),
    ("UnitedFrontPower", "A united flame front symbol, multiple flame sources joining into one wall of fire, linked ember aura, game power icon, dark background"),
]

ALL_ASSETS = [
    ("relics", RELICS),
    ("potions", POTIONS),
    ("powers", POWERS),
]


def curl_request(url, timeout=180):
    """Use curl to make GET request, return raw bytes"""
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", str(timeout), url],
        capture_output=True
    )
    return result.stdout


def generate_image(name, prompt, output_dir, retries=5):
    """Generate one icon image using curl"""
    full_prompt = f"{prompt}, {ICON_STYLE}"
    encoded = quote(full_prompt)
    url = f"{IMAGE_API}?prompt={encoded}&image_size=square"

    for attempt in range(retries):
        try:
            raw = curl_request(url)
            if not raw:
                print(f"  [EMPTY] {name}: empty response, retry...")
                time.sleep(10)
                continue

            # Check if response is binary image data (JPEG/PNG)
            is_jpeg = raw[:2] == b'\xff\xd8'
            is_png = raw[:4] == b'\x89PNG'
            has_jfif = b'JFIF' in raw[:20]

            if is_jpeg or is_png or has_jfif:
                filepath = os.path.join(output_dir, f"{name}.png")
                with open(filepath, "wb") as f:
                    f.write(raw)
                size_kb = len(raw) / 1024
                print(f"  [OK] {name}.png ({size_kb:.0f}KB)")
                return True

            # Try to parse as text (URL response)
            text = raw.decode("utf-8", errors="replace").strip()
            img_url = ""
            match = re.search(r'!\[\]\((https?://[^\s\)]+)\)', text)
            if match:
                img_url = match.group(1)
            elif text.startswith("http"):
                img_url = text.strip()
            else:
                match = re.search(r'(https?://[^\s\)"\']+)', text)
                if match:
                    img_url = match.group(1)

            if img_url:
                filepath = os.path.join(output_dir, f"{name}.png")
                dl_raw = curl_request(img_url, 60)
                if dl_raw and len(dl_raw) > 1000:
                    with open(filepath, "wb") as f:
                        f.write(dl_raw)
                    size_kb = len(dl_raw) / 1024
                    print(f"  [OK] {name}.png ({size_kb:.0f}KB)")
                    return True

            print(f"  [NO IMAGE] {name}: response {len(raw)} bytes")
            time.sleep(5)

        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

        if attempt < retries - 1:
            time.sleep(10)

    return False


def main():
    force = "--force" in sys.argv or "-f" in sys.argv
    total = sum(len(items) for _, items in ALL_ASSETS)

    print("=" * 50)
    print("  Icon Art Generation (curl + Built-in API)")
    print("=" * 50)
    print(f"  Total: {total} icons ({len(RELICS)} relics, {len(POTIONS)} potions, {len(POWERS)} powers)")
    print("=" * 50)
    print()

    success = 0
    fail = 0
    fail_list = []
    count = 0

    for subdir, items in ALL_ASSETS:
        output_dir = os.path.join(OUTPUT_DIR, "Reed", "Reed", "images", subdir)
        os.makedirs(output_dir, exist_ok=True)

        print(f"--- {subdir.upper()} ({len(items)}) ---")
        for name, prompt in items:
            count += 1
            filepath = os.path.join(output_dir, f"{name}.png")
            if os.path.exists(filepath) and not force:
                print(f"  [SKIP] {name}.png already exists")
                success += 1
                continue

            print(f"[{count}/{total}] {name}")
            ok = generate_image(name, prompt, output_dir)
            if ok:
                success += 1
            else:
                fail += 1
                fail_list.append(f"{subdir}/{name}")

            if count < total:
                time.sleep(REQUEST_INTERVAL)
        print()

    print("=" * 50)
    print(f"  Done: Success {success}, Failed {fail}")
    if fail_list:
        print(f"  Failed: {', '.join(fail_list)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
