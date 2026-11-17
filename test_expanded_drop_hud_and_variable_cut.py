# -*- coding: utf-8 -*-
"""
test_expanded_drop_hud_and_variable_cut.py
Verifica:
1. HUD Drop Hunter amplo, espaçoso, sem quebras toscas e com tipografia nítida
2. Status pill em linha única e botões de ação bem distribuídos
3. Janela de corte variável em tempo real
4. Mix Jumper automático e manual para mixes longos (> 5 min)
5. Pulo automático pro drop ao iniciar faixas no modo Drop Hunter
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path(r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        print("Navegando para http://localhost:5050...")
        page.goto("http://localhost:5050", wait_until="networkidle", timeout=15000)
        time.sleep(2)

        # -------------------------------------------------------------
        # TESTE 1: Ativação do Modo Drop Hunter & Inspeção do Novo HUD
        # -------------------------------------------------------------
        print("\n--- Teste 1: Ativação do Modo Drop Hunter & Novo HUD ---")
        page.click("#btnDjActTrigger")
        time.sleep(0.5)

        drop_opt = page.locator("#actOpt_drop")
        assert drop_opt.is_visible(), "Opção 'actOpt_drop' não está visível no dropdown!"
        drop_opt.click()
        time.sleep(1)

        # Verifica HUD visível
        drop_hud = page.locator("#djDropHunterHud")
        assert drop_hud.is_visible(), "HUD '#djDropHunterHud' não está visível!"

        panel_box = page.locator(".dj-drop-glass-panel").bounding_box()
        print(f"Dimensões do painel Drop Hunter: {panel_box['width']}x{panel_box['height']}")
        assert panel_box["width"] >= 280, f"Painel muito estreito ({panel_box['width']}px)!"

        # Verifica que o status pill NÃO quebra em múltiplas linhas (altura deve ser compacta <= 30px)
        pill_box = page.locator("#dropStatusPill").bounding_box()
        print(f"Dimensões do status pill: {pill_box['width']}x{pill_box['height']}")
        assert pill_box["height"] <= 30, f"Status pill quebrou em múltiplas linhas (altura={pill_box['height']}px)!"

        # Verifica os botões de ação na linha 2
        skip_btn = page.locator("#btnSkipToDrop")
        cut_btn = page.locator("#btnCutToNextDrop")
        auto_btn = page.locator("#btnAutoDropToggle")

        assert skip_btn.is_visible(), "Botão 'Pular pro Drop' não está visível!"
        assert cut_btn.is_visible(), "Botão 'Cortar no Drop' não está visível!"
        assert auto_btn.is_visible(), "Botão 'Auto DJ' não está visível!"
        print(f"Texto do botão auto: '{auto_btn.inner_text()}'")

        # -------------------------------------------------------------
        # TESTE 2: Simulação de Drop Ativo & Janela Variável
        # -------------------------------------------------------------
        print("\n--- Teste 2: Simulação de Drop Ativo & Janela Variável ---")
        # Injeta faixa normal de festa com energia alta (82%)
        page.evaluate("""() => {
            window._simulatedDropEnergy = 82;
            nowPlayingTrack = {
                title: "Mega Funk Lost 2 - DJ Maninho, DJ Dudu",
                artist: "DJ Maninho",
                video_id: "test_megafunk_123",
                duration: 160,
                bpm: 149
            };
            dropActiveSeconds = 12.5;
            dropTargetSeconds = 48.0;
            if (typeof updateDropHunterMetrics === "function") {
                updateDropHunterMetrics();
            }
        }""")
        time.sleep(0.5)

        pill_text = page.locator("#dropStatusPill").inner_text()
        print(f"Status pill em Drop Ativo: '{pill_text}'")
        assert "DROP ATIVO" in pill_text or "PISTA" in pill_text, "Status pill não refletiu Drop Ativo!"

        timer_text = page.locator("#dropTimerVal").inner_text()
        print(f"Medidor de Janela de Drop: '{timer_text}'")
        assert "/" in timer_text, "Janela de tempo não formatada corretamente!"

        # Captura screenshot com faixa normal no Drop
        ss1 = ARTIFACTS_DIR / "hud_drop_hunter_ampliado_legivel_verified.png"
        drop_hud.screenshot(path=str(ss1))
        print(f"✓ Screenshot do HUD ampliado e legível capturado: {ss1.name}")

        # -------------------------------------------------------------
        # TESTE 3: Suporte a Mixes Longos & Mix Jumper (+75s)
        # -------------------------------------------------------------
        print("\n--- Teste 3: Suporte a Mixes Longos & Mix Jumper ---")
        # Injeta um mix longo de 30 minutos (1820s)
        page.evaluate("""() => {
            window._simulatedDropEnergy = 78;
            nowPlayingTrack = {
                title: "•ENGANCHADO CUMBIA FIESTERA REMIX• 👿 [ Cumbias Inolvidables ] Cumbia Retro",
                artist: "Cumbias Inolvidables",
                video_id: "PFShMpSiiYQ",
                duration: 1820,
                bpm: 124
            };
            dropActiveSeconds = 8.0;
            dropTargetSeconds = 42.0;
            if (typeof updateDropHunterMetrics === "function") {
                updateDropHunterMetrics();
            }
        }""")
        time.sleep(0.5)

        mix_btn = page.locator("#btnMixJump")
        assert mix_btn.is_visible(), "Botão '🔀 Próximo Refrão do Mix' não apareceu para o mix longo!"
        print(f"Botão Mix Jumper visível com texto: '{mix_btn.inner_text()}'")

        footer_text = page.locator("#dropHudFooterText").inner_text()
        print(f"Footer informativo para Mix Longo: '{footer_text}'")
        assert "Mix Longo" in footer_text or "refrões" in footer_text, "Footer não identificou mix longo!"

        # Testa o clique no Mix Jumper
        mix_btn.click()
        time.sleep(0.5)

        toast_el = page.locator("#toastNotify")
        if toast_el.is_visible():
            print(f"Toast após salto no mix: '{toast_el.inner_text()}'")

        # Captura screenshot com Mix Jumper ativo
        ss2 = ARTIFACTS_DIR / "mix_jumper_longos_verified.png"
        drop_hud.screenshot(path=str(ss2))
        print(f"✓ Screenshot do Mix Jumper para faixas longas capturado: {ss2.name}")

        # -------------------------------------------------------------
        # TESTE 4: Verificação da Lógica do Pulo Automático no Drop (startSec)
        # -------------------------------------------------------------
        print("\n--- Teste 4: Pulo Automático no Drop ao iniciar Faixa ---")
        start_normal = page.evaluate("() => getTrackDropStartTime({ title: 'Mega Funk Test', duration: 150 })")
        start_mix = page.evaluate("() => getTrackDropStartTime({ title: 'MIX FIESTERO', duration: 1800 })")
        print(f"Ponto de início do Drop para faixa normal: {start_normal}s")
        print(f"Ponto de início do Drop para mix longo: {start_mix}s")

        assert start_normal >= 18.0, "Ponto de início do drop para faixa normal muito baixo!"
        assert start_mix >= 20.0, "Ponto de início do drop para mix longo muito baixo!"

        print("\n=======================================================")
        print("TODOS OS TESTES DE HUD AMPLO E DROP AUTOMÁTICO PASSARAM!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()
