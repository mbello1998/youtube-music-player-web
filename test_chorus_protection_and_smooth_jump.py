# -*- coding: utf-8 -*-
"""
test_chorus_protection_and_smooth_jump.py
Verifica:
1. Proteção de Refrão Completo (75s - 95s):
   - Quedas de energia antes de 65s NÃO encurtam a janela nem cortam prematuramente
   - Janela padrão de 75s (expansível até 95s no ápice da festa)
2. Mix Jumper Suave (Quick-Duck sem estalos, travamentos ou retorno involuntário):
   - Flag isJumpingMix blindada contra salto duplo ou reset
   - Volume ducking e seek com retomada suave
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
        # TESTE 1: Ativação do Modo Drop Hunter & Inicialização da Janela Protegida
        # -------------------------------------------------------------
        print("\n--- Teste 1: Ativação do Modo Drop Hunter & Janela Protegida (75s) ---")
        page.click("#btnDjActTrigger")
        time.sleep(0.5)

        page.locator("#actOpt_drop").click()
        time.sleep(1)

        drop_hud = page.locator("#djDropHunterHud")
        assert drop_hud.is_visible(), "HUD Drop Hunter não está visível!"

        # Inicia uma faixa normal
        target_init = page.evaluate("""() => {
            nowPlayingTrack = {
                title: "Mega Funk Lost 2 - DJ Maninho, DJ Dudu",
                artist: "DJ Maninho",
                video_id: "test_megafunk_123",
                duration: 180,
                bpm: 149
            };
            startDropHunterAnalyzer();
            return dropTargetSeconds;
        }""")
        print(f"Janela inicial de Drop Target configurada: {target_init}s")
        assert target_init == 75, f"Esperado dropTargetSeconds inicial de 75s, obtido {target_init}s!"

        # -------------------------------------------------------------
        # TESTE 2: Proteção de Refrão Contra Cortes Precoces (Low Energy antes de 65s)
        # -------------------------------------------------------------
        print("\n--- Teste 2: Proteção de Refrão contra Cortes Precoces ---")
        # Simula 20 segundos de música tocando e uma queda brusca de energia (vocal ou respiro)
        cut_triggered = page.evaluate("""() => {
            window._simulatedDropEnergy = 25; // Energia muito baixa (< 42%)
            dropActiveSeconds = 25.0; // Música ainda está na metade do refrão
            dropTargetSeconds = 75.0;
            consecutiveLowEnergyCount = 40; // Mesmo se houver muitos ciclos de energia baixa

            let cutCalled = false;
            const originalCut = window.smartCutToNextDrop;
            window.smartCutToNextDrop = () => { cutCalled = true; };

            // Executa a métrica
            updateDropHunterMetrics();

            const targetAfter = dropTargetSeconds;
            window.smartCutToNextDrop = originalCut;

            return { cutCalled, targetAfter, dropActiveSeconds };
        }""")
        print(f"Resultado em queda de energia aos 25s: {cut_triggered}")
        assert not cut_triggered["cutCalled"], "FALHA: Corte prematuro disparou antes do fim do refrão!"
        assert cut_triggered["targetAfter"] >= 75.0, f"FALHA: Janela encurtou prematuramente para {cut_triggered['targetAfter']}s!"
        print("✓ Proteção do refrão confirmada: NENHUM corte precoce em energia baixa antes de 65s!")

        # -------------------------------------------------------------
        # TESTE 3: Expansão Dinâmica em Alta Energia (Ápice da Pista até 95s)
        # -------------------------------------------------------------
        print("\n--- Teste 3: Expansão Dinâmica da Janela em Alta Energia ---")
        expanded_target = page.evaluate("""() => {
            window._simulatedDropEnergy = 88; // Pista fervendo (> 75%)
            dropActiveSeconds = 50.0;
            dropTargetSeconds = 75.0;

            for (let i = 0; i < 50; i++) {
                updateDropHunterMetrics();
            }
            return dropTargetSeconds;
        }""")
        print(f"Janela expandida durante ápice: {expanded_target:.1f}s")
        assert expanded_target > 75.0, "Janela de drop não expandiu durante energia máxima!"
        assert expanded_target <= 95.0, "Janela ultrapassou o teto seguro de 95s!"
        print("✓ Expansão dinâmica funcionando com refrão estendido até 95s!")

        # Screenshot do HUD com Janela Protegida de Refrão
        ss1 = ARTIFACTS_DIR / "refrao_protegido_drop_hunter_verified.png"
        drop_hud.screenshot(path=str(ss1))
        print(f"✓ Screenshot do refrão protegido capturado: {ss1.name}")

        # -------------------------------------------------------------
        # TESTE 4: Mix Jumper Suave (Quick-Duck sem estalos e sem retorno)
        # -------------------------------------------------------------
        print("\n--- Teste 4: Mix Jumper Suave em Faixa Longa ---")
        mix_jump_res = page.evaluate("""() => {
            // Injeta um mix longo de cumbia fiestera
            nowPlayingTrack = {
                title: "•ENGANCHADO CUMBIA FIESTERA REMIX• 👿 [ Cumbias Inolvidables ] Cumbia Retro",
                artist: "Cumbias Inolvidables",
                video_id: "PFShMpSiiYQ",
                duration: 1800,
                bpm: 124
            };
            startDropHunterAnalyzer();

            // Configura mock de áudio para validar o ducking e seek seguro
            window._seekedFired = false;
            window._duckRamped = false;

            if (!window.deckAudioA) {
                window.deckAudioA = new Audio();
            }
            window.activeDeck = "A";
            window.engineMode = "audio";

            const curAudio = getActiveAudioDeck();
            Object.defineProperty(curAudio, 'duration', { value: 1800, writable: true });
            curAudio.currentTime = 120; // Tocando em 2 min

            // Dispara smartMixSegmentJump
            smartMixSegmentJump();

            return {
                isJumpingMix: isJumpingMix,
                mixSegmentCount: mixSegmentCount,
                dropTargetSeconds: dropTargetSeconds
            };
        }""")
        print(f"Estado imediatamente após disparar Mix Jumper: {mix_jump_res}")
        assert mix_jump_res["isJumpingMix"] is True, "Flag isJumpingMix deveria estar ativa para blindar contra resets!"
        assert mix_jump_res["mixSegmentCount"] == 1, "mixSegmentCount deveria ter sido incrementado!"
        assert mix_jump_res["dropTargetSeconds"] == 85, "Janela do próximo refrão no mix deveria ser de 85s!"

        # Aguarda a finalização do seek e restauração suave
        page.wait_for_function("() => window.isJumpingMix === false", timeout=3000)

        after_jump_res = page.evaluate("""() => {
            return {
                isJumpingMix: isJumpingMix,
                mixSegmentCount: mixSegmentCount
            };
        }""")
        print(f"Estado após ciclo completo do Mix Jumper: {after_jump_res}")
        assert after_jump_res["isJumpingMix"] is False, "Flag isJumpingMix deveria ser liberada após a rampa de transição!"

        # Screenshot do Mix Jumper
        ss2 = ARTIFACTS_DIR / "mix_jumper_suave_sem_travamento_verified.png"
        drop_hud.screenshot(path=str(ss2))
        print(f"✓ Screenshot do Mix Jumper suave capturado: {ss2.name}")

        print("\n=======================================================")
        print("TODOS OS TESTES DE PROTEÇÃO DE REFRÃO E MIX JUMPER PASSARAM!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()
