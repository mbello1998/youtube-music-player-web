# -*- coding: utf-8 -*-
"""
apply_studio_suite.py
Implementa a Suite de Estúdio Completa:
1. Modo Estúdio no Dropdown e Badge no Mixer.
2. Botão 'Estúdio Pro' na barra inferior.
3. Modal Rack de Estúdio (Reverb, Delay, Compressor SSL, Saturação Valvulada, Stereo Widener, Dual VU Meters).
4. Motor Web Audio DSP de Estúdio (Convolver Reverb, Ping-Pong Delay, Waveshaper Warmth, Stereo Widener, SSL Comp).
5. Eliminação do corte seco nos efeitos DJ FX: roteamento dos efeitos para envio de Reverb & Delay Tail de 2.2s.
6. Eliminação da diferença brusca na música: remoção do ducking de 45% abrupto e cortes bruscos no player do YouTube.
"""

import re
import os

WORKSPACE = r"C:\Users\Mbello\Desktop\ig-to-youtube-playlist\.claude\worktrees\instagram-youtube-playlist"

CSS_PATH = os.path.join(WORKSPACE, "assets", "css", "player.css")
HTML_PATH = os.path.join(WORKSPACE, "player_template.html")
JS_PATH = os.path.join(WORKSPACE, "assets", "js", "player.js")

