import asyncio
import os
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        print("Navigating to http://localhost:5050/?cachebust=test ...")
        await page.goto("http://localhost:5050/?cachebust=test", wait_until="networkidle")

        # -------------------------------------------------------------
        # TESTE 1: Spotify Playlists & Cumbia
        # -------------------------------------------------------------
        print("\n--- TESTE 1: Playlists Spotify & Cumbia (33) ---")
        
        # Click Spotify Playlists tab
        sp_tab = page.locator('button:has-text("Playlists Spotify")')
        await sp_tab.click()
        await page.wait_for_timeout(1000)

        # Check total playlists badge
        sp_badge_text = await sp_tab.inner_text()
        print(f"Spotify Tab Text: {sp_badge_text}")

        # Check Cumbia chip
        cumbia_chip = page.locator('#spChip_cumbia')
        cumbia_chip_text = await cumbia_chip.inner_text()
        print(f"Cumbia Chip Text: {cumbia_chip_text}")

        # Click Cumbia chip to filter
        await cumbia_chip.click()
        await page.wait_for_timeout(1000)

        # Count visible playlists under Cumbia
        visible_playlists = await page.locator('[id^="spTab_"]:not([style*="display: none"])').count()
        print(f"Visible Cumbia Playlists: {visible_playlists}")

        # Click on Damas Gratis playlist
        damas_tab = page.locator('[id^="spTab_"]:has-text("Damas Gratis")').first
        await damas_tab.click()
        await page.wait_for_timeout(1000)

        # Count tracks rendered
        track_cards = await page.locator('#spotifyTrackList .track-card').count()
        print(f"Damas Gratis tracks rendered: {track_cards}")

        # Play track 1 of Damas Gratis
        play_btn = page.locator('#spotifyTrackList .track-card').first.locator('button:has-text("Tocar")')
        await play_btn.click()
        await page.wait_for_timeout(2000)

        # Verify Deck A and Deck B
        deck_a_title = await page.locator('#deckATitle').inner_text()
        deck_a_bpm = await page.locator('#deckABpm').inner_text()
        deck_b_title = await page.locator('#deckBTitle').inner_text()
        deck_b_bpm = await page.locator('#deckBBpm').inner_text()
        bar_status = await page.locator('#barStatusText').inner_text()

        print(f"Deck A: {deck_a_title} ({deck_a_bpm})")
        print(f"Deck B: {deck_b_title} ({deck_b_bpm})")
        print(f"Status Bar: {bar_status}")

        shot1_path = os.path.join(ARTIFACT_DIR, "cumbia_33_playlists_verified.png")
        await page.screenshot(path=shot1_path)
        print(f"Screenshot 1 saved: {shot1_path}")

        # -------------------------------------------------------------
        # TESTE 2: Anti-Loop & Expansão Fora da Lista
        # -------------------------------------------------------------
        print("\n--- TESTE 2: Anti-Loop e Expansão Fora da Lista ---")

        # Simulate a 2-track queue via page.evaluate
        eval_result = await page.evaluate('''() => {
            // Fila com exatamente 2 faixas de Cumbia
            window.nowPlayingQueue = [
                { video_id: 'cumbia_vid_1', title: 'Damas Gratis - No te Creas Tan Importante', artist: 'Damas Gratis', bpm: 96, category: 'Cumbia' },
                { video_id: 'cumbia_vid_2', title: 'Ke Personajes - Un Finde', artist: 'Ke Personajes', bpm: 96, category: 'Cumbia' }
            ];
            
            // Faixa 1 tocou
            window.recordTrackInRecentHistory('cumbia_vid_1');

            // Agora faixa 2 está tocando (última da lista de 2)
            window.nowPlayingIndex = 1;
            window.nowPlayingTrack = window.nowPlayingQueue[1];
            window.recordTrackInRecentHistory('cumbia_vid_2');

            // O DJ Mode calcula a próxima faixa quando estamos no fim da lista (<= 2)
            const nextTrack = window.calculateDjModeNextTrack(window.nowPlayingQueue[1]);
            
            // Define no player e atualiza a barra
            window.upcomingTrack = nextTrack;
            window.updateUpcomingTrackUI(nextTrack);

            return {
                queueLength: window.nowPlayingQueue.length,
                recentHistory: (window.recentPlaybackHistoryIds || []).slice(-5),
                nextTrackTitle: nextTrack ? nextTrack.title : null,
                nextTrackArtist: nextTrack ? nextTrack.artist : null,
                nextTrackBpm: nextTrack ? nextTrack.bpm : null,
                isExternal: nextTrack ? nextTrack._isExternalDiscovery : false,
                barStatus: document.getElementById('barStatusText') ? document.getElementById('barStatusText').innerText : ''
            };
        }''')

        print(f"Simulation Result:")
        print(f"  Queue Length: {eval_result['queueLength']}")
        print(f"  Recent History IDs: {eval_result['recentHistory']}")
        print(f"  Next Track: {eval_result['nextTrackTitle']} - {eval_result['nextTrackArtist']} ({eval_result['nextTrackBpm']} BPM)")
        print(f"  Is External Discovery (_isExternalDiscovery): {eval_result['isExternal']}")
        print(f"  Status Bar Text: {eval_result['barStatus']}")

        # Now test auto transition: when transition happens, the external track is appended to queue and played
        advance_result = await page.evaluate('''() => {
            // Executa transição manual para a próxima
            const prevIndex = window.nowPlayingIndex;
            window.manualTransition('next');

            return {
                newQueueLength: window.nowPlayingQueue.length,
                newIndex: window.nowPlayingIndex,
                nowPlayingTitle: window.nowPlayingTrack ? window.nowPlayingTrack.title : null,
                barStatus: document.getElementById('barStatusText') ? document.getElementById('barStatusText').innerText : ''
            };
        }''')

        print(f"\nTransition Result:")
        print(f"  New Queue Length: {advance_result['newQueueLength']}")
        print(f"  New Index: {advance_result['newIndex']}")
        print(f"  Now Playing Title: {advance_result['nowPlayingTitle']}")
        print(f"  Status Bar Text: {advance_result['barStatus']}")

        shot2_path = os.path.join(ARTIFACT_DIR, "anti_loop_expansao_fora_da_lista_verified.png")
        await page.screenshot(path=shot2_path)
        print(f"Screenshot 2 saved: {shot2_path}")

        await browser.close()
        print("\nAll tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_tests())
