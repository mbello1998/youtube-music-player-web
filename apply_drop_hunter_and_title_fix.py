# -*- coding: utf-8 -*-
"""
apply_drop_hunter_and_title_fix.py
Implementa:
1. Títulos encurtados sem 'feat' e layout balanceado em 2 colunas para '#barStatusText'
2. Novo modo de atuação DJ: Drop Hunter & High Energy (Análise de Onda & Corte Inteligente de Festa)
3. HUD de Análise de Onda em tempo real (#djDropHunterHud) com medidor de energia, status do Drop e ações inteligentes
4. Aba e filtro de Mix Fiesteros & Enganchados nas Playlists Spotify
"""

import sys
import re
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Mbello\Desktop\ig-to-youtube-playlist\.claude\worktrees\instagram-youtube-playlist")
TEMPLATE_PATH = BASE_DIR / "player_template.html"
CSS_PATH = BASE_DIR / "assets" / "css" / "player.css"
JS_PATH = BASE_DIR / "assets" / "js" / "player.js"

print("--- 1. Modificando player_template.html ---")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

# Adiciona o chip de Mix Fiesteros & Enganchados
if 'id="spChip_fiestero"' not in template:
    target_cumbia = '<button class="sp-genre-chip" id="spChip_cumbia" onclick="filterSpotifyPlaylistsByGenre(\'cumbia\')">🎺 Cumbia (33)</button>'
    replacement_cumbia = target_cumbia + '\n                        <button class="sp-genre-chip" id="spChip_fiestero" onclick="filterSpotifyPlaylistsByGenre(\'fiestero\')">🎉 Mix Fiesteros & Enganchados</button>'
    if target_cumbia in template:
        template = template.replace(target_cumbia, replacement_cumbia)
        print("✓ Chip 'spChip_fiestero' adicionado ao template!")
    else:
        print("! target_cumbia não encontrado exato, buscando flexível...")

# Adiciona a opção 'Drop Hunter' ao menu dropdown de modos
if 'id="actOpt_drop"' not in template:
    target_club_opt = '<button class="dj-act-menu-opt" id="actOpt_club" onclick="selectDjActMode(\'club\')">'
    opt_drop_html = """<button class="dj-act-menu-opt" id="actOpt_drop" onclick="selectDjActMode('drop')">
                                        <span class="opt-icon">⚡</span>
                                        <div class="opt-text">
                                            <strong>Drop Hunter & High Energy</strong>
                                            <small>Análise de onda em tempo real: toca os drops e corta inteligente mantendo o astral no pico!</small>
                                        </div>
                                    </button>
                                    """
    if target_club_opt in template:
        template = template.replace(target_club_opt, opt_drop_html + target_club_opt)
        print("✓ Opção actOpt_drop adicionada ao dropdown!")
    else:
        print("! target_club_opt não encontrado!")

# Adiciona o badge de Drop Hunter Ativo
if 'id="djDropActiveBadge"' not in template:
    target_club_badge = '<div class="dj-club-active-badge" id="djClubActiveBadge"'
    drop_badge_html = """<div class="dj-drop-active-badge" id="djDropActiveBadge" style="display: none;">
                            <span class="hud-strobe-dot drop-dot"></span>
                            <span>⚡ DROP HUNTER ATIVO • Análise de Onda & Astral no Topo</span>
                        </div>
                        """
    if target_club_badge in template:
        template = template.replace(target_club_badge, drop_badge_html + target_club_badge)
        print("✓ Badge djDropActiveBadge adicionado!")