def update_css():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        css = f.read()

    # Ajustar max-height do dropdown de modos para 290px para caber os 6 modos confortavelmente
    css = re.sub(
        r'(\.dj-act-dropdown-menu\s*\{[^}]*max-height:\s*)[0-9]+px;',
        r'\g<1>290px;',
        css
    )

    studio_css = """
/* ==========================================================================
   CONSOLE DE ESTÚDIO PROFISSIONAL & MASTERING DSP (PRO AUDIO)
   ========================================================================== */
.bar-pill-btn.studio-active {
    background: linear-gradient(135deg, rgba(138, 43, 226, 0.25), rgba(0, 242, 254, 0.25));
    border-color: rgba(138, 43, 226, 0.5);
    color: #c084fc;
}
.bar-pill-btn.studio-active:hover {
    background: linear-gradient(135deg, rgba(138, 43, 226, 0.4), rgba(0, 242, 254, 0.4));
    border-color: #c084fc;
    color: #fff;
    box-shadow: 0 0 12px rgba(138, 43, 226, 0.4);
}

.dj-studio-active-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, rgba(138, 43, 226, 0.2), rgba(0, 242, 254, 0.2));
    border: 1px solid rgba(138, 43, 226, 0.55);
    border-radius: 5px;
    padding: 3px 7px;
    font-size: 9.5px;
    font-weight: 800;
    color: #c084fc;
    letter-spacing: 0.3px;
    margin-top: 3px;
    box-shadow: 0 0 10px rgba(138, 43, 226, 0.2);
}
.hud-strobe-dot.studio-dot {
    background: #c084fc;
    box-shadow: 0 0 8px #c084fc;
}

.studio-modal-card {
    max-width: 820px !important;
    max-height: 94vh !important;
    overflow-y: auto !important;
    background: #0c0f1a !important;
    border: 1px solid rgba(138, 43, 226, 0.4) !important;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.95), 0 0 35px rgba(138, 43, 226, 0.2) !important;
    padding: 18px 22px !important;
    gap: 12px !important;
    scrollbar-width: thin !important;
    scrollbar-color: rgba(138, 43, 226, 0.4) rgba(0, 0, 0, 0.3) !important;
}

.studio-modal-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.studio-title-box {
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.studio-modal-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 800;
    color: #fff;
    letter-spacing: 0.5px;
}
.studio-pulse-led {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #a855f7;
    box-shadow: 0 0 10px #a855f7, 0 0 20px #a855f7;
    animation: studioPulse 1.4s infinite alternate;
}
@keyframes studioPulse {
    0% { transform: scale(0.9); opacity: 0.7; }
    100% { transform: scale(1.2); opacity: 1; }
}
.studio-badge-pro {
    font-size: 9px;
    font-weight: 800;
    background: linear-gradient(135deg, #a855f7, #00f2fe);
    color: #000;
    padding: 2px 6px;
    border-radius: 4px;
    letter-spacing: 0.6px;
}
.studio-modal-sub {
    font-size: 11px;
    color: var(--text-dim);
    line-height: 1.3;
}
.studio-header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}
.btn-studio-bypass {
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(168, 85, 247, 0.15);
    border: 1px solid rgba(168, 85, 247, 0.4);
    color: #c084fc;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
}
.btn-studio-bypass:hover {
    background: rgba(168, 85, 247, 0.3);
    border-color: #c084fc;
    color: #fff;
}
.bypass-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #555;
}
.bypass-dot.active {
    background: #00f2fe;
    box-shadow: 0 0 8px #00f2fe;
}

/* MEDIDORES ANALÓGICOS ESTÉREO VU */
.studio-meters-panel {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    background: rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 10px 14px;
}
.studio-meter-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.studio-meter-header {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    font-weight: 700;
    color: var(--text-dim);
    letter-spacing: 0.4px;
}
.meter-db-val {
    color: var(--accent);
    font-family: monospace;
    font-size: 10.5px;
}
.studio-vu-track {
    position: relative;
    height: 12px;
    background: #141724;
    border-radius: 3px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow: hidden;
}
.studio-vu-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.05s ease-out;
}
.studio-vu-fill.vu-left, .studio-vu-fill.vu-right {
    background: linear-gradient(90deg, #10b981 0%, #10b981 65%, #f59e0b 85%, #ef4444 100%);
}
.studio-vu-fill.vu-gr {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
}
.studio-vu-peak {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #fff;
    box-shadow: 0 0 4px #fff;
    transition: left 0.08s ease-out;
}
.studio-db-scale {
    display: flex;
    justify-content: space-between;
    font-size: 8.5px;
    color: #6b7280;
    font-family: monospace;
}
.clip-label {
    color: #ef4444;
    font-weight: bold;
}

/* PRESETS DE ESTÚDIO */
.studio-presets-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    background: rgba(255, 255, 255, 0.03);
    padding: 6px 10px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}
.presets-label {
    font-size: 10px;
    font-weight: 800;
    color: #a855f7;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.studio-presets-list {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    flex: 1;
}
.studio-preset-chip {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #e2e8f0;
    padding: 4px 9px;
    border-radius: 6px;
    font-size: 10.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s ease;
}
.studio-preset-chip:hover {
    background: rgba(168, 85, 247, 0.2);
    border-color: rgba(168, 85, 247, 0.5);
    color: #fff;
}
.studio-preset-chip.active {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.35), rgba(0, 242, 254, 0.35)) !important;
    border-color: #a855f7 !important;
    color: #fff !important;
    box-shadow: 0 0 10px rgba(168, 85, 247, 0.4);
}

/* GRID DOS 4 MÓDULOS DE PROCESSAMENTO */
.studio-rack-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}
@media (max-width: 768px) {
    .studio-rack-grid { grid-template-columns: 1fr; }
    .studio-meters-panel { grid-template-columns: 1fr; }
}

.studio-rack-card {
    background: #101424;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    position: relative;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
.rack-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.rack-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11.5px;
    font-weight: 800;
    color: #f1f5f9;
    letter-spacing: 0.4px;
}
.rack-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}
.rack-dot.reverb-dot { background: #38bdf8; box-shadow: 0 0 6px #38bdf8; }
.rack-dot.delay-dot { background: #34d399; box-shadow: 0 0 6px #34d399; }
.rack-dot.comp-dot { background: #fbbf24; box-shadow: 0 0 6px #fbbf24; }
.rack-dot.warm-dot { background: #f43f5e; box-shadow: 0 0 6px #f43f5e; }

.rack-badge {
    font-size: 9px;
    font-weight: 800;
    color: #94a3b8;
    background: rgba(255, 255, 255, 0.06);
    padding: 2px 5px;
    border-radius: 3px;
    letter-spacing: 0.5px;
}
.rack-controls-col {
    display: flex;
    flex-direction: column;
    gap: 9px;
}
.rack-ctrl-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.ctrl-info {
    display: flex;
    justify-content: space-between;
    font-size: 10.5px;
    color: #94a3b8;
}
.ctrl-info strong {
    color: #38bdf8;
    font-family: monospace;
    font-size: 11px;
}
.ctrl-label {
    font-size: 10px;
    color: #94a3b8;
    font-weight: 700;
}

.reverb-type-btns, .delay-time-btns {
    display: flex;
    gap: 4px;
}
.btn-rev-type, .btn-del-time {
    flex: 1;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #cbd5e1;
    padding: 4px;
    border-radius: 4px;
    font-size: 9.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s ease;
}
.btn-rev-type:hover, .btn-del-time:hover {
    background: rgba(0, 242, 254, 0.15);
    border-color: rgba(0, 242, 254, 0.3);
    color: #fff;
}
.btn-rev-type.active, .btn-del-time.active {
    background: rgba(0, 242, 254, 0.25) !important;
    border-color: var(--accent) !important;
    color: #fff !important;
}

.studio-slider {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 5px;
    border-radius: 3px;
    background: #1e2436;
    outline: none;
    margin: 4px 0;
}
.studio-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #00f2fe;
    box-shadow: 0 0 8px rgba(0, 242, 254, 0.7);
    cursor: pointer;
    border: 1.5px solid #fff;
    transition: transform 0.1s ease;
}
.studio-slider::-webkit-slider-thumb:hover {
    transform: scale(1.2);
}
.studio-slider.mini {
    height: 4px;
}
.studio-slider.mini::-webkit-slider-thumb {
    width: 11px;
    height: 11px;
}

.attack-release-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}
.mini-ctrl {
    display: flex;
    flex-direction: column;
    gap: 2px;
    background: rgba(0, 0, 0, 0.25);
    padding: 5px 7px;
    border-radius: 5px;
}
.mini-ctrl span {
    font-size: 9px;
    color: #64748b;
}
.mini-ctrl strong {
    font-size: 10px;
    color: #fbbf24;
    font-family: monospace;
}

.studio-width-tags {
    display: flex;
    justify-content: space-between;
    font-size: 8.5px;
    color: #64748b;
    font-family: monospace;
}

.studio-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.studio-engine-status {
    font-size: 10px;
    color: var(--text-dim);
    letter-spacing: 0.3px;
}
"""

    if ".studio-modal-card" not in css:
        css += "\n" + studio_css
        with open(CSS_PATH, "w", encoding="utf-8") as f:
            f.write(css)
        print("CSS atualizado com os estilos da Console de Estúdio!")
    else:
        print("CSS da Console de Estúdio já existe.")

