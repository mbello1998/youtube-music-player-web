import re
import os

print("Iniciando implementação do Modo Balada exclusivo e upgrade de alta potência dos Efeitos Sonoros DJ...")

# =============================================================
# 1. ATUALIZAR player_template.html COM O BADGE DO MODO BALADA
# =============================================================
with open("player_template.html", "r", encoding="utf-8") as f:
    html = f.read()

# Inserir o badge ativo do modo balada dentro de #djActModeBox
target_html = '''                                </div>
                            </div>
                        </div>'''

replacement_html = '''                                </div>
                            </div>
                        </div>

                        <!-- Indicador Ativo do Modo Balada & Efeitos Especiais -->
                        <div class="dj-club-active-badge" id="djClubActiveBadge" style="display: none;">
                            <span class="hud-strobe-dot"></span>
                            <span>🔥 MODO BALADA ATIVO • Efeitos Sonoros DJ & Drops habilitados</span>
                        </div>'''

if target_html in html and "id=\"djClubActiveBadge\"" not in html:
    html = html.replace(target_html, replacement_html, 1)
    print("player_template.html: Badge do Modo Balada inserido com sucesso!")

with open("player_template.html", "w", encoding="utf-8") as f:
    f.write(html)


# =============================================================
# 2. ATUALIZAR assets/css/player.css COM CSS VISÍVEL E ANTI-CORTE
# =============================================================
with open("assets/css/player.css", "r", encoding="utf-8") as f:
    css = f.read()

# 2.1 Garantir overflow: visible no .spotify-dj-mixer para não cortar dropdowns
old_mixer_rule = '''.spotify-dj-mixer {
            background: linear-gradient(145deg, #0e111a, #151926);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 10px 12px;
            margin-top: 4px;
            display: flex;
            flex-direction: column;
            gap: 7px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            width: 100%;
            box-sizing: border-box;
            overflow: hidden;
            flex: 1;
            min-height: 310px;
        }'''

new_mixer_rule = '''.spotify-dj-mixer {
            background: linear-gradient(145deg, #0e111a, #151926);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 10px 12px;
            margin-top: 4px;
            display: flex;
            flex-direction: column;
            gap: 7px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            width: 100%;
            box-sizing: border-box;
            overflow: visible !important;
            flex: 1;
            min-height: 310px;
            position: relative;
        }'''

if old_mixer_rule in css:
    css = css.replace(old_mixer_rule, new_mixer_rule)
    print("assets/css/player.css: .spotify-dj-mixer atualizado para overflow: visible")

# 2.2 Atualizar estilos do dropdown do Modo de Atuação e adicionar o badge do Modo Balada
old_dropdown_pattern = r'\.dj-act-dropdown\s*\{.*?\.dj-act-menu-opt\s*\.opt-text\s*small\s*\{[^}]*\}'