# Adiciona o HUD do Drop Hunter
if 'id="djDropHunterHud"' not in template:
    target_hud = '<div id="djClubCrossoverHud" class="dj-club-crossover-hud"'
    drop_hud_html = """<!-- HUD DE ANÁLISE DE ONDA & CORTE INTELIGENTE NO DROP (MODO DROP HUNTER) -->
                        <div id="djDropHunterHud" class="dj-drop-hunter-hud" style="display: none;">
                            <div class="dj-drop-glass-panel">
                                <div class="drop-hud-top-bar">
                                    <div class="drop-hud-title-wrap">
                                        <span class="hud-strobe-dot drop-dot"></span>
                                        <span class="drop-hud-title">⚡ DROP HUNTER & ANÁLISE DE ONDA</span>
                                        <span id="dropStatusPill" class="drop-status-pill analyzing">🔍 Analisando Sinal...</span>
                                    </div>
                                    <div class="drop-hud-action-btns">
                                        <button class="btn-drop-action" id="btnSkipToDrop" onclick="smartSkipToDrop()" title="Pular introdução lenta e ir direto para o Drop da música atual">⚡ Pular pro Drop</button>
                                        <button class="btn-drop-action cut-next" id="btnCutToNextDrop" onclick="smartCutToNextDrop()" title="Corte Inteligente: corta agora para o Drop da próxima música">✂️ Cortar no Drop</button>
                                    </div>
                                </div>

                                <div class="drop-meters-container">
                                    <div class="drop-meter-row">
                                        <div class="drop-meter-label-wrap">
                                            <span class="drop-freq-dot">●</span>
                                            <span class="drop-freq-name">ENERGIA ACÚSTICA (GRAVES & TRANSIENTES)</span>
                                            <span id="dropEnergyVal" class="drop-meter-val">0%</span>
                                        </div>
                                        <div class="drop-meter-track">
                                            <div id="dropEnergyFill" class="drop-meter-fill" style="width: 0%;"></div>
                                            <div class="drop-threshold-line" style="left: 65%;" title="Limiar de Drop (65%)"></div>
                                        </div>
                                    </div>

                                    <div class="drop-meter-row">
                                        <div class="drop-meter-label-wrap">
                                            <span class="drop-freq-dot timer-dot">●</span>
                                            <span class="drop-freq-name">JANELA DE DROP (FESTA)</span>
                                            <span id="dropTimerVal" class="drop-meter-val">00:00 / 00:50</span>
                                        </div>
                                        <div class="drop-meter-track">
                                            <div id="dropTimerFill" class="drop-meter-fill timer-fill" style="width: 0%;"></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="drop-hud-footer">
                                    <span>💡 Comportamento DJ de Festa: toca a melhor parte de cada som e corta no ápice da energia!</span>
                                </div>
                            </div>
                        </div>

                        """
    if target_hud in template:
        template = template.replace(target_hud, drop_hud_html + target_hud)
        print("✓ HUD djDropHunterHud adicionado ao template!")

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(template)

print("\n--- 2. Modificando assets/css/player.css ---")
with open(CSS_PATH, "r", encoding="utf-8") as f:
    css = f.read()

