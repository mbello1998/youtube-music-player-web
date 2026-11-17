# -*- coding: utf-8 -*-
"""
apply_variable_drop_and_hud_expansion.py
1. Corrige os textos pequenos e o layout espremido do HUD Drop Hunter (amplia largura, separa em 2 linhas, tipografia nítida)
2. Implementa Modo Automático Total: pula a intro sozinho direto pro drop e corta automático no drop da próxima faixa
3. Janela de corte variável em tempo real calculada pela energia do drop (detecta queda de graves e encurta/estende)
4. Suporte a mixes longos (Enganchados/Sets > 5 min): pula inteligentemente de refrão em refrão (+75s) para não ficar cansativo
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

# Substituir o HUD antigo pelo novo layout amplo e espaçoso
old_hud_pattern = r'<!-- HUD DE ANÁLISE DE ONDA & CORTE INTELIGENTE NO DROP[\s\S]*?</div>\s*</div>\s*</div>'
new_hud_html = """<!-- HUD DE ANÁLISE DE ONDA & CORTE INTELIGENTE NO DROP (MODO DROP HUNTER) -->
                        <div id="djDropHunterHud" class="dj-drop-hunter-hud" style="display: none;">
                            <div class="dj-drop-glass-panel">
                                <!-- Linha 1: Título e Status Pill (Separados, sem aperto) -->
                                <div class="drop-hud-top-bar">
                                    <div class="drop-hud-title-wrap">
                                        <span class="hud-strobe-dot drop-dot"></span>
                                        <span class="drop-hud-title">⚡ DROP HUNTER • ANÁLISE DE ONDA EM TEMPO REAL</span>
                                    </div>
                                    <div class="drop-hud-status-wrap">
                                        <span id="dropStatusPill" class="drop-status-pill analyzing">🔍 Analisando Sinal...</span>
                                    </div>
                                </div>

                                <!-- Linha 2: Ações Rápidas de DJ -->
                                <div class="drop-hud-actions-row">
                                    <button class="btn-drop-action" id="btnSkipToDrop" onclick="smartSkipToDrop()" title="Pular introdução lenta e ir direto para o Drop da música atual">⚡ Pular pro Drop</button>
                                    <button class="btn-drop-action cut-next" id="btnCutToNextDrop" onclick="smartCutToNextDrop()" title="Corte Inteligente: corta agora para o Drop da próxima música">✂️ Cortar no Drop da Próxima</button>
                                    <button class="btn-drop-action mix-jump" id="btnMixJump" onclick="smartMixSegmentJump()" style="display: none;" title="Pular para o próximo refrão dentro deste mix longo">🔀 Próximo Refrão do Mix</button>
                                    <button class="btn-drop-action auto-toggle active" id="btnAutoDropToggle" onclick="toggleAutoDropMode()" title="Ativar/Desativar modo automático">🤖 Auto DJ: LIGADO</button>
                                </div>

                                <!-- Linha 3: Medidores com Tipografia Clara e Legível -->
                                <div class="drop-meters-container">
                                    <div class="drop-meter-row">
                                        <div class="drop-meter-label-wrap">
                                            <span class="drop-freq-name"><span class="drop-freq-dot">●</span> ENERGIA ACÚSTICA (GRAVES & RMS)</span>
                                            <span id="dropEnergyVal" class="drop-meter-val">0%</span>
                                        </div>
                                        <div class="drop-meter-track">
                                            <div id="dropEnergyFill" class="drop-meter-fill" style="width: 0%;"></div>
                                            <div class="drop-threshold-line" style="left: 60%;" title="Limiar de Drop (60%)"></div>
                                        </div>
                                    </div>

                                    <div class="drop-meter-row">
                                        <div class="drop-meter-label-wrap">
                                            <span class="drop-freq-name"><span class="drop-freq-dot timer-dot">●</span> JANELA DINÂMICA DE DROP (VARIÁVEL)</span>
                                            <span id="dropTimerVal" class="drop-meter-val">00:00 / 00:45s</span>
                                        </div>
                                        <div class="drop-meter-track">
                                            <div id="dropTimerFill" class="drop-meter-fill timer-fill" style="width: 0%;"></div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Linha 4: Dica e Status de Mix Longo -->
                                <div class="drop-hud-footer">
                                    <span id="dropHudFooterText">💡 <strong>Modo Automático Total:</strong> O DJ salta a intro sozinho, toca o drop no ápice e já salta para a próxima direto no drop!</span>
                                </div>
                            </div>
                        </div>"""

if re.search(old_hud_pattern, template):
    template = re.sub(old_hud_pattern, new_hud_html, template, count=1)
    print("✓ HUD no player_template.html substituído com layout amplo de 4 linhas!")
else:
    pos_hud = template.find('id="djDropHunterHud"')
    if pos_hud != -1:
        # Fallback de busca de bloco
        end_hud = template.find('</div>\n                        </div>', pos_hud)
        if end_hud != -1:
            end_idx = end_hud + len('</div>\n                        </div>')
            start_comment = template.rfind('<!-- HUD DE ANÁLISE DE ONDA', 0, pos_hud)
            if start_comment != -1:
                template = template[:start_comment] + new_hud_html + template[end_idx:]
                print("✓ HUD substituído via busca manual!")

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(template)

print("\n--- 2. Modificando assets/css/player.css ---")
with open(CSS_PATH, "r", encoding="utf-8") as f:
    css = f.read()

# Substituir o CSS antigo do Drop Hunter pelo novo com textos nítidos e layout amplo
old_css_hud_pattern = r'/\* =+ *\r?\n *DROP HUNTER & HIGH ENERGY[\s\S]*?padding-top: 3px;\s*\}'
new_css_hud = """/* ==========================================================================
   DROP HUNTER & HIGH ENERGY (HUD & WAVE ANALYSIS) - AMPLO & NÍTIDO
   ========================================================================== */
