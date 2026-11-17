# -*- coding: utf-8 -*-
"""
update_hud_layout.py
Ajusta player_template.html e assets/css/player.css para o layout de 2 itens por linha,
garantindo que o status pill e o título nunca quebrem ou se espremam no container do visualizador (~320-360px).
"""

from pathlib import Path
import re

BASE_DIR = Path(r"C:\Users\Mbello\Desktop\ig-to-youtube-playlist\.claude\worktrees\instagram-youtube-playlist")
TEMPLATE_PATH = BASE_DIR / "player_template.html"
CSS_PATH = BASE_DIR / "assets" / "css" / "player.css"

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

new_hud_html = """<!-- HUD DE ANÁLISE DE ONDA & CORTE INTELIGENTE NO DROP (MODO DROP HUNTER) -->
                        <div id="djDropHunterHud" class="dj-drop-hunter-hud" style="display: none;">
                            <div class="dj-drop-glass-panel">
                                <!-- Linha 1: Título e Status Pill (Apenas 2 elementos, nunca quebra em 4 linhas) -->
                                <div class="drop-hud-top-bar">
                                    <div class="drop-hud-title-wrap">
                                        <span class="hud-strobe-dot drop-dot"></span>
                                        <span class="drop-hud-title">⚡ DROP HUNTER</span>
                                    </div>
                                    <div class="drop-hud-status-wrap">
                                        <span id="dropStatusPill" class="drop-status-pill analyzing">🔍 Analisando...</span>
                                    </div>
                                </div>

                                <!-- Linha 2: Botões de Ação de DJ bem distribuídos -->
                                <div class="drop-hud-actions-row">
                                    <button class="btn-drop-action" id="btnSkipToDrop" onclick="smartSkipToDrop()" title="Pular introdução lenta e ir direto para o Drop da música atual">⚡ Pular pro Drop</button>
                                    <button class="btn-drop-action cut-next" id="btnCutToNextDrop" onclick="smartCutToNextDrop()" title="Corte Inteligente: corta agora para o Drop da próxima música">✂️ Cortar no Drop</button>
                                    <button class="btn-drop-action auto-toggle active" id="btnAutoDropToggle" onclick="toggleAutoDropMode()" title="Ativar/Desativar modo automático">🤖 Auto: ON</button>
                                </div>

                                <!-- Botão Especial para Mixes Longos (Aparece apenas quando mix > 5 min) -->
                                <button class="btn-drop-action mix-jump" id="btnMixJump" onclick="smartMixSegmentJump()" style="display: none; width: 100%; justify-content: center;" title="Pular para o próximo refrão dentro deste mix longo">🔀 Próximo Refrão do Mix (+75s)</button>

                                <!-- Linha 3: Medidores com Tipografia Clara e Legível -->
                                <div class="drop-meters-container">
                                    <div class="drop-meter-row">
                                        <div class="drop-meter-label-wrap">
                                            <span class="drop-freq-name"><span class="drop-freq-dot">●</span> ENERGIA ACÚSTICA (GRAVES)</span>
                                            <span id="dropEnergyVal" class="drop-meter-val">0%</span>
                                        </div>
                                        <div class="drop-meter-track">
                                            <div id="dropEnergyFill" class="drop-meter-fill" style="width: 0%;"></div>
                                            <div class="drop-threshold-line" style="left: 60%;" title="Limiar de Drop (60%)"></div>
                                        </div>
                                    </div>

                                    <div class="drop-meter-row">
                                        <div class="drop-meter-label-wrap">
                                            <span class="drop-freq-name"><span class="drop-freq-dot timer-dot">●</span> JANELA DINÂMICA (VARIÁVEL)</span>
                                            <span id="dropTimerVal" class="drop-meter-val">00:00 / 00:45s</span>
                                        </div>
                                        <div class="drop-meter-track">
                                            <div id="dropTimerFill" class="drop-meter-fill timer-fill" style="width: 0%;"></div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Linha 4: Dica e Status de Mix Longo -->
                                <div class="drop-hud-footer">
                                    <span id="dropHudFooterText">💡 <strong>Auto Drop DJ:</strong> Pula a intro sozinho, toca o drop no ápice e já salta para a próxima direto no drop!</span>
                                </div>
                            </div>
                        </div>"""