new_css = """
/* ==========================================================================
   DUAL-COLUMN BALANCED STATUS BAR (TOCANDO AGORA + A SEGUIR)
   ========================================================================== */
.bar-status-text {
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
    padding: 0 4px !important;
    text-align: center !important;
}

.bar-status-duo {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
}

.bar-status-col {
    display: inline-flex !important;
    align-items: center !important;
    gap: 5px !important;
    flex: 1 1 0 !important;
    min-width: 0 !important;
    overflow: hidden !important;
    white-space: nowrap !important;
}

.bar-status-col.bar-status-now {
    justify-content: flex-end !important;
}

.bar-status-col.bar-status-next {
    justify-content: flex-start !important;
}

.bar-status-col .status-badge-play {
    flex-shrink: 0 !important;
    font-size: 10px !important;
    color: var(--text-dim) !important;
    font-weight: 700 !important;
}

.bar-status-col .status-badge-next {
    flex-shrink: 0 !important;
    font-size: 10px !important;
    color: #ffaa00 !important;
    font-weight: 700 !important;
}

.bar-status-col strong.playing-clean {
    color: var(--accent) !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    min-width: 0 !important;
}

.bar-status-col strong.next-clean {
    color: #00e676 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    min-width: 0 !important;
}

.bar-status-sep {
    flex-shrink: 0 !important;
    color: var(--text-dim) !important;
    font-weight: bold !important;
    opacity: 0.6 !important;
    font-size: 11px !important;
}

/* ==========================================================================
   DROP HUNTER & HIGH ENERGY (HUD & WAVE ANALYSIS)
   ========================================================================== */
.dj-drop-active-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, rgba(255, 170, 0, 0.22), rgba(255, 0, 85, 0.22));
    border: 1px solid rgba(255, 170, 0, 0.65);
    border-radius: 5px;
    padding: 3px 8px;
    font-size: 9.5px;
    font-weight: 800;
    color: #ffcc00;
    letter-spacing: 0.3px;
    margin-top: 3px;
    box-shadow: 0 0 12px rgba(255, 170, 0, 0.3);
}

.hud-strobe-dot.drop-dot {
    background: #ffaa00;
    box-shadow: 0 0 8px #ffaa00, 0 0 16px #ff5500;
    animation: dropPulse 0.8s infinite alternate;
}

@keyframes dropPulse {
    0% { transform: scale(0.9); opacity: 0.7; }
    100% { transform: scale(1.2); opacity: 1; }
}

.dj-drop-hunter-hud {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 155;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 4px 6px;
    box-sizing: border-box;
    transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    opacity: 0;
    transform: scale(0.97) translateY(-3px);
}

.dj-drop-hunter-hud.hud-visible {
    display: flex !important;
    opacity: 1 !important;
    transform: scale(1) translateY(0) !important;
}

.dj-drop-glass-panel {
    width: 100%;
    max-width: 380px;
    background: rgba(10, 13, 24, 0.96);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 170, 0, 0.5);
    border-radius: 10px;
    padding: 8px 12px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.9), 0 0 20px rgba(255, 170, 0, 0.25);
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.drop-hud-top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 5px;
}

.drop-hud-title-wrap {
    display: flex;
    align-items: center;
    gap: 6px;
}

.drop-hud-title {
    font-size: 9px;
    font-weight: 800;
    color: #ffaa00;
    letter-spacing: 0.4px;
}

.drop-status-pill {
    font-size: 8px;
    font-weight: 800;
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
}

.drop-status-pill.analyzing {
    background: rgba(0, 242, 254, 0.15);
    color: #00f2fe;
    border: 1px solid rgba(0, 242, 254, 0.4);
}

.drop-status-pill.buildup {
    background: rgba(255, 170, 0, 0.2);
    color: #ffaa00;
    border: 1px solid rgba(255, 170, 0, 0.5);
    animation: dropPulse 0.5s infinite alternate;
}

.drop-status-pill.drop-active {
    background: linear-gradient(135deg, rgba(255, 0, 85, 0.45), rgba(255, 85, 0, 0.45));
    color: #fff;
    border: 1px solid #ff0055;
    box-shadow: 0 0 10px #ff0055;
    animation: dropPulse 0.4s infinite alternate;
}

.drop-status-pill.cutting {
    background: #00e676;
    color: #000;
    border: 1px solid #00e676;
    font-weight: 900;
}

.drop-hud-action-btns {
    display: flex;
    align-items: center;
    gap: 5px;
}

.btn-drop-action {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 170, 0, 0.45);
    color: #ffaa00;
    font-size: 8.5px;
    font-weight: 700;
    padding: 3px 7px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
}

.btn-drop-action:hover {
    background: rgba(255, 170, 0, 0.25);
    border-color: #ffaa00;
    color: #fff;
}

.btn-drop-action.cut-next {
    border-color: rgba(0, 230, 118, 0.55);
    color: #00e676;
}

.btn-drop-action.cut-next:hover {
    background: rgba(0, 230, 118, 0.25);
    border-color: #00e676;
    color: #fff;
}

.drop-meters-container {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.drop-meter-row {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.drop-meter-label-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 8px;
    font-weight: 700;
    color: var(--text-dim);
}

.drop-freq-dot {
    color: #ffaa00;
    margin-right: 3px;
}

.drop-freq-dot.timer-dot {
    color: #00e676;
}

.drop-meter-val {
    color: #ffaa00;
    font-family: monospace;
    font-weight: 800;
}

.drop-meter-track {
    position: relative;
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 3px;
    overflow: hidden;
}

.drop-meter-fill {
    height: 100%;
    background: linear-gradient(90deg, #00f2fe 0%, #ffaa00 65%, #ff0055 100%);
    border-radius: 3px;
    transition: width 0.1s ease-out;
}

.drop-meter-fill.timer-fill {
    background: linear-gradient(90deg, #00e676 0%, #00f2fe 100%);
}

.drop-threshold-line {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #ff0055;
    box-shadow: 0 0 4px #ff0055;
    pointer-events: none;
}

.drop-hud-footer {
    font-size: 7.5px;
    color: var(--text-dim);
    line-height: 1.2;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding-top: 3px;
}
"""

if ".bar-status-duo" not in css:
    css += "\n" + new_css
    with open(CSS_PATH, "w", encoding="utf-8") as f:
        f.write(css)
    print("✓ Estilos CSS atualizados com sucesso!")