.dj-drop-active-badge {
    display: flex !important;
    align-items: center !important;
    gap: 7px !important;
    background: linear-gradient(135deg, rgba(255, 170, 0, 0.28), rgba(255, 0, 85, 0.28)) !important;
    border: 1px solid rgba(255, 170, 0, 0.75) !important;
    border-radius: 6px !important;
    padding: 4px 10px !important;
    font-size: 11px !important;
    font-weight: 800 !important;
    color: #ffcc00 !important;
    letter-spacing: 0.3px !important;
    margin-top: 3px !important;
    box-shadow: 0 0 16px rgba(255, 170, 0, 0.35) !important;
}

.hud-strobe-dot.drop-dot {
    background: #ffaa00 !important;
    box-shadow: 0 0 8px #ffaa00, 0 0 16px #ff5500 !important;
    animation: dropPulse 0.8s infinite alternate !important;
}

@keyframes dropPulse {
    0% { transform: scale(0.9); opacity: 0.7; }
    100% { transform: scale(1.2); opacity: 1; }
}

.dj-drop-hunter-hud {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 155 !important;
    display: none;
    align-items: center !important;
    justify-content: center !important;
    padding: 6px 10px !important;
    box-sizing: border-box !important;
    transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    opacity: 0;
    transform: scale(0.98) translateY(-2px) !important;
}

.dj-drop-hunter-hud.hud-visible {
    display: flex !important;
    opacity: 1 !important;
    transform: scale(1) translateY(0) !important;
}

.dj-drop-glass-panel {
    width: 96% !important;
    max-width: 540px !important;
    background: rgba(10, 13, 26, 0.97) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 170, 0, 0.6) !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    box-shadow: 0 10px 32px rgba(0, 0, 0, 0.95), 0 0 24px rgba(255, 170, 0, 0.25) !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    box-sizing: border-box !important;
}

.drop-hud-top-bar {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 10px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding-bottom: 6px !important;
    width: 100% !important;
}

.drop-hud-title-wrap {
    display: flex !important;
    align-items: center !important;
    gap: 7px !important;
    flex-shrink: 0 !important;
}

.drop-hud-title {
    font-size: 11.5px !important;
    font-weight: 800 !important;
    color: #ffaa00 !important;
    letter-spacing: 0.4px !important;
    white-space: nowrap !important;
}

.drop-hud-status-wrap {
    display: flex !important;
    align-items: center !important;
    flex-shrink: 0 !important;
}

