import os
import sys
import time
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def test_equalizer_pro_and_pause_button():
    print("Iniciando testes automatizados do Botão Pause (no esquadro) e Equalizador Pro (10 bandas)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 768})

        url = "http://localhost:5050/player.html"
        print(f"Navegando para: {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # -------------------------------------------------------------
        # TESTE 1: BOTÃO PLAY/PAUSE MATEMATICAMENTE NO ESQUADRO
        # -------------------------------------------------------------
        print("\n--- TESTE 1: Botão Play/Pause no Esquadro ---")
        bar_play = page.locator("#barPlayBtn")
        assert bar_play.is_visible(), "Botão #barPlayBtn não encontrado!"

        # Capturar screenshot no estado Pausado (Play icon SVG)
        transport = page.locator(".bar-transport-cluster")
        play_shot = os.path.join(EVIDENCE_DIR, "botao_play_esquadro_verified.png")
        transport.screenshot(path=play_shot)
        print(f"Screenshot do botão Play capturado: {play_shot}")

        # Inspecionar SVG no estado Pausado
        svg_html = page.evaluate("() => document.getElementById('playIconSpan').innerHTML")
        print("SVG interno no estado Pausado (exibe Play):")
        print(svg_html.strip())
        assert "<polygon" in svg_html or "<svg" in svg_html, "SVG de Play não renderizado!"

        # Simular Play (chamar updatePlayPauseButtons(true))
        page.evaluate("() => updatePlayPauseButtons(true)")
        time.sleep(0.5)

        # Capturar screenshot no estado Tocando (Pause icon SVG)
        pause_shot = os.path.join(EVIDENCE_DIR, "botao_pause_esquadro_verified.png")
        transport.screenshot(path=pause_shot)
        print(f"Screenshot do botão Pause capturado: {pause_shot}")

        # Inspecionar SVG no estado Tocando
        svg_pause_html = page.evaluate("() => document.getElementById('playIconSpan').innerHTML")
        print("SVG interno no estado Tocando (exibe Pause):")
        print(svg_pause_html.strip())
        assert "<rect" in svg_pause_html and 'x="5.5"' in svg_pause_html and 'x="14.5"' in svg_pause_html, "SVG de Pause não possui as barras simétricas x=5.5 e x=14.5!"

        # Verificar se as classes e dimensões estão simétricas
        metrics = page.evaluate("""() => {
            const btn = document.getElementById('barPlayBtn');
            const rect = btn.getBoundingClientRect();
            const computed = window.getComputedStyle(btn);
            return {
                width: rect.width,
                height: rect.height,
                padding: computed.padding,
                display: computed.display,
                alignItems: computed.alignItems,
                justifyContent: computed.justifyContent
            };
        }""")
        print(f"Métricas do botão Pause: {metrics}")
        assert abs(metrics["width"] - metrics["height"]) < 1, f"Botão não é perfeitamente circular! width={metrics['width']}, height={metrics['height']}"

        # -------------------------------------------------------------
        # TESTE 2: EQUALIZADOR PRO (10 BANDAS, 14 PRESETS, CURVA, PREAMP)
        # -------------------------------------------------------------
        print("\n--- TESTE 2: Equalizador Pro (10 Bandas & Curva Analítica) ---")
        
        # Abrir modal do equalizador
        page.evaluate("() => openEqualizerModal()")
        time.sleep(0.5)

        modal = page.locator("#equalizerModal")
        assert modal.is_visible(), "Modal #equalizerModal não está visível!"

        # Verificar as 10 bandas ISO
        freqs = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        for f in freqs:
            slider = page.locator(f"#eqSlider_{f}")
            val_lbl = page.locator(f"#eqVal_{f}")
            assert slider.is_visible(), f"Slider da banda {f} Hz não encontrado!"
            assert val_lbl.is_visible(), f"Label de valor da banda {f} Hz não encontrado!"
        print(f"Todas as 10 bandas ISO ({freqs}) verificadas com sucesso.")

        # Verificar Canvas da curva espectral
        canvas = page.locator("#eqCurveCanvas")
        assert canvas.is_visible(), "Canvas da curva de resposta #eqCurveCanvas não encontrado!"
        
        canvas_info = page.evaluate("""() => {
            const c = document.getElementById('eqCurveCanvas');
            const ctx = c.getContext('2d');
            const imgData = ctx.getImageData(0, 0, c.width, c.height).data;
            let nonZeroPixels = 0;
            for (let i = 0; i < imgData.length; i += 4) {
                if (imgData[i+3] > 0) nonZeroPixels++; // Alpha > 0
            }
            return {
                width: c.width,
                height: c.height,
                nonZeroPixels: nonZeroPixels
            };
        }""")
        print(f"Canvas info: {canvas_info}")
        assert canvas_info["nonZeroPixels"] > 500, "O canvas da curva analítica está vazio!"

        # Testar seleção de Presets (ex: Mega Bass, Funk, Balada, Cumbia)
        test_presets = ["grave", "funk", "balada", "cumbia"]
        for p_key in test_presets:
            page.evaluate(f"() => selectEqPreset('{p_key}')")
            time.sleep(0.1)
            preset_name = page.evaluate("() => document.getElementById('eqActivePresetTag').textContent")
            print(f"Preset selecionado '{p_key}': tag = '{preset_name}'")
            assert p_key in preset_name.lower() or "bass" in preset_name.lower() or "funk" in preset_name.lower() or "balada" in preset_name.lower() or "cumbia" in preset_name.lower()

        # Selecionar o Preset Balada / Club
        page.evaluate("() => selectEqPreset('balada')")
        time.sleep(0.2)

        # Capturar screenshot do Modal do Equalizador Pro com o Preset Balada
        eq_card = page.locator(".eq-modal-card.eq-modal-pro")
        eq_shot = os.path.join(EVIDENCE_DIR, "equalizador_pro_10bandas_verified.png")
        eq_card.screenshot(path=eq_shot)
        print(f"Screenshot do Equalizador Pro capturado: {eq_shot}")

        # Testar Pre-Amp
        page.evaluate("() => setEqPreAmp(3.5)")
        time.sleep(0.1)
        preamp_val = page.evaluate("() => document.getElementById('eqPreAmpVal').textContent")
        print(f"Pre-Amp ajustado para +3.5 dB: exibindo '{preamp_val}'")
        assert "+3.5" in preamp_val

        # Testar Reset para Flat (0 dB)
        page.evaluate("() => resetEqToFlat()")
        time.sleep(0.1)
        flat_check = page.evaluate("""() => {
            const freqs = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000];
            const allZero = freqs.every(f => document.getElementById(`eqSlider_${f}`).value === '0');
            const preZero = document.getElementById('eqPreAmpVal').textContent.includes('0');
            return allZero && preZero;
        }""")
        print(f"Reset Flat executado com sucesso: {flat_check}")
        assert flat_check, "Reset Flat não zerou todas as bandas!"

        # Capturar screenshot do Equalizador Pro em modo Flat
        eq_flat_shot = os.path.join(EVIDENCE_DIR, "equalizador_pro_flat_verified.png")
        eq_card.screenshot(path=eq_flat_shot)
        print(f"Screenshot do Equalizador Flat capturado: {eq_flat_shot}")

        # Fechar modal
        page.evaluate("() => closeEqualizerModal()")
        time.sleep(0.2)

        # Capturar screenshot completo do player inferior para conferir esquadro e botões
        player_bar = page.locator(".bottom-player-bar")
        bar_shot = os.path.join(EVIDENCE_DIR, "bottom_bar_esquadro_verified.png")
        player_bar.screenshot(path=bar_shot)
        print(f"Screenshot da barra inferior completa capturado: {bar_shot}")

        browser.close()
        print("\n TODOS OS TESTES PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    test_equalizer_pro_and_pause_button()