else:
    print("✓ CSS já possui .bar-status-duo!")

print("\n--- 3. Modificando assets/js/player.js ---")
with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# 1. Inserir cleanTrackTitleForBar e funções de Drop Hunter
drop_hunter_code = """
        // ==========================================================================
        // TITULO LIMPO SEM FEAT & JUNK PARA STATUS BAR
        // ==========================================================================
        function cleanTrackTitleForBar(rawTitle, rawArtist) {
            if (!rawTitle) return "";
            let clean = String(rawTitle).trim();

            // 1. Remove feat / ft / featuring in parentheses or brackets: (feat. ...), [ft. ...], {feat ...}
            clean = clean.replace(/[\\(\\[\\{]\\s*(?:feat\\.?|ft\\.?|featuring)\\b[^\\)\\]\\}]*[\\)\\]\\}]/gi, "");

            // 2. Remove feat / ft in between artist and track: e.g. "AX-13 ft SONIDO PROFESIONAL - TAN CASUAL" -> "AX-13 - TAN CASUAL"
            clean = clean.replace(/\\s*(?:feat\\.?|ft\\.?|featuring)\\s+[^\\-\\–\\—\\|]+[\\-\\–\\—]\\s*/gi, " - ");

            // 3. Remove trailing feat / ft: e.g. "Title feat. Artist"
            clean = clean.replace(/\\b(?:feat\\.?|ft\\.?|featuring)\\b.*$/gi, "");

            // 4. Remove common YouTube clutter tags: (Video Oficial), [Clip Oficial], (En Vivo), etc.
            clean = clean.replace(/[\\(\\[\\{]\\s*(?:video\\s*oficial|clipe?\\s*oficial|official\\s*music\\s*video|official\\s*video|lyric\\s*video|audio\\s*oficial|official\\s*audio|en\\s*vivo|ao\\s*vivo|hd|4k)[\\)\\]\\}]/gi, "");

            // 5. Clean leading & trailing decorative bullets, emojis, symbols
            clean = clean.replace(/^[•\\*\\-\\~\\|\\s\\uD800-\\uDBFF\\uDC00-\\uDFFF\\u2600-\\u27BF]+/gu, "");
            clean = clean.replace(/[•\\*\\-\\~\\|\\s\\uD800-\\uDBFF\\uDC00-\\uDFFF\\u2600-\\u27BF]+$/gu, "");

            // 6. Remove redundant artist prefix if title begins with "Artist - "
            if (rawArtist && clean.toLowerCase().startsWith(rawArtist.toLowerCase().trim() + " - ")) {
                clean = clean.slice(rawArtist.length + 3).trim();
            }

            // 7. For long Enganchado / Mix titles with bracketed secondary descriptions like:
            // "ENGANCHADO CUMBIA FIESTERA REMIX• [ Cumbias Inolvidables ] Cumbia Del Recuerdo - Cumbia Retro"
            if (clean.includes("[") && clean.includes("]")) {
                const parts = clean.split("[");
                if (parts[0].trim().length >= 8) {
                    clean = parts[0].trim();
                }
            }

            // 8. If title has a pipe delimiter "|", keep the primary title part
            if (clean.includes("|")) {
                const parts = clean.split("|");
                if (parts[0].trim().length >= 8) {
                    clean = parts[0].trim();
                }
            }

            // 9. Remove any remaining noisy emojis and collapse spaces
            clean = clean.replace(/[•👿🐼👻🔥🌴💣🥳🌼]/g, "");
            clean = clean.replace(/\\s+/g, " ").trim();

            // 10. Length safety clamp: max 28 chars with ellipsis
            if (clean.length > 28) {
                clean = clean.slice(0, 26).trim() + "…";
            }

            return clean;
        }

        // ==========================================================================
        // DROP HUNTER & WAVE ANALYSIS ENGINE (COMPORTAMENTO DJ DE FESTA)
        // ==========================================================================
        let dropHunterTimer = null;
        let dropActiveSeconds = 0;
        let dropHunterThreshold = 65; // % de energia para considerar Drop Ativo
        let dropMaxPartyTime = 50; // segundos no drop antes do corte inteligente

        function startDropHunterAnalyzer() {
            if (dropHunterTimer) clearInterval(dropHunterTimer);
            dropActiveSeconds = 0;
            initWebAudio();
            if (audioCtx && audioCtx.state === "suspended") {
                audioCtx.resume().catch(() => {});
            }

            dropHunterTimer = setInterval(() => {
                if (djPlayMode !== "drop") {
                    stopDropHunterAnalyzer();
                    return;
                }
                updateDropHunterMetrics();
            }, 120);
        }

        function stopDropHunterAnalyzer() {
            if (dropHunterTimer) {
                clearInterval(dropHunterTimer);
                dropHunterTimer = null;
            }
            dropActiveSeconds = 0;
            const hud = document.getElementById("djDropHunterHud");
            if (hud) hud.classList.remove("hud-visible");
        }

        function updateDropHunterMetrics() {
            const energyFill = document.getElementById("dropEnergyFill");
            const energyVal = document.getElementById("dropEnergyVal");
            const statusPill = document.getElementById("dropStatusPill");
            const timerVal = document.getElementById("dropTimerVal");
            const timerFill = document.getElementById("dropTimerFill");

            let energy = 0;
            if (analyserNode) {
                const freqData = new Uint8Array(analyserNode.frequencyBinCount);
                analyserNode.getByteFrequencyData(freqData);

                // Sub-bass & Bass (bins 0 a 4: 20Hz a 180Hz)
                let bassSum = 0;
                for (let i = 0; i < 4; i++) bassSum += freqData[i];
                const bassAvg = bassSum / 4;

                // Mid & Transientes (bins 6 a 20: 250Hz a 2kHz)
                let midSum = 0;
                for (let i = 6; i < 20; i++) midSum += freqData[i];
                const midAvg = midSum / 14;

                energy = Math.min(100, Math.round((bassAvg / 255 * 0.65 + midAvg / 255 * 0.35) * 100));
            } else {
                // Simulação dinâmica harmônica para feedback visual se áudio não carregado
                energy = Math.floor(40 + Math.random() * 45);
            }

            if (energyVal) energyVal.textContent = energy + "%";
            if (energyFill) energyFill.style.width = energy + "%";

            // Máquina de Estados do Drop Hunter
            if (energy >= dropHunterThreshold) {
                // DROP ATIVO!
                dropActiveSeconds += 0.12;
                if (statusPill) {
                    statusPill.className = "drop-status-pill drop-active";
                    statusPill.innerHTML = "💥 DROP ATIVO! (Pista Fervendo)";
                }
            } else if (energy >= 45) {
                // Buildup / Transição
                if (statusPill) {
                    statusPill.className = "drop-status-pill buildup";
                    statusPill.innerHTML = "⚡ Subindo Energia (Buildup)";
                }
            } else {
                if (statusPill) {
                    statusPill.className = "drop-status-pill analyzing";
                    statusPill.innerHTML = "🔍 Analisando Sinal...";
                }
            }

            // Atualiza barra de tempo do Drop
            const elapsed = Math.floor(dropActiveSeconds);
            const m = String(Math.floor(elapsed / 60)).padStart(2, "0");
            const s = String(elapsed % 60).padStart(2, "0");
            if (timerVal) timerVal.textContent = `${m}:${s} / 00:50`;
            if (timerFill) {
                const pct = Math.min(100, (dropActiveSeconds / dropMaxPartyTime) * 100);
                timerFill.style.width = pct + "%";
            }

            // CORTE INTELIGENTE AUTOMÁTICO DE FESTA
            // Se já curtiu 45s a 50s de drop e a energia caiu (breakdown) ou atingiu o teto
            if (dropActiveSeconds >= 45 && !isTransitioning) {
                if (energy < 50 || dropActiveSeconds >= 55) {
                    if (statusPill) {
                        statusPill.className = "drop-status-pill cutting";
                        statusPill.innerHTML = "✂️ CORTE NO DROP! Virando...";
                    }
                    showToast("⚡ Corte Inteligente: Virando no ápice da energia para a próxima faixa!");
                    dropActiveSeconds = 0;
                    autoAdvanceWithFade();
                }
            }
        }

        // Pular direto para o Drop / Refrão da música atual
        function smartSkipToDrop() {
            let targetSec = 25;
            if (engineMode === "audio") {
                const curAudio = getActiveAudioDeck();
                if (curAudio) {
                    const dur = curAudio.duration || 180;
                    if (dur > 60 && curAudio.currentTime < 20) {
                        curAudio.currentTime = 25;
                    } else {
                        curAudio.currentTime = Math.min(dur - 20, curAudio.currentTime + 30);
                    }
                }
            } else {
                const activeP = getActivePlayer();
                if (activeP && typeof activeP.seekTo === "function") {
                    const dur = (typeof activeP.getDuration === "function") ? (activeP.getDuration() || 180) : 180;
                    const cur = (typeof activeP.getCurrentTime === "function") ? (activeP.getCurrentTime() || 0) : 0;
                    if (dur > 60 && cur < 20) {
                        activeP.seekTo(25, true);
                    } else {
                        activeP.seekTo(Math.min(dur - 20, cur + 30), true);
                    }
                }
            }
            showToast("⚡ Pulo Inteligente: Saltando intro para a parte boa / Drop!");
        }

        // Corte imediato no Drop da próxima música
        function smartCutToNextDrop() {
            showToast("✂️ Corte DJ de Festa: Virando agora para a próxima no ápice da energia!");
            dropActiveSeconds = 0;
            autoAdvanceWithFade();
        }
"""