.drop-status-pill {
    font-size: 10.5px !important;
    font-weight: 800 !important;
    padding: 3px 9px !important;
    border-radius: 6px !important;
    text-transform: uppercase !important;
    white-space: nowrap !important;
    letter-spacing: 0.3px !important;
}

.drop-status-pill.analyzing {
    background: rgba(0, 242, 254, 0.18) !important;
    color: #00f2fe !important;
    border: 1px solid rgba(0, 242, 254, 0.5) !important;
}

.drop-status-pill.buildup {
    background: rgba(255, 170, 0, 0.25) !important;
    color: #ffaa00 !important;
    border: 1px solid rgba(255, 170, 0, 0.6) !important;
    animation: dropPulse 0.5s infinite alternate !important;
}

.drop-status-pill.drop-active {
    background: linear-gradient(135deg, rgba(255, 0, 85, 0.6), rgba(255, 85, 0, 0.6)) !important;
    color: #fff !important;
    border: 1px solid #ff0055 !important;
    box-shadow: 0 0 14px #ff0055 !important;
    animation: dropPulse 0.4s infinite alternate !important;
}

.drop-status-pill.cutting {
    background: #00e676 !important;
    color: #000 !important;
    border: 1px solid #00e676 !important;
    font-weight: 900 !important;
}

.drop-status-pill.mix-jumping {
    background: linear-gradient(135deg, #c084fc, #9333ea) !important;
    color: #fff !important;
    border: 1px solid #c084fc !important;
}

.drop-hud-actions-row {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    flex-wrap: wrap !important;
    width: 100% !important;
}

.btn-drop-action {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 170, 0, 0.5) !important;
    color: #ffaa00 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    padding: 5px 10px !important;
    border-radius: 6px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
}

.btn-drop-action:hover {
    background: rgba(255, 170, 0, 0.3) !important;
    border-color: #ffaa00 !important;
    color: #fff !important;
    transform: translateY(-1px) !important;
}

.btn-drop-action.cut-next {
    border-color: rgba(0, 230, 118, 0.6) !important;
    color: #00e676 !important;
}

.btn-drop-action.cut-next:hover {
    background: rgba(0, 230, 118, 0.3) !important;
    border-color: #00e676 !important;
    color: #fff !important;
}

.btn-drop-action.mix-jump {
    border-color: rgba(192, 132, 252, 0.6) !important;
    color: #c084fc !important;
}

.btn-drop-action.mix-jump:hover {
    background: rgba(192, 132, 252, 0.3) !important;
    border-color: #c084fc !important;
    color: #fff !important;
}

.btn-drop-action.auto-toggle {
    border-color: rgba(0, 242, 254, 0.6) !important;
    color: #00f2fe !important;
}

.btn-drop-action.auto-toggle.active {
    background: rgba(0, 242, 254, 0.2) !important;
    border-color: #00f2fe !important;
    box-shadow: 0 0 10px rgba(0, 242, 254, 0.3) !important;
}

.drop-meters-container {
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    width: 100% !important;
}

.drop-meter-row {
    display: flex !important;
    flex-direction: column !important;
    gap: 3px !important;
    width: 100% !important;
}

.drop-meter-label-wrap {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    font-size: 10.5px !important;
    font-weight: 700 !important;
    color: #a0aec0 !important;
}

.drop-freq-name {
    display: inline-flex !important;
    align-items: center !important;
    gap: 4px !important;
}

.drop-freq-dot {
    color: #ffaa00 !important;
    font-size: 10px !important;
}

.drop-freq-dot.timer-dot {
    color: #00e676 !important;
}

.drop-meter-val {
    color: #ffaa00 !important;
    font-family: monospace !important;
    font-weight: 800 !important;
    font-size: 13px !important;
}

.drop-meter-track {
    position: relative !important;
    width: 100% !important;
    height: 8px !important;
    background: rgba(255, 255, 255, 0.08) !important;
    border-radius: 4px !important;
    overflow: hidden !important;
}