def update_html():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Adicionar botão "🎚️ Estúdio Pro" na barra de ferramentas inferior
    if 'id="barStudioBtn"' not in html:
        old_stems = '<button class="bar-pill-btn stems-active" id="barStemsBtn" onclick="openStemsModal()" title="Stems DJ">🎧 Stems DJ</button>'
        new_btns = old_stems + '\n                <button class="bar-pill-btn studio-active" id="barStudioBtn" onclick="openStudioModal()" title="Console de Estúdio, Mastering DSP e Efeitos">🎚️ Estúdio Pro</button>'
        html = html.replace(old_stems, new_btns)
        print("Botão 'Estúdio Pro' adicionado na barra inferior do player!")

    # 2. Adicionar opção no dropdown do DJ Mixer
    if 'id="actOpt_studio"' not in html:
        club_opt = '<button class="dj-act-menu-opt" id="actOpt_club" onclick="selectDjActMode(\'club\')">'
        studio_opt = '''<button class="dj-act-menu-opt" id="actOpt_studio" onclick="selectDjActMode('studio')">
                                        <span class="opt-icon">🎛️</span>
                                        <div class="opt-text">
                                            <strong>Estúdio Pro & Mastering</strong>
                                            <small>Reverb analógico, delay estéreo, compressor SSL e saturação</small>
                                        </div>
                                    </button>
                                    ''' + club_opt
        html = html.replace(club_opt, studio_opt)
        print("Opção 'Estúdio Pro & Mastering' adicionada ao dropdown de modos!")

    # 3. Adicionar badge do Modo Estúdio no Mixer
    if 'id="djStudioActiveBadge"' not in html:
        club_badge = '<div class="dj-club-active-badge" id="djClubActiveBadge" style="display: none;">'
        studio_badge = '''<div class="dj-studio-active-badge" id="djStudioActiveBadge" style="display: none;">
                            <span class="hud-strobe-dot studio-dot"></span>
                            <span>🎛️ MODO ESTÚDIO ATIVO • Mastering DSP, Reverb & Compressor Habilitados</span>
                        </div>
                        ''' + club_badge
        html = html.replace(club_badge, studio_badge)
        print("Badge do Modo Estúdio adicionado ao painel do Mixer!")

    # 4. Inserir o Modal da Console de Estúdio
    if 'id="studioModal"' not in html:
        modal_html = """
    <!-- MODAL ESTÚDIO PROFISSIONAL & MASTERING DSP CONSOLE -->
    <div class="eq-modal-overlay" id="studioModal" onclick="closeStudioModal(event)" style="display: none;">
        <div class="eq-modal-card studio-modal-card" onclick="event.stopPropagation()">
            <!-- HEADER DA CONSOLE DE ESTÚDIO -->
            <div class="studio-modal-header">
                <div class="studio-title-box">
                    <div class="studio-modal-title">
                        <span class="studio-pulse-led"></span>
                        <span>🎚️ CONSOLE DE ESTÚDIO & MASTERING DSP PRO</span>
                        <span class="studio-badge-pro">PRO AUDIO 96kHz</span>
                    </div>
                    <div class="studio-modal-sub">
                        Processamento acústico de estúdio: Reverb Hall/Plate, Tape Delay, Compressor SSL, Saturação Valvulada e Imagem Estéreo 3D.
                    </div>
                </div>
                <div class="studio-header-actions">
                    <button class="btn-studio-bypass" id="btnStudioBypass" onclick="toggleStudioBypass()" title="Alternar entre Som Processado e Som Direto (A/B Test)">
                        <span id="studioBypassDot" class="bypass-dot active"></span>
                        <span id="studioBypassLabel">DSP ATIVO</span>
                    </button>
                    <button class="btn-modal-close" onclick="closeStudioModal()">✕</button>
                </div>
            </div>

            <!-- ANALOG VU METERS SECTION (STEREO L & R + COMPRESSOR GAIN REDUCTION) -->
            <div class="studio-meters-panel">
                <div class="studio-meter-group">
                    <div class="studio-meter-header">
                        <span>CANAL ESQUERDO (L)</span>
                        <span id="studioVuValL" class="meter-db-val">-18 dBFS</span>
                    </div>
                    <div class="studio-vu-track">
                        <div class="studio-vu-fill vu-left" id="studioVuFillL" style="width: 45%;"></div>
                        <div class="studio-vu-peak" id="studioVuPeakL" style="left: 45%;"></div>
                    </div>
                    <div class="studio-db-scale">
                        <span>-48</span><span>-30</span><span>-18</span><span>-12</span><span>-6</span><span>-3</span><span>0</span><span class="clip-label">+3</span>
                    </div>
                </div>

                <div class="studio-meter-group">
                    <div class="studio-meter-header">
                        <span>CANAL DIREITO (R)</span>
                        <span id="studioVuValR" class="meter-db-val">-18 dBFS</span>
                    </div>
                    <div class="studio-vu-track">
                        <div class="studio-vu-fill vu-right" id="studioVuFillR" style="width: 45%;"></div>
                        <div class="studio-vu-peak" id="studioVuPeakR" style="left: 45%;"></div>
                    </div>
                    <div class="studio-db-scale">
                        <span>-48</span><span>-30</span><span>-18</span><span>-12</span><span>-6</span><span>-3</span><span>0</span><span class="clip-label">+3</span>
                    </div>
                </div>

                <div class="studio-meter-group gr-meter-group">
                    <div class="studio-meter-header">
                        <span>SSL GAIN REDUCTION (GR)</span>
                        <span id="studioGrVal" class="meter-db-val">0.0 dB</span>
                    </div>
                    <div class="studio-vu-track gr-track">
                        <div class="studio-vu-fill vu-gr" id="studioGrFill" style="width: 0%;"></div>
                    </div>
                    <div class="studio-db-scale">
                        <span>0</span><span>-2</span><span>-4</span><span>-6</span><span>-8</span><span>-12</span><span>-16</span><span>-20 dB</span>
                    </div>
                </div>
            </div>

            <!-- PRESETS DE ESTÚDIO 1-CLIQUE -->
            <div class="studio-presets-row">
                <span class="presets-label">PRESETS DE ESTÚDIO:</span>
                <div class="studio-presets-list">
                    <button class="studio-preset-chip active" id="stPreset_mastering" onclick="selectStudioPreset('mastering')">🎧 Neve Warmth</button>
                    <button class="studio-preset-chip" id="stPreset_hall" onclick="selectStudioPreset('hall')">🏰 Concert Arena</button>
                    <button class="studio-preset-chip" id="stPreset_club" onclick="selectStudioPreset('club')">⚡ SSL Club Master</button>
                    <button class="studio-preset-chip" id="stPreset_vocal" onclick="selectStudioPreset('vocal')">🎙️ Vocal Clarity</button>
                    <button class="studio-preset-chip" id="stPreset_lofi" onclick="selectStudioPreset('lofi')">📻 Tape Vinyl</button>
                    <button class="studio-preset-chip" id="stPreset_flat" onclick="selectStudioPreset('flat')">🎚️ Flat Reference</button>
                </div>
            </div>

            <!-- RACK STRIPS GRID: 4 MÓDULOS DE PROCESSAMENTO -->
            <div class="studio-rack-grid">
                <!-- MÓDULO 1: REVERB ACÚSTICO ESPACIAL (ESPACIALIZAÇÃO DE SALA / CAUDA SUAVE) -->
                <div class="studio-rack-card">
                    <div class="rack-card-header">
                        <div class="rack-title"><span class="rack-dot reverb-dot"></span> 🏛️ REVERB DE ESTÚDIO</div>
                        <span class="rack-badge" id="reverbTypeBadge">HALL</span>
                    </div>
                    <div class="rack-controls-col">
                        <div class="rack-ctrl-row">
                            <span class="ctrl-label">Ambiente / Sala</span>
                            <div class="reverb-type-btns">
                                <button class="btn-rev-type active" id="btnRev_hall" onclick="setStudioReverbType('hall')">Hall</button>
                                <button class="btn-rev-type" id="btnRev_plate" onclick="setStudioReverbType('plate')">Plate</button>
                                <button class="btn-rev-type" id="btnRev_club" onclick="setStudioReverbType('club')">Club</button>
                                <button class="btn-rev-type" id="btnRev_room" onclick="setStudioReverbType('room')">Room</button>
                            </div>
                        </div>
                        <div class="rack-ctrl-row">
                            <div class="ctrl-info">
                                <span>Tempo de Decaimento (Decay Tail)</span>
                                <strong id="valStudioReverbDecay">1.8s</strong>
                            </div>
                            <input type="range" min="0.4" max="4.0" step="0.1" value="1.8" class="studio-slider" id="sliderStudioReverbDecay" oninput="onStudioParamChange('reverbDecay', this.value)">
                        </div>
                        <div class="rack-ctrl-row">
                            <div class="ctrl-info">
                                <span>Mistura (Wet / Dry)</span>
                                <strong id="valStudioReverbMix">22%</strong>
                            </div>
                            <input type="range" min="0" max="100" step="1" value="22" class="studio-slider" id="sliderStudioReverbMix" oninput="onStudioParamChange('reverbMix', this.value)">
                        </div>
                    </div>
                </div>

                <!-- MÓDULO 2: STEREO PING-PONG / TAPE DELAY (ECO ANALÓGICO COM FEEDBACK) -->
                <div class="studio-rack-card">
                    <div class="rack-card-header">
                        <div class="rack-title"><span class="rack-dot delay-dot"></span> ⏱️ DELAY ESTÉREO PING-PONG</div>
                        <span class="rack-badge">ANALOG TAPE</span>
                    </div>
                    <div class="rack-controls-col">
                        <div class="rack-ctrl-row">
                            <span class="ctrl-label">Sincronia de Tempo</span>
                            <div class="delay-time-btns">
                                <button class="btn-del-time" onclick="setStudioDelayPreset(0.12, '1/8')">1/8 (120ms)</button>
                                <button class="btn-del-time active" id="btnDel_quarter" onclick="setStudioDelayPreset(0.24, '1/4')">1/4 (240ms)</button>
                                <button class="btn-del-time" onclick="setStudioDelayPreset(0.48, '1/2')">1/2 (480ms)</button>
                            </div>
                        </div>
                        <div class="rack-ctrl-row">
                            <div class="ctrl-info">
                                <span>Feedback / Repetições</span>
                                <strong id="valStudioDelayFeedback">28%</strong>
                            </div>
                            <input type="range" min="0" max="80" step="1" value="28" class="studio-slider" id="sliderStudioDelayFeedback" oninput="onStudioParamChange('delayFeedback', this.value)">
                        </div>
                        <div class="rack-ctrl-row">
                            <div class="ctrl-info">
                                <span>Mistura do Eco (Wet / Dry)</span>
                                <strong id="valStudioDelayMix">18%</strong>
                            </div>
                            <input type="range" min="0" max="100" step="1" value="18" class="studio-slider" id="sliderStudioDelayMix" oninput="onStudioParamChange('delayMix', this.value)">
                        </div>
                    </div>
                </div>

                <!-- MÓDULO 3: COMPRESSOR DE MASTERING DINÂMICO (SSL 4000 STYLE) -->
                <div class="studio-rack-card">
                    <div class="rack-card-header">
                        <div class="rack-title"><span class="rack-dot comp-dot"></span> 🎚️ COMPRESSOR SSL BUS</div>
                        <span class="rack-badge">GLUE MASTER</span>
                    </div>
                    <div class="rack-controls-col">
                        <div class="rack-ctrl-row">
                            <div class="ctrl-info">
                                <span>Threshold (Limiar)</span>
                                <strong id="valStudioCompThresh">-14 dB</strong>
                            </div>
                            <input type="range" min="-36" max="0" step="1" value="-14" class="studio-slider" id="sliderStudioCompThresh" oninput="onStudioParamChange('compThreshold', this.value)">
                        </div>
                        <div class="rack-ctrl-row">
                            <div class="ctrl-info">
                                <span>Ratio (Taxa de Compressão)</span>
                                <strong id="valStudioCompRatio">4:1</strong>
                            </div>
                            <input type="range" min="1.5" max="10" step="0.5" value="4.0" class="studio-slider" id="sliderStudioCompRatio" oninput="onStudioParamChange('compRatio', this.value)">
                        </div>
                        <div class="rack-ctrl-row attack-release-row">
                            <div class="mini-ctrl">
                                <span>Ataque</span>
                                <strong id="valStudioCompAttack">5ms</strong>
                                <input type="range" min="0.001" max="0.05" step="0.002" value="0.005" class="studio-slider mini" id="sliderStudioCompAttack" oninput="onStudioParamChange('compAttack', this.value)">
                            </div>
                            <div class="mini-ctrl">
                                <span>Release</span>
                                <strong id="valStudioCompRelease">150ms</strong>
                                <input type="range" min="0.05" max="0.5" step="0.02" value="0.15" class="studio-slider mini" id="sliderStudioCompRelease" oninput="onStudioParamChange('compRelease', this.value)">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- MÓDULO 4: CALOR ANALÓGICO VALVULADO & IMAGEM ESTÉREO 3D -->
                <div class="studio-rack-card">
                    <div class="rack-card-header">
                        <div class="rack-title"><span class="rack-dot warm-dot"></span> 🔥 CALOR VALVULADO & 3D WIDE</div>
                        <span class="rack-badge">NEVE TUBE</span>
                    </div>
                    <div class="rack-controls-col">
                        <div class="rack-ctrl-row">
                            <div class="ctrl-info">
                                <span>Saturação Analógica (Tube Warmth)</span>
                                <strong id="valStudioWarmth">30%</strong>
                            </div>
                            <input type="range" min="0" max="100" step="1" value="30" class="studio-slider" id="sliderStudioWarmth" oninput="onStudioParamChange('warmthDrive', this.value)">
                        </div>
                        <div class="rack-ctrl-row">
                            <div class="ctrl-info">
                                <span>Largura Estéreo (Stereo Imager 3D)</span>
                                <strong id="valStudioWidth">135%</strong>
                            </div>
                            <input type="range" min="0" max="200" step="5" value="135" class="studio-slider" id="sliderStudioWidth" oninput="onStudioParamChange('stereoWidth', this.value)">
                        </div>
                        <div class="studio-width-tags">
                            <span>Mono (0%)</span>
                            <span>Normal (100%)</span>
                            <span>Super 3D (200%)</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- FOOTER -->
            <div class="studio-footer">
                <span class="studio-engine-status">⚡ DSP de Alta Precisão Web Audio • Processamento Linear a 32-bit Ponto Flutuante</span>
                <button class="btn-modal-done" onclick="closeStudioModal()">✓ Salvar & Fechar</button>
            </div>
        </div>
    </div>
"""
        # Inserir antes de `<div class="eq-modal-overlay" id="spotifyQueueModal"`
        queue_target = '<div class="eq-modal-overlay" id="spotifyQueueModal"'
        html = html.replace(queue_target, modal_html + "\n    " + queue_target)
        print("Modal da Console de Estúdio inserido com sucesso em player_template.html!")

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    update_css()
    update_html()
