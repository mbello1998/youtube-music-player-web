# -*- coding: utf-8 -*-
"""
test_fiesteros_and_drop_hunter.py
Verifica integralmente:
1. Exibição limpa e simultânea de música tocando e a seguir (sem feat, sem corte de '⏭️ A Seguir')
2. Playlists autênticas de Mix Fiesteros e Enganchados no painel Spotify
3. Modo DJ Drop Hunter & High Energy com HUD de Análise de Onda em tempo real
"""

import sys
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
        # TESTE 1: Títulos Longos & Barra de Status Dual-Column (Sem corte)
        # -------------------------------------------------------------
        print("\n--- Teste 1: Títulos Longos & Barra de Status Dual-Column ---")
        
        # Injeta uma faixa tocando com título super longo (o mesmo da imagem do usuário)
        # e uma faixa a seguir também com título longo
        page.evaluate("""() => {
            nowPlayingTrack = {
                title: "•ENGANCHADO CUMBIA FIESTERA REMIX• 👿 [ Cumbias Inolvidables ] Cumbia Del Recuerdo - Cumbia Retro 🐼",
                artist: "Cumbias Inolvidables",
                video_id: "PFShMpSiiYQ",
                bpm: 124
            };
            // Próxima faixa com feat longo
            djModeNextTrack = {
                title: "MIX FIESTERO #11 😎 (feat. DJ Cu3rvo & Sonido) | PREVIA Y CACHENGUE 2026 | CHEKO DJ | LO MAS ESCUCHADO 🔥",
                artist: "CHEKO DJ",
                video_id: "4ugmfIPxOCw",
                bpm: 128
            };
            updateUpcomingTrackUI();
        }""")
        time.sleep(1)

        bar_status = page.locator("#barStatusText")
        bar_text = bar_status.inner_text()
        print(f"Texto renderizado na barra: '{bar_text}'")

        # Verifica se ambos os blocos existem e estão visíveis
        bar_now = page.locator(".bar-status-col.bar-status-now")
        bar_next = page.locator(".bar-status-col.bar-status-next")
        assert bar_now.is_visible(), "Bloco 'bar-status-now' não está visível!"
        assert bar_next.is_visible(), "Bloco 'bar-status-next' não está visível!"

        now_clean_text = page.locator(".bar-status-now strong.playing-clean").inner_text()
        next_clean_text = page.locator(".bar-status-next strong.next-clean").inner_text()
        print(f"Tocando agora (limpo): '{now_clean_text}'")
        print(f"A seguir (limpo): '{next_clean_text}'")

        assert "feat" not in now_clean_text.lower(), "Título tocando ainda contém 'feat'!"
        assert "feat" not in next_clean_text.lower(), "Título a seguir ainda contém 'feat'!"
        assert "A Seguir" in bar_text, "Label 'A Seguir' foi cortado!"
        assert len(next_clean_text) > 3, "Próxima música não apareceu!"

        # Captura screenshot da barra de controle inferior
        bottom_bar = page.locator(".bottom-player-bar")
        bar_screenshot = ARTIFACTS_DIR / "status_bar_duo_titles_verified.png"
        bottom_bar.screenshot(path=str(bar_screenshot))
        print(f"✓ Screenshot da barra de status capturado: {bar_screenshot.name}")

        # -------------------------------------------------------------
        # TESTE 2: Playlists de Mix Fiesteros & Enganchados no Spotify
        # -------------------------------------------------------------
        print("\n--- Teste 2: Playlists de Mix Fiesteros & Enganchados no Spotify ---")
        page.click("#navSpotify")
        time.sleep(1)

        fiestero_chip = page.locator("#spChip_fiestero")
        assert fiestero_chip.is_visible(), "Chip 'spChip_fiestero' não está visível!"
        fiestero_chip.click()
        time.sleep(1)

        # Verifica se as abas das playlists fiesteras aparecem
        tabs_text = page.locator("#spotifyTabsContainer").inner_text()
        print(f"Abas de playlists exibidas:\n{tabs_text}")
        assert "Fiestero" in tabs_text or "ENGANCHADO" in tabs_text, "Playlists fiesteras não encontradas nas abas!"

        sp_screenshot = ARTIFACTS_DIR / "playlists_fiesteros_enganchados_verified.png"
        page.locator("#paneSpotify").screenshot(path=str(sp_screenshot))
        print(f"✓ Screenshot das playlists fiesteras capturado: {sp_screenshot.name}")

        # Volta para a view da biblioteca
        page.click("#navLibrary")
        time.sleep(1)

        # -------------------------------------------------------------
        # TESTE 3: Modo Drop Hunter & High Energy + HUD de Análise de Onda
        # -------------------------------------------------------------
        print("\n--- Teste 3: Modo Drop Hunter & High Energy + HUD ---")
        # Abre o dropdown de modos
        page.click("#btnDjActTrigger")
        time.sleep(0.5)

        drop_opt = page.locator("#actOpt_drop")
        assert drop_opt.is_visible(), "Opção 'actOpt_drop' não está visível no dropdown!"
        drop_opt.click()
        time.sleep(1)

        # Verifica o label ativo
        active_label = page.locator("#djActModeActiveLabel").inner_text()
        print(f"Label de modo ativo: '{active_label}'")
        assert "Drop Hunter" in active_label, "Modo Drop Hunter não ficou ativo!"

        # Verifica o badge de confirmação
        drop_badge = page.locator("#djDropActiveBadge")
        assert drop_badge.is_visible(), "Badge '#djDropActiveBadge' não está visível!"

        # Verifica o HUD de Análise de Onda
        drop_hud = page.locator("#djDropHunterHud")
        assert drop_hud.is_visible(), "HUD '#djDropHunterHud' não está visível!"

        # Testa os botões de ação do Drop
        skip_btn = page.locator("#btnSkipToDrop")
        cut_btn = page.locator("#btnCutToNextDrop")
        assert skip_btn.is_visible(), "Botão 'Pular pro Drop' não está visível!"
        assert cut_btn.is_visible(), "Botão 'Cortar no Drop' não está visível!"

        skip_btn.click()
        time.sleep(0.5)
        toast_el = page.locator("#toastNotify")
        if toast_el.is_visible():
            toast_text = toast_el.inner_text()
            print(f"Toast após clique 'Pular pro Drop': '{toast_text}'")

        # Captura screenshot do painel DJ com Drop Hunter ativo
        mixer_panel = page.locator("#spotifyDjMixer")
        mixer_screenshot = ARTIFACTS_DIR / "drop_hunter_wave_hud_verified.png"
        mixer_panel.screenshot(path=str(mixer_screenshot))
        print(f"✓ Screenshot do HUD Drop Hunter capturado: {mixer_screenshot.name}")

        print("\n=======================================================")
        print("TODOS OS TESTES DE MIX FIESTEROS E DROP HUNTER PASSARAM (100%)!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()