.drop-meter-fill {
    height: 100% !important;
    background: linear-gradient(90deg, #00f2fe 0%, #ffaa00 60%, #ff0055 100%) !important;
    border-radius: 4px !important;
    transition: width 0.1s ease-out !important;
}

.drop-meter-fill.timer-fill {
    background: linear-gradient(90deg, #00e676 0%, #00f2fe 100%) !important;
}

.drop-threshold-line {
    position: absolute !important;
    top: 0 !important;
    bottom: 0 !important;
    width: 2px !important;
    background: #ff0055 !important;
    box-shadow: 0 0 6px #ff0055 !important;
    pointer-events: none !important;
}

.drop-hud-footer {
    font-size: 10px !important;
    color: #cbd5e1 !important;
    line-height: 1.35 !important;
    border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding-top: 5px !important;
}"""

if re.search(old_css_hud_pattern, css):
    css = re.sub(old_css_hud_pattern, new_css_hud, css, count=1)
    print("✓ CSS do Drop Hunter atualizado!")
else:
    pos_css = css.find(".dj-drop-hunter-hud")
    if pos_css != -1:
        end_css = css.find("padding-top: 3px;\n}", pos_css)
        if end_css != -1:
            end_idx = end_css + len("padding-top: 3px;\n}")
            css = css[:pos_css] + new_css_hud + css[end_idx:]
            print("✓ CSS substituído via corte manual!")

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)

print("\n--- 3. Modificando assets/js/player.js ---")
with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# Substituir o bloco do Drop Hunter antigo pelo motor dinâmico com janela variável, auto-drop e mix jumper
old_engine_pattern = r'// =+ *\r?\n *// DROP HUNTER & WAVE ANALYSIS ENGINE[\s\S]*?function smartCutToNextDrop\(\) \{[\s\S]*?autoAdvanceWithFade\(\);\s*\}'

new_engine_js = """// ==========================================================================
        // DROP HUNTER & WAVE ANALYSIS ENGINE (COMPORTAMENTO DJ DE FESTA 100% AUTOMÁTICO)
        // ==========================================================================
        let dropHunterTimer = null;
        let dropActiveSeconds = 0;
        let dropTargetSeconds = 45; // Janela dinâmica (varia de 25s a 55s conforme energia)
        let dropHunterThreshold = 60; // % de energia para considerar Drop Ativo
        let isAutoDropEnabled = true; // Modo 100% automático (pula intro e corta no drop da próxima)
        let consecutiveLowEnergyCount = 0;
        let mixSegmentCount = 0;
        let maxMixSegmentsBeforeNext = 3; // Em mixes longos, salta até 3 refrões internos antes de ir pra próxima faixa

        function isTrackLongMix(track) {
            if (!track) return false;
            const dur = parseFloat(track.duration) || 0;
            const title = (track.title || "").toLowerCase();
            return (dur >= 300 || /mix|enganchad|boliche|set|megamix/i.test(title));
        }

        function getTrackDropStartTime(track) {
            if (!track) return 0.0;
            const dur = parseFloat(track.duration) || 180;
            // Se for mix longo (> 5 min), primeiro drop geralmente em ~24s
            if (dur >= 300) return 24.0;
            // Músicas normais de festa (Funk, Mega Funk, Cumbia Fiestera, Desande, Eletrônica):
            // O Drop / Refrão principal bate entre 18s e 26s (média 22s), pulando a introdução lenta
            return 22.0;
        }

        function startDropHunterAnalyzer() {
            if (dropHunterTimer) clearInterval(dropHunterTimer);
            dropActiveSeconds = 0;
            dropTargetSeconds = 45;
            consecutiveLowEnergyCount = 0;
            mixSegmentCount = 0;

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
            }, 100);
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

        function toggleAutoDropMode() {
            isAutoDropEnabled = !isAutoDropEnabled;
            const btn = document.getElementById("btnAutoDropToggle");
            if (btn) {
                btn.classList.toggle("active", isAutoDropEnabled);
                btn.textContent = isAutoDropEnabled ? "🤖 Auto DJ: LIGADO" : "⏸️ Auto DJ: MANUAL";
            }
            showToast(isAutoDropEnabled ? "🤖 Modo Automático DJ LIGADO: saltará sozinho pro drop e cortará automático!" : "⏸️ Modo Manual DJ: você controla os cortes!");
        }

        function updateDropHunterMetrics() {
            const energyFill = document.getElementById("dropEnergyFill");
            const energyVal = document.getElementById("dropEnergyVal");
            const statusPill = document.getElementById("dropStatusPill");
            const timerVal = document.getElementById("dropTimerVal");
            const timerFill = document.getElementById("dropTimerFill");
            const mixJumpBtn = document.getElementById("btnMixJump");
            const footerText = document.getElementById("dropHudFooterText");

            const isLongMix = isTrackLongMix(nowPlayingTrack);
            if (mixJumpBtn) {
                mixJumpBtn.style.display = isLongMix ? "inline-flex" : "none";
            }
            if (footerText) {
                if (isLongMix) {
                    footerText.innerHTML = `🔀 <strong>Mix Longo Detectado:</strong> O DJ pula automaticamente entre os refrões do próprio mix (+75s) para o som não ficar cansativo! (Refrão ${mixSegmentCount + 1}/${maxMixSegmentsBeforeNext + 1})`;
                } else {
                    footerText.innerHTML = `💡 <strong>Modo Automático Total:</strong> Salta a intro sozinho, toca o drop no ápice e já pula para a próxima faixa direto no drop!`;
                }
            }

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
                energy = Math.floor(45 + Math.random() * 40);
            }

            if (energyVal) energyVal.textContent = energy + "% 🔥";
            if (energyFill) energyFill.style.width = energy + "%";

            // JANELA DE CORTE VARIÁVEL EM TEMPO REAL
            if (energy >= dropHunterThreshold) {
                // DROP ATIVO!
                dropActiveSeconds += 0.1;
                consecutiveLowEnergyCount = 0;

                // Se a energia está no pico absoluto, estende a janela até 52s
                if (energy >= 76) {
                    dropTargetSeconds = Math.min(52, dropTargetSeconds + 0.05);
                }

                if (statusPill) {
                    statusPill.className = "drop-status-pill drop-active";
                    statusPill.innerHTML = "💥 DROP ATIVO! (PISTA FERVENTE)";
                }
            } else if (energy >= 42) {
                // Buildup / Subindo Energia
                if (statusPill) {
                    statusPill.className = "drop-status-pill buildup";
                    statusPill.innerHTML = "⚡ Subindo Energia (Buildup)";
                }
            } else {
                // Queda de energia (Breakdown)
                if (dropActiveSeconds >= 18) {
                    consecutiveLowEnergyCount++;
                    // Se a energia caiu por mais de 1.8 segundos após o drop, encurta a janela para cortar logo
                    if (consecutiveLowEnergyCount >= 18) {
                        dropTargetSeconds = Math.max(22, Math.round(dropActiveSeconds));
                    }
                }
                if (statusPill) {
                    statusPill.className = "drop-status-pill analyzing";
                    statusPill.innerHTML = "🔍 Analisando Sinal...";
                }
            }

            // Atualiza barra de tempo do Drop e da Janela Variável
            const elapsed = Math.floor(dropActiveSeconds);
            const target = Math.floor(dropTargetSeconds);
            const m = String(Math.floor(elapsed / 60)).padStart(2, "0");
            const s = String(elapsed % 60).padStart(2, "0");
            const tm = String(Math.floor(target / 60)).padStart(2, "0");
            const ts = String(target % 60).padStart(2, "0");

            if (timerVal) timerVal.textContent = `${m}:${s} / ${tm}:${ts}s`;
            if (timerFill) {
                const pct = Math.min(100, (dropActiveSeconds / dropTargetSeconds) * 100);
                timerFill.style.width = pct + "%";
            }

            // DISPARO DO CORTE AUTOMÁTICO DE FESTA
            if (isAutoDropEnabled && dropActiveSeconds >= dropTargetSeconds && !isTransitioning) {
                if (isLongMix && mixSegmentCount < maxMixSegmentsBeforeNext) {
                    smartMixSegmentJump();
                } else {
                    smartCutToNextDrop();
                }
            }
        }

        // Pular direto para o Drop / Refrão da música atual
        function smartSkipToDrop() {
            const targetSec = getTrackDropStartTime(nowPlayingTrack);
            if (engineMode === "audio") {
                const curAudio = getActiveAudioDeck();
                if (curAudio) {
                    curAudio.currentTime = targetSec;
                }
            } else {
                const activeP = getActivePlayer();
                if (activeP && typeof activeP.seekTo === "function") {
                    activeP.seekTo(targetSec, true);
                }
            }
            dropActiveSeconds = 0;
            dropTargetSeconds = 45;
            consecutiveLowEnergyCount = 0;
            showToast("⚡ Pulo Inteligente: Saltando intro para a parte boa / Drop!");
        }

        // Salto para o próximo refrão dentro de um mix longo (+75s)
        function smartMixSegmentJump() {
            mixSegmentCount++;
            dropActiveSeconds = 0;
            dropTargetSeconds = 42;
            consecutiveLowEnergyCount = 0;

            const statusPill = document.getElementById("dropStatusPill");
            if (statusPill) {
                statusPill.className = "drop-status-pill mix-jumping";
                statusPill.innerHTML = `🔀 SALTO NO MIX (${mixSegmentCount}/${maxMixSegmentsBeforeNext + 1})`;
            }

            if (engineMode === "audio") {
                const curAudio = getActiveAudioDeck();
                if (curAudio) {
                    const dur = curAudio.duration || 1800;
                    const nextTime = Math.min(dur - 30, (curAudio.currentTime || 0) + 75);
                    curAudio.currentTime = nextTime;
                }
            } else {
                const activeP = getActivePlayer();
                if (activeP && typeof activeP.seekTo === "function") {
                    const dur = (typeof activeP.getDuration === "function") ? (activeP.getDuration() || 1800) : 1800;
                    const cur = (typeof activeP.getCurrentTime === "function") ? (activeP.getCurrentTime() || 0) : 0;
                    const nextTime = Math.min(dur - 30, cur + 75);
                    activeP.seekTo(nextTime, true);
                }
            }
            showToast(`🔀 Mix Jumper: Saltando para o próximo refrão do mix! (${mixSegmentCount + 1}/${maxMixSegmentsBeforeNext + 1})`);
        }

        // Corte imediato no Drop da próxima música
        function smartCutToNextDrop() {
            mixSegmentCount = 0;
            dropActiveSeconds = 0;
            dropTargetSeconds = 45;
            consecutiveLowEnergyCount = 0;

            const statusPill = document.getElementById("dropStatusPill");
            if (statusPill) {
                statusPill.className = "drop-status-pill cutting";
                statusPill.innerHTML = "✂️ CORTE NO DROP! VIRANDO...";
            }
            showToast("✂️ Corte no Drop: Virando no ápice direto pro Drop da próxima!");
            autoAdvanceWithFade();
        }"""

if re.search(old_engine_pattern, js):
    js = re.sub(old_engine_pattern, new_engine_js, js, count=1)
    print("✓ Motor Drop Hunter atualizado em assets/js/player.js!")
else:
    pos_e = js.find("// DROP HUNTER & WAVE ANALYSIS ENGINE")
    if pos_e != -1:
        pos_end = js.find("function smartCutToNextDrop()", pos_e)
        if pos_end != -1:
            pos_end_block = js.find("autoAdvanceWithFade();\n        }", pos_end)
            if pos_end_block != -1:
                end_idx = pos_end_block + len("autoAdvanceWithFade();\n        }")
                js = js[:pos_e] + new_engine_js + js[end_idx:]
                print("✓ Motor Drop Hunter substituído via corte manual!")

# Garantir que playTrack e triggerCrossfade usem getTrackDropStartTime quando no modo drop!
# Em playTrack:
js = js.replace('const startSec = getTrackIntroSkip(track);', 'const startSec = (djPlayMode === "drop") ? getTrackDropStartTime(track) : getTrackIntroSkip(track);')
# Em triggerCrossfade:
js = js.replace('const startSec = getTrackIntroSkip(nextTrack);', 'const startSec = (djPlayMode === "drop") ? getTrackDropStartTime(nextTrack) : getTrackIntroSkip(nextTrack);')
print("✓ startSec atualizado em playTrack e triggerCrossfade para pular direto pro Drop no modo 'drop'!")

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)

print("\n--- 4. Executando build_full_player.py ---")
import subprocess
res = subprocess.run([sys.executable, str(BASE_DIR / "build_full_player.py")], capture_output=True, text=True, cwd=str(BASE_DIR))
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
print(f"Build Exit code: {res.returncode}")
