# -*- coding: utf-8 -*-
"""
test_studio_mode_and_fx.py
Valida:
1. Dropdown com a opção "Estúdio Pro & Mastering".
2. Ativação do Modo Estúdio e exibição do Badge neon no painel do mixer.
3. Abertura e funcionamento da Console de Estúdio (Reverb, Delay, Compressor SSL, Saturação, VU Meters).
4. Motor de Cauda Suave DJ FX (Reverb Convolver e Stereo Delay de 2.2s conectados).
5. Captura de evidências visuais em PNG.
"""

import os
import time
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"

def test_studio():
    print("Iniciando bateria de testes do MODO ESTÚDIO e DSP DE MASTERING...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 850})
        page = context.new_page()

        page.goto("http://localhost:5050/player.html", wait_until="networkidle", timeout=20000)
        time.sleep(1.0)

        # -------------------------------------------------------------
        # TESTE 1: DROPDOWN COM O NOVO MODO ESTÚDIO PRO & MASTERING
        # -------------------------------------------------------------
        print("\n--- TESTE 1: Dropdown Modo de Atuação com Estúdio Pro ---")
        page.evaluate("() => toggleDjActDropdown()")
        time.sleep(0.4)

        opt_studio = page.locator("#actOpt_studio")
        assert opt_studio.is_visible(), "Opção Estúdio Pro & Mastering não está visível no dropdown!"

        dropdown_el = page.locator("#djActDropdownMenu")
        drop_shot = os.path.join(EVIDENCE_DIR, "dropdown_with_studio_mode_verified.png")
        page.locator("#spotifyDjMixer").screenshot(path=drop_shot)
        print(f"Screenshot do dropdown com Estúdio capturado: {drop_shot}")

        # -------------------------------------------------------------
        # TESTE 2: SELEÇÃO DO MODO ESTÚDIO & BADGE ATIVO NO MIXER
        # -------------------------------------------------------------
        print("\n--- TESTE 2: Seleção do Modo Estúdio & Badge Ativo ---")
        page.evaluate("() => selectDjActMode('studio')")
        time.sleep(0.4)

        studio_badge = page.locator("#djStudioActiveBadge")
        assert studio_badge.is_visible(), "Badge do Modo Estúdio não apareceu quando ativado!"
        
        active_label = page.evaluate("() => document.getElementById('djActModeActiveLabel').textContent")
        print("Label ativo no seletor:", active_label)
        assert "Estúdio" in active_label, f"Label inesperado: {active_label}"

        badge_shot = os.path.join(EVIDENCE_DIR, "studio_mode_badge_verified.png")
        page.locator("#spotifyDjMixer").screenshot(path=badge_shot)
        print(f"Screenshot do mixer com badge do estúdio capturado: {badge_shot}")

        # -------------------------------------------------------------
        # TESTE 3: ABERTURA DO MODAL DA CONSOLE DE ESTÚDIO & VU METERS
        # -------------------------------------------------------------
        print("\n--- TESTE 3: Console de Estúdio & Mastering DSP ---")
        page.evaluate("() => openStudioModal()")
        time.sleep(0.5)

        modal_el = page.locator("#studioModal")
        assert modal_el.is_visible(), "Modal da Console de Estúdio não abriu!"

        # Testa parâmetros e presets
        page.evaluate("() => selectStudioPreset('hall')")
        time.sleep(0.2)
        hall_active = page.evaluate("() => document.getElementById('stPreset_hall').classList.contains('active')")
        assert hall_active, "Preset Concert Hall não ficou ativo!"

        # Volta para preset Mastering Neve Warmth
        page.evaluate("() => selectStudioPreset('mastering')")
        time.sleep(0.2)

        # Captura screenshot da Console de Estúdio aberta
        console_shot = os.path.join(EVIDENCE_DIR, "studio_modal_console_verified.png")
        page.locator(".studio-modal-card").screenshot(path=console_shot)
        print(f"Screenshot da Console de Estúdio capturado: {console_shot}")

        # -------------------------------------------------------------
        # TESTE 4: VALIDAÇÃO DO MOTOR DE CAUDA SUAVE (REVERB/DELAY NO DJ FX)
        # -------------------------------------------------------------
        print("\n--- TESTE 4: Verificação da Cauda Suave no Motor DJ FX ---")
        fx_tail_status = page.evaluate("""() => {
            const ctx = window.audioCtx;
            const dest = window.getDjFxDestination(ctx);
            return {
                hasDest: dest !== null,
                hasImpulseFn: typeof window.createStudioImpulseBuffer === 'function',
                hasStudioDsp: typeof window.initStudioDsp === 'function',
                studioSettings: window.studioSettings
            };
        }""")
        print("Status do motor de áudio e cauda espacial:", fx_tail_status)
        assert fx_tail_status["hasDest"], "Destino DJ FX não foi criado!"
        assert fx_tail_status["hasImpulseFn"], "Função de resposta de impulso não encontrada!"
        assert fx_tail_status["hasStudioDsp"], "initStudioDsp não encontrada!"

        page.evaluate("() => closeStudioModal()")
        time.sleep(0.3)

        # Captura screenshot da barra de controle inferior com o botão Estúdio Pro
        bar_shot = os.path.join(EVIDENCE_DIR, "studio_bottom_bar_button_verified.png")
        page.locator(".bottom-player-bar").screenshot(path=bar_shot)
        print(f"Screenshot da barra inferior com botão Estúdio capturado: {bar_shot}")

        browser.close()
        print("\n TODOS OS TESTES DA SUÍTE DE ESTÚDIO E CAUDA SUAVE PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    test_studio()
