import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path(r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576")

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 1000})
        page = context.new_page()

        print("Navegando para http://localhost:5050...")
        page.goto("http://localhost:5050", wait_until="networkidle")
        page.wait_for_timeout(1500)

        # -------------------------------------------------------------
        # TESTE 1: Botão Fechar do Studio Pro com estilo profissional (.eq-close-btn)
        # -------------------------------------------------------------
        print("\n--- Teste 1: Botão Fechar da Console Studio Pro ---")
        page.locator("#barStudioBtn").click()
        page.wait_for_timeout(1000)

        studio_modal = page.locator("#studioModal")
        assert studio_modal.is_visible(), "Modal Studio Pro não abriu!"

        close_btn = page.locator("#studioModal .eq-close-btn")
        assert close_btn.is_visible(), "Botão .eq-close-btn não encontrado no header do Studio Modal!"
        svg_icon = close_btn.locator("svg")
        assert svg_icon.is_visible(), "Ícone SVG do botão fechar não encontrado!"

        box = close_btn.bounding_box()
        print(f"Bounding box do botão fechar: {box}")
        assert box["width"] >= 30 and box["height"] >= 30, f"Dimensões do botão fechar incorretas: {box}"

        # Screenshot do Header com o Botão Fechar Estilizado
        ss1 = ARTIFACTS_DIR / "botao_fechar_studio_estilizado_verified.png"
        page.locator(".studio-modal-header").screenshot(path=str(ss1))
        print(f"✓ Screenshot 1 capturado: {ss1.name}")

        # Fecha o modal clicando no novo botão estilizado
        close_btn.click()
        page.wait_for_timeout(500)
        assert not studio_modal.is_visible(), "Modal não fechou ao clicar no novo botão fechar!"
        print("✓ Modal fechou perfeitamente ao clicar no botão fechar estilizado!")

        # -------------------------------------------------------------
        # TESTE 2: Drop Hunter HUD Ampliado e Espaçoso Sem Scrollbars
        # -------------------------------------------------------------
        print("\n--- Teste 2: Drop Hunter HUD Espaçoso e Proporcional ---")
        # Ativa o modo Drop Hunter
        page.evaluate("""() => {
            selectDjActMode('drop');
            const hud = document.getElementById('djDropHunterHud');
            if (hud) {
                hud.style.display = 'flex';
                hud.classList.add('hud-visible');
            }
            const btnMix = document.getElementById('btnMixJump');
            if (btnMix) {
                btnMix.style.display = 'inline-flex';
            }
            const pill = document.getElementById('dropStatusPill');
            if (pill) {
                pill.className = 'drop-status-pill drop-active';
                pill.innerHTML = '💥 DROP ATIVO! (FERVENDO)';
            }
            const energyFill = document.getElementById('dropEnergyFill');
            if (energyFill) energyFill.style.width = '75%';
            const energyVal = document.getElementById('dropEnergyVal');
            if (energyVal) energyVal.textContent = '75% 🔥';
            const timerFill = document.getElementById('dropTimerFill');
            if (timerFill) timerFill.style.width = '35%';
            const timerVal = document.getElementById('dropTimerVal');
            if (timerVal) timerVal.textContent = '00:26 / 01:15s';
        }""")
        page.wait_for_timeout(800)

        # Verifica dimensões do videoContainer
        vc_box = page.locator("#videoContainer").bounding_box()
        print(f"Dimensões do videoContainer: {vc_box}")
        assert vc_box["height"] >= 210, f"Altura do videoContainer ({vc_box['height']}px) menor que 210px!"

        # Verifica se há scroll no painel de vidro
        scroll_info = page.evaluate("""() => {
            const panel = document.querySelector('.dj-drop-glass-panel');
            return {
                scrollHeight: panel.scrollHeight,
                clientHeight: panel.clientHeight,
                scrollWidth: panel.scrollWidth,
                clientWidth: panel.clientWidth
            };
        }""")
        print(f"Info de Scroll do Drop Glass Panel: {scroll_info}")
        assert scroll_info["scrollHeight"] <= scroll_info["clientHeight"] + 2, f"Scroll vertical indesejado detectado: {scroll_info}"
        assert scroll_info["scrollWidth"] <= scroll_info["clientWidth"] + 2, f"Scroll horizontal indesejado detectado: {scroll_info}"

        # Verifica visibilidade de todos os componentes internos
        assert page.locator("#btnSkipToDrop").is_visible(), "Botão 'Pular pro Drop' não visível!"
        assert page.locator("#btnCutToNextDrop").is_visible(), "Botão 'Cortar no Drop' não visível!"
        assert page.locator("#btnAutoDropToggle").is_visible(), "Botão 'Auto: ON' não visível!"
        assert page.locator("#btnMixJump").is_visible(), "Botão 'Próximo Refrão do Mix' não visível!"
        assert page.locator("#dropEnergyVal").is_visible(), "Medidor de energia não visível!"
        assert page.locator("#dropTimerVal").is_visible(), "Medidor de timer do refrão não visível!"
        assert page.locator("#dropHudFooterText").is_visible(), "Dica de rodapé do HUD não visível!"

        # Screenshot do HUD Drop Hunter Ampliado e Perfeito
        ss2 = ARTIFACTS_DIR / "hud_drop_hunter_espacoso_sem_scroll_verified.png"
        page.locator("#videoFrameWrap").screenshot(path=str(ss2))
        print(f"✓ Screenshot 2 capturado: {ss2.name}")

        print("\n=======================================================")
        print("AMBAS AS CORREÇÕES VALIDADAS COM 100% DE SUCESSO!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_verification()