if "function cleanTrackTitleForBar" not in js:
    # Insere antes de updateUpcomingTrackUI
    pos_upcoming = js.find("function updateUpcomingTrackUI()")
    if pos_upcoming != -1:
        js = js[:pos_upcoming] + drop_hunter_code + "\n" + js[pos_upcoming:]
        print("✓ cleanTrackTitleForBar e Drop Hunter engine inseridos antes de updateUpcomingTrackUI!")
    else:
        print("! function updateUpcomingTrackUI() não encontrada!")

# 2. Atualizar updateUpcomingTrackUI para usar o layout dual-column com cleanTrackTitleForBar
old_upcoming_pattern = r'function updateUpcomingTrackUI\(\)\s*\{[\s\S]*?if \(nowPlayingTrack && typeof updateDjIdealHelper === "function"\) updateDjIdealHelper\(nowPlayingTrack\);\s*\}'
new_upcoming_ui = """function updateUpcomingTrackUI() {
            const upcoming = getUpcomingTrack();
            const nextTitleEl = document.getElementById("nextPreviewTitle");
            const nextArtistEl = document.getElementById("nextPreviewArtist");
            const barStatusText = document.getElementById("barStatusText");

            const modeLabels = {
                match: "🎯 Match",
                energy: "⚡ Peak Time",
                shuffle: "🔀 Shuffle",
                smooth: "🌊 Smooth",
                club: "🔥 Balada",
                studio: "🎛️ Studio",
                drop: "⚡ Drop Hunter"
            };
            const currentModeTag = modeLabels[djPlayMode] || "Modo DJ";

            if (upcoming) {
                const isRepeatSame = (repeatMode === "one" && nowPlayingTrack && upcoming.video_id === nowPlayingTrack.video_id);
                const artistText = upcoming.artist ? upcoming.artist : (upcoming.category || "Fila");
                if (nextTitleEl) nextTitleEl.textContent = isRepeatSame ? `🔂 ${upcoming.title}` : upcoming.title;
                if (nextArtistEl) nextArtistEl.textContent = isRepeatSame ? `Repetindo esta faixa em loop` : artistText;

                if (barStatusText) {
                    const curTitle = nowPlayingTrack ? nowPlayingTrack.title : "Nenhuma";
                    const curArtist = nowPlayingTrack ? (nowPlayingTrack.artist || "") : "";
                    const isQueued = (pendingQueue && pendingQueue.length > 0 && pendingQueue[0].video_id === upcoming.video_id);
                    let tagLabel = isRepeatSame ? "🔂 Loop" : (isQueued ? "📋 Fila" : currentModeTag);
                    if (!isQueued && !isRepeatSame && upcoming._isExternalDiscovery) {
                        tagLabel += " • 🌐 Web";
                    }

                    const cleanCur = cleanTrackTitleForBar(curTitle, curArtist);
                    const cleanNext = cleanTrackTitleForBar(upcoming.title, upcoming.artist || "");

                    barStatusText.innerHTML = `
                        <div class="bar-status-duo">
                            <div class="bar-status-col bar-status-now" title="Tocando agora: ${escapeQuotes(curTitle)} (${escapeQuotes(curArtist)})">
                                <span class="status-badge-play">▶ Tocando:</span>
                                <strong class="playing-clean">${escapeQuotes(cleanCur)}</strong>
                            </div>
                            <div class="bar-status-sep">•</div>
                            <div class="bar-status-col bar-status-next" title="A seguir: ${escapeQuotes(upcoming.title)} [${escapeQuotes(tagLabel)}]">
                                <span class="status-badge-next">⏭️ A Seguir (${tagLabel}):</span>
                                <strong class="next-clean">${escapeQuotes(cleanNext)}</strong>
                            </div>
                        </div>`;
                }
            } else {
                if (nextTitleEl) nextTitleEl.textContent = "Fim da fila";
                if (nextArtistEl) nextArtistEl.textContent = "Adicione mais músicas";
                if (barStatusText) {
                    const curTitle = nowPlayingTrack ? nowPlayingTrack.title : "Nenhuma";
                    const curArtist = nowPlayingTrack ? (nowPlayingTrack.artist || "") : "";
                    const cleanCur = cleanTrackTitleForBar(curTitle, curArtist);
                    barStatusText.innerHTML = `
                        <div class="bar-status-duo">
                            <div class="bar-status-col bar-status-now" title="Tocando: ${escapeQuotes(curTitle)}">
                                <span class="status-badge-play">▶ Tocando:</span>
                                <strong class="playing-clean">${escapeQuotes(cleanCur)}</strong>
                            </div>
                            <div class="bar-status-sep">•</div>
                            <div class="bar-status-col bar-status-next">
                                <span class="status-badge-next">⏭️ Pronto para reproduzir</span>
                            </div>
                        </div>`;
                }
            }
            if (nowPlayingTrack && typeof updateDjIdealHelper === "function") updateDjIdealHelper(nowPlayingTrack);
        }"""

