import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_club_dj_and_hud():
    artifacts_dir = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"
    os.makedirs(artifacts_dir, exist_ok=True)
    hud_active_shot = os.path.join(artifacts_dir, "dj_club_hud_active_verified.png")
    hud_settled_shot = os.path.join(artifacts_dir, "dj_club_hud_settled_verified.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        
        # Open local player
        url = "http://localhost:5050/?cachebust=" + str(int(time.time()))
        print(f"Opening {url}...")
        page.goto(url, wait_until="networkidle", timeout=25000)
        time.sleep(1.5)

        # 1. Test selecting "🔥 Balada & Club DJ"
        print("Selecting club mode...")
        page.evaluate("selectDjActMode('club')")
        time.sleep(0.5)

        act_label = page.evaluate("document.getElementById('djActModeActiveLabel').textContent.trim()")
        print(f"Active Mode Label: {act_label}")
        assert "Balada & Club DJ" in act_label, f"Expected Balada & Club DJ, got: {act_label}"

        # 2. Test calculateDjModeNextTrack in club mode
        calc_res = page.evaluate("""() => {
            const cur = {
                title: "Mega Mexicano DJ Dedda",
                category: "Mega Funk & Ritmadas",
                bpm: 144,
                video_id: "test_cur_123"
            };
            const next = calculateDjModeNextTrack(cur);
            return {
                mode: djPlayMode,
                nextTitle: next ? next.title : null,
                nextBpm: next ? next.bpm : null,
                nextCategory: next ? next.category : null
            };
        }""")
        print(f"Club Mode Next Track: {calc_res}")
        assert calc_res['mode'] == 'club', f"Mode should be club, got {calc_res['mode']}"
        assert calc_res['nextTitle'] is not None, "Next track should be selected in club mode"

        # 3. Test detectGenreFx for different genres
        fx_eval = page.evaluate("""() => {
            const funk = detectGenreFx({ title: "Mega Funk Mandelao", category: "Funk" }, { title: "Ritmada", category: "Funk", bpm: 145 });
            const house = detectGenreFx({ title: "Deep House Club", category: "Eletrônica" }, { title: "Desande Bass", category: "Eletrônica", bpm: 126 });
            const cumbia = detectGenreFx({ title: "Cumbia Villera Santafesina", category: "Cumbia" }, { title: "Charanga Damas", category: "Cumbia", bpm: 105 });
            const gaucho = detectGenreFx({ title: "Vanera Gaúcha Fandango", category: "Músicas Gaúchas" }, { title: "Quaraí Fronteira", category: "Músicas Gaúchas", bpm: 130 });
            const trap = detectGenreFx({ title: "Trap Beat 808", category: "Rap" }, { title: "Drill Flow", category: "Rap", bpm: 140 });
            return { funk, house, cumbia, gaucho, trap };
        }""")
        print("DJ FX Genre Detection Results:")
        for genre, data in fx_eval.items():
            print(f"  - {genre}: {data['icon']} {data['name']} ({data['tag']})")
            assert data['name'], f"Missing FX name for {genre}"

        # 4. Test HUD appearance and 3-band crossover update
        print("Triggering HUD and crossover simulation...")
        hud_info = page.evaluate("""() => {
            const cur = { title: "Mega Mexicano DJ Dedda", category: "Mega Funk & Ritmadas", bpm: 144, video_id: "dedda_123" };
            const nxt = { title: "RITMADA MAS QUE NADA", category: "Mega Funk & Ritmadas", bpm: 140, video_id: "ritmada_456" };
            const fx = detectGenreFx(cur, nxt);
            showDjClubHud(fx);
            updateDjClubHud(0.55, 'A', 'B'); // 55% progress (right after bass swap drop)
            
            const hud = document.getElementById("djClubCrossoverHud");
            const fxBadge = document.getElementById("djHudFxBadge");
            const fxName = document.getElementById("djHudFxName");
            const bassStatus = document.getElementById("djHudBassStatus");
            const dropInd = document.getElementById("djHudDropIndicator");
            const barBassA = document.getElementById("djBarBassA");
            const barBassB = document.getElementById("djBarBassB");
            const barMidA = document.getElementById("djBarMidA");
            const barMidB = document.getElementById("djBarMidB");
            const barHighA = document.getElementById("djBarHighA");
            const barHighB = document.getElementById("djBarHighB");

            return {
                display: hud ? hud.style.display : null,
                hasVisibleClass: hud ? hud.classList.contains("hud-visible") : false,
                fxName: fxName ? fxName.textContent : null,
                bassStatus: bassStatus ? bassStatus.textContent : null,
                dropText: dropInd ? dropInd.textContent : null,
                bassAWidth: barBassA ? barBassA.style.width : null,
                bassBWidth: barBassB ? barBassB.style.width : null,
                midAWidth: barMidA ? barMidA.style.width : null,
                midBWidth: barMidB ? barMidB.style.width : null,
                highAWidth: barHighA ? barHighA.style.width : null,
                highBWidth: barHighB ? barHighB.style.width : null
            };
        }""")
        print(f"HUD State at 55% Crossover: {hud_info}")
        assert hud_info['hasVisibleClass'] is True, "HUD should have hud-visible class"
        assert "808 Sub Drop" in hud_info['fxName'], f"Expected 808 Sub Drop FX, got: {hud_info['fxName']}"
        assert "DROP" in hud_info['dropText'] or "DROP" in hud_info['bassStatus'], "Should indicate bass drop"

        time.sleep(0.5)
        # Capture screenshot of HUD active during transition
        page.screenshot(path=hud_active_shot)
        print(f"Saved active HUD screenshot to: {hud_active_shot}")

        # 5. Test orderly disappearance of the HUD
        print("Testing orderly disappearance (hideDjClubHud)...")
        page.evaluate("hideDjClubHud()")
        time.sleep(0.7) # wait for 550ms fade-out transition

        hud_settled = page.evaluate("""() => {
            const hud = document.getElementById("djClubCrossoverHud");
            return {
                display: hud ? hud.style.display : null,
                hasVisibleClass: hud ? hud.classList.contains("hud-visible") : false,
                hasHidingClass: hud ? hud.classList.contains("hud-hiding") : false
            };
        }""")
        print(f"HUD State after fade-out: {hud_settled}")
        assert hud_settled['display'] == 'none', f"HUD should be hidden (display: none), got: {hud_settled['display']}"
        assert hud_settled['hasVisibleClass'] is False, "HUD should not have hud-visible class"

        page.screenshot(path=hud_settled_shot)
        print(f"Saved settled HUD screenshot to: {hud_settled_shot}")

        browser.close()
        print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_club_dj_and_hud()
