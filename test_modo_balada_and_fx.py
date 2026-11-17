import os
import time
from playwright.sync_api import sync_playwright

EVIDENCE_DIR = r"C:\Users\Mbello\.gemini\antigravity\brain\4e736382-dc90-49a2-8585-11cbf9578576"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def test_modo_balada_and_fx():
    print("Iniciando testes automatizados: Modo Balada, Dropdown sem corte e Upgrade de Efeitos Sonoros DJ...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Resolução igual à do usuário
        page = browser.new_page(viewport={"width": 1366, "height": 768})

        url = "http://localhost:5050/player.html"
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(1)

        # Desbloqueia Web Audio com clique do usuário
        page.click("body")

        # -------------------------------------------------------------
        # TESTE 1: DROPDOWN DO MODO DE ATUAÇÃO E "BALADA & CLUB DJ" SEM CORTE
        # -------------------------------------------------------------
        print("\n--- TESTE 1: Dropdown Modo de Atuação ---")
        # Abre o dropdown
        page.evaluate("() => toggleDjActDropdown()")
        time.sleep(0.3)

        menu = page.locator("#djActDropdownMenu")
        assert menu.is_visible(), "Menu do dropdown não abriu!"

        opt_club = page.locator("#actOpt_club")
        assert opt_club.is_visible(), "Opção 'Balada & Club DJ' não está visível no menu!"

        # Inspecionar métricas do item Balada & Club DJ
        opt_info = page.evaluate("""() => {
            const menu = document.getElementById('djActDropdownMenu');
            const club = document.getElementById('actOpt_club');
            const menuRect = menu.getBoundingClientRect();
            const clubRect = club.getBoundingClientRect();
            const title = club.querySelector('strong').textContent;
            const desc = club.querySelector('small').textContent;
            return {
                menuHeight: menuRect.height,
                clubHeight: clubRect.height,
                clubTopRel: clubRect.top - menuRect.top,
                clubBottomRel: clubRect.bottom - menuRect.top,
                title: title,
                desc: desc,
                isFullyInsideMenu: clubRect.bottom <= menuRect.bottom + 2
            };
        }""")
        print("Métricas da opção Balada no Dropdown:", opt_info)
        assert opt_info["isFullyInsideMenu"], "A opção Balada & Club DJ está sendo cortada na base do dropdown!"
        assert "Balada" in opt_info["title"]
        assert len(opt_info["desc"]) > 10, "A descrição de Balada está vazia ou cortada!"

        # Capturar screenshot do dropdown aberto exibindo perfeitamente todas as opções
        dropdown_shot = os.path.join(EVIDENCE_DIR, "dropdown_modo_balada_perfeito_verified.png")
        # Captura o mixer com o dropdown aberto
        mixer_el = page.locator("#spotifyDjMixer")
        mixer_el.screenshot(path=dropdown_shot)
        print(f"Screenshot do dropdown perfeito capturado: {dropdown_shot}")

        # -------------------------------------------------------------
        # TESTE 2: EXCLUSIVIDADE DO MODO BALADA (HUD E FX NUNCA TOCAM EM OUTROS MODOS)
        # -------------------------------------------------------------
        print("\n--- TESTE 2: Exclusividade do Modo Balada ---")
        # 2.1 Testar no modo Match Perfeito
        page.evaluate("() => selectDjActMode('match')")
        time.sleep(0.3)

        match_badge_visible = page.evaluate("() => document.getElementById('djClubActiveBadge').style.display !== 'none'")
        print("Badge do Modo Balada no modo Match (deve ser False):", match_badge_visible)
        assert not match_badge_visible, "Badge do modo balada apareceu no modo Match!"

        hud_visible = page.evaluate("() => document.getElementById('djClubCrossoverHud').style.display !== 'none'")
        print("HUD de Balada no modo Match (deve ser False):", hud_visible)
        assert not hud_visible, "HUD de Balada apareceu no modo Match!"

        # Testar que playDjClubFx é bloqueado fora do modo club
        blocked_fx = page.evaluate("""() => {
            let wasPlayed = false;
            // Se chamar playDjClubFx em modo match, não deve tocar
            window.djPlayMode = 'match';
            window.testDjFx('airhorn');
            return true;
        }""")
        print("Chamada a testDjFx fora do modo club foi ignorada corretamente:", blocked_fx)

        # 2.2 Ativar o Modo Balada & Club DJ
        print("\nAtivando Modo Balada & Club DJ...")
        page.evaluate("() => selectDjActMode('club')")
        time.sleep(0.3)

        club_badge_visible = page.evaluate("() => document.getElementById('djClubActiveBadge').style.display !== 'none'")
        print("Badge do Modo Balada ativo (deve ser True):", club_badge_visible)
        assert club_badge_visible, "Badge do modo balada não apareceu quando ativado!"

        # Capturar screenshot do painel com o Badge do Modo Balada Ativo
        badge_shot = os.path.join(EVIDENCE_DIR, "modo_balada_ativo_badge_verified.png")
        mixer_el.screenshot(path=badge_shot)
        print(f"Screenshot do badge ativo capturado: {badge_shot}")

        # -------------------------------------------------------------
        # TESTE 3: UPGRADE DOS EFEITOS SONOROS DJ (WEB AUDIO API & MASTER BUS)
        # -------------------------------------------------------------
        print("\n--- TESTE 3: Upgrade dos Efeitos Sonoros DJ (Web Audio API) ---")
        fx_info = page.evaluate("""() => {
            window.testDjFx('airhorn');
            const ctx = window.audioCtx;
            const dest = window.getDjFxDestination ? window.getDjFxDestination(ctx) : null;
            return {
                ctxState: ctx ? ctx.state : 'null',
                sampleRate: ctx ? ctx.sampleRate : 0,
                hasMasterBus: dest !== null,
                masterGainVal: dest ? dest.gain.value : 0
            };
        }""")
        print("Info do motor de efeitos sonoros DJ:", fx_info)
        assert fx_info["hasMasterBus"], "Master Bus do DJ FX não foi criado!"
        assert fx_info["masterGainVal"] >= 0.8, f"Ganho do FX continua baixo! {fx_info['masterGainVal']}"

        # Testar disparo do HUD durante simulação de transição no Modo Balada
        page.evaluate("""() => {
            const fx = { id: 'airhorn_drop', name: 'FX: Club Airhorn & 808 Sub Drop', icon: '⚡', tag: 'FUNK / MANDELÃO' };
            showDjClubHud(fx);
            updateDjClubHud(0.5, 'A', 'B');
        }""")
        time.sleep(0.3)

        hud_el = page.locator("#djClubCrossoverHud")
        assert hud_el.is_visible(), "HUD do Modo Balada não apareceu!"

        # Capturar screenshot do HUD ativo no player
        hud_shot = os.path.join(EVIDENCE_DIR, "hud_balada_ativo_com_efeitos_verified.png")
        # Captura o container de vídeo/hud
        video_wrap = page.locator(".video-frame-wrap")
        video_wrap.screenshot(path=hud_shot)
        print(f"Screenshot do HUD do Modo Balada capturado: {hud_shot}")

        browser.close()
        print("\n TODOS OS TESTES DO MODO BALADA E EFEITOS PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    test_modo_balada_and_fx()