new_dropdown_css = '''.dj-act-dropdown {
    position: relative;
    flex: 1;
    min-width: 0;
    z-index: 100;
}
.btn-dj-act-trigger {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: linear-gradient(135deg, rgba(0, 242, 254, 0.15), rgba(79, 172, 254, 0.1));
    border: 1px solid rgba(0, 242, 254, 0.45);
    color: #fff;
    padding: 4px 8px;
    border-radius: 5px;
    font-size: 10.5px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    box-sizing: border-box;
}
.btn-dj-act-trigger:hover {
    background: linear-gradient(135deg, rgba(0, 242, 254, 0.25), rgba(79, 172, 254, 0.2));
    border-color: var(--accent);
    box-shadow: 0 0 10px rgba(0, 242, 254, 0.35);
}
.dj-dropdown-caret {
    font-size: 10px;
    color: var(--accent);
    margin-left: 6px;
}
.dj-act-dropdown-menu {
    position: absolute;
    top: calc(100% + 4px);
    left: 0;
    right: 0;
    min-width: 250px;
    background: #0b0e18;
    border: 1px solid rgba(0, 242, 254, 0.45);
    border-radius: 8px;
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.95), 0 0 16px rgba(0, 242, 254, 0.2);
    z-index: 99999 !important;
    display: flex;
    flex-direction: column;
    padding: 4px;
    gap: 3px;
    max-height: 230px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 242, 254, 0.4) rgba(0, 0, 0, 0.3);
}
.dj-act-dropdown-menu::-webkit-scrollbar {
    width: 4px;
}
.dj-act-dropdown-menu::-webkit-scrollbar-thumb {
    background: rgba(0, 242, 254, 0.4);
    border-radius: 4px;
}
.dj-act-menu-opt {
    display: flex;
    align-items: center;
    gap: 7px;
    background: transparent;
    border: 1px solid transparent;
    color: #fff;
    padding: 5px 7px;
    border-radius: 5px;
    cursor: pointer;
    text-align: left;
    transition: all 0.15s ease;
    width: 100%;
    box-sizing: border-box;
    flex-shrink: 0;
}
.dj-act-menu-opt:hover {
    background: rgba(0, 242, 254, 0.16);
    border-color: rgba(0, 242, 254, 0.35);
    color: var(--accent);
}
.dj-act-menu-opt.active {
    background: rgba(0, 242, 254, 0.22) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
}
.dj-act-menu-opt .opt-icon {
    font-size: 15px;
    flex-shrink: 0;
}
.dj-act-menu-opt .opt-text {
    display: flex;
    flex-direction: column;
    gap: 1px;
    overflow: hidden;
    min-width: 0;
}
.dj-act-menu-opt .opt-text strong {
    font-size: 10.5px;
    font-weight: 700;
    white-space: nowrap;
}
.dj-act-menu-opt .opt-text small {
    font-size: 8.5px;
    color: var(--text-dim);
    line-height: 1.15;
    white-space: normal;
}
.dj-club-active-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, rgba(255, 0, 85, 0.18), rgba(255, 106, 0, 0.22));
    border: 1px solid rgba(255, 0, 85, 0.55);
    border-radius: 5px;
    padding: 3px 7px;
    font-size: 9.5px;
    font-weight: 800;
    color: #ff3366;
    letter-spacing: 0.3px;
    margin-top: 3px;
    animation: pulseClubBadge 2.2s infinite ease-in-out;
}
@keyframes pulseClubBadge {
    0%, 100% { box-shadow: 0 0 8px rgba(255, 0, 85, 0.2); border-color: rgba(255, 0, 85, 0.5); }
    50% { box-shadow: 0 0 14px rgba(255, 0, 85, 0.5); border-color: rgba(255, 106, 0, 0.85); color: #ff6a00; }
}'''

css, count_drop = re.subn(old_dropdown_pattern, new_dropdown_css, css, flags=re.DOTALL)
print(f"assets/css/player.css: Dropdown menu styles atualizados ({count_drop} ocorrência)")

with open("assets/css/player.css", "w", encoding="utf-8") as f:
    f.write(css)


# =============================================================
# 3. ATUALIZAR assets/js/player.js: EXCLUSIVIDADE DO MODO BALADA E UPGRADE DOS EFEITOS
# =============================================================
with open("assets/js/player.js", "r", encoding="utf-8") as f:
    js = f.read()

# 3.1 Em performCrossfade: HUD e Efeitos SOMENTE NO MODO BALADA
old_hud_call = '''            // Mostra o HUD visual de crossover de 3 bandas no player de forma ordenada
            showDjClubHud(fxInfo);'''

new_hud_call = '''            // O HUD visual e os Efeitos de DJ SÓ DEVEM FUNCIONAR NO MODO BALADA & CLUB DJ!
            if (djPlayMode === "club") {
                showDjClubHud(fxInfo);
            } else {
                hideDjClubHud();
            }'''

if old_hud_call in js:
    js = js.replace(old_hud_call, new_hud_call, 1)
    print("assets/js/player.js: showDjClubHud condicionado estritamente a djPlayMode === 'club'")

# 3.2 Atualizar o disparo de som de transição no engineMode === "audio":
old_audio_fx = '''                // Dispara efeitos sonoros DJ FX no modo Club ou transições com Stems
                if (djPlayMode === "club" || (stemsState && (stemsState.solo || stemsState.muted.bass || stemsState.bass !== 100))) {
                    playDjClubFx(fxInfo, incBpm, durationMs, fromAudio, toAudio);
                }'''

new_audio_fx = '''                // Dispara efeitos sonoros DJ FX EXCLUSIVAMENTE quando o Modo Balada & Club DJ estiver ativo!
                if (djPlayMode === "club") {
                    playDjClubFx(fxInfo, incBpm, durationMs, fromAudio, toAudio);
                }'''

if old_audio_fx in js:
    js = js.replace(old_audio_fx, new_audio_fx, 1)
    print("assets/js/player.js: playDjClubFx (audio) restrito exclusivamente ao modo club")

# 3.3 Atualizar a chamada de updateDjClubHud dentro do loop de crossfade:
old_update_hud = '''                    // Atualiza o HUD visual de 3 bandas no player em tempo real
                    updateDjClubHud(progress, outgoingDeckName, incomingDeckName);'''

