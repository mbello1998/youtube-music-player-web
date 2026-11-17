import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_fx_rotation():
    artifacts_dir = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"
    os.makedirs(artifacts_dir, exist_ok=True)
    shot_airhorn = os.path.join(artifacts_dir, "dj_fx_airhorn_verified.png")
    shot_spinback = os.path.join(artifacts_dir, "dj_fx_spinback_verified.png")
    shot_flanger = os.path.join(artifacts_dir, "dj_fx_flanger_verified.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        
        url = "http://localhost:5050/?cachebust=" + str(int(time.time()))
        print(f"Opening {url}...")
        page.goto(url, wait_until="networkidle", timeout=25000)
        time.sleep(1.5)

        # 1. Inspect catalog size per genre
        catalog_eval = page.evaluate("""() => {
            const cat = window.DJ_GENRE_EFFECTS_CATALOG || {};
            const summary = {};
            let total = 0;
            for (const [k, v] of Object.entries(cat)) {
                summary[k] = v.map(e => `${e.icon} ${e.name} (${e.type})`);
                total += v.length;
            }
            return { summary, total };
        }""")
        print(f"\n--- DJ FX CATALOG TOTAL: {catalog_eval['total']} EFEITOS ---")
        for genre, effects in catalog_eval['summary'].items():
            print(f"[{genre.upper()}] ({len(effects)} efeitos):")
            for eff in effects:
                print(f"   • {eff}")
            assert len(effects) >= 4, f"Genre {genre} should have at least 4 effects, found {len(effects)}"

        # 2. Test rotation in Funk (5 consecutive transitions should return 5 DIFFERENT effects)
        print("\n--- TESTANDO ROTAÇÃO EM FUNK ---")
        funk_rotations = page.evaluate("""() => {
            const cur = { title: "Mega Mexicano DJ Dedda", category: "Mega Funk & Ritmadas", bpm: 144 };
            const nxt = { title: "RITMADA MAS QUE NADA", category: "Mega Funk & Ritmadas", bpm: 140 };
            const results = [];
            for (let i = 0; i < 5; i++) {
                results.push(detectGenreFx(cur, nxt));
            }
            return results;
        }""")
        for idx, res in enumerate(funk_rotations):
            print(f"  Transição {idx + 1}: {res['icon']} {res['name']} [Idx: {res['rotationIndex'] + 1}/{res['totalInGenre']}]")

        names = [r['name'] for r in funk_rotations]
        assert len(set(names)) == 5, f"All 5 funk effects should be unique, got: {names}"

        # 3. Test rotation in House / Eletrônica
        print("\n--- TESTANDO ROTAÇÃO EM HOUSE / ELETRÔNICA ---")
        house_rotations = page.evaluate("""() => {
            const cur = { title: "Vintage Culture Desande", category: "Eletrônica, House & Desande", bpm: 126 };
            const nxt = { title: "Mochakk Club Mix", category: "Eletrônica, House & Desande", bpm: 128 };
            const results = [];
            for (let i = 0; i < 5; i++) {
                results.push(detectGenreFx(cur, nxt));
            }
            return results;
        }""")
        for idx, res in enumerate(house_rotations):
            print(f"  Transição {idx + 1}: {res['icon']} {res['name']} [Idx: {res['rotationIndex'] + 1}/{res['totalInGenre']}]")
        names_house = [r['name'] for r in house_rotations]
        assert len(set(names_house)) == 5, f"All 5 house effects should be unique, got: {names_house}"

        # 4. Test rotation in Cumbia
        print("\n--- TESTANDO ROTAÇÃO EM CUMBIA ---")
        cumbia_rotations = page.evaluate("""() => {
            const cur = { title: "Ke Personajes Piel Cumbia", category: "Cumbia", bpm: 100 };
            const nxt = { title: "Damas Gratis Charanga", category: "Cumbia", bpm: 104 };
            const results = [];
            for (let i = 0; i < 5; i++) {
                results.push(detectGenreFx(cur, nxt));
            }
            return results;
        }""")
        for idx, res in enumerate(cumbia_rotations):
            print(f"  Transição {idx + 1}: {res['icon']} {res['name']} [Idx: {res['rotationIndex'] + 1}/{res['totalInGenre']}]")
        names_cumbia = [r['name'] for r in cumbia_rotations]
        assert len(set(names_cumbia)) == 5, f"All 5 cumbia effects should be unique, got: {names_cumbia}"

        # 5. Visual HUD Verification for Airhorn
        print("\n--- VERIFICANDO HUD VISUAL: AIRHORN ---")
        page.evaluate("""() => {
            const fx = DJ_GENRE_EFFECTS_CATALOG.funk.find(e => e.id === "airhorn_impact");
            showDjClubHud(fx);
            updateDjClubHud(0.5, 'A', 'B');
        }""")
        time.sleep(0.4)
        page.screenshot(path=shot_airhorn)
        print(f"Saved airhorn screenshot to: {shot_airhorn}")

        # 6. Visual HUD Verification for Spinback
        print("\n--- VERIFICANDO HUD VISUAL: SPINBACK ---")
        page.evaluate("""() => {
            const fx = DJ_GENRE_EFFECTS_CATALOG.funk.find(e => e.id === "spinback_drop");
            showDjClubHud(fx);
            updateDjClubHud(0.6, 'A', 'B');
        }""")
        time.sleep(0.4)
        page.screenshot(path=shot_spinback)
        print(f"Saved spinback screenshot to: {shot_spinback}")

        # 7. Visual HUD Verification for Jet Flanger
        print("\n--- VERIFICANDO HUD VISUAL: JET FLANGER ---")
        page.evaluate("""() => {
            const fx = DJ_GENRE_EFFECTS_CATALOG.house.find(e => e.id === "jet_flanger");
            showDjClubHud(fx);
            updateDjClubHud(0.7, 'A', 'B');
        }""")
        time.sleep(0.4)
        page.screenshot(path=shot_flanger)
        print(f"Saved flanger screenshot to: {shot_flanger}")

        # 8. Test clean disappearance
        print("\n--- TESTANDO DESAPARECIMENTO DO HUD ---")
        page.evaluate("hideDjClubHud()")
        time.sleep(0.7)
        disp = page.evaluate("document.getElementById('djClubCrossoverHud').style.display")
        assert disp == "none", f"HUD display should be none, got: {disp}"
        print("HUD disappeared cleanly as expected!")

        browser.close()
        print("\nALL ROTATION TESTS PASSED 100% SUCCESSFULLY!")

if __name__ == "__main__":
    test_fx_rotation()