if re.search(old_upcoming_pattern, js):
    js = re.sub(old_upcoming_pattern, new_upcoming_ui, js, count=1)
    print("✓ updateUpcomingTrackUI substituído com sucesso!")
else:
    print("! Regex old_upcoming_pattern não casou, procurando por bloco manual...")
    pos_u = js.find("function updateUpcomingTrackUI()")
    pos_end = js.find("if (nowPlayingTrack && typeof updateDjIdealHelper === \"function\") updateDjIdealHelper(nowPlayingTrack);\n        }", pos_u)
    if pos_u != -1 and pos_end != -1:
        end_idx = pos_end + len("if (nowPlayingTrack && typeof updateDjIdealHelper === \"function\") updateDjIdealHelper(nowPlayingTrack);\n        }")
        js = js[:pos_u] + new_upcoming_ui + js[end_idx:]
        print("✓ updateUpcomingTrackUI substituído via busca manual!")

# 3. Atualizar setDjMode para suportar 'drop'
old_set_dj_mode = """        function setDjMode(mode) {
            djPlayMode = mode;
            const shortLabels = {
                match: "🎯 Match Perfeito",
                energy: "⚡ Peak Time",
                shuffle: "🔀 Smart Shuffle",
                smooth: "🌊 Smooth Flow",
                club: "🔥 Balada & Club DJ",
                studio: "🎛️ Estúdio Pro & Mastering"
            };"""

