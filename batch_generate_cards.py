"""
Batch Generate Card Art - Pollinations.ai (Free, No API Key)
Usage: python batch_generate_cards.py [--force]
"""
import subprocess
import time
import os
import sys
from urllib.parse import quote

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Reed", "Reed", "images", "cards")
IMAGE_API = "https://image.pollinations.ai/prompt/"
IMAGE_WIDTH = 768
IMAGE_HEIGHT = 768
REQUEST_INTERVAL = 3.0

STYLE_SUFFIX = "abstract magical fire effect, glowing ember and ash particles on pure black background, centered energy burst, no wielder, no holder, floating weaponless, dark fantasy illustration, digital painting, warm orange-red-amber palette, dramatic lighting, no text"

CARDS = [
    ("Strike", "A concentrated beam of fire shooting forward with trailing embers, glowing orange energy bolt, impact sparks"),
    ("Defend", "A circular barrier of condensed flame and ash, protective ember wall glowing warm orange, embers swirling around the barrier"),
    ("SpearFlame", "A concentrated jet of flame igniting, fire lance bursting with orange-red flames, scorch marks spreading from impact"),
    ("SwiftThrust", "A rapid streak of fire, speed lines and motion blur, swift piercing energy leaving a brief ember trail, new light points condensing from the energy"),
    ("AshenBulwark", "A wall of compressed ash and ember forming a solid defensive barrier, glowing cracks of orange light in dark ash walls, embers floating around"),
    ("DragonbloodBoiling", "Boiling ancient blood energy, glowing orange lava-like liquid energy surging outward, intense heat radiating"),
    ("EmberIgnition", "A dying ember reigniting into a blazing burst of fire, small glowing ember transforming into explosive flame, ignition moment"),
    ("CinderSpear", "A concentrated cinder fire lance, trailing scorching embers, dual energy streams"),
    ("CinderSpearCombo", "Three rapid fire energy streams in succession, ember trails overlapping, cinder particles flying"),
    ("EmberShield", "A dome of glowing embers, ember particles condensing into a protective barrier, barrier intensity growing with surrounding scorch flames, the more fire around the stronger the shield"),
    ("EmberConduit", "A vertical conduit of flowing embers and ash particles swirling upward, channel of glowing ash energy, new light orbs condensing from the energy stream"),
    ("EmberEye", "A glowing ember eye shape opening in darkness, radiating heat and light, searing gaze effect"),
    ("AshenArmor", "Armor-like plating made of hardened ash and ember, glowing cracks of orange light between ash plates, ash layers stacking"),
    ("FlameScale", "Scale-like patterns of flame, each scale glowing with scorching heat, scales shimmering orange-red, defensive scales intensifying with surrounding scorch flames"),
    ("ScorchBastion", "A massive wall engulfed in scorching flames, fortification of intense orange fire, structure of pure heat, wall strength doubling with surrounding scorch intensity"),
    ("ScorchingCharge", "A surging force of scorching flames, flame trail, embers erupting forward, self-inflicted scorch flames wrapping around the blast"),
    ("SpontaneousCombustion", "Spontaneous combustion, flames erupting from a central point, explosive self-immolation, energy bursting outward"),
    ("CinderShield", "A dome of solidified cinder and ash, protective barrier crumbling, dark ash dome with glowing ember core"),
    ("AshGathering", "Ash particles converging from all directions into a concentrated mass, swirling ash vortex gathering power"),
    ("AshBath", "Falling ash like rain, scorching flames dissolving into healing ash, embers being absorbed, transformation of fire to ash"),
    ("AshIgnition", "Stored ash exploding into scorching fire, ash-to-flame transformation, pile of grey ash igniting into orange blaze"),
    ("AshResonance", "Rings of ash and ember resonating outward, shockwave of scorching energy, defensive aura of resonating ash"),
    ("BurnAway", "Scorching flames burning away and dissolving, fire peeling off into nothing"),
    ("BurnOut", "A massive final burst of fire consuming all accumulated scorch, explosive ignition, devastating final flame nova"),
    ("Cremation", "Intense scorching cremation fire, funeral pyre of concentrated flame"),
    ("DragonBreath", "A massive cone of ancient fire breath, ash-fueled devastating fire cone"),
    ("EmberBlade", "An edge of solidified embers, scorching flame edge leaving burn marks, ember-glowing fire blade"),
    ("Embers", "Glowing embers floating in the air, small burning fragments swirling, ember cloud effect, new light orbs condensing from the ember cloud"),
    ("FlameBurst", "A burst of flame spawning multiple sparks, flame eruption scattering small fire seeds"),
    ("FlameInheritance", "Scorching flames leaping and spreading from one point to all others, fire transferring and spreading"),
    ("FlameShadowArt", "Shadowy flames with ember trails, dark fire energy casting scorch on all surrounding, flame and shadow blending, new light orbs condensing from the dark fire"),
    ("FlameWhirl", "A whirlwind of flame spinning, scorching vortex of fire"),
    ("PassingTheTorch", "A burning flame passing its fire, scorch consuming as new fire erupts, transferring fire power"),
    ("ReedsSpear", "A massive concentrated fire lance, devastating energy beam doubling in power, legendary fire effect"),
    ("ScorchAwakening", "Scorching flames dissolving into raw energy, self-burning awakening into power, fire transforming to pure energy"),
    ("ScorchBurst", "Accumulated scorch erupting in a devastating burst, all scorch exploding outward, fire nova"),
    ("ScorchedEarth", "A scorched earth battlefield, ground cracked and burning, spreading scorch, devastating fire-scorched landscape"),
    ("ScorchedEarthProtocol", "A dark ritual of ash, consuming unwanted energy for power, ash ritual circle with burning symbols"),
    ("ScorchingHeart", "A heart shape made of pure scorching fire, beating with ember energy, self-immolating core radiating power"),
    ("SearingPierce", "A blinding beam of white-hot fire piercing horizontally through a dark stone wall, molten debris and ember sparks bursting from impact, glowing cracks radiating from penetration hole, heat distortion waves, beam intensity amplifying with surrounding scorch flames"),
    ("ShadowflameProwl", "A shadowy flame barrier, dark fire shield, ember cloak of dark fire, dark fire and shadow blending, defensive barrier"),
    ("WitheredRevival", "Withered reed burning and transforming into new ember life, rebirth from ashes, old flame dissolving as new fire emerges from scorched ground, ash particles converging into new glowing orbs"),
    ("AshRecovery", "Ash swirling around restoring energy, healing ash aura"),
    ("EmberPact", "A pact sealed in ember and ash, glowing contract of fire, ash energy spreading to multiple points, new light orbs condensing from the pact"),
    ("ScorchingBond", "A bond of scorching flame connecting points, fire link between energies"),
    ("BreathOfCalamity", "A dark calamity breath spreading, disaster miasma of scorching fire, ominous fire storm"),
    ("DragonsLegacy", "An ancient legacy power awakening, ancient fire heritage, growing strength, ancient scales and flame crown"),
    ("Everflame", "An eternal flame that never dies, perpetual fire feeding on scorch, unquenchable ember burning forever"),
    ("FlameShadowReed", "A flame shadow form, reed-like silhouette wreathed in dark fire, ember and shadow fusion"),
    ("InfernoStorm", "A massive inferno storm, swirling fire tornado with scorching embers, devastating fire storm"),
    ("UnitedFront", "A wall of scorching flame, shared fire front, linked ember aura"),
    ("VictoriasVow", "A solemn vow of victory sealed in flame, power growing with each burning, vow crown of fire"),
    ("Wildfire", "A wildfire spreading uncontrollably, scorch jumping from point to point, prairie fire"),
    ("Spark", "A single small spark of flame, tiny but potent fire seed, small ember with scorching power"),
    ("AshStorm", "A storm of ash particles swirling, grey ash cyclone with glowing embers, all-encompassing ash storm"),
    ("EternalEmber", "An eternal ember radiating infinite power, supreme protective ash aura, ancient and ultimate fire"),
]


