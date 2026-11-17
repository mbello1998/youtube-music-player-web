# -*- coding: utf-8 -*-
"""
test_predictive_wave_and_manual_window.py
Verifica:
1. Botões Manuais na HUD (➖ 10s / ➕ 10s) para aumentar e diminuir a Janela do Refrão livremente
2. Análise Preditiva de Onda (Calcula tendência da curva e antecipa a troca antes de despencar no silêncio)
3. Detecção de Silêncio e Fim de Música (Impede corte atrasado ou término da música no vazio)
4. Efeitos de Troca de Música correspondentes ao gênero musical (Cumbia Fiestera, Mega Funk, Eletrônica, etc.)
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
        # TESTE 1: Ativação do Modo Drop Hunter & Botões de Ajuste Manual
        # -------------------------------------------------------------
        print("\n--- Teste 1: Modo Drop Hunter & Botões de Ajuste Manual (➖ 10s / ➕ 10s) ---")
        page.click("#btnDjActTrigger")
        time.sleep(0.4)
        page.locator("#actOpt_drop").click()
        time.sleep(0.8)

        drop_hud = page.locator("#djDropHunterHud")
        assert drop_hud.is_visible(), "HUD Drop Hunter não está visível!"

        btn_minus = page.locator("#btnDropWinMinus")
        btn_plus = page.locator("#btnDropWinPlus")
        assert btn_minus.is_visible(), "Botão '➖ 10s' não está visível no HUD!"
        assert btn_plus.is_visible(), "Botão '➕ 10s' não está visível no HUD!"

        # Testa aumento manual (+10s)
        btn_plus.click()
        time.sleep(0.3)
        res_plus = page.evaluate("() => ({ base: dropWindowManualBase, target: dropTargetSeconds })")
        print(f"Janela após ➕ 10s: {res_plus}")
        assert res_plus["base"] == 85, f"Esperado 85s, obtido {res_plus['base']}s!"

        # Testa diminuição manual (-10s duas vezes)
        btn_minus.click()
        time.sleep(0.2)
        btn_minus.click()
        time.sleep(0.3)
        res_minus = page.evaluate("() => ({ base: dropWindowManualBase, target: dropTargetSeconds })")
        print(f"Janela após ➖ 20s: {res_minus}")
        assert res_minus["base"] == 65, f"Esperado 65s, obtido {res_minus['base']}s!"

        # Captura screenshot dos botões manuais integrados na barra da janela
        ss1 = ARTIFACTS_DIR / "janela_refrao_botoes_manuais_verified.png"
        drop_hud.screenshot(path=str(ss1))
        print(f"✓ Screenshot com botões manuais da janela capturado: {ss1.name}")

        # Retorna para 75s
        btn_plus.click()
        time.sleep(0.3)

        # -------------------------------------------------------------
        # TESTE 2: Efeitos Sonoros de Transição Relacionados ao Gênero
        # -------------------------------------------------------------
        print("\n--- Teste 2: Detecção de Efeitos DJ Sonoros por Gênero Musical ---")
        fx_cumbia = page.evaluate("""() => {
            const trackA = { title: "•ENGANCHADO CUMBIA FIESTERA REMIX•", category: "Cumbia Fiestera", bpm: 124 };
            const trackB = { title: "Nadie Me Vera Llorar - Sonido Profesional", category: "Cumbia Fiestera", bpm: 122 };
            return detectGenreFx(trackA, trackB);
        }""")
        print(f"Efeito detectado para Cumbia Fiestera: {fx_cumbia['name']} ({fx_cumbia['tag']})")
        assert "cumbia" in fx_cumbia["tag"].lower() or "latino" in fx_cumbia["tag"].lower() or "frontera" in fx_cumbia["tag"].lower(), "Gênero Cumbia não identificado!"

        fx_funk = page.evaluate("""() => {
            const trackA = { title: "Mega Funk Lost 2 - DJ Maninho", category: "Mega Funk", bpm: 149 };
            const trackB = { title: "Mega Mexicana - DJ Dédda", category: "Mega Funk", bpm: 144 };
            return detectGenreFx(trackA, trackB);
        }""")
        print(f"Efeito detectado para Mega Funk: {fx_funk['name']} ({fx_funk['tag']})")
        assert "funk" in fx_funk["tag"].lower(), "Gênero Funk não identificado!"

        # -------------------------------------------------------------
        # TESTE 3: Detecção de Silêncio e Prevenção de Fim de Música
        # -------------------------------------------------------------
        print("\n--- Teste 3: Prevenção de Silêncio e Término Vazio da Música ---")
        silence_res = page.evaluate("""() => {
            window._simulatedDropEnergy = 5; // Silêncio quase absoluto (< 12%)
            dropActiveSeconds = 35.0; // Já tocou 35s
            dropTargetSeconds = 75.0;

            let cutReason = null;
            const originalCut = window.smartCutToNextDrop;
            window.smartCutToNextDrop = (reason) => { cutReason = reason; };

            // Simula 9 frames de silêncio (0.9s contínuos)
            for (let i = 0; i < 9; i++) {
                updateDropHunterMetrics();
            }

            window.smartCutToNextDrop = originalCut;
            return { cutReason };
        }""")
        print(f"Disparo de corte em silêncio: {silence_res}")
        assert silence_res["cutReason"] == "silence_or_outro", "FALHA: Não disparou corte preventivo em silêncio!"
        print("✓ Prevenção de silêncio funcionando: corte imediato sem esperar o fim do timer!")

        # -------------------------------------------------------------
        # TESTE 4: Análise Preditiva de Queda da Onda
        # -------------------------------------------------------------
        print("\n--- Teste 4: Análise Preditiva da Onda (Antecipação de Queda) ---")
        predictive_res = page.evaluate("""() => {
            dropActiveSeconds = 50.0; // Já tocou a maior parte do refrão
            dropTargetSeconds = 75.0;
            dropEnergyHistory = [];

            let cutReason = null;
            const originalCut = window.smartCutToNextDrop;
            window.smartCutToNextDrop = (reason) => { cutReason = reason; };

            // Simula queda brusca da curva de energia da onda: 80% -> 70% -> 55% -> 45% -> 38%
            const fallingEnergies = [80, 78, 75, 70, 65, 55, 50, 46, 42, 38, 36, 35, 34, 33];
            for (const e of fallingEnergies) {
                window._simulatedDropEnergy = e;
                updateDropHunterMetrics();
            }

            window.smartCutToNextDrop = originalCut;
            return {
                cutReason,
                pillText: document.getElementById("dropStatusPill")?.innerText
            };
        }""")
        print(f"Disparo da análise preditiva: {predictive_res}")
        assert predictive_res["cutReason"] == "predictive_fall", "FALHA: Não disparou corte preditivo na queda da onda!"
        print("✓ Análise preditiva funcionando: antecipou a queda da onda e virou no clímax!")

        # Captura screenshot final
        ss2 = ARTIFACTS_DIR / "corte_preditivo_e_fx_genero_verified.png"
        drop_hud.screenshot(path=str(ss2))
        print(f"✓ Screenshot do corte preditivo e efeitos capturado: {ss2.name}")

        print("\n=======================================================")
        print("TODOS OS TESTES DE REFRÃO PREDITIVO E AJUSTES PASSARAM!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()