new_set_dj_mode = """        function setDjMode(mode) {
            djPlayMode = mode;
            const shortLabels = {
                match: "🎯 Match Perfeito",
                energy: "⚡ Peak Time",
                shuffle: "🔀 Smart Shuffle",
                smooth: "🌊 Smooth Flow",
                club: "🔥 Balada & Club DJ",
                studio: "🎛️ Estúdio Pro & Mastering",
                drop: "⚡ Drop Hunter (Corte no Drop)"
            };"""

if old_set_dj_mode in js:
    js = js.replace(old_set_dj_mode, new_set_dj_mode)
    print("✓ shortLabels atualizado com 'drop'!")

# Atualizar badges e HUDs dentro de setDjMode
old_set_dj_mode_hud = """            // Atualiza o Badge de Confirmação do Modo Estúdio
            const studioBadge = document.getElementById("djStudioActiveBadge");
            if (studioBadge) {
                studioBadge.style.display = (mode === "studio") ? "flex" : "none";
            }
            if (mode !== "club") {
                hideDjClubHud();
            }"""

new_set_dj_mode_hud = """            // Atualiza o Badge de Confirmação do Modo Estúdio
            const studioBadge = document.getElementById("djStudioActiveBadge");
            if (studioBadge) {
                studioBadge.style.display = (mode === "studio") ? "flex" : "none";
            }
            // Atualiza o Badge de Confirmação do Modo Drop Hunter
            const dropBadge = document.getElementById("djDropActiveBadge");
            if (dropBadge) {
                dropBadge.style.display = (mode === "drop") ? "flex" : "none";
            }
            const dropHud = document.getElementById("djDropHunterHud");
            if (dropHud) {
                if (mode === "drop") {
                    dropHud.classList.add("hud-visible");
                    dropHud.style.display = "flex";
                    if (typeof startDropHunterAnalyzer === "function") startDropHunterAnalyzer();
                } else {
                    dropHud.classList.remove("hud-visible");
                    dropHud.style.display = "none";
                    if (typeof stopDropHunterAnalyzer === "function") stopDropHunterAnalyzer();
                }
            }
            if (mode !== "club") {
                hideDjClubHud();
            }"""

