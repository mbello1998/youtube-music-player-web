# -*- coding: utf-8 -*-
import os
import time
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def test_history_and_repeat():
    print("Iniciando bateria de testes para Historico, Salvamento e Botao Repetir...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 720})
        url = "http://localhost:5050/player.html"
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1)

        # -------------------------------------------------------------
        # TESTE 1: BOTAO REPETIR NO TRANSPORTE (AO LADO DO AUTOPLAY)
        # -------------------------------------------------------------
        print("\n--- Teste 1: Botao Repetir Musica ao lado do AutoPlay ---")
        repeat_btn = page.locator("#barRepeatBtn")
        assert repeat_btn.is_visible(), "Botao #barRepeatBtn nao esta visivel no player!"
        
        auto_box = page.locator("#barAutoPlayBtn").bounding_box()
        rep_box = repeat_btn.bounding_box()
        print(f"Posicao AutoPlay: {auto_box}")
        print(f"Posicao Repetir:  {rep_box}")
        assert abs(rep_box["y"] - auto_box["y"]) < 5, "Botao Repetir deveria estar na mesma linha do AutoPlay!"
        assert rep_box["x"] > auto_box["x"], "Botao Repetir deveria estar a direita do AutoPlay!"

        # Ciclo 1: Clicar para ativar 'Repetir Mesma Musica (1)'
        repeat_btn.click()
        time.sleep(0.3)
        assert "active" in repeat_btn.get_attribute("class")
        assert "1" in repeat_btn.inner_text()
        print(f"  ✓ Estado 1: {repeat_btn.inner_text()} (Ativo para mesma musica)")

        # Ciclo 2: Clicar para ativar 'Repetir Playlist (Todas)'
        repeat_btn.click()
        time.sleep(0.3)
        assert "active" in repeat_btn.get_attribute("class")
        assert "Todas" in repeat_btn.inner_text()
        print(f"  ✓ Estado 2: {repeat_btn.inner_text()} (Ativo para toda playlist)")

        # Ciclo 3: Clicar para Desativar
        repeat_btn.click()
        time.sleep(0.3)
        assert "active" not in repeat_btn.get_attribute("class")
        print(f"  ✓ Estado 0: {repeat_btn.inner_text()} (Desativado)")

        # Deixar no modo 'Repetir: 1' para teste e screenshot
        repeat_btn.click()
        time.sleep(0.3)
        bottom_bar_shot = os.path.join(EVIDENCE_DIR, "botao_repetir_ao_lado_autoplay_verified.png")
        page.locator(".bottom-player-bar").screenshot(path=bottom_bar_shot)
        print(f"Screenshot da barra inferior com botao repetir: {bottom_bar_shot}")

        # -------------------------------------------------------------
        # TESTE 2: HISTORICO DE REPRODUCAO & SALVAR NA BIBLIOTECA
        # -------------------------------------------------------------
        print("\n--- Teste 2: Historico de Reproducao & Salvamento Real na Biblioteca ---")
        page.click("#navHistory")
        time.sleep(0.6)

        hist_modal = page.locator("#historyModal")
        assert hist_modal.is_visible(), "Modal de historico nao abriu!"

        # Verificar contador no cabecalho do modal (NAO pode ser '0 faixas')
        modal_badge = page.locator("#modalHistoryBadgeCount")
        badge_text = modal_badge.inner_text()
        print(f"Badge do Modal de Historico: '{badge_text}'")
        assert "0 faixas" not in badge_text, f"Badge continua travado em 0 faixas! Valor: '{badge_text}'"

        # Localizar botao de salvar em uma faixa do historico
        save_buttons = page.locator("#historyModal .btn-history-save")
        save_count = save_buttons.count()
        print(f"Faixas disponiveis para salvar no historico: {save_count}")
        
        if save_count > 0:
            first_save_btn = save_buttons.first
            target_card = first_save_btn.locator('xpath=ancestor::div[contains(@class, "history-track-card")]')
            target_card_id = target_card.get_attribute("id")
            target_title = target_card.locator(".history-title").inner_text()
            print(f"Faixa do historico a ser salva: id={target_card_id}, titulo='{target_title}'")

            lib_count_before = page.evaluate("() => { let total = 0; CATEGORIES.forEach(c => total += (DATA[c]||[]).length); return total; }")
            print(f"Total de musicas na biblioteca antes: {lib_count_before}")

            first_save_btn.click()
            time.sleep(1.5)

            saved_badge = page.locator(f"#{target_card_id} .history-saved-badge")
            assert saved_badge.is_visible(), "Botao nao foi substituido pelo badge '✓ Salvo na Biblioteca'!"
            print(f"  ✓ Badge atualizado com sucesso: '{saved_badge.inner_text()}'")

            lib_count_after = page.evaluate("() => { let total = 0; CATEGORIES.forEach(c => total += (DATA[c]||[]).length); return total; }")
            print(f"Total de musicas na biblioteca apos: {lib_count_after}")
            assert lib_count_after == lib_count_before + 1, f"Biblioteca nao incrementou! Antes={lib_count_before}, Depois={lib_count_after}"

        hist_shot = os.path.join(EVIDENCE_DIR, "historico_salvo_na_biblioteca_verified.png")
        page.locator(".history-modal-card").screenshot(path=hist_shot)
        print(f"Screenshot do modal de historico capturado: {hist_shot}")

        # Fechar modal via evaluate
        page.evaluate("() => closeHistoryModal()")
        time.sleep(0.4)

        # -------------------------------------------------------------
        # TESTE 3: VERIFICAR FAIXA NA ABA DA BIBLIOTECA
        # -------------------------------------------------------------
        print("\n--- Teste 3: Verificacao Visual na Minha Biblioteca ---")
        page.click("#navLibrary")
        time.sleep(0.5)

        total_now = page.evaluate("() => { let total = 0; CATEGORIES.forEach(c => total += (DATA[c]||[]).length); return total; }")
        nav_text = page.locator("#navLibraryText").inner_text()
        print(f"Texto da Aba Minha Biblioteca: '{nav_text}' (Total={total_now})")
        assert f"({total_now})" in nav_text

        lib_shot = os.path.join(EVIDENCE_DIR, "minha_biblioteca_atualizada_verified.png")
        page.screenshot(path=lib_shot)
        print(f"Screenshot da Minha Biblioteca: {lib_shot}")

        browser.close()
        print("\n=======================================================")
        print("TODOS OS TESTES DE REPETIR E SALVAMENTO PASSARAM 100%!")
        print("=======================================================")

if __name__ == "__main__":
    test_history_and_repeat()
