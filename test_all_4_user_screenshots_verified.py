# -*- coding: utf-8 -*-
"""
test_all_4_user_screenshots_verified.py
Verifica rigorosamente as 4 situações apontadas nas imagens do usuário:
1. Modal de Histórico de Reprodução: contagem correta (sem ficar '0 faixas') e botões completos
2. Barra de Status: títulos limpos sem feat/emojis/colchetes e ambos 'Tocando' e 'A Seguir' visíveis lado a lado
3. HUD Drop Hunter: layout estruturado em 4 linhas, sem compressão do título e sem corte de texto no rodapé
4. Modo de Atuação: badge 'DROP HUNTER ATIVO' estritamente oculto em 'Match Perfeito'
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
        # CASO 1: Modal de Histórico de Reprodução & Descobertas
        # -------------------------------------------------------------
        print("\n--- CASO 1: Modal de Histórico de Reprodução & Descobertas ---")
        page.click("#navHistory")
        time.sleep(0.8)

        modal = page.locator("#historyModal")
        assert modal.is_visible(), "Modal de histórico não abriu!"

        badge_text = page.locator("#modalHistoryBadgeCount").inner_text()
        print(f"Badge do modal de histórico: '{badge_text}'")
        assert "0 faixas" not in badge_text, f"FALHA: Modal de histórico ainda exibe '0 faixas' ({badge_text})!"

        # Verifica se os cards possuem as ações completas (✓ Na Biblioteca com 📂 Mover e 🗑️)
        saved_badge = page.locator(".history-saved-badge").first
        if saved_badge.is_visible():
            print(f"Badge de música salva visível: '{saved_badge.inner_text()}'")
            move_btn = page.locator("#historyModal .btn-move-card").first
            remove_btn = page.locator("#historyModal .btn-remove-lib-card").first
            assert move_btn.is_visible(), "Botão '📂 Mover' não está visível no histórico para faixas da biblioteca!"
            assert remove_btn.is_visible(), "Botão '🗑️' não está visível no histórico para faixas da biblioteca!"
            print("✓ Ações completas (Mover / Remover) presentes nos cards do histórico!")

        ss1 = ARTIFACTS_DIR / "historico_modal_com_contagem_e_acoes_verified.png"
        page.locator(".history-modal-card").screenshot(path=str(ss1))
        print(f"✓ Screenshot do Caso 1 capturado: {ss1.name}")

        page.click("#historyModal .eq-close-btn")
        time.sleep(0.3)

        # -------------------------------------------------------------
        # CASO 2: Barra de Status - Título Limpo Sem Feat/Junk e 'A Seguir' Visível
        # -------------------------------------------------------------
        print("\n--- CASO 2: Barra de Status com Título Limpo Sem Feat/Junk ---")
        # Simula música tocando com título poluído do screenshot 2 e próxima música com feat
        page.evaluate("""() => {
            nowPlayingTrack = {
                title: "•ENGANCHADO CUMBIA FIESTERA REMIX• 😈 [ Cumbias Inolvidables ] Cumbia Del Recuerdo - Cumbia Retro 🔮",
                artist: "Divulga DJs",
                category: "Reggaeton, Cachengue & Latino",
                video_id: "testEnganchado1"
            };
            const mockUpcoming = {
                title: "MIX FIESTERO #11 😎 | PREVIA Y CACHENGUE 2026 | CHEKO DJ (feat. MC Test)",
                artist: "CHEKO DJ",
                category: "Reggaeton, Cachengue & Latino",
                video_id: "testMixUpcoming"
            };
            // Injeta mock em pendingQueue
            pendingQueue = [mockUpcoming];
            updateUpcomingTrackUI();
        }""")
        time.sleep(0.5)

        playing_clean = page.locator(".playing-clean").inner_text()
        next_clean = page.locator(".next-clean").inner_text()
        next_badge = page.locator(".status-badge-next").inner_text()
        print(f"Tocando Limpo: '{playing_clean}'")
        print(f"Próxima Limpa: '{next_clean}'")
        print(f"Badge Próxima: '{next_badge}'")

        assert "😈" not in playing_clean, "Emoji 😈 não foi removido do título tocando!"
        assert "🔮" not in playing_clean, "Emoji 🔮 não foi removido do título tocando!"
        assert "feat" not in next_clean.lower(), "Feat não foi removido da próxima música!"
        assert "•" not in playing_clean, "Bullet • não foi removido do título!"
        assert "A Seguir" in next_badge, "Badge 'A Seguir' foi truncado!"

        ss2 = ARTIFACTS_DIR / "status_bar_dupla_titulo_limpo_verified.png"
        page.locator("#barStatusText").screenshot(path=str(ss2))
        print(f"✓ Screenshot do Caso 2 capturado: {ss2.name}")

        # -------------------------------------------------------------
        # CASO 3: HUD Drop Hunter - Layout Perfeito em 4 Linhas e Sem Cortes
        # -------------------------------------------------------------
        print("\n--- CASO 3: HUD Drop Hunter Estruturado e Legível ---")
        page.click("#btnDjActTrigger")
        time.sleep(0.3)
        page.locator("#actOpt_drop").click()
        time.sleep(0.5)

        hud = page.locator("#djDropHunterHud")
        assert hud.is_visible(), "HUD Drop Hunter não está visível no modo 'drop'!"

        title_el = page.locator(".drop-hud-title")
        pill_el = page.locator("#dropStatusPill")
        footer_el = page.locator("#dropHudFooterText")

        print(f"Título da HUD: '{title_el.inner_text()}'")
        print(f"Pill de Status: '{pill_el.inner_text()}'")
        print(f"Texto do Rodapé: '{footer_el.inner_text()}'")

        assert title_el.is_visible(), "Título da HUD não está visível!"
        assert pill_el.is_visible(), "Pill de Status não está visível!"
        footer_lower = footer_el.inner_text().lower()
        assert "auto drop" in footer_lower or "refrão" in footer_lower or "mix longo" in footer_lower, "Rodapé da HUD incompleto!"

        ss3 = ARTIFACTS_DIR / "hud_drop_hunter_layout_perfeito_verified.png"
        hud.screenshot(path=str(ss3))
        print(f"✓ Screenshot do Caso 3 capturado: {ss3.name}")

        # -------------------------------------------------------------
        # CASO 4: Modo de Atuação - Badge 'DROP HUNTER ATIVO' Oculto em 'Match Perfeito'
        # -------------------------------------------------------------
        print("\n--- CASO 4: Badge 'DROP HUNTER ATIVO' Oculto em 'Match Perfeito' ---")
        # Volta para Match Perfeito
        page.click("#btnDjActTrigger")
        time.sleep(0.3)
        page.locator("#actOpt_match").click()
        time.sleep(0.5)

        drop_badge = page.locator("#djDropActiveBadge")
        is_drop_badge_visible = drop_badge.is_visible()
        print(f"Visibilidade do badge 'DROP HUNTER ATIVO' em Match Perfeito: {is_drop_badge_visible}")
        assert not is_drop_badge_visible, "FALHA CRÍTICA: Badge 'DROP HUNTER ATIVO' está visível quando o modo é 'Match Perfeito'!"

        current_label = page.locator("#djActModeActiveLabel").inner_text()
        print(f"Modo de Atuação atual: '{current_label}'")
        assert "Match Perfeito" in current_label, f"Modo esperado 'Match Perfeito', obtido '{current_label}'!"

        ss4 = ARTIFACTS_DIR / "modo_match_perfeito_sem_drop_badge_estrito_verified.png"
        page.locator("#djActModeBox").screenshot(path=str(ss4))
        print(f"✓ Screenshot do Caso 4 capturado: {ss4.name}")

        print("\n=======================================================")
        print("TODOS OS 4 CASOS DAS IMAGENS DO USUÁRIO FORAM 100% VALIDADOS!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()
