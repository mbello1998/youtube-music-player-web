# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path(r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 950})
        page = context.new_page()

        logs = []
        errors = []
        page.on("console", lambda m: logs.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        print("1. Navegando para http://localhost:5050...")
        page.goto("http://localhost:5050", wait_until="networkidle")
        page.wait_for_timeout(1500)

        # =========================================================================
        # TESTE 1 (IMAGEM 2): BOTÃO FECHAR ESTILIZADO (.eq-close-btn)
        # =========================================================================
        print("\n=== TESTE 1: Botão Fechar Estilizado (.eq-close-btn) ===")
        page.locator("#barStudioBtn").click()
        page.wait_for_timeout(800)

        studio_modal = page.locator("#studioModal")
        assert studio_modal.is_visible(), "Modal Studio Pro não abriu!"

        close_btn = page.locator("#studioModal .eq-close-btn")
        assert close_btn.is_visible(), "Botão .eq-close-btn não visível no Studio Modal!"

        # Checa estilos computados do botão fechar (não pode ser branco nem borda grossa padrão de browser)
        btn_styles = page.evaluate("""() => {
            const btn = document.querySelector('#studioModal .eq-close-btn');
            const style = window.getComputedStyle(btn);
            return {
                backgroundColor: style.backgroundColor,
                color: style.color,
                borderRadius: style.borderRadius,
                width: style.width,
                height: style.height,
                display: style.display
            };
        }""")
        print(f"Estilos computados do botão fechar: {btn_styles}")
        assert "32px" in btn_styles["width"] or "34px" in btn_styles["width"], f"Largura incorreta: {btn_styles['width']}"
        assert btn_styles["borderRadius"] in ["8px", "50%"], f"Border-radius incorreto: {btn_styles['borderRadius']}"

        # Screenshot do Header com o Botão Fechar Estilizado
        ss1 = ARTIFACTS_DIR / "botao_fechar_estilizado_verified.png"
        page.locator(".studio-modal-header").screenshot(path=str(ss1))
        print(f"✓ Screenshot 1 capturado: {ss1.name}")

        # Clica para fechar o modal
        close_btn.click()
        page.wait_for_timeout(500)
        assert not studio_modal.is_visible(), "Modal não fechou ao clicar em .eq-close-btn!"
        print("✓ Botão fechar estúdio funcional e estilizado com sucesso!")

        # =========================================================================
        # TESTE 2 (IMAGEM 1): DROP HUNTER HUD ESPAÇOSO SEM SCROLLBARS
        # =========================================================================
        print("\n=== TESTE 2: Drop Hunter HUD Amplo e Sem Scrollbars ===")
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
                pill.innerHTML = '✨ DROP ATIVO! (PISTA FERVENTE)';
            }
        }""")
        page.wait_for_timeout(600)

        # Checa scroll do painel
        scroll_info = page.evaluate("""() => {
            const panel = document.querySelector('.dj-drop-glass-panel');
            const vc = document.getElementById('videoContainer');
            return {
                scrollHeight: panel.scrollHeight,
                clientHeight: panel.clientHeight,
                scrollWidth: panel.scrollWidth,
                clientWidth: panel.clientWidth,
                vcHeight: vc.clientHeight,
                hasDropHudClass: vc.classList.contains('has-drop-hud')
            };
        }""")
        print(f"Info de Scroll do Drop Hunter: {scroll_info}")
        assert scroll_info["scrollHeight"] <= scroll_info["clientHeight"] + 2, f"Scroll vertical indesejado detectado: {scroll_info}"
        assert scroll_info["scrollWidth"] <= scroll_info["clientWidth"] + 2, f"Scroll horizontal indesejado detectado: {scroll_info}"
        assert scroll_info["vcHeight"] >= 240, f"Altura do container ({scroll_info['vcHeight']}px) menor que 240px!"

        # Screenshot do Drop Hunter HUD Amplo e Perfeito
        ss2 = ARTIFACTS_DIR / "drop_hunter_hud_sem_scrollbars_verified.png"
        page.locator("#djDropHunterHud").screenshot(path=str(ss2))
        print(f"✓ Screenshot 2 capturado: {ss2.name}")

        # Fecha o HUD Drop Hunter
        page.evaluate("selectDjActMode('match');")
        page.wait_for_timeout(500)

        # =========================================================================
        # TESTE 3 (IMAGEM 3): TRANSIÇÕES SUAVES SEM TRAVAMENTO (SAINDO / ENTRANDO)
        # =========================================================================
        print("\n=== TESTE 3: Troca de Músicas e Transição Fluida ===")
        # Toca faixa 1
        page.evaluate("""() => {
            playLibraryTrack(browseCategory, 1);
        }""")
        page.wait_for_timeout(800)

        track1_title = page.evaluate("nowPlayingTrack ? nowPlayingTrack.title : null")
        print(f"Música 1 tocando: {track1_title}")

        # Dispara crossfade para faixa 3
        page.evaluate("""() => {
            playLibraryTrack(browseCategory, 3);
        }""")
        page.wait_for_timeout(500)

        mid_trans = page.evaluate("""() => {
            return {
                isTransitioning,
                outBadge: !!document.querySelector('.badge-outgoing-track'),
                inBadge: !!document.querySelector('.badge-incoming-track')
            };
        }""")
        print(f"Em transição: {mid_trans}")
        assert mid_trans["isTransitioning"] == True, "Transição deveria estar ativa!"

        # Aguarda crossfade finalizar (crossfade dura 6s)
        print("Aguardando finalização do crossfade (7.5s)...")
        page.wait_for_timeout(7500)

        final_trans = page.evaluate("""() => {
            return {
                isTransitioning,
                activeDeck,
                nowPlaying: nowPlayingTrack ? nowPlayingTrack.title : null,
                outBadgeCount: document.querySelectorAll('.badge-outgoing-track').length,
                inBadgeCount: document.querySelectorAll('.badge-incoming-track').length
            };
        }""")
        print(f"Após transição completa: {final_trans}")
        assert final_trans["isTransitioning"] == False, "Transição ainda está ativa após o tempo limite!"
        assert final_trans["nowPlaying"] != track1_title, f"Música não trocou! Ainda está em {track1_title}"
        assert final_trans["outBadgeCount"] == 0, f"Ainda restam badges de SAINDO no DOM: {final_trans['outBadgeCount']}"
        assert final_trans["inBadgeCount"] == 0, f"Ainda restam badges de ENTRANDO no DOM: {final_trans['inBadgeCount']}"

        # Screenshot da Lista com Transição Concluída e Limpa
        ss3 = ARTIFACTS_DIR / "transicao_concluida_e_limpa_verified.png"
        page.locator("#trackList").screenshot(path=str(ss3))
        print(f"✓ Screenshot 3 capturado: {ss3.name}")

        # =========================================================================
        # TESTE 4: STEMS PURO DSP (SEM SCRIPTPROCESSOR, ZERO DISTORÇÃO)
        # =========================================================================
        print("\n=== TESTE 4: DJ Stems Puro DSP Web Audio ===")
        page.evaluate("openStemsModal();")
        page.wait_for_timeout(800)

        stems_modal = page.locator("#djStemsModal")
        assert stems_modal.is_visible(), "Modal Stems DJ não abriu!"

        # Testa ausência de ScriptProcessorNode e presença de nós C++ nativos
        dsp_check = page.evaluate("""() => {
            return {
                initialized: window.stemsDspInitialized,
                hasVocalGain: !!window.stemGain_vocal,
                hasBassLp1: !!window.stemBassLp1,
                hasDrumsKick: !!window.stemDrumsKickBp,
                hasDryGain: !!window.stemsDryGain,
                scriptProcessorExists: !!window.stemVocalCleanProcessor
            };
        }""")
        print(f"Verificação do grafo Stems DSP: {dsp_check}")
        assert dsp_check["initialized"] == True, "Stems DSP não inicializado!"
        assert dsp_check["hasVocalGain"] == True, "stemGain_vocal não encontrado!"
        assert dsp_check["scriptProcessorExists"] == False, "ScriptProcessorNode ainda presente! Deve ser 100% C++ nativo!"

        # Testa isolamento Vocal Acapella Solo
        page.evaluate("applyStemPreset('vocal');")
        page.wait_for_timeout(400)

        vocal_gains = page.evaluate("""() => {
            return {
                dryGain: window.stemsDryGain ? window.stemsDryGain.gain.value : null,
                vocalGain: window.stemGain_vocal ? window.stemGain_vocal.gain.value : null,
                drumsGain: window.stemGain_drums ? window.stemGain_drums.gain.value : null,
                bassGain: window.stemGain_bass ? window.stemGain_bass.gain.value : null,
                instGain: window.stemGain_inst ? window.stemGain_inst.gain.value : null
            };
        }""")
        print(f"Gains no Preset Vocal (Acapella): {vocal_gains}")
        assert vocal_gains["dryGain"] == 0.0, "Dry bypass deveria ser 0 no solo vocal!"
        assert vocal_gains["vocalGain"] > 1.0, f"Vocal gain ({vocal_gains['vocalGain']}) deveria ser > 1.0!"
        assert vocal_gains["drumsGain"] == 0.0, "Drums deveriam ser 0 no solo vocal!"
        assert vocal_gains["bassGain"] == 0.0, "Bass deveria ser 0 no solo vocal!"
        assert vocal_gains["instGain"] == 0.0, "Inst deveria ser 0 no solo vocal!"

        # Screenshot do Modal Stems com Vocal Solo Ativo
        ss4 = ARTIFACTS_DIR / "stems_vocal_solo_puro_dsp_verified.png"
        page.locator("#djStemsModal .stems-modal-card").screenshot(path=str(ss4))
        print(f"✓ Screenshot 4 capturado: {ss4.name}")

        # Testa retorno ao Full Mix (Bypass bit-perfect)
        page.evaluate("applyStemPreset('full');")
        page.wait_for_timeout(300)

        full_gains = page.evaluate("""() => {
            return {
                dryGain: window.stemsDryGain ? window.stemsDryGain.gain.value : null,
                vocalGain: window.stemGain_vocal ? window.stemGain_vocal.gain.value : null
            };
        }""")
        print(f"Gains no Preset Full: {full_gains}")
        assert full_gains["dryGain"] >= 0.99, "Dry gain deveria ser 1.0 no modo Full!"
        assert full_gains["vocalGain"] == 0.0, "Vocal gain deveria ser 0.0 no modo Full!"

        # Fecha modal stems
        page.evaluate("closeStemsModal();")
        page.wait_for_timeout(300)

        print("\n=======================================================")
        print("TODOS OS 4 TESTES PASSARAM COM 100% DE SUCESSO!")
        print("=======================================================")

if __name__ == "__main__":
    run_tests()
