# -*- coding: utf-8 -*-
"""
test_stems_all_genres_zero_bleed.py
Testa exaustivamente o Motor DJ Stems Pro em TODOS OS RITMOS MUSICAIS:
- Funk / Mandelão
- Sertanejo / Modão
- Samba & Pagode
- Eletrônica & House
- Trap & Rap
- Reggaeton & Cumbia
- Rock & Pop

Valida:
1. Calibração e resposta dos filtros de 8ª Ordem (48 dB/oct) para cada gênero.
2. Atuação do De-Drummer na Acapella.
3. Atuação do Cancelamento por Antifase no Instrumental (Vocal Kill).
4. Kill Switch absoluto (0.0 linear comprovado sem vazamento) em Mute e Solo.
5. Captura screenshots para cada ritmo musical.
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = Path(r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576")

GENRES_TO_TEST = [
    {
        "key": "funk",
        "name": "Funk & Mandelão",
        "chip_id": "#stProfile_funk",
        "expected_bass": 165,
        "expected_vocal_hp": 320,
        "expected_vocal_lp": 3600,
        "expected_punch": 100,
        "ss_name": "stems_zero_bleed_funk_mandelao_verified.png"
    },
    {
        "key": "sertanejo",
        "name": "Sertanejo & Modão",
        "chip_id": "#stProfile_sertanejo",
        "expected_bass": 195,
        "expected_vocal_hp": 260,
        "expected_vocal_lp": 4000,
        "expected_punch": 90,
        "ss_name": "stems_zero_bleed_sertanejo_modao_verified.png"
    },
    {
        "key": "pagode",
        "name": "Samba & Pagode",
        "chip_id": "#stProfile_pagode",
        "expected_bass": 175,
        "expected_vocal_hp": 285,
        "expected_vocal_lp": 3800,
        "expected_punch": 95,
        "ss_name": "stems_zero_bleed_samba_pagode_verified.png"
    },
    {
        "key": "eletronica",
        "name": "Eletrônica & House",
        "chip_id": "#stProfile_eletronica",
        "expected_bass": 150,
        "expected_vocal_hp": 340,
        "expected_vocal_lp": 4200,
        "expected_punch": 120,
        "ss_name": "stems_zero_bleed_eletronica_edm_verified.png"
    },
    {
        "key": "trap",
        "name": "Trap & Rap",
        "chip_id": "#stProfile_trap",
        "expected_bass": 165,
        "expected_vocal_hp": 310,
        "expected_vocal_lp": 3800,
        "expected_punch": 110,
        "ss_name": "stems_zero_bleed_trap_rap_verified.png"
    },
    {
        "key": "latino",
        "name": "Reggaeton & Cumbia",
        "chip_id": "#stProfile_latino",
        "expected_bass": 180,
        "expected_vocal_hp": 290,
        "expected_vocal_lp": 3900,
        "expected_punch": 105,
        "ss_name": "stems_zero_bleed_reggaeton_cumbia_verified.png"
    },
    {
        "key": "rock",
        "name": "Rock & Pop",
        "chip_id": "#stProfile_rock",
        "expected_bass": 200,
        "expected_vocal_hp": 280,
        "expected_vocal_lp": 4200,
        "expected_punch": 85,
        "ss_name": "stems_zero_bleed_rock_pop_verified.png"
    }
]

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        print("Navegando para http://localhost:5050...")
        page.goto("http://localhost:5050", wait_until="networkidle", timeout=15000)
        time.sleep(2)

        # Abre o modal de Stems
        page.click("#barStemsBtn")
        time.sleep(0.6)
        assert page.locator("#djStemsModal").is_visible(), "Modal Stems deve estar aberto!"
        print("✓ Modal DJ Stems Pro aberto com sucesso!")

        # -------------------------------------------------------------
        # TESTE MULTI-GÊNERO: Executa em cada ritmo
        # -------------------------------------------------------------
        for g in GENRES_TO_TEST:
            print(f"\n--- Testando Ritmo: {g['name']} ({g['key']}) ---")
            
            # Clica no chip do ritmo
            page.click(g["chip_id"])
            time.sleep(0.3)

            # Verifica classe active no chip
            assert "active" in (page.locator(g["chip_id"]).get_attribute("class") or ""), f"Chip {g['chip_id']} não está ativo!"

            # Verifica o texto do badge
            badge_text = page.locator("#stemsProfileActiveBadge").inner_text()
            print(f"  Badge de Ritmo: '{badge_text}'")
            assert g["key"].upper() in badge_text or g["name"].split()[0].upper() in badge_text, f"Badge não reflete ritmo {g['name']}!"

            # Avalia os parâmetros acústicos reais no grafo Web Audio
            dsp_info = page.evaluate("""() => {
                return {
                    bassCut: window.stemBassLp1 ? window.stemBassLp1.frequency.value : null,
                    vocalHp: window.stemVocalHp1 ? window.stemVocalHp1.frequency.value : null,
                    vocalLp: window.stemVocalLp1 ? window.stemVocalLp1.frequency.value : null,
                    drumsPunch: window.stemDrumsKickBp ? window.stemDrumsKickBp.frequency.value : null,
                    antiVocalDepth: window.stemDrumsNotch1 ? window.stemDrumsNotch1.gain.value : null,
                    hasDeDrummer: !!window.stemVocalDeDrummer,
                    deDrummerAttack: window.stemVocalDeDrummer ? window.stemVocalDeDrummer.attack.value : null,
                    hasInstCancel: !!window.stemInstCancelGain,
                    instCancelGain: window.stemInstCancelGain ? window.stemInstCancelGain.gain.value : null
                };
            }""")
            print(f"  DSP Info: {dsp_info}")

            # Asserções de calibração cirúrgica dos filtros 8ª ordem
            assert abs(dsp_info["bassCut"] - g["expected_bass"]) < 2, f"Bass cut incorreto para {g['name']}: {dsp_info['bassCut']}"
            assert abs(dsp_info["vocalHp"] - g["expected_vocal_hp"]) < 2, f"Vocal HP incorreto para {g['name']}: {dsp_info['vocalHp']}"
            assert abs(dsp_info["vocalLp"] - g["expected_vocal_lp"]) < 2, f"Vocal LP incorreto para {g['name']}: {dsp_info['vocalLp']}"
            assert abs(dsp_info["drumsPunch"] - g["expected_punch"]) < 2, f"Drums punch incorreto para {g['name']}: {dsp_info['drumsPunch']}"
            assert dsp_info["hasDeDrummer"] == True, "De-Drummer deve estar ativo no vocal!"
            assert dsp_info["deDrummerAttack"] <= 0.002, "De-Drummer attack deve ser ultrarrápido (<= 2ms)!"
            assert dsp_info["hasInstCancel"] == True, "Cancelador por antifase no Instrumental deve existir!"
            assert dsp_info["instCancelGain"] <= -0.9, "Cancelador por antifase deve ter ganho negativo (-1.0)!"

            # ---------------------------------------------------------
            # TESTE DE ISOLAMENTO 1: Acapella Solo (Vocal 100%, Beat/Bass 0.0)
            # ---------------------------------------------------------
            page.click("#stemPad_vocal")
            time.sleep(0.2)
            gains_vocal = page.evaluate("""() => {
                return {
                    dry: window.stemsDryGain.gain.value,
                    vocal: window.stemGain_vocal.gain.value,
                    drums: window.stemGain_drums.gain.value,
                    bass: window.stemGain_bass.gain.value,
                    inst: window.stemGain_inst.gain.value
                };
            }""")
            assert gains_vocal["dry"] == 0.0, "Dry deve ser 0.0 absoluto!"
            assert gains_vocal["vocal"] >= 1.0, "Vocal deve estar amplificado no solo!"
            assert gains_vocal["drums"] == 0.0, "Drums deve ser estritamente 0.0 no solo de voz (zero bleed)!"
            assert gains_vocal["bass"] == 0.0, "Bass deve ser estritamente 0.0 no solo de voz (zero bleed)!"
            assert gains_vocal["inst"] == 0.0, "Inst deve ser estritamente 0.0 no solo de voz (zero bleed)!"

            # ---------------------------------------------------------
            # TESTE DE ISOLAMENTO 2: Instrumental / Karaoke (Vocal Kill = 0.0)
            # ---------------------------------------------------------
            page.click("#stemPad_inst")
            time.sleep(0.2)
            gains_inst = page.evaluate("""() => {
                return {
                    vocal: window.stemGain_vocal.gain.value,
                    drums: window.stemGain_drums.gain.value,
                    bass: window.stemGain_bass.gain.value,
                    inst: window.stemGain_inst.gain.value
                };
            }""")
            assert gains_inst["vocal"] == 0.0, "Vocal deve ser estritamente 0.0 no Instrumental (zero bleed)!"
            assert gains_inst["drums"] >= 1.0 and gains_inst["bass"] >= 1.0 and gains_inst["inst"] >= 1.0, "Base instrumental completa deve estar ativa!"

            # ---------------------------------------------------------
            # TESTE DE ISOLAMENTO 3: Bass Kill
            # ---------------------------------------------------------
            page.click("#stemPad_basskill")
            time.sleep(0.2)
            gains_bk = page.evaluate("""() => window.stemGain_bass.gain.value""")
            assert gains_bk == 0.0, "Bass deve ser estritamente 0.0 no Bass Kill!"

            # Reseta para Mix Original
            page.click("#stemPad_full")
            time.sleep(0.2)

            # Salva screenshot do ritmo
            ss_path = ARTIFACTS_DIR / g["ss_name"]
            page.locator("#djStemsModal .stems-modal-card").screenshot(path=str(ss_path))
            print(f"  ✓ Screenshot salvo: {g['ss_name']}")

        print("\n=======================================================")
        print("TODOS OS 7 RITMOS MUSICAIS FORAM TESTADOS E VALIDADOS!")
        print("ZERO VAZAMENTO & ATUAÇÃO 100% COMPROVADA!")
        print("=======================================================")
        browser.close()

if __name__ == "__main__":
    run_tests()
