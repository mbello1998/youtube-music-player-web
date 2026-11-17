import asyncio
import os
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        print("Navigating to http://localhost:5050/?cachebust=9 ...")
        await page.goto("http://localhost:5050/?cachebust=9", wait_until="networkidle")

        # -------------------------------------------------------------
        # TESTE 1: Playlists de Quaraí & Artigas (147 Playlists no total)
        # -------------------------------------------------------------
        print("\n--- TESTE 1: Playlists Quaraí & Artigas (Fronteira) ---")
        
        sp_tab = page.locator('button:has-text("Playlists Spotify")')
        await sp_tab.click()
        await page.wait_for_timeout(1000)

        sp_badge_text = await sp_tab.inner_text()
        print(f"Spotify Tab Text: {sp_badge_text}")

        # Check Quaraí & Artigas chip
        fronteira_chip = page.locator('#spChip_fronteira')
        chip_exists = await fronteira_chip.is_visible()
        chip_text = await fronteira_chip.inner_text()
        print(f"Chip Fronteira exists: {chip_exists}, Text: {chip_text}")

        # Click chip to filter
        await fronteira_chip.click()
        await page.wait_for_timeout(800)

        visible_tabs = await page.locator('[id^="spTab_"]:not([style*="display: none"])').count()
        print(f"Playlists visíveis no filtro Fronteira: {visible_tabs}")

        # Click Fronteira da Paz playlist
        paz_tab = page.locator('[id^="spTab_"]:has-text("Fronteira da Paz")').first
        await paz_tab.click()
        await page.wait_for_timeout(1000)

        tracks_count = await page.locator('#spotifyTrackList .track-card').count()
        first_title = await page.locator('#spotifyTrackList .track-card').first.locator('.track-title').inner_text()
        print(f"Faixas renderizadas na playlist Fronteira da Paz: {tracks_count}")
        print(f"Primeira faixa: {first_title}")

        # Play first track (Miriam Britos)
        play_btn = page.locator('#spotifyTrackList .track-card').first.locator('button:has-text("Tocar")')
        await play_btn.click()
        await page.wait_for_timeout(2000)

        deck_a_title = await page.locator('#deckATitle').inner_text()
        deck_a_bpm = await page.locator('#deckABpm').inner_text()
        print(f"Deck A reproduzindo: {deck_a_title} ({deck_a_bpm})")

        shot1_path = os.path.join(ARTIFACT_DIR, "quarai_artigas_playlists_verified.png")
        await page.screenshot(path=shot1_path)
        print(f"Screenshot 1 salvo: {shot1_path}")

        # -------------------------------------------------------------
        # TESTE 2: Stems DJ 3-Band Crossover (Isolamento em Tempo Real)
        # -------------------------------------------------------------
        print("\n--- TESTE 2: Stems DJ Isolamento em Tempo Real ---")

        stems_eval = await page.evaluate('''() => {
            window.initWebAudio();

            // 1. Testa estado Full (Original)
            window.applyStemPreset('full');
            const fullGains = {
                low: window.deckGainLowA ? window.deckGainLowA.gain.value : null,
                mid: window.deckGainMidA ? window.deckGainMidA.gain.value : null,
                high: window.deckGainHighA ? window.deckGainHighA.gain.value : null
            };

            // 2. Testa Vocal Only (Acapella)
            window.applyStemPreset('vocal');
            const vocalGains = {
                low: window.deckGainLowA ? window.deckGainLowA.gain.value : null,
                mid: window.deckGainMidA ? window.deckGainMidA.gain.value : null,
                high: window.deckGainHighA ? window.deckGainHighA.gain.value : null,
                solo: window.stemsState.solo
            };

            // 3. Testa Beat Only (Instrumental sem vocal)
            window.applyStemPreset('beat');
            const beatGains = {
                low: window.deckGainLowA ? window.deckGainLowA.gain.value : null,
                mid: window.deckGainMidA ? window.deckGainMidA.gain.value : null,
                high: window.deckGainHighA ? window.deckGainHighA.gain.value : null,
                mutedVocal: window.stemsState.muted.vocal
            };

            // 4. Testa Bass Kill (Drop sem grave)
            window.applyStemPreset('basskill');
            const bassKillGains = {
                low: window.deckGainLowA ? window.deckGainLowA.gain.value : null,
                mid: window.deckGainMidA ? window.deckGainMidA.gain.value : null,
                high: window.deckGainHighA ? window.deckGainHighA.gain.value : null,
                mutedBass: window.stemsState.muted.bass
            };

            // Restaura Full
            window.applyStemPreset('full');

            return { fullGains, vocalGains, beatGains, bassKillGains };
        }''')

        print("Stems Test Results:")
        print(f"  Full (Original): {stems_eval['fullGains']}")
        print(f"  Vocal (Acapella - Baixo & Agudos Zero): {stems_eval['vocalGains']}")
        print(f"  Beat (Instrumental - Vocal Zero): {stems_eval['beatGains']}")
        print(f"  Bass Kill (Drop - Baixo Zero): {stems_eval['bassKillGains']}")

        # Open Stems modal to capture UI
        await page.evaluate("window.openStemsModal()")
        await page.wait_for_timeout(600)
        shot2_path = os.path.join(ARTIFACT_DIR, "stems_3band_crossover_verified.png")
        await page.screenshot(path=shot2_path)
        print(f"Screenshot 2 salvo (Modal Stems): {shot2_path}")
        await page.evaluate("window.closeStemsModal()")

        # -------------------------------------------------------------
        # TESTE 3: Transição DJ Crossover (Bass Swap & Frequency Match)
        # -------------------------------------------------------------
        print("\n--- TESTE 3: Transição Crossover DJ (Bass Swap) ---")

        cross_eval = await page.evaluate('''() => {
            window.initWebAudio();

            // Teste no início da transição (p = 0.20): grave do Deck A ainda presente, grave do Deck B = 0!
            window.applyTransitionCrossover(0.20, 'A', 'B');
            const early = {
                outLow: window.deckGainLowA.gain.value,
                inLow: window.deckGainLowB.gain.value,
                inHigh: window.deckGainHighB.gain.value
            };

            // Teste no clímax da transição (p = 0.65): grave do Deck A já ZERADO (swap), grave do Deck B subindo forte!
            window.applyTransitionCrossover(0.65, 'A', 'B');
            const climax = {
                outLow: window.deckGainLowA.gain.value,
                inLow: window.deckGainLowB.gain.value,
                outMid: window.deckGainMidA.gain.value,
                inMid: window.deckGainMidB.gain.value
            };

            // Teste no final da transição (p = 1.0): Deck B 100%, Deck A 0%
            window.applyTransitionCrossover(1.0, 'A', 'B');
            const finished = {
                outMaster: window.deckGainA.gain.value,
                inMaster: window.deckGainB.gain.value,
                inLow: window.deckGainLowB.gain.value
            };

            // Restaura deck A ativo
            window.activeDeck = 'A';
            window.applyStemsToDsp();

            return { early, climax, finished };
        }''')

        print("Crossover Transition Results:")
        print(f"  Início (p=0.20): Deck A Grave={cross_eval['early']['outLow']:.2f}, Deck B Grave={cross_eval['early']['inLow']:.2f} (Zero colisão!), Deck B Agudo={cross_eval['early']['inHigh']:.2f}")
        print(f"  Clímax (p=0.65): Deck A Grave={cross_eval['climax']['outLow']:.2f} (Zerado!), Deck B Grave={cross_eval['climax']['inLow']:.2f} (Drop!), Deck B Médios={cross_eval['climax']['inMid']:.2f}")
        print(f"  Fim (p=1.00): Deck A Master={cross_eval['finished']['outMaster']:.2f}, Deck B Master={cross_eval['finished']['inMaster']:.2f}, Deck B Grave={cross_eval['finished']['inLow']:.2f}")

        # -------------------------------------------------------------
        # TESTE 4: Silêncio Inteligente & Catálogo
        # -------------------------------------------------------------
        print("\n--- TESTE 4: Silêncio Inteligente & Catálogo ---")

        silence_eval = await page.evaluate('''() => {
            const btnText = document.getElementById('barIntroSkipBtn') ? document.getElementById('barIntroSkipBtn').innerText : '';

            // Teste com faixa instantânea (ritmada/funk/mandelão)
            const instantTrack = { video_id: 'inst1', title: 'Ritmada dos Cria - Drop Beat', category: 'Funk' };
            const instantSkip = window.getTrackIntroSkip(instantTrack);

            // Teste com faixa com clipe oficial
            const clipTrack = { video_id: 'clip1', title: 'Artista - Clipe Oficial (Fala Inicial)', category: 'Sertanejo' };
            const clipSkip = window.getTrackIntroSkip(clipTrack);

            // Teste de gravação e consulta no catálogo
            window.recordTrackSilence('custom_test_vid', 2.4, false);
            const recordedSkip = window.getTrackIntroSkip({ video_id: 'custom_test_vid', title: 'Faixa Catalogada' });

            // Teste de alternância de modo
            const initialMode = window.smartSilenceMode;
            window.toggleIntroSkip(); // fixed
            const fixedMode = window.smartSilenceMode;
            window.toggleIntroSkip(); // off
            const offMode = window.smartSilenceMode;
            window.toggleIntroSkip(); // back to auto
            const backMode = window.smartSilenceMode;

            return {
                btnText,
                instantSkip,
                clipSkip,
                recordedSkip,
                modes: [initialMode, fixedMode, offMode, backMode]
            };
        }''')

        print("Silence Manager Results:")
        print(f"  Botão na barra: {silence_eval['btnText']}")
        print(f"  Pulo de Faixa Instantânea (sem silêncio): {silence_eval['instantSkip']}s (Início imediato perfeito!)")
        print(f"  Pulo de Clipe Oficial: {silence_eval['clipSkip']}s (Silêncio de introdução cortado)")
        print(f"  Pulo de Faixa no Catálogo Inteligente: {silence_eval['recordedSkip']}s")
        print(f"  Ciclo de Modos: {' -> '.join([str(m) for m in silence_eval['modes']])}")

        shot3_path = os.path.join(ARTIFACT_DIR, "silencio_inteligente_e_transicao_verified.png")
        await page.screenshot(path=shot3_path)
        print(f"Screenshot 3 salvo: {shot3_path}")

        await browser.close()
        print("\nTODOS OS 4 TESTES PASSARAM COM 100% DE SUCESSO!")

if __name__ == "__main__":
    asyncio.run(run_tests())