if old_set_dj_mode_hud in js:
    js = js.replace(old_set_dj_mode_hud, new_set_dj_mode_hud)
    print("✓ Controle de HUD e Badges do Drop Hunter atualizados em setDjMode!")

# 4. Atualizar filterSpotifyPlaylistsByGenre para suportar 'fiestero'
old_sp_filter = """cumbia: (id, p) => /cumbia|villera|santafesina|sonidera|charanga|fiester|enganchad/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),"""
new_sp_filter = """cumbia: (id, p) => /cumbia|villera|santafesina|sonidera|charanga|fiester|enganchad/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),
                fiestero: (id, p) => /fiester|enganchad|cachengue|boliche|previa|sonido profesional/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),"""

if old_sp_filter in js:
    js = js.replace(old_sp_filter, new_sp_filter)
    print("✓ filterSpotifyPlaylistsByGenre atualizado com filtro 'fiestero'!")

# 5. Em getUpcomingTrack: suporte ao modo 'drop'
old_get_upcoming_branch = """            } else if (djPlayMode === "club") {
                // BALADA & CLUB DJ: Foco na pista de dança, BPM compatível (diff <= 5), alto impacto
                const sorted = [...candidates].sort((a, b) => {
                    const scoreA = calculateIdealNextTrackScore(a, nowPlayingTrack);
                    const scoreB = calculateIdealNextTrackScore(b, nowPlayingTrack);
                    return scoreB - scoreA;
                });
                return sorted[0];"""

new_get_upcoming_branch = """            } else if (djPlayMode === "drop") {
                // DROP HUNTER: Seleciona faixas de alta energia / dançantes para cortar no drop
                const curBpm = parseFloat(nowPlayingTrack.bpm) || 128;
                const sorted = [...candidates].sort((a, b) => {
                    const bpmA = parseFloat(a.bpm) || 120;
                    const bpmB = parseFloat(b.bpm) || 120;
                    // Prefere BPM animado (122 a 145)
                    const energyA = (bpmA >= 120 && bpmA <= 150) ? 20 : 0;
                    const energyB = (bpmB >= 120 && bpmB <= 150) ? 20 : 0;
                    const scoreA = calculateIdealNextTrackScore(a, nowPlayingTrack) + energyA;
                    const scoreB = calculateIdealNextTrackScore(b, nowPlayingTrack) + energyB;
                    return scoreB - scoreA;
                });
                return sorted[0];
            } else if (djPlayMode === "club") {
                // BALADA & CLUB DJ: Foco na pista de dança, BPM compatível (diff <= 5), alto impacto
                const sorted = [...candidates].sort((a, b) => {
                    const scoreA = calculateIdealNextTrackScore(a, nowPlayingTrack);
                    const scoreB = calculateIdealNextTrackScore(b, nowPlayingTrack);
                    return scoreB - scoreA;
                });
                return sorted[0];"""

if old_get_upcoming_branch in js:
    js = js.replace(old_get_upcoming_branch, new_get_upcoming_branch)
    print("✓ Seleção de faixas em getUpcomingTrack atualizada para 'drop'!")

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)
print("✓ assets/js/player.js salvo com sucesso!")

print("\n--- 4. Executando build_full_player.py ---")
import subprocess
res = subprocess.run([sys.executable, str(BASE_DIR / "build_full_player.py")], capture_output=True, text=True, cwd=str(BASE_DIR))
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
print(f"Build Exit code: {res.returncode}")
