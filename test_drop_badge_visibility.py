# -*- coding: utf-8 -*-
"""
test_drop_badge_visibility.py
Verifica:
1. Ao abrir o player em modo 'Match Perfeito', o badge '⚡ DROP HUNTER ATIVO' NÃO deve estar visível!
2. Ao alternar entre os modos de atuação (match, club, studio, drop), cada badge deve respeitar estritamente o seu modo.
3. Ao voltar para 'Match Perfeito', o badge '⚡ DROP HUNTER ATIVO' permanece oculto.
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

        drop_badge = page.locator("#djDropActiveBadge")
        club_badge = page.locator("#djClubActiveBadge")
        studio_badge = page.locator("#djStudioActiveBadge")

        # -------------------------------------------------------------
        # TESTE 1: Estado Inicial (Match Perfeito)
        # -------------------------------------------------------------
        print("\n--- Teste 1: Estado Inicial com Match Perfeito ---")
        active_mode_label = page.locator("#djActModeActiveLabel").inner_text()
        print(f"Modo atual: '{active_mode_label}'")

        is_drop_visible = drop_badge.is_visible()
        print(f"Badge Drop Hunter visível no Match Perfeito? {is_drop_visible}")
        assert not is_drop_visible, "FALHA: Badge '⚡ DROP HUNTER ATIVO' não deveria estar visível em 'Match Perfeito'!"

        # Captura screenshot da área dos controles de modo com Match Perfeito
        ss_area = page.locator("#djActModeBox")
        ss1 = ARTIFACTS_DIR / "modo_match_perfeito_sem_drop_badge_verified.png"
        ss_area.screenshot(path=str(ss1))
        print(f"✓ Screenshot comprovando badge oculto em Match Perfeito: {ss1.name}")

        # -------------------------------------------------------------
        # TESTE 2: Alternar para Modo Drop Hunter
        # -------------------------------------------------------------
        print("\n--- Teste 2: Alternar para Modo Drop Hunter ---")
        page.click("#btnDjActTrigger")
        time.sleep(0.4)
        page.locator("#actOpt_drop").click()
        time.sleep(0.6)

        assert drop_badge.is_visible(), "FALHA: Badge Drop Hunter DEVERIA estar visível no modo Drop Hunter!"
        print("✓ Badge Drop Hunter visível corretamente quando modo 'drop' está selecionado.")

        # -------------------------------------------------------------
        # TESTE 3: Alternar de volta para Modo Match Perfeito
        # -------------------------------------------------------------
        print("\n--- Teste 3: Alternar de volta para Match Perfeito ---")
        page.click("#btnDjActTrigger")
        time.sleep(0.4)
        page.locator("#actOpt_match").click()
        time.sleep(0.6)

        assert not drop_badge.is_visible(), "FALHA: Badge Drop Hunter permaneceu visível após voltar para Match Perfeito!"
        print("✓ Badge Drop Hunter sumiu com sucesso ao voltar para Match Perfeito!")

        # -------------------------------------------------------------
        # TESTE 4: Alternar para Modo Balada & Club
        # -------------------------------------------------------------
        print("\n--- Teste 4: Alternar para Balada & Club ---")
        page.click("#btnDjActTrigger")
        time.sleep(0.4)
        page.locator("#actOpt_club").click()
        time.sleep(0.6)

        assert club_badge.is_visible(), "FALHA: Badge Balada deveria estar visível!"
        assert not drop_badge.is_visible(), "FALHA: Badge Drop Hunter não deveria aparecer no modo Balada!"
        print("✓ Apenas Badge Balada visível no modo Balada.")

        # Captura screenshot final
        ss2 = ARTIFACTS_DIR / "alternancia_modos_badges_estritos_verified.png"
        page.locator("#djActModeBox").screenshot(path=str(ss2))
        print(f"✓ Screenshot geral dos modos e badges verificado: {ss2.name}")

        print("\n=======================================================")
        print("TODOS OS TESTES DE VISIBILIDADE DE BADGES PASSARAM 100%!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()
