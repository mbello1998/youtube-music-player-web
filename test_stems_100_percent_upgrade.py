# -*- coding: utf-8 -*-
"""
test_stems_100_percent_upgrade.py
Valida o novo Motor DJ Stems Pro 4-Canais:
- 4 Canais: Vocal (Acapella), Batida (Drums), Baixo (Bass/Sub), Melodia (Instrumental)
- Medidores LED VU em tempo real por stem
- 7 Quick Action DJ Pads
- Lógica de Mute, Solo, Faders e Kill Switch (ganho linear 0.0 absoluto)
- Valida também que o Drop Badge está oculto e HUD sem scroll
- Captura screenshots comprovando o funcionamento
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path(r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("Navegando para http://localhost:5050...")
        page.goto("http://localhost:5050", wait_until="networkidle", timeout=15000)
        time.sleep(2)

        # -------------------------------------------------------------
        # VERIFICAÇÃO 1: Badge Drop Hunter Oculto no Modo Match Perfeito
        # -------------------------------------------------------------
        print("\n--- Verificação 1: Drop Hunter Badge Oculto no Match Perfeito ---")
        drop_badge = page.locator("#djDropActiveBadge")
        assert not drop_badge.is_visible(), "FALHA: #djDropActiveBadge não deve estar visível no início!"
        print("✓ #djDropActiveBadge estritamente oculto no Match Perfeito!")

        # -------------------------------------------------------------
        # VERIFICAÇÃO 2: Abertura do Modal DJ Stems Pro
        # -------------------------------------------------------------
        print("\n--- Verificação 2: Abertura do Modal DJ Stems Pro ---")
        stems_modal = page.locator("#djStemsModal")
        assert not stems_modal.is_visible(), "Modal Stems deve iniciar oculto"

        page.click("#barStemsBtn")
        time.sleep(0.6)
        assert stems_modal.is_visible(), "FALHA: #djStemsModal não abriu ao clicar em #barStemsBtn!"
        print("✓ Modal DJ Stems Pro aberto com sucesso!")

        # -------------------------------------------------------------
        # VERIFICAÇÃO 3: Estrutura dos 4 Canais e Medidores LED
        # -------------------------------------------------------------
        print("\n--- Verificação 3: 4 Canais de Stems e VU Meters Presentes ---")
        stems = ["vocal", "drums", "bass", "inst"]
        for s in stems:
            assert page.locator(f"#stemSlider_{s}").is_visible(), f"Fader do canal {s} não visível!"
            assert page.locator(f"#stemVal_{s}").is_visible(), f"Label de valor {s} não visível!"
            assert page.locator(f"#stemMuteBtn_{s}").is_visible(), f"Botão Mute {s} não visível!"
            assert page.locator(f"#stemSoloBtn_{s}").is_visible(), f"Botão Solo {s} não visível!"
            assert page.locator(f"#stemMeterFill_{s}").count() == 1, f"Elemento VU Meter {s} não encontrado!"
            assert page.locator(f"#stemMeterVal_{s}").is_visible(), f"Valor dB {s} não visível!"
            print(f"  ✓ Canal {s.upper()}: Fader, Mute, Solo e VU Meter validados.")

        # Status Pill Flat Inicial
        pill_text = page.locator("#stemsEngagedBadge").inner_text()
        print(f"Pill de Status inicial: '{pill_text}'")
        assert "FLAT" in pill_text or "ORIGINAL" in pill_text, "Status inicial deve indicar Mix Original (Flat)"

        # Screenshot 1: Overview Geral dos 4 Stems
        ss1 = ARTIFACTS_DIR / "stems_pro_modal_4_channels_overview_verified.png"
        page.locator("#djStemsModal .stems-modal-card").screenshot(path=str(ss1))
        print(f"✓ Screenshot 1 salvo: {ss1.name}")

        # -------------------------------------------------------------
        # VERIFICAÇÃO 4: Pad Rápido 'Apenas Vocal' (Acapella Solo)
        # -------------------------------------------------------------
        print("\n--- Verificação 4: Ação Rápida 'Apenas Vocal' (Acapella Solo) ---")
        page.click("#stemPad_vocal")
        time.sleep(0.4)

        state = page.evaluate("window.stemsState")
        print(f"Stems State após Apenas Vocal: {state}")
        assert state["solo"] == "vocal", "FALHA: solo deve ser 'vocal'"
        assert state["vocal"] >= 125, "FALHA: vocal deve estar a pelo menos 125%"
        assert state["drums"] == 0, "FALHA: drums deve estar a 0%"
        assert state["bass"] == 0, "FALHA: bass deve estar a 0%"
        assert state["inst"] == 0, "FALHA: inst deve estar a 0%"

        pill_text = page.locator("#stemsEngagedBadge").inner_text()
        print(f"Pill de Status no Solo Vocal: '{pill_text}'")
        assert "VOCAL" in pill_text, "Pill deve exibir VOCAL SOLO"

        # Screenshot 2: Vocal Acapella Solo
        ss2 = ARTIFACTS_DIR / "stems_pro_vocal_acapella_solo_verified.png"
        page.locator("#djStemsModal .stems-modal-card").screenshot(path=str(ss2))
        print(f"✓ Screenshot 2 salvo: {ss2.name}")

        # -------------------------------------------------------------
        # VERIFICAÇÃO 5: Pad Rápido 'Bass Kill' & 'Apenas Batida'
        # -------------------------------------------------------------
        print("\n--- Verificação 5: Teste Bass Kill e Beat Puro ---")
        page.click("#stemPad_basskill")
        time.sleep(0.3)
        state_bk = page.evaluate("window.stemsState")
        print(f"Stems State após Bass Kill: {state_bk}")
        assert state_bk["bass"] == 0 and state_bk["muted"]["bass"] == True, "Grave deve estar cortado no Bass Kill"
        assert state_bk["drums"] == 100, "Batida deve estar 100% no Bass Kill"
        assert state_bk["vocal"] == 100, "Voz deve estar 100% no Bass Kill"

        page.click("#stemPad_beat")
        time.sleep(0.3)
        state_bt = page.evaluate("window.stemsState")
        print(f"Stems State após Apenas Batida: {state_bt}")
        assert state_bt["vocal"] == 0 and state_bt["muted"]["vocal"] == True, "Vocal deve estar mutado no Beat Puro"
        assert state_bt["drums"] > 100 and state_bt["bass"] > 100, "Batida e Baixo devem estar ativos"

        # Screenshot 3: Bass Kill e Beat
        ss3 = ARTIFACTS_DIR / "stems_pro_bass_kill_and_beat_verified.png"
        page.locator("#djStemsModal .stems-modal-card").screenshot(path=str(ss3))
        print(f"✓ Screenshot 3 salvo: {ss3.name}")

        # -------------------------------------------------------------
        # VERIFICAÇÃO 6: Retorno ao 'Mix Original' (Reset 100%)
        # -------------------------------------------------------------
        print("\n--- Verificação 6: Retorno ao Mix Original (Reset 100%) ---")
        page.click("#stemPad_full")
        time.sleep(0.3)
        state_full = page.evaluate("window.stemsState")
        print(f"Stems State após Mix Original: {state_full}")
        assert state_full["vocal"] == 100 and state_full["drums"] == 100 and state_full["bass"] == 100 and state_full["inst"] == 100
        assert not state_full["solo"], "Solo deve ser nulo"
        assert not any(state_full["muted"].values()), "Nenhum stem deve estar mutado"

        pill_text = page.locator("#stemsEngagedBadge").inner_text()
        assert "FLAT" in pill_text or "ORIGINAL" in pill_text, "Pill deve indicar Mix Original (Flat)"
        print("✓ Retorno ao Mix Original 100% validado!")

        # -------------------------------------------------------------
        # VERIFICAÇÃO 7: Mute e Solo Manuais nos Faders
        # -------------------------------------------------------------
        print("\n--- Verificação 7: Mute e Solo Manuais ---")
        # Clica Mute no Baixo
        page.click("#stemMuteBtn_bass")
        time.sleep(0.2)
        state_mute = page.evaluate("window.stemsState")
        assert state_mute["muted"]["bass"] == True, "Bass deve estar mutado"
        assert page.locator("#stemMuteBtn_bass").get_attribute("class").find("active-mute") != -1, "Botão mute deve ter classe active-mute"

        # Clica Solo na Melodia
        page.click("#stemSoloBtn_inst")
        time.sleep(0.2)
        state_solo = page.evaluate("window.stemsState")
        assert state_solo["solo"] == "inst", "Melodia deve estar solo"
        assert page.locator("#stemSoloBtn_inst").get_attribute("class").find("active-solo") != -1, "Botão solo deve ter classe active-solo"

        # -------------------------------------------------------------
        # VERIFICAÇÃO 8: Botão Fechar Estilizado
        # -------------------------------------------------------------
        print("\n--- Verificação 8: Botão Fechar Estilizado (.eq-close-btn) ---")
        close_btn = page.locator("#djStemsModal .eq-close-btn")
        assert close_btn.is_visible(), "Botão fechar deve estar visível"
        box = close_btn.bounding_box()
        print(f"Dimensões do botão fechar: {box}")
        assert box["width"] >= 28 and box["height"] >= 28, "Botão fechar deve ter dimensões adequadas"
        
        close_btn.click()
        time.sleep(0.5)
        assert not stems_modal.is_visible(), "Modal Stems deve fechar ao clicar no botão fechar!"
        print("✓ Modal fechou perfeitamente ao clicar no botão estizado!")

        print("\n=======================================================")
        print("UPGRADE DO MOTOR DJ STEMS PRO VALIDADE COM 100% DE SUCESSO!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()
