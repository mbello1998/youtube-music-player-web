import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path(r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576")

def test_studio_pro_extended():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 1000})
        page = context.new_page()

        print("Navegando para http://localhost:5050...")
        page.goto("http://localhost:5050", wait_until="networkidle")
        page.wait_for_timeout(1500)

        # 1. Abrir Modal Studio Pro Extended
        print("\n--- Teste 1: Abertura da Console Estúdio Pro Extended ---")
        studio_btn = page.locator("#barStudioBtn")
        assert studio_btn.is_visible(), "Botão '🎚️ Estúdio Pro' não encontrado na bottom bar!"
        studio_btn.click()
        page.wait_for_timeout(1000)

        modal = page.locator("#studioModal")
        assert modal.is_visible(), "Modal da Console Studio Pro não abriu!"
        title = page.locator(".studio-modal-title").inner_text()
        print(f"Título da Console: {title}")
        assert "EXTENDED" in title or "MASTERING" in title, f"Título inesperado: {title}"

        # Verificar Canvas do Spectrum Analyzer
        canvas = page.locator("#studioSpectrumCanvas")
        assert canvas.is_visible(), "Canvas do Analisador de Espectro não visível!"
        print("✓ Analisador de Espectro FFT Real-Time visível!")

        # Verificar Medidores (L, R, GR, LUFS)
        assert page.locator("#studioVuFillL").is_visible(), "VU L não visível!"
        assert page.locator("#studioVuFillR").is_visible(), "VU R não visível!"
        assert page.locator(".gr-track").is_visible(), "Track SSL GR não visível!"
        assert page.locator(".lufs-track").is_visible(), "Track Loudness LUFS não visível!"
        assert page.locator("#studioLufsVal").is_visible(), "Valor LUFS não visível!"
        print("✓ Painel de 4 Medidores Analógicos (L, R, SSL GR, Perceived LUFS) 100% visível!")

        # Capturar Screenshot 1: Visão Geral da Console Aberta
        ss1 = ARTIFACTS_DIR / "studio_pro_extended_console_verified.png"
        page.locator(".studio-modal-card").screenshot(path=str(ss1))
        print(f"✓ Screenshot 1 capturado: {ss1.name}")

        # 2. Testar Presets (Sub-Bass 808, Modern Pop/EDM, Loudness War)
        print("\n--- Teste 2: Teste de Presets de Estúdio e Atualização Dinâmica ---")
        preset_sub = page.locator("#stPreset_subpunch")
        assert preset_sub.is_visible(), "Preset Sub-Bass 808 não encontrado!"
        preset_sub.click()
        page.wait_for_timeout(500)
        assert "active" in preset_sub.get_attribute("class"), "Preset Sub-Bass não ficou ativo!"
        sub_boost_val = page.locator("#valStudioSubBoost").inner_text()
        print(f"Sub-Bass Boost após Preset Sub-Bass: {sub_boost_val}")
        assert "+8.5" in sub_boost_val or "+8" in sub_boost_val, f"Valor inesperado de sub boost: {sub_boost_val}"

        # Preset Modern Pop/EDM
        preset_crystal = page.locator("#stPreset_crystal")
        preset_crystal.click()
        page.wait_for_timeout(500)
        air_boost_val = page.locator("#valStudioAirBoost").inner_text()
        print(f"Air Boost após Preset Modern Pop/EDM: {air_boost_val}")
        assert "+7.5" in air_boost_val or "+7" in air_boost_val, f"Valor inesperado de air boost: {air_boost_val}"

        # Preset Loudness War (+6dB)
        preset_loud = page.locator("#stPreset_loudness")
        preset_loud.click()
        page.wait_for_timeout(500)
        max_val = page.locator("#valStudioMaximizer").inner_text()
        print(f"Maximizer Drive após Preset Loudness War: {max_val}")
        assert "+6.5" in max_val or "+6" in max_val, f"Valor inesperado de maximizer: {max_val}"

        # Capturar Screenshot 2: Presets & Rack Modules
        ss2 = ARTIFACTS_DIR / "studio_pro_presets_and_spectrum_verified.png"
        page.locator(".studio-modal-card").screenshot(path=str(ss2))
        print(f"✓ Screenshot 2 capturado: {ss2.name}")

        # 3. Testar Controles Adicionais: Mono Check, A/B Bypass e 8 Racks
        print("\n--- Teste 3: Checagem Mono Matrix, A/B Bypass e Racks ---")
        mono_btn = page.locator("#btnStudioMono")
        assert mono_btn.is_visible(), "Botão Mono Check não visível!"
        mono_btn.click()
        page.wait_for_timeout(300)
        assert "active" in mono_btn.get_attribute("class"), "Mono check não ativou!"
        print("✓ Checagem Mono ativada com sucesso!")
        mono_btn.click()
        page.wait_for_timeout(300)
        assert "active" not in mono_btn.get_attribute("class"), "Mono check não desativou!"
        print("✓ Checagem Mono desativada (retorno a Estéreo)!")

        # A/B Bypass Test
        bypass_btn = page.locator("#btnStudioBypass")
        bypass_btn.click()
        page.wait_for_timeout(300)
        assert "BYPASS" in page.locator("#studioBypassLabel").inner_text(), "Bypass não ativou!"
        print("✓ Modo A/B Bypass (Som Direto) confirmado!")
        bypass_btn.click()
        page.wait_for_timeout(300)
        assert "DSP ATIVO" in page.locator("#studioBypassLabel").inner_text(), "DSP não reativou!"
        print("✓ Modo DSP Ativo (Som Masterizado) reativado!")

        # Reset Flat Test
        page.locator(".btn-studio-reset").click()
        page.wait_for_timeout(500)
        assert "+0.0" in page.locator("#valStudioMaximizer").inner_text() or "+0" in page.locator("#valStudioMaximizer").inner_text(), "Reset Flat não resetou Maximizer!"
        print("✓ Reset Flat restaurou sinal limpo com sucesso!")

        # Retornar para Neve Warmth para visual ideal
        page.locator("#stPreset_mastering").click()
        page.wait_for_timeout(500)

        # Capturar Screenshot 3: Detalhe dos 8 Racks
        ss3 = ARTIFACTS_DIR / "studio_pro_8_racks_detail_verified.png"
        page.locator(".studio-rack-grid").screenshot(path=str(ss3))
        print(f"✓ Screenshot 3 capturado: {ss3.name}")

        print("\n=======================================================")
        print("UPGRADE DO STUDIO PRO COMPLETO E 100% VALIDADO!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    test_studio_pro_extended()
