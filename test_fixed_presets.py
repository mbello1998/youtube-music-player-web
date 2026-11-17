import os
import time
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def test_fixed_presets_layout():
    print("Testando layout corrigido dos Presets Acústicos no Equalizador...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Testar em resolução de notebook padrão (1366x768 com viewport útil de ~680px de altura)
        page = browser.new_page(viewport={"width": 1366, "height": 680})

        url = "http://localhost:5050/player.html"
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1)

        # Abrir modal do equalizador
        page.evaluate("() => openEqualizerModal()")
        time.sleep(0.5)

        # Inspecionar dimensões
        info = page.evaluate("""() => {
            const grid = document.querySelector('.eq-presets-grid-scroll');
            const card0 = document.getElementById('eqCard_padrao');
            const card1 = document.getElementById('eqCard_grave');
            const name0 = card0.querySelector('.eq-preset-name').textContent;
            const desc0 = card0.querySelector('.eq-preset-desc').textContent;
            return {
                gridHeight: grid.offsetHeight,
                gridScrollHeight: grid.scrollHeight,
                cardHeight: card0.offsetHeight,
                cardWidth: card0.offsetWidth,
                name: name0,
                desc: desc0,
                isPadraoVisible: card0.getBoundingClientRect().height > 25,
                isGraveVisible: card1.getBoundingClientRect().height > 25
            };
        }""")
        print("Dimensões dos Presets após correção:", info)
        assert info["cardHeight"] >= 36, f"Card continua muito baixo! {info['cardHeight']}"
        assert info["gridHeight"] >= 120, f"Grid continua colapsado! {info['gridHeight']}"
        assert info["isPadraoVisible"] and info["isGraveVisible"]

        # Capturar screenshot do container de presets
        presets_box = page.locator(".eq-presets-grid-scroll")
        presets_shot = os.path.join(EVIDENCE_DIR, "presets_acusticos_corrigidos_grid.png")
        presets_box.screenshot(path=presets_shot)
        print(f"Screenshot dos presets capturado: {presets_shot}")

        # Capturar screenshot do modal inteiro
        modal_card = page.locator(".eq-modal-card.eq-modal-pro")
        modal_shot = os.path.join(EVIDENCE_DIR, "equalizador_pro_presets_visiveis_verified.png")
        modal_card.screenshot(path=modal_shot)
        print(f"Screenshot do modal completo capturado: {modal_shot}")

        # Testar seleção de preset clicando no card
        page.click("#eqCard_funk")
        time.sleep(0.2)
        funk_active = page.evaluate("() => document.getElementById('eqCard_funk').classList.contains('active')")
        print("Preset Funk ativado com sucesso:", funk_active)
        assert funk_active

        browser.close()
        print("\nTESTE DO LAYOUT DOS PRESETS PASSOU COM SUCESSO!")

if __name__ == "__main__":
    test_fixed_presets_layout()
