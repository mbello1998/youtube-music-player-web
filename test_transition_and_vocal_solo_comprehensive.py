# -*- coding: utf-8 -*-
import os
import time
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def test_transition_and_vocal_solo():
    print("Iniciando testes: Transição Fluida e Isolamento Vocal Acapella Absoluto (Zero Bleed)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 768})

        url = "http://localhost:5050/?v=20261116_17"
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1.0)
        page.click("body")

        # -------------------------------------------------------------
        # TESTE 1: TRANSIÇÃO FLUIDA ENTRE MÚSICAS (SEM TRAVAMENTO)
        # -------------------------------------------------------------
        print("\n--- TESTE 1: Transição de Músicas (Crossfade Crossover) ---")
        
        # Testar cálculo do crossover DSP
        crossover_test = page.evaluate("""() => {
            initWebAudio();
            let errs = [];
            try {
                applyTransitionCrossover(0.0, 'A', 'B');
                const lowA0 = deckGainLowA.gain.value;
                const lowB0 = deckGainLowB.gain.value;

                applyTransitionCrossover(0.45, 'A', 'B');
                const lowA45 = deckGainLowA.gain.value;
                const lowB45 = deckGainLowB.gain.value;

                applyTransitionCrossover(1.0, 'A', 'B');
                const lowA100 = deckGainLowA.gain.value;
                const lowB100 = deckGainLowB.gain.value;

                return {
                    success: true,
                    lowA0, lowB0,
                    lowA45, lowB45,
                    lowA100, lowB100
                };
            } catch (e) {
                return { success: false, error: e.message };
            }
        }""")
        print("Resultado do cálculo do crossover DSP:", crossover_test)
        assert crossover_test["success"], f"Erro no crossover DSP: {crossover_test.get('error')}"
        assert crossover_test["lowA0"] > 0.9, "Deck A deveria ter baixo total no início"
        assert crossover_test["lowB0"] == 0.0, "Deck B deveria ter zero baixo no início"
        assert crossover_test["lowA100"] == 0.0, "Deck A deveria ter zero baixo no final"
        assert crossover_test["lowB100"] > 0.9, "Deck B deveria ter baixo total no final"

        # Simular transição completa via triggerCrossfade com crossfadeSeconds = 1.0s
        print("\nSimulando triggerCrossfade completa (1.0s)...")
        transition_res = page.evaluate("""() => {
            return new Promise((resolve) => {
                const track1 = { title: "2. Flash / Zé Vaqueiro", category: "Sertanejo & Piseiro", bpm: 129, video_id: "test_v1" };
                const track2 = { title: "4. Não Mexe nas Minhas Gavetas", category: "Sertanejo & Piseiro", bpm: 120, video_id: "test_v2" };
                
                window.nowPlayingTrack = track1;
                window.isTransitioning = false;
                window.crossfadeSeconds = 1.0;
                
                triggerCrossfade(track2);
                
                const stepCheck = {
                    initialIsTrans: window.isTransitioning,
                    crossfadeTimerActive: window.crossfadeTimer !== null
                };
                
                setTimeout(() => {
                    resolve({
                        initial: stepCheck,
                        finalIsTrans: window.isTransitioning,
                        finalTimer: window.crossfadeTimer,
                        nowPlayingTitle: window.nowPlayingTrack ? window.nowPlayingTrack.title : null
                    });
                }, 1600);
            });
        }""")
        print("Resultado da transição executada:", transition_res)
        assert transition_res["initial"]["initialIsTrans"], "Transição não foi iniciada!"
        assert not transition_res["finalIsTrans"], "Transição ficou travada (isTransitioning ainda true)!"
        assert transition_res["finalTimer"] is None, "crossfadeTimer não foi limpo!"
        assert transition_res["nowPlayingTitle"] == "4. Não Mexe nas Minhas Gavetas", "Faixa que entra não virou nowPlayingTrack!"

        # Capturar screenshot do player com a nova música ativa sem nenhum card travado
        trans_shot = os.path.join(ARTIFACTS_DIR, "transicao_completa_sem_travamento_verified.png")
        page.screenshot(path=trans_shot)
        print(f"Screenshot da transição bem-sucedida salvo em: {trans_shot}")

        # -------------------------------------------------------------
        # TESTE 2: ISOLAMENTO VOCAL ACAPELLA ABSOLUTO (ZERO BLEED)
        # -------------------------------------------------------------
        print("\n--- TESTE 2: Isolamento Vocal Acapella Absoluto ---")
        
        # Abre o modal de Stems
        page.click("#barStemsBtn")
        time.sleep(0.4)

        modal_visible = page.is_visible("#djStemsModal")
        print("Modal Stems visível:", modal_visible)
        assert modal_visible, "Modal de Stems (#djStemsModal) não abriu!"

        # Clica no pad "Apenas Vocal"
        print("Ativando preset 'Apenas Vocal' (#stemPad_vocal)...")
        page.click("#stemPad_vocal")
        time.sleep(0.3)

        vocal_state = page.evaluate("""() => {
            return {
                solo: stemsState.solo,
                preset: stemsState.activePreset,
                vocalVal: stemsState.vocal,
                drumsVal: stemsState.drums,
                bassVal: stemsState.bass,
                instVal: stemsState.inst,
                stemsDryGain: stemsDryGain ? stemsDryGain.gain.value : null,
                stemGain_vocal: stemGain_vocal ? stemGain_vocal.gain.value : null,
                stemGain_drums: stemGain_drums ? stemGain_drums.gain.value : null,
                stemGain_bass: stemGain_bass ? stemGain_bass.gain.value : null,
                stemGain_inst: stemGain_inst ? stemGain_inst.gain.value : null,
                vocalHpFreq: stemVocalHp1 ? stemVocalHp1.frequency.value : null,
                vocalLpFreq: stemVocalLp1 ? stemVocalLp1.frequency.value : null,
                vocalNotch1Freq: stemVocalNotch1 ? stemVocalNotch1.frequency.value : null,
                vocalNotch2Freq: stemVocalNotch2 ? stemVocalNotch2.frequency.value : null,
                vocalFormant1Freq: stemVocalFormant1 ? stemVocalFormant1.frequency.value : null,
                vocalFormant2Freq: stemVocalFormant2 ? stemVocalFormant2.frequency.value : null,
                hasCleanProcessor: stemVocalCleanProcessor !== null,
                badgeText: document.getElementById('stemsEngagedBadge').textContent.trim()
            };
        }""")
        print("Estado DSP do Vocal Solo:", vocal_state)
        assert vocal_state["solo"] == "vocal", "Solo não é vocal!"
        assert vocal_state["preset"] == "vocal", "Preset não é vocal!"
        assert vocal_state["stemsDryGain"] == 0.0, "stemsDryGain deveria ser ZERO absoluto!"
        assert vocal_state["stemGain_drums"] == 0.0, "stemGain_drums deveria ser ZERO absoluto!"
        assert vocal_state["stemGain_bass"] == 0.0, "stemGain_bass deveria ser ZERO absoluto!"
        assert vocal_state["stemGain_inst"] == 0.0, "stemGain_inst deveria ser ZERO absoluto!"
        assert vocal_state["stemGain_vocal"] > 1.0, f"stemGain_vocal deveria ser > 1.0, veio: {vocal_state['stemGain_vocal']}"
        assert vocal_state["vocalHpFreq"] >= 300, f"Highpass de vocal deveria ser >= 300Hz, veio: {vocal_state['vocalHpFreq']}"
        assert vocal_state["vocalLpFreq"] <= 3600, f"Lowpass de vocal deveria ser <= 3600Hz, veio: {vocal_state['vocalLpFreq']}"
        assert vocal_state["vocalNotch1Freq"] == 210, "Notch 1 de caixa deveria ser 210Hz"
        assert vocal_state["vocalNotch2Freq"] == 420, "Notch 2 de caixa deveria ser 420Hz"
        assert vocal_state["hasCleanProcessor"], "Processador de Centro e Rejeição Estéreo não foi inicializado!"
        assert "VOCAL SOLO" in vocal_state["badgeText"], f"Badge incorreto: {vocal_state['badgeText']}"

        # Capturar screenshot do modal de Stems com Vocal Solo ativado e 100% isolado
        vocal_shot = os.path.join(ARTIFACTS_DIR, "vocal_acapella_solo_absoluto_verified.png")
        page.locator("#djStemsModal .stems-modal-card").screenshot(path=vocal_shot)
        print(f"Screenshot do modal Stems com Vocal Solo capturado em: {vocal_shot}")

        # Testar calibração acústica dos perfis de ritmo em tempo real
        print("\nTestando alternância de perfis acústicos por ritmo:")
        for genre in ["funk", "sertanejo", "pagode", "eletronica", "trap", "latino", "rock"]:
            page.evaluate(f"setStemGenreProfile('{genre}')")
            freq = page.evaluate("() => stemVocalHp1.frequency.value")
            name = page.evaluate("() => GENRE_STEM_PROFILES[activeEffectiveProfileKey].name")
            print(f"  • Perfil {genre.upper()}: {name} (Vocal HP: {freq} Hz)")
            assert freq > 0, f"Frequência inválida para {genre}"

        # Voltar para auto
        page.evaluate("setStemGenreProfile('auto')")

        # Fechar o modal
        page.click("#djStemsModal .eq-close-btn")
        time.sleep(0.3)
        assert not page.is_visible("#djStemsModal"), "Modal de Stems não fechou!"

        browser.close()
        print("\n TODOS OS TESTES PASSARAM COM SUCESSO ABSOLUTO!")

if __name__ == "__main__":
    test_transition_and_vocal_solo()
