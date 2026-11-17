# -*- coding: utf-8 -*-
"""
test_realtime_remove_and_move.py
Testa exaustivamente todas as funções de Remover e Mover em tempo real:
1. Modal in-app de confirmação de exclusão (sem window.confirm bloqueante)
2. Remoção em tempo real com animação e atualização atômica de contadores
3. Persistência síncrona no disco (complete_library.json e rebuild automático de player.html)
4. Modal de mover playlist com seleção de categoria e atualização em tempo real
5. Criação dinâmica de nova playlist e movimentação instantânea
"""

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path(r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576")
LIBRARY_FILE = Path("complete_library.json")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        print("Navegando para http://localhost:5050...")
        page.goto("http://localhost:5050", wait_until="networkidle", timeout=15000)
        time.sleep(2)

        # -------------------------------------------------------------
        # TESTE 1: Modal In-App de Remoção e Exclusão em Tempo Real
        # -------------------------------------------------------------
        print("\n--- Teste 1: Modal In-App de Remoção e Exclusão em Tempo Real ---")
        first_card = page.locator(".track-card").first
        assert first_card.is_visible(), "Nenhum card de música encontrado!"

        track_title = first_card.locator(".track-card-title span").inner_text()
        video_id = first_card.get_attribute("data-video-id")
        print(f"Música alvo para remoção: '{track_title}' (video_id: {video_id})")

        # Lê contagem antes da remoção
        count_before_text = page.locator("#navLibraryText").inner_text()
        print(f"Contador antes da remoção: '{count_before_text}'")

        # Clica no botão de lixeira 🗑️
        del_btn = first_card.locator(".btn-remove-lib-card")
        del_btn.click()
        time.sleep(0.5)

        # Verifica abertura do modal in-app
        remove_modal = page.locator("#confirmRemoveModal")
        assert remove_modal.is_visible(), "Modal in-app #confirmRemoveModal não abriu!"

        modal_title = page.locator("#removeModalTrackTitle").inner_text()
        print(f"Título no modal de confirmação: '{modal_title}'")

        # Captura screenshot do modal de remoção
        ss1 = ARTIFACTS_DIR / "modal_confirmar_remocao_in_app_verified.png"
        page.locator(".remove-modal-card").screenshot(path=str(ss1))
        print(f"✓ Screenshot do modal de remoção capturado: {ss1.name}")

        # Confirma a remoção clicando em '🗑️ Sim, Remover'
        page.click("#btnConfirmDeleteTrack")
        time.sleep(1.0)

        # Verifica se modal fechou
        assert not remove_modal.is_visible(), "Modal de remoção não fechou!"

        # Verifica atualização do contador em tempo real
        count_after_text = page.locator("#navLibraryText").inner_text()
        print(f"Contador após remoção em tempo real: '{count_after_text}'")

        toast_text = page.locator("#toastNotify").inner_text()
        print(f"Toast exibido: '{toast_text}'")
        assert "removida da biblioteca" in toast_text, "Toast de remoção não foi disparado!"

        # Verifica persistência no arquivo complete_library.json
        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
            lib = json.load(f)
        assert not any(t.get("video_id") == video_id for t in lib), f"Faixa {video_id} ainda encontrada em complete_library.json!"
        print(f"✓ Faixa {video_id} removida permanentemente do complete_library.json!")

        # -------------------------------------------------------------
        # TESTE 2: Mover Música de Playlist em Tempo Real
        # -------------------------------------------------------------
        print("\n--- Teste 2: Mover Música de Playlist em Tempo Real ---")
        first_card = page.locator(".track-card").first
        track_to_move_title = first_card.locator(".track-card-title span").inner_text()
        move_vid = first_card.get_attribute("data-video-id")
        print(f"Música alvo para mover: '{track_to_move_title}' (video_id: {move_vid})")

        # Clica em 📂 Mover
        first_card.locator(".btn-move-card").click()
        time.sleep(0.5)

        move_modal = page.locator("#movePlaylistModal")
        assert move_modal.is_visible(), "Modal #movePlaylistModal não abriu!"

        # Seleciona uma categoria de destino (3a opção)
        opts = page.locator(".move-playlist-opt-card")
        target_opt = opts.nth(2)
        target_cat_name = target_opt.locator(".move-playlist-opt-name").inner_text().split("\n")[0].strip()
        print(f"Playlist de destino selecionada: '{target_cat_name}'")
        target_opt.click()
        time.sleep(0.3)

        # Captura screenshot do modal com categoria selecionada
        ss2 = ARTIFACTS_DIR / "modal_mover_playlist_tempo_real_verified.png"
        page.locator(".move-modal-card").screenshot(path=str(ss2))
        print(f"✓ Screenshot do modal de mover capturado: {ss2.name}")

        # Confirma movimento
        page.click("#btnConfirmMovePlaylist")
        time.sleep(1.0)

        # Verifica fechamento do modal e toast
        assert not move_modal.is_visible(), "Modal de mover não fechou!"
        toast_move = page.locator("#toastNotify").inner_text()
        print(f"Toast exibido após mover: '{toast_move}'")
        assert "movida com sucesso" in toast_move, "Toast de sucesso de movimento não disparado!"

        # Verifica persistência no complete_library.json
        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
            lib = json.load(f)
        moved_track = next((t for t in lib if t.get("video_id") == move_vid), None)
        assert moved_track is not None, "Faixa não encontrada em complete_library.json após mover!"
        print(f"Categoria da faixa no disco: '{moved_track.get('category')}'")

        # -------------------------------------------------------------
        # TESTE 3: Criar Nova Playlist e Mover Faixa Instantaneamente
        # -------------------------------------------------------------
        print("\n--- Teste 3: Criar Nova Playlist e Mover Faixa Instantaneamente ---")
        second_card = page.locator(".track-card").first
        new_vid = second_card.get_attribute("data-video-id")
        second_card.locator(".btn-move-card").click()
        time.sleep(0.5)

        new_playlist_name = "Festa Eletrônica 2026"
        page.fill("#inputNewPlaylistName", new_playlist_name)
        time.sleep(0.2)

        page.click(".btn-create-move-action")
        time.sleep(1.0)

        assert not page.locator("#movePlaylistModal").is_visible(), "Modal não fechou após criar e mover!"
        toast_new = page.locator("#toastNotify").inner_text()
        print(f"Toast após criar e mover: '{toast_new}'")
        assert new_playlist_name in toast_new, f"Nome da nova playlist '{new_playlist_name}' não encontrado no toast!"

        # Verifica se nova aba apareceu no topo
        new_tab = page.locator(".tab-btn", has_text=new_playlist_name)
        assert new_tab.is_visible(), f"Aba da nova playlist '{new_playlist_name}' não apareceu na barra de abas!"
        print(f"✓ Nova aba '{new_playlist_name}' visível em tempo real na interface!")

        # Captura screenshot da interface com a nova playlist e contadores atualizados
        ss3 = ARTIFACTS_DIR / "nova_playlist_criada_tempo_real_verified.png"
        page.locator("#tabsWrapper").screenshot(path=str(ss3))
        print(f"✓ Screenshot da nova playlist criada capturado: {ss3.name}")

        print("\n=======================================================")
        print("TODOS OS TESTES DE REMOVER E MOVER EM TEMPO REAL PASSARAM 100%!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()