new_update_hud = '''                    // Atualiza o HUD visual de 3 bandas no player em tempo real SOMENTE no Modo Balada
                    if (djPlayMode === "club") {
                        updateDjClubHud(progress, outgoingDeckName, incomingDeckName);
                    }'''

if old_update_hud in js:
    js = js.replace(old_update_hud, new_update_hud, 1)
    print("assets/js/player.js: updateDjClubHud restrito ao modo club")

# 3.4 Em setDjMode: atualizar o badge de modo balada e ocultar HUD se sair do modo balada
old_set_dj_mode_start = '''        function setDjMode(mode) {
            djPlayMode = mode;
            const shortLabels = {
                match: "🎯 Match Perfeito",
                energy: "⚡ Peak Time",
                shuffle: "🔀 Smart Shuffle",
                smooth: "🌊 Smooth Flow",
                club: "🔥 Balada & Club DJ"
            };
            const activeLabel = document.getElementById("djActModeActiveLabel");
            if (activeLabel) activeLabel.textContent = shortLabels[mode] || mode;'''

new_set_dj_mode_start = '''        function setDjMode(mode) {
            djPlayMode = mode;
            const shortLabels = {
                match: "🎯 Match Perfeito",
                energy: "⚡ Peak Time",
                shuffle: "🔀 Smart Shuffle",
                smooth: "🌊 Smooth Flow",
                club: "🔥 Balada & Club DJ"
            };
            const activeLabel = document.getElementById("djActModeActiveLabel");
            if (activeLabel) activeLabel.textContent = shortLabels[mode] || mode;

            // Atualiza o Badge de Confirmação do Modo Balada
            const clubBadge = document.getElementById("djClubActiveBadge");
            if (clubBadge) {
                clubBadge.style.display = (mode === "club") ? "flex" : "none";
            }
            if (mode !== "club") {
                hideDjClubHud();
            }'''

if old_set_dj_mode_start in js:
    js = js.replace(old_set_dj_mode_start, new_set_dj_mode_start, 1)
    print("assets/js/player.js: setDjMode atualizado com controle do badge e hideDjClubHud")

# 3.5 Substituir todo o bloco de SÍNTESE DE EFEITOS (de synth808SubDrop até playDjClubFx)
# por um motor de síntese profissional de alta potência com Master FX Bus, Limiter, Auto-Ducking e volume cheio
old_synths_block_pattern = r'// ==========================================================\s*// SÍNTESE PROCEDURAL DE EFEITOS SONOROS DE DJ.*?(?=function showDjClubHud)'