def generate_card(name, prompt, retries=5):
    """Generate one card image via Pollinations.ai"""
    full_prompt = f"{prompt}, {STYLE_SUFFIX}, no person, no human, no animal, no dragon, no creature, no character, no hand, no arm, no body, no face"
    encoded = quote(full_prompt)
    url = f"{IMAGE_API}{encoded}?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&nologo=true&seed={abs(hash(name)) % 999999}"

    for attempt in range(retries):
        try:
            filepath = os.path.join(OUTPUT_DIR, f"{name}.png")
            result = subprocess.run(
                ["curl", "-s", "-L", "--max-time", "180", "-o", filepath, url],
                capture_output=True
            )

            if os.path.exists(filepath) and os.path.getsize(filepath) > 5000:
                size_kb = os.path.getsize(filepath) / 1024
                print(f"  [OK] {name}.png ({size_kb:.0f}KB)")
                return True
            else:
                print(f"  [RETRY] {name}: file too small or missing, attempt {attempt+1}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                time.sleep(15)

        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

        if attempt < retries - 1:
            time.sleep(10)

    return False


def main():
    force = "--force" in sys.argv or "-f" in sys.argv
    print("=" * 50)
    print("  Card Art Generation (Pollinations.ai)")
    print("=" * 50)
    print(f"  Size: {IMAGE_WIDTH}x{IMAGE_HEIGHT}")
    print(f"  Cards: {len(CARDS)}")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 50)
    print()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    existing = set()
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".png") and not f.endswith(".import"):
            existing.add(f.replace(".png", ""))

    if force:
        to_generate = CARDS
        print(f"  [FORCE] Regenerating all {len(to_generate)} cards")
    else:
        to_generate = [(n, p) for n, p in CARDS if n not in existing]

    print(f"  Existing: {len(existing)} | To generate: {len(to_generate)}")
    print()

    if not to_generate:
        print("All cards already generated. Use --force to regenerate.")
        return

    success = 0
    fail = 0
    fail_list = []
    for i, (name, prompt) in enumerate(to_generate, 1):
        print(f"[{i}/{len(to_generate)}] {name}")
        ok = generate_card(name, prompt)
        if ok:
            success += 1
        else:
            fail += 1
            fail_list.append(name)
        if i < len(to_generate):
            time.sleep(REQUEST_INTERVAL)

    print()
    print("=" * 50)
    print(f"  Done: Success {success}, Failed {fail}")
    if fail_list:
        print(f"  Failed: {', '.join(fail_list)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