old_hud_pattern = r'<!-- HUD DE ANÁLISE DE ONDA & CORTE INTELIGENTE NO DROP[\s\S]*?</div>\s*</div>\s*</div>'
template = re.sub(old_hud_pattern, new_hud_html, template, count=1)

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(template)
print("✓ player_template.html atualizado!")

with open(CSS_PATH, "r", encoding="utf-8") as f:
    css = f.read()

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
    padding: 4px 6px !important;
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
    width: 100% !important;
    max-width: 100% !important;
    background: rgba(10, 13, 26, 0.97) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(255, 170, 0, 0.6) !important;
    border-radius: 10px !important;
    padding: 8px 10px !important;
    box-shadow: 0 8px 26px rgba(0, 0, 0, 0.95), 0 0 20px rgba(255, 170, 0, 0.25) !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    box-sizing: border-box !important;
}

.drop-hud-top-bar {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 8px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding-bottom: 5px !important;
    width: 100% !important;
}

.drop-hud-title-wrap {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
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
    font-size: 10px !important;
    font-weight: 800 !important;
    padding: 3px 8px !important;
    border-radius: 5px !important;
    text-transform: uppercase !important;
    white-space: nowrap !important;
    letter-spacing: 0.3px !important;
    display: inline-block !important;
    line-height: 1.2 !important;
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
    background: linear-gradient(135deg, rgba(255, 0, 85, 0.7), rgba(255, 85, 0, 0.7)) !important;
    color: #fff !important;
    border: 1px solid #ff0055 !important;
    box-shadow: 0 0 12px #ff0055 !important;
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
    gap: 6px !important;
    width: 100% !important;
}

.btn-drop-action {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 170, 0, 0.5) !important;
    color: #ffaa00 !important;
    font-size: 10.5px !important;
    font-weight: 700 !important;
    padding: 5px 8px !important;
    border-radius: 5px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 4px !important;
    flex: 1 1 0 !important;
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
    flex: none !important;
}

.btn-drop-action.mix-jump:hover {
    background: rgba(192, 132, 252, 0.3) !important;
    border-color: #c084fc !important;
    color: #fff !important;
}

.btn-drop-action.auto-toggle {
    border-color: rgba(0, 242, 254, 0.6) !important;
    color: #00f2fe !important;
    flex: 0 0 auto !important;
    padding: 5px 7px !important;
}

.btn-drop-action.auto-toggle.active {
    background: rgba(0, 242, 254, 0.2) !important;
    border-color: #00f2fe !important;
    box-shadow: 0 0 10px rgba(0, 242, 254, 0.3) !important;
}

.drop-meters-container {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    width: 100% !important;
}

.drop-meter-row {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
    width: 100% !important;
}

.drop-meter-label-wrap {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    font-size: 10px !important;
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
    font-size: 9px !important;
}

.drop-freq-dot.timer-dot {
    color: #00e676 !important;
}

.drop-meter-val {
    color: #ffaa00 !important;
    font-family: monospace !important;
    font-weight: 800 !important;
    font-size: 12.5px !important;
}

.drop-meter-track {
    position: relative !important;
    width: 100% !important;
    height: 7px !important;
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
    font-size: 9.5px !important;
    color: #cbd5e1 !important;
    line-height: 1.3 !important;
    border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding-top: 4px !important;
}"""

old_css_hud_pattern = r'/\* =+ *\r?\n *DROP HUNTER & HIGH ENERGY[\s\S]*?padding-top: 5px !important;\s*\}'
css = re.sub(old_css_hud_pattern, new_css_hud, css, count=1)

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)
print("✓ assets/css/player.css atualizado!")