new_synths_block = '''// ==========================================================
        // MOTOR PROFISSIONAL DE EFEITOS SONOROS DJ (WEB AUDIO API PRO)
        // ALTA POTÊNCIA, AUTO-DUCKING DE MÚSICA E ROTEAMENTO DEDICADO
        // ==========================================================
        let djFxBusNode = null;
        let djFxLimiterNode = null;

        function getDjFxDestination(ctx) {
            if (!ctx) return null;
            if (!djFxBusNode) {
                try {
                    djFxBusNode = ctx.createGain();
                    // Master do FX calibrado para presença de pista (+3.5 dB sobre a faixa)
                    djFxBusNode.gain.value = 0.88;

                    // Limiter ultra-rápido de estúdio para impedir distorção digital
                    djFxLimiterNode = ctx.createDynamicsCompressor();
                    djFxLimiterNode.threshold.value = -1.2;
                    djFxLimiterNode.knee.value = 3.0;
                    djFxLimiterNode.ratio.value = 18.0;
                    djFxLimiterNode.attack.value = 0.001; // 1ms
                    djFxLimiterNode.release.value = 0.06;

                    djFxBusNode.connect(djFxLimiterNode);
                    djFxLimiterNode.connect(ctx.destination);
                } catch (e) {
                    return ctx.destination;
                }
            }
            return djFxBusNode;
        }

        // Auto-Ducking: atenua a música suavemente para o efeito cortar a mixagem com impacto
        function triggerMusicDucking(durationSec = 2.0) {
            const ctx = audioCtx;
            if (ctx && engineMode === "audio") {
                const activeGain = (activeDeck === "A") ? deckGainA : deckGainB;
                if (activeGain && activeGain.gain) {
                    try {
                        const now = ctx.currentTime;
                        activeGain.gain.cancelScheduledValues(now);
                        activeGain.gain.setValueAtTime(activeGain.gain.value, now);
                        // Mergulho de 45% na faixa atual (sidechain clássico de DJ)
                        activeGain.gain.linearRampToValueAtTime(0.55, now + 0.05);
                        activeGain.gain.linearRampToValueAtTime(1.0, now + durationSec);
                    } catch (e) {}
                }
            } else if (engineMode === "video") {
                const fromPlayer = getActivePlayer();
                if (fromPlayer && typeof fromPlayer.setVolume === "function") {
                    try {
                        const origVol = masterVolume;
                        fromPlayer.setVolume(Math.round(origVol * 0.55));
                        setTimeout(() => {
                            try { fromPlayer.setVolume(origVol); } catch (err) {}
                        }, durationSec * 1000);
                    } catch (e) {}
                }
            }
        }

        // 1. SUB DROP 808 EXPLOSIVO (PUNCH DE TRANSITÓRIO + SUB-GRAVE TREME-TERRA)
        function synth808SubDrop(ctx, startTime, duration = 1.4) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;

                // Click transient do batedor de bumbo (punch audível em celular/fones)
                const clickOsc = ctx.createOscillator();
                const clickGain = ctx.createGain();
                clickOsc.type = "triangle";
                clickOsc.frequency.setValueAtTime(180, t0);
                clickOsc.frequency.exponentialRampToValueAtTime(65, t0 + 0.025);
                clickGain.gain.setValueAtTime(0.85, t0);
                clickGain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.035);
                clickOsc.connect(clickGain);
                clickGain.connect(outNode);
                clickOsc.start(t0);
                clickOsc.stop(t0 + 0.04);

                // Onda Senoidal com saturação harmônica para grave profundo (85Hz -> 36Hz)
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(88, t0);
                osc.frequency.exponentialRampToValueAtTime(36, t0 + duration);

                gain.gain.setValueAtTime(0.001, t0);
                gain.gain.linearRampToValueAtTime(0.85, t0 + 0.02);
                gain.gain.setValueAtTime(0.75, t0 + 0.35);
                gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duration);

                osc.connect(gain);
                gain.connect(outNode);
                osc.start(t0);
                osc.stop(t0 + duration);
            } catch (e) {}
        }

        // 2. CORNETA DE BAILE FUNK & DANCEHALL (AIRHORN AUTÊNTICO 3 RAJADAS)
        function synthAirHorn(ctx, startTime) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;

                // 3 Rajadas clássicas de Airhorn: PA! PA! PAAAAAA!
                const blasts = [
                    { start: t0, dur: 0.13 },
                    { start: t0 + 0.16, dur: 0.13 },
                    { start: t0 + 0.34, dur: 0.55 }
                ];

                // Frequências da corneta de pressão (Bb4, B4 desafinado com batimento pneumático, Eb5 e F5)
                const freqs = [466.16, 471.85, 622.25, 698.46];

                blasts.forEach(b => {
                    freqs.forEach((freq, idx) => {
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        // Mix de dente-de-serra e quadrada para o timbre metálico de latão
                        osc.type = (idx % 2 === 0) ? "sawtooth" : "square";
                        osc.frequency.setValueAtTime(freq, b.start);
                        osc.frequency.linearRampToValueAtTime(freq * 1.025, b.start + b.dur * 0.4);
                        osc.frequency.linearRampToValueAtTime(freq * 0.985, b.start + b.dur);

                        const peakGain = (idx === 0) ? 0.38 : (idx === 1 ? 0.34 : 0.22);
                        gain.gain.setValueAtTime(0.0001, b.start);
                        gain.gain.linearRampToValueAtTime(peakGain, b.start + 0.015);
                        gain.gain.setValueAtTime(peakGain, b.start + b.dur - 0.035);
                        gain.gain.exponentialRampToValueAtTime(0.0001, b.start + b.dur);

                        osc.connect(gain);
                        gain.connect(outNode);
                        osc.start(b.start);
                        osc.stop(b.start + b.dur);
                    });
                });
            } catch (e) {}
        }

        // 3. VINYL SPINBACK & BACKSPIN (FREIO DE DISCO + MOTOR REVERSO)
        function synthSpinback(ctx, fromAudio, startTime) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const dur = 0.85;

                // Chiado de atrito da agulha nos sulcos do vinil
                const bufSize = Math.floor(ctx.sampleRate * dur);
                const buffer = ctx.createBuffer(1, bufSize, ctx.sampleRate);
                const data = buffer.getChannelData(0);
                for (let i = 0; i < bufSize; i++) data[i] = (Math.random() * 2 - 1) * 0.45;
                const noise = ctx.createBufferSource();
                noise.buffer = buffer;
                const noiseFilter = ctx.createBiquadFilter();
                noiseFilter.type = "bandpass";
                noiseFilter.Q.value = 4.0;
                noiseFilter.frequency.setValueAtTime(1400, t0);
                noiseFilter.frequency.exponentialRampToValueAtTime(4500, t0 + 0.25);
                noiseFilter.frequency.exponentialRampToValueAtTime(300, t0 + dur);
                const noiseGain = ctx.createGain();
                noiseGain.gain.setValueAtTime(0.001, t0);
                noiseGain.gain.linearRampToValueAtTime(0.45, t0 + 0.08);
                noiseGain.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
                noise.connect(noiseFilter);
                noiseFilter.connect(noiseGain);
                noiseGain.connect(outNode);
                noise.start(t0);
                noise.stop(t0 + dur);

                // Mergulho harmônico da rotação invertida do prato
                const osc = ctx.createOscillator();
                const filter = ctx.createBiquadFilter();
                const gain = ctx.createGain();
                osc.type = "sawtooth";
                osc.frequency.setValueAtTime(450, t0);
                osc.frequency.exponentialRampToValueAtTime(2200, t0 + 0.24);
                osc.frequency.exponentialRampToValueAtTime(65, t0 + dur);

                filter.type = "bandpass";
                filter.Q.value = 5.5;
                filter.frequency.setValueAtTime(900, t0);
                filter.frequency.exponentialRampToValueAtTime(3200, t0 + 0.24);
                filter.frequency.exponentialRampToValueAtTime(160, t0 + dur);

                gain.gain.setValueAtTime(0.0001, t0);
                gain.gain.linearRampToValueAtTime(0.72, t0 + 0.06);
                gain.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);

                osc.connect(filter);
                filter.connect(gain);
                gain.connect(outNode);
                osc.start(t0);
                osc.stop(t0 + dur);

                // Freia a música do deck físico em rotação reversa
                if (fromAudio && fromAudio.playbackRate) {
                    const orig = fromAudio.playbackRate;
                    fromAudio.playbackRate = 1.7;
                    setTimeout(() => { if (fromAudio) fromAudio.playbackRate = 0.25; }, 200);
                    setTimeout(() => { if (fromAudio) fromAudio.playbackRate = orig; }, 850);
                }
            } catch (e) {}
        }

        // 4. HPF NOISE SWEEP & RISER EDM (RESSONÂNCIA ALTA + STUTTER GATE)
        function synthHpfNoiseSweep(ctx, startTime, duration = 1.8) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const dur = Math.max(0.8, Math.min(3.2, duration));
                const bufSize = Math.floor(ctx.sampleRate * dur);
                const buffer = ctx.createBuffer(1, bufSize, ctx.sampleRate);
                const data = buffer.getChannelData(0);
                for (let i = 0; i < bufSize; i++) data[i] = (Math.random() * 2 - 1);
                const noise = ctx.createBufferSource();
                noise.buffer = buffer;

                const filter = ctx.createBiquadFilter();
                filter.type = "bandpass";
                filter.Q.value = 8.5; // Ressonância bem alta e presente de pista

                const gain = ctx.createGain();
                const t0 = startTime || ctx.currentTime;

                filter.frequency.setValueAtTime(320, t0);
                filter.frequency.exponentialRampToValueAtTime(9500, t0 + dur);

                gain.gain.setValueAtTime(0.0001, t0);
                gain.gain.linearRampToValueAtTime(0.65, t0 + dur * 0.85);
                gain.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);

                noise.connect(filter);
                filter.connect(gain);
                gain.connect(outNode);
                noise.start(t0);
                noise.stop(t0 + dur);
            } catch (e) {}
        }

        // 5. SPACE ECHO & DUB TAPE DELAY COM RETORNO
        function synthDubEcho(ctx, bpm = 130) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const delaySec = Math.max(0.18, Math.min(0.55, (60 / bpm) * 0.75));
                const osc = ctx.createOscillator();
                const oscGain = ctx.createGain();
                const delay = ctx.createDelay();
                const feedback = ctx.createGain();
                const filter = ctx.createBiquadFilter();
                const masterFx = ctx.createGain();

                osc.type = "sawtooth";
                const t0 = ctx.currentTime;
                osc.frequency.setValueAtTime(540, t0);
                osc.frequency.exponentialRampToValueAtTime(180, t0 + 0.25);

                oscGain.gain.setValueAtTime(0.65, t0);
                oscGain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.25);

                delay.delayTime.value = delaySec;
                feedback.gain.value = 0.52;
                filter.type = "lowpass";
                filter.frequency.value = 1800;
                masterFx.gain.value = 0.65;

                osc.connect(oscGain);
                oscGain.connect(delay);
                delay.connect(filter);
                filter.connect(feedback);
                feedback.connect(delay);
                delay.connect(masterFx);
                masterFx.connect(outNode);

                osc.start(t0);
                osc.stop(t0 + 0.26);
                setTimeout(() => {
                    try { delay.disconnect(); feedback.disconnect(); masterFx.disconnect(); } catch (e) {}
                }, 2400);
            } catch (e) {}
        }

        // 6. SCRATCH DE VINIL HIP-HOP (BABY SCRATCH & CHIRP)
        function synthVinylScratch(ctx, startTime) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const scratches = [
                    { t: t0, fStart: 250, fEnd: 1100, dur: 0.08 },
                    { t: t0 + 0.09, fStart: 1100, fEnd: 300, dur: 0.09 },
                    { t: t0 + 0.20, fStart: 400, fEnd: 1500, dur: 0.12 }
                ];

                scratches.forEach(s => {
                    const osc = ctx.createOscillator();
                    const filter = ctx.createBiquadFilter();
                    const gain = ctx.createGain();

                    osc.type = "sawtooth";
                    osc.frequency.setValueAtTime(s.fStart, s.t);
                    osc.frequency.exponentialRampToValueAtTime(s.fEnd, s.t + s.dur);

                    filter.type = "bandpass";
                    filter.Q.value = 7.0;
                    filter.frequency.setValueAtTime(s.fStart * 1.5, s.t);
                    filter.frequency.exponentialRampToValueAtTime(s.fEnd * 1.5, s.t + s.dur);

                    gain.gain.setValueAtTime(0.001, s.t);
                    gain.gain.linearRampToValueAtTime(0.68, s.t + 0.02);
                    gain.gain.exponentialRampToValueAtTime(0.0001, s.t + s.dur);

                    osc.connect(filter);
                    filter.connect(gain);
                    gain.connect(outNode);
                    osc.start(s.t);
                    osc.stop(s.t + s.dur);
                });
            } catch (e) {}
        }

        // 7. SIRENE RAVE / DUB SIREN
        function synthSirenRiser(ctx, startTime, duration = 2.0) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const osc = ctx.createOscillator();
                const lfo = ctx.createOscillator();
                const lfoGain = ctx.createGain();
                const gain = ctx.createGain();

                osc.type = "sawtooth";
                lfo.type = "sine";
                lfo.frequency.setValueAtTime(2.5, t0);
                lfo.frequency.linearRampToValueAtTime(10.0, t0 + duration);

                lfoGain.gain.setValueAtTime(120, t0);
                lfoGain.gain.linearRampToValueAtTime(380, t0 + duration);

                lfo.connect(lfoGain);
                lfoGain.connect(osc.frequency);

                osc.frequency.setValueAtTime(520, t0);
                osc.frequency.linearRampToValueAtTime(1800, t0 + duration);

                gain.gain.setValueAtTime(0.001, t0);
                gain.gain.linearRampToValueAtTime(0.55, t0 + 0.08);
                gain.gain.setValueAtTime(0.55, t0 + duration - 0.1);
                gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duration);

                osc.connect(gain);
                gain.connect(outNode);

                lfo.start(t0);
                osc.start(t0);
                lfo.stop(t0 + duration);
                osc.stop(t0 + duration);
            } catch (e) {}
        }

        // 8. JET FLANGER ESPACIAL
        function synthJetFlanger(ctx, startTime, duration = 2.2) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const bufSize = Math.floor(ctx.sampleRate * duration);
                const buffer = ctx.createBuffer(1, bufSize, ctx.sampleRate);
                const data = buffer.getChannelData(0);
                for (let i = 0; i < bufSize; i++) data[i] = Math.random() * 2 - 1;

                const noise = ctx.createBufferSource();
                noise.buffer = buffer;

                const filter = ctx.createBiquadFilter();
                filter.type = "bandpass";
                filter.Q.value = 6.5;

                const lfo = ctx.createOscillator();
                const lfoGain = ctx.createGain();
                lfo.frequency.value = 0.8;
                lfoGain.gain.value = 2200;

                filter.frequency.setValueAtTime(800, t0);
                filter.frequency.exponentialRampToValueAtTime(7500, t0 + duration);

                lfo.connect(lfoGain);
                lfoGain.connect(filter.frequency);

                const gain = ctx.createGain();
                gain.gain.setValueAtTime(0.0001, t0);
                gain.gain.linearRampToValueAtTime(0.58, t0 + duration * 0.7);
                gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duration);

                noise.connect(filter);
                filter.connect(gain);
                gain.connect(outNode);

                lfo.start(t0);
                noise.start(t0);
                lfo.stop(t0 + duration);
                noise.stop(t0 + duration);
            } catch (e) {}
        }

        // 9. SNARE ROLL ACCELERATOR (REPIQUE DE CAIXA DE PISTA)
        function synthSnareRoll(ctx, startTime, duration = 2.0, bpm = 128) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const hitTimes = [];
                let currT = 0;
                let curInterval = 0.22; // Inicia em colcheias
                while (currT < duration - 0.1) {
                    hitTimes.push(t0 + currT);
                    curInterval = Math.max(0.038, curInterval * 0.82); // Acelera exponencialmente
                    currT += curInterval;
                }

                hitTimes.forEach((hitT, idx) => {
                    const osc = ctx.createOscillator();
                    const oscGain = ctx.createGain();
                    osc.type = "triangle";
                    osc.frequency.setValueAtTime(190 + (idx * 5), hitT);
                    oscGain.gain.setValueAtTime(0.55, hitT);
                    oscGain.gain.exponentialRampToValueAtTime(0.0001, hitT + 0.05);

                    osc.connect(oscGain);
                    oscGain.connect(outNode);
                    osc.start(hitT);
                    osc.stop(hitT + 0.06);
                });
            } catch (e) {}
        }

        // 10. REVERSE CYMBAL / CRASH SWELL
        function synthReverseCrash(ctx, startTime, duration = 1.6) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const bufSize = Math.floor(ctx.sampleRate * duration);
                const buffer = ctx.createBuffer(1, bufSize, ctx.sampleRate);
                const data = buffer.getChannelData(0);
                for (let i = 0; i < bufSize; i++) data[i] = Math.random() * 2 - 1;

                const noise = ctx.createBufferSource();
                noise.buffer = buffer;
                const filter = ctx.createBiquadFilter();
                filter.type = "highpass";
                filter.frequency.value = 4500;

                const gain = ctx.createGain();
                gain.gain.setValueAtTime(0.0001, t0);
                gain.gain.exponentialRampToValueAtTime(0.72, t0 + duration - 0.05);
                gain.gain.setValueAtTime(0.0001, t0 + duration);

                noise.connect(filter);
                filter.connect(gain);
                gain.connect(outNode);
                noise.start(t0);
                noise.stop(t0 + duration);
            } catch (e) {}
        }

        // 11. PITCH DIVE
        function synthPitchDive(ctx, startTime, duration = 1.6) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();

                osc.type = "sawtooth";
                osc.frequency.setValueAtTime(950, t0);
                osc.frequency.exponentialRampToValueAtTime(45, t0 + duration);

                gain.gain.setValueAtTime(0.0001, t0);
                gain.gain.linearRampToValueAtTime(0.65, t0 + 0.04);
                gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duration);

                osc.connect(gain);
                gain.connect(outNode);
                osc.start(t0);
                osc.stop(t0 + duration);
            } catch (e) {}
        }

        // 12. UPLIFTER
        function synthUplifter(ctx, startTime, duration = 2.0) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(140, t0);
                osc.frequency.exponentialRampToValueAtTime(3200, t0 + duration);
                gain.gain.setValueAtTime(0.0001, t0);
                gain.gain.linearRampToValueAtTime(0.65, t0 + duration * 0.85);
                gain.gain.exponentialRampToValueAtTime(0.0001, t0 + duration);
                osc.connect(gain);
                gain.connect(outNode);
                osc.start(t0);
                osc.stop(t0 + duration);
            } catch (e) {}
        }

        // 13. DUB SIREN
        function synthDubSiren(ctx, startTime, duration = 1.8) {
            synthSirenRiser(ctx, startTime, duration);
        }

        // 14. SALÃO REVERB
        function synthSalaoReverb(ctx, startTime, duration = 2.0) {
            synthDubEcho(ctx, 120);
        }

        // 15. RADIO AM FILTER
        function synthRadioAmFilter(ctx, startTime, duration = 1.8) {
            synthHpfNoiseSweep(ctx, startTime, duration);
        }

        // 16. PING PONG
        function synthPingPong(ctx, startTime, bpm = 128) {
            synthDubEcho(ctx, bpm);
        }

        // 17. GUNSHOT SLIDE
        function synthGunshotSlide(ctx, startTime, duration = 1.4) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sawtooth";
                osc.frequency.setValueAtTime(800, t0);
                osc.frequency.exponentialRampToValueAtTime(45, t0 + 0.35);
                gain.gain.setValueAtTime(0.85, t0);
                gain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.35);
                osc.connect(gain);
                gain.connect(outNode);
                osc.start(t0);
                osc.stop(t0 + 0.36);
            } catch (e) {}
        }

        // DISPATCHER PRINCIPAL DOS EFEITOS SONOROS DE BALADA
        function playDjClubFx(fxInfo, bpm, durationMs, fromAudio, toAudio) {
            // OBRIGATÓRIO: EFEITOS SÓ PODEM TOCAR NO MODO BALADA & CLUB DJ!
            if (djPlayMode !== "club") return;

            initWebAudio();
            if (!audioCtx) return;
            if (audioCtx.state === "suspended") {
                audioCtx.resume();
            }

            const t0 = audioCtx.currentTime;
            const durSec = (durationMs || 4000) / 1000;
            const dropTime = t0 + (durSec * 0.45);

            // Dispara Auto-Ducking na música para o efeito sobressair na pista
            triggerMusicDucking(Math.min(2.5, durSec * 0.6));

            try {
                const type = (fxInfo && fxInfo.type) ? fxInfo.type : "sub_drop";
                switch (type) {
                    case "airhorn":
                        synthAirHorn(audioCtx, t0);
                        synth808SubDrop(audioCtx, dropTime, 1.3);
                        break;

                    case "spinback":
                        synthSpinback(audioCtx, fromAudio, t0);
                        synth808SubDrop(audioCtx, dropTime, 1.4);
                        break;

                    case "sub_drop":
                        synth808SubDrop(audioCtx, dropTime, 1.5);
                        break;

                    case "stutter_gate":
                    case "riser_drop":
                        synthHpfNoiseSweep(audioCtx, t0, durSec * 0.45);
                        synth808SubDrop(audioCtx, dropTime, 1.3);
                        break;

                    case "siren_riser":
                    case "space_siren":
                        synthSirenRiser(audioCtx, t0, durSec * 0.48);
                        synth808SubDrop(audioCtx, dropTime, 1.2);
                        break;

                    case "jet_flanger":
                    case "guiro_flange":
                        synthJetFlanger(audioCtx, t0, durSec * 0.42);
                        synth808SubDrop(audioCtx, dropTime, 1.2);
                        break;

                    case "snare_buildup":
                        synthSnareRoll(audioCtx, t0, durSec * 0.45, bpm);
                        synth808SubDrop(audioCtx, dropTime, 1.3);
                        break;

                    case "pitch_dive":
                        synthPitchDive(audioCtx, t0, durSec * 0.42);
                        synth808SubDrop(audioCtx, dropTime, 1.2);
                        break;

                    case "uplifter":
                        synthUplifter(audioCtx, t0, durSec * 0.48);
                        synth808SubDrop(audioCtx, dropTime, 1.2);
                        break;

                    case "dub_echo":
                    case "lpf_swell":
                    case "tape_wobble":
                        synthDubEcho(audioCtx, bpm);
                        synth808SubDrop(audioCtx, dropTime, 1.1);
                        break;

                    case "tape_stop":
                        synthSpinback(audioCtx, fromAudio, t0);
                        synthDubEcho(audioCtx, bpm);
                        break;

                    case "vinyl_scratch":
                        synthVinylScratch(audioCtx, t0);
                        synth808SubDrop(audioCtx, dropTime, 1.2);
                        break;

                    case "radio_am":
                        synthRadioAmFilter(audioCtx, t0, durSec * 0.45);
                        synth808SubDrop(audioCtx, dropTime, 1.1);
                        break;

                    case "gunshot":
                        synthGunshotSlide(audioCtx, t0);
                        synth808SubDrop(audioCtx, dropTime, 1.3);
                        break;

                    case "reverse_crash":
                        synthReverseCrash(audioCtx, t0, durSec * 0.45);
                        synth808SubDrop(audioCtx, dropTime, 1.3);
                        break;

                    default:
                        synth808SubDrop(audioCtx, dropTime, 1.3);
                        break;
                }
            } catch (e) {
                console.warn("playDjClubFx warning:", e);
            }
        }

        '''

js, count_syn = re.subn(old_synths_block_pattern, new_synths_block, js, flags=re.DOTALL)
print(f"assets/js/player.js: Motor de Síntese de Efeitos DJ atualizado ({count_syn} ocorrência)")

# 3.6 Expor window.audioCtx e window.testDjFx para inspeção/testes
extra_exports = '''
window.audioCtx = audioCtx;
window.getDjFxDestination = getDjFxDestination;
window.triggerMusicDucking = triggerMusicDucking;
window.testDjFx = function(type) {
    if (!audioCtx) initWebAudio();
    if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
    playDjClubFx({ type: type || "airhorn" }, 130, 4000, null, null);
};
'''

if "window.testDjFx = function" not in js:
    js = js.rstrip() + "\n" + extra_exports
    print("assets/js/player.js: window.testDjFx e audioCtx exportados")

with open("assets/js/player.js", "w", encoding="utf-8") as f:
    f.write(js)

print("Código atualizado com sucesso!")
