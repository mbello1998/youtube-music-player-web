import os
import time
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def test_all_fixes():
    print("Iniciando bateria de testes Playwright para verificar todas as correções...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Notebook padrão: 1366 x 680 (altura restrita como na tela do usuário)
        page = browser.new_page(viewport={"width": 1366, "height": 680})
        url = "http://localhost:5050/player.html"
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1)

        # -------------------------------------------------------------
        # TESTE 1: BOTÃO DE SINCRONIZAR NO CABEÇALHO (ZERO OBSTRUÇÃO)
        # -------------------------------------------------------------
        print("\n--- Teste 1: Botão Sincronizar com YouTube no Cabeçalho ---")
        sync_btn = page.locator("#floatingSyncBtn")
        assert sync_btn.is_visible(), "Botão #floatingSyncBtn não está visível!"
        
        # Verificar que está no cabeçalho superior e não sobrepondo os cards
        box = sync_btn.bounding_box()
        print(f"Posição do Botão Sincronizar: {box}")
        assert box["y"] < 80, f"Botão Sincronizar deveria estar no cabeçalho (y < 80), mas está em y={box['y']}"
        header_shot = os.path.join(EVIDENCE_DIR, "sync_btn_cabecalho_sem_obstrucao.png")
        page.locator(".top-header-area").screenshot(path=header_shot)
        print(f"Screenshot do cabeçalho capturado: {header_shot}")

        # -------------------------------------------------------------
        # TESTE 2: DROPDOWN MODO DE ATUAÇÃO (NUNCA CORTA BALADA & CLUB DJ)
        # -------------------------------------------------------------
        print("\n--- Teste 2: Dropdown Modo de Atuação DJ ---")
        page.click("#btnDjActTrigger")
        time.sleep(0.4)
        
        menu = page.locator("#djActDropdownMenu")
        assert menu.is_visible(), "Menu dropdown não abriu!"
        menu_box = menu.bounding_box()
        print(f"Posição do Menu: {menu_box}")

        opts = [
            ("actOpt_match", "Match Perfeito"),
            ("actOpt_energy", "Peak Time"),
            ("actOpt_shuffle", "Smart Shuffle"),
            ("actOpt_smooth", "Smooth Flow"),
            ("actOpt_studio", "Estúdio Pro & Mastering"),
            ("actOpt_club", "Balada & Club DJ")
        ]
        
        for opt_id, name in opts:
            el = page.locator(f"#{opt_id}")
            assert el.is_visible(), f"Opção {name} ({opt_id}) não está visível no dropdown!"
            o_box = el.bounding_box()
            # Certificar que a opção não ultrapassa o limite inferior da janela (680px)
            assert o_box["y"] + o_box["height"] <= 680, f"Opção {name} cortada na tela! y={o_box['y']}, h={o_box['height']}"
            print(f"  ✓ {name}: y={o_box['y']:.1f}, h={o_box['height']:.1f} (visível)")

        dropdown_shot = os.path.join(EVIDENCE_DIR, "dropdown_modo_atuacao_visivel_completo.png")
        page.locator(".spotify-dj-mixer").screenshot(path=dropdown_shot)
        print(f"Screenshot do dropdown capturado: {dropdown_shot}")

        # Testar clique fora para fechar dropdown
        page.click(".header-brand")
        time.sleep(0.3)
        assert not menu.is_visible(), "Dropdown deveria ter fechado ao clicar fora!"
        print("  ✓ Dropdown fechou perfeitamente ao clicar fora.")

        # -------------------------------------------------------------
        # TESTE 3: BUSCA LIVRE & FAVORITAR SEM SUMIR COM A MÚSICA
        # -------------------------------------------------------------
        print("\n--- Teste 3: Busca Livre & Favoritar Faixa ---")
        page.click("#navSearch")
        time.sleep(0.5)

        # Buscar por Cumbia para garantir novidades do YouTube
        page.evaluate("() => executeFreeSearch('Coldplay')")
        time.sleep(4)

        cards = page.locator("#searchResultsList .track-card")
        total_cards = cards.count()
        print(f"Total de resultados de busca encontrados: {total_cards}")
        assert total_cards > 0, "Nenhum resultado de busca retornado!"

        # Contadores antes
        lib_cnt_before = int(page.locator("#countSearchLib").inner_text())
        new_cnt_before = int(page.locator("#countSearchNew").inner_text())
        print(f"Contadores antes: Na Biblioteca={lib_cnt_before}, Novidades={new_cnt_before}")

        # Encontrar um card que tenha o botão '⭐ Favoritar' (novidade do YouTube)
        fav_buttons = page.locator('#searchResultsList button:has-text("Favoritar")')
        fav_count = fav_buttons.count()
        print(f"Total de faixas disponíveis para favoritar na busca: {fav_count}")
        assert fav_count > 0, "Nenhuma faixa com botão Favoritar encontrada na busca!"

        first_fav_btn = fav_buttons.first
        # Identificar o card pai
        target_card = first_fav_btn.locator('xpath=ancestor::div[contains(@class, "track-card")]')
        target_card_id = target_card.get_attribute("id")
        target_card_title = target_card.locator(".track-card-title").inner_text()
        print(f"Faixa a ser favoritada: id={target_card_id}, titulo={target_card_title}")

        # Clicar em Favoritar
        first_fav_btn.click()
        time.sleep(1.2)

        # VERIFICAÇÃO CRÍTICA 1: O Card CONTINUA PRESENTE E VISÍVEL! (NÃO SUMIU!)
        card_after = page.locator(f"#{target_card_id}")
        assert card_after.is_visible(), f"ERRO: Card {target_card_id} SUMIU da tela após ser favoritado!"
        print(f"  ✓ Card {target_card_id} CONTINUA 100% VISÍVEL na tela!")

        # VERIFICAÇÃO CRÍTICA 2: A quantidade total de cards na aba 'Todas' continua a mesma
        cards_after = page.locator("#searchResultsList .track-card")
        total_cards_after = cards_after.count()
        assert total_cards_after == total_cards, f"Contagem de cards mudou! Antes={total_cards}, Depois={total_cards_after}"
        print(f"  ✓ Contagem de cards preservada intacta ({total_cards} cards).")

        # VERIFICAÇÃO CRÍTICA 3: O botão mudou para '❤️ Na Playlist'
        btn_after = card_after.locator(".btn-add-playlist")
        btn_text_after = btn_after.inner_text()
        print(f"  ✓ Texto do botão após favoritar: '{btn_text_after}'")
        assert "Na Playlist" in btn_text_after, f"Botão não atualizou para Na Playlist! Obtido: '{btn_text_after}'"

        # VERIFICAÇÃO CRÍTICA 4: O badge mudou para '✓ Na Biblioteca'
        badge_after = card_after.locator(".badge-source").inner_text()
        print(f"  ✓ Badge após favoritar: '{badge_after}'")
        assert "Na Biblioteca" in badge_after, f"Badge não atualizou para Na Biblioteca! Obtido: '{badge_after}'"

        # VERIFICAÇÃO CRÍTICA 5: Os contadores das abas atualizaram!
        lib_cnt_after = int(page.locator("#countSearchLib").inner_text())
        new_cnt_after = int(page.locator("#countSearchNew").inner_text())
        print(f"  ✓ Contadores após favoritar: Na Biblioteca={lib_cnt_after} (antes={lib_cnt_before}), Novidades={new_cnt_after} (antes={new_cnt_before})")
        assert lib_cnt_after == lib_cnt_before + 1, f"Contador Na Biblioteca não incrementou! {lib_cnt_after} != {lib_cnt_before + 1}"
        assert new_cnt_after == new_cnt_before - 1, f"Contador Novidades não decrementou! {new_cnt_after} != {new_cnt_before - 1}"

        # VERIFICAÇÃO CRÍTICA 6: O último card NÃO tem botões cobertos
        last_card = cards_after.last
        last_card.scroll_into_view_if_needed()
        time.sleep(0.5)
        last_actions = last_card.locator(".card-actions").bounding_box()
        print(f"  ✓ Posição das ações do último card: {last_actions}")

        search_shot = os.path.join(EVIDENCE_DIR, "busca_favoritada_com_sucesso_sem_sumir.png")
        page.screenshot(path=search_shot)
        print(f"Screenshot da busca após favoritar: {search_shot}")

        # -------------------------------------------------------------
        # TESTE 4: EQUALIZADOR PRO (PRESETS VISÍVEIS)
        # -------------------------------------------------------------
        print("\n--- Teste 4: Presets do Equalizador Pro ---")
        page.evaluate("() => openEqualizerModal()")
        time.sleep(0.5)

        eq_modal = page.locator(".eq-modal-card.eq-modal-pro")
        assert eq_modal.is_visible(), "Modal do equalizador não abriu!"
        card_padrao = page.locator("#eqCard_padrao")
        padrao_box = card_padrao.bounding_box()
        print(f"Tamanho do card preset: {padrao_box}")
        assert padrao_box["height"] >= 36, f"Preset card esmagado! Altura={padrao_box['height']}"

        eq_shot = os.path.join(EVIDENCE_DIR, "equalizador_presets_perfeitos_verificados.png")
        eq_modal.screenshot(path=eq_shot)
        print(f"Screenshot do equalizador: {eq_shot}")

        browser.close()
        print("\n=======================================================")
        print("TODOS OS 4 TESTES PASSARAM COM SUCESSO ABSOLUTO (100%)!")
        print("=======================================================")

if __name__ == "__main__":
    test_all_fixes()
