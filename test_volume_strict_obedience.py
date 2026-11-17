# -*- coding: utf-8 -*-
"""
test_volume_strict_obedience.py
Valida a obediência estrita de TODOS os elementos e efeitos sonoros ao volume master e ao mudo.
"""

import os
import time
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"

def test_volume_obedience():
    print("Iniciando testes de OBEDIÊNCIA ESTRITA AO VOLUME DO PLAYER...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 850})
        page = context.new_page()

        page.goto("http://localhost:5050/player.html", wait_until="networkidle", timeout=20000)
        time.sleep(1.0)

        # Ativa o modo club para testar efeitos
        page.evaluate("() => selectDjActMode('club')")
        time.sleep(0.3)

        # -------------------------------------------------------------
        # TESTE 1: Volume Normal a 100%
        # -------------------------------------------------------------
        print("\n--- TESTE 1: Volume Master a 100% ---")
        page.evaluate("() => setMasterVolume(100)")
        time.sleep(0.2)

        vol_100_info = page.evaluate("""() => {
            window.testDjFx('airhorn');
            const dest = window.getDjFxDestination ? window.getDjFxDestination(window.audioCtx) : null;
            const fxBusVal = dest ? dest.gain.value : 0;
            return {
                masterVolume: masterVolume,
                isMuted: isMuted,
                fxGain: fxBusVal
            };
        }""")
        print("Info em 100%:", vol_100_info)
        assert vol_100_info["masterVolume"] == 100
        assert not vol_100_info["isMuted"]
        assert abs(vol_100_info["fxGain"] - 0.85) < 0.05, f"Ganho inesperado em 100%: {vol_100_info['fxGain']}"

        # -------------------------------------------------------------
        # TESTE 2: Volume a 50% (Efeitos devem tocar na metade do volume)
        # -------------------------------------------------------------
        print("\n--- TESTE 2: Volume Master a 50% ---")
        page.evaluate("() => setMasterVolume(50)")
        time.sleep(0.2)

        vol_50_info = page.evaluate("""() => {
            window.testDjFx('airhorn');
            const dest = window.getDjFxDestination(window.audioCtx);
            return {
                masterVolume: masterVolume,
                isMuted: isMuted,
                fxGain: dest ? dest.gain.value : 0
            };
        }""")
        print("Info em 50%:", vol_50_info)
        assert vol_50_info["masterVolume"] == 50
        assert abs(vol_50_info["fxGain"] - 0.425) < 0.05, f"Ganho inesperado em 50%: {vol_50_info['fxGain']}"

        # Captura screenshot em 50%
        shot_50 = os.path.join(EVIDENCE_DIR, "volume_50_pct_verified.png")
        page.locator(".bottom-player-bar").screenshot(path=shot_50)
        print(f"Screenshot em 50% capturado: {shot_50}")

        # -------------------------------------------------------------
        # TESTE 3: Volume a 0% / Mudo (Efeitos devem silenciar completamente: 0.0)
        # -------------------------------------------------------------
        print("\n--- TESTE 3: Volume Master MUDO (0%) ---")
        page.evaluate("() => toggleMute()")
        time.sleep(0.2)

        vol_0_info = page.evaluate("""() => {
            window.testDjFx('airhorn');
            const dest = window.getDjFxDestination(window.audioCtx);
            return {
                masterVolume: masterVolume,
                isMuted: isMuted,
                fxGain: dest ? dest.gain.value : 0
            };
        }""")
        print("Info em Mudo (0%):", vol_0_info)
        assert vol_0_info["masterVolume"] == 0 or vol_0_info["isMuted"], "Player não ficou mudo!"
        assert abs(vol_0_info["fxGain"]) < 0.001, f"Ganho não zerou no mudo: {vol_0_info['fxGain']}"

        # Captura screenshot no mudo
        shot_mute = os.path.join(EVIDENCE_DIR, "volume_mudo_zero_verified.png")
        page.locator(".bottom-player-bar").screenshot(path=shot_mute)
        print(f"Screenshot no mudo capturado: {shot_mute}")

        # -------------------------------------------------------------
        # TESTE 4: Volume Super VLC a 150% (Efeitos devem escalar para 150%)
        # -------------------------------------------------------------
        print("\n--- TESTE 4: Super Volume VLC a 150% ---")
        page.evaluate("() => setMasterVolume(150)")
        time.sleep(0.2)

        vol_150_info = page.evaluate("""() => {
            window.testDjFx('airhorn');
            const dest = window.getDjFxDestination(window.audioCtx);
            return {
                masterVolume: masterVolume,
                isMuted: isMuted,
                fxGain: dest ? dest.gain.value : 0
            };
        }""")
        print("Info em 150% VLC:", vol_150_info)
        assert vol_150_info["masterVolume"] == 150
        assert abs(vol_150_info["fxGain"] - 1.275) < 0.08, f"Ganho inesperado em 150%: {vol_150_info['fxGain']}"

        # Captura screenshot em 150% VLC
        shot_150 = os.path.join(EVIDENCE_DIR, "volume_150_vlc_verified.png")
        page.locator(".bottom-player-bar").screenshot(path=shot_150)
        print(f"Screenshot em 150% VLC capturado: {shot_150}")

        # Retorna para volume 100%
        page.evaluate("() => setMasterVolume(100)")
        time.sleep(0.2)

        browser.close()
        print("\n TODOS OS TESTES DE OBEDIÊNCIA AO VOLUME PASSARAM COM 100% DE SUCESSO!")

if __name__ == "__main__":
    test_volume_obedience()
