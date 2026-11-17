import re
import os

print("Iniciando aplicação dos upgrades no Equalizador e Botão Pause...")

# -------------------------------------------------------------
# 1. ATUALIZAR player_template.html
# -------------------------------------------------------------
with open("player_template.html", "r", encoding="utf-8") as f:
    template_html = f.read()

# Substituir o botão barPlayBtn para garantir precisão absoluta
pattern_btn = r'<button class="bar-btn bar-play" id="barPlayBtn" onclick="togglePlayPause\(\)" title="Play/Pause">\s*<span id="playIconSpan">.*?</span>\s*</button>'
replacement_btn = '''<button class="bar-btn bar-play" id="barPlayBtn" onclick="togglePlayPause()" title="Play/Pause">
                    <span id="playIconSpan">
                        <svg class="control-svg-icon" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="display:block; transform: translateX(1px);">
                            <polygon points="7.5,4.5 19.5,12 7.5,19.5"></polygon>
                        </svg>
                    </span>
                </button>'''

template_html, count_btn = re.subn(pattern_btn, replacement_btn, template_html, flags=re.DOTALL)
print(f"player_template.html: barPlayBtn atualizado ({count_btn} ocorrência)")

with open("player_template.html", "w", encoding="utf-8") as f:
    f.write(template_html)

# -------------------------------------------------------------
# 2. ATUALIZAR assets/js/player.js
# -------------------------------------------------------------
with open("assets/js/player.js", "r", encoding="utf-8") as f:
    js = f.read()

# 2.1 Atualizar EQ_PRESETS com 14 presets e 10 bandas ISO
old_eq_presets_pattern = r'// CONFIGURAÇÕES DE EQUALIZADOR ESTILO SPOTIFY\s*const EQ_PRESETS = \{.*?\};'
new_eq_presets = '''// CONFIGURAÇÕES DE EQUALIZADOR PROFISSIONAL (10 BANDAS ISO & 14 PRESETS)
        const EQ_PRESETS = {
            "padrao": { name: "Padrão (Flat)", icon: "🎵", gains: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] },
            "grave": { name: "Mega Bass / 808", icon: "💥", gains: [8, 9, 6, 3, 0, -1, 0, 1, 2, 2] },
            "funk": { name: "Funk & Mandelão", icon: "🔥", gains: [7, 9, 7, 1, -1, 2, 4, 3, 2, 1] },
            "balada": { name: "Balada / Club", icon: "⚡", gains: [8, 7, 5, 1, -2, 1, 3, 5, 7, 8] },
            "eletronica": { name: "House & Desande", icon: "🌀", gains: [6, 8, 6, 2, -1, 0, 2, 5, 6, 7] },
            "cumbia": { name: "Cumbia & Charanga", icon: "🪘", gains: [3, 5, 6, 3, 2, 3, 4, 3, 4, 5] },
            "gaucho": { name: "Fandango & Vanera", icon: "🪗", gains: [4, 6, 5, 2, 3, 4, 3, 4, 3, 2] },
            "trap": { name: "Trap & Hip-Hop", icon: "🎤", gains: [9, 10, 6, 0, -2, 1, 3, 4, 6, 7] },
            "voz": { name: "Mais Voz / Clareza", icon: "🎙️", gains: [-3, -1, 1, 2, 5, 7, 6, 4, 2, 0] },
            "fone": { name: "Fone de Ouvido Hi-Fi", icon: "🎧", gains: [5, 4, 2, 0, 1, 2, 3, 5, 7, 6] },
            "sala": { name: "Sala / Espacial", icon: "🏛️", gains: [4, 2, -1, 1, 3, 5, 4, 3, 5, 6] },
            "rock": { name: "Rock & Metal", icon: "🎸", gains: [6, 5, 3, 0, -2, 2, 4, 6, 5, 6] },
            "acustico": { name: "Acústico & Voz", icon: "🎻", gains: [-2, 0, 2, 2, 4, 6, 5, 4, 3, 2] },
            "claridade": { name: "Super Clareza", icon: "✨", gains: [-4, -2, 0, 1, 3, 5, 6, 7, 8, 9] }
        };
        let eqPreAmpGain = null;
        let eqPreAmpValue = parseFloat(localStorage.getItem("pref_eq_preamp") || "0");'''

js, count_presets = re.subn(old_eq_presets_pattern, new_eq_presets, js, flags=re.DOTALL)
print(f"assets/js/player.js: EQ_PRESETS atualizado ({count_presets} ocorrência)")

# 2.2 Atualizar WebAudio DSP Chain em initWebAudio()
old_webaudio_pattern = r'// Master Mixer que recebe Deck A e Deck B\s*const deckMixer = audioCtx\.createGain\(\);.*?eqFilters\[eqFilters\.length - 1\]\.connect\(analyserNode\);\s*// Master Gain'
new_webaudio_chain = '''// Master Mixer que recebe Deck A e Deck B
                const deckMixer = audioCtx.createGain();
                deckGainA.connect(deckMixer);
                deckGainB.connect(deckMixer);

                // Pre-Amp Gain (-6 a +6 dB)
                eqPreAmpGain = audioCtx.createGain();
                const initPreAmpLin = Math.pow(10, eqPreAmpValue / 20);
                eqPreAmpGain.gain.value = initPreAmpLin;
                deckMixer.connect(eqPreAmpGain);

                // Equalizador Gráfico de Precisão: 10 Bandas ISO Pro (32Hz até 16kHz)
                const EQ_ISO_FREQS = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000];
                const EQ_ISO_TYPES = ["lowshelf", "peaking", "peaking", "peaking", "peaking", "peaking", "peaking", "peaking", "peaking", "highshelf"];
                eqFilters = EQ_ISO_FREQS.map((f, i) => {
                    const filter = audioCtx.createBiquadFilter();
                    filter.type = EQ_ISO_TYPES[i];
                    filter.frequency.value = f;
                    if (EQ_ISO_TYPES[i] === "peaking") filter.Q.value = 1.4;
                    filter.gain.value = 0;
                    return filter;
                });

                eqPreAmpGain.connect(eqFilters[0]);
                for (let i = 0; i < eqFilters.length - 1; i++) {
                    eqFilters[i].connect(eqFilters[i + 1]);
                }

                // Analisador para o Visualizador em tempo real (Tapped Pre-Master-Gain)
                analyserNode = audioCtx.createAnalyser();
                analyserNode.fftSize = 256;
                analyserNode.smoothingTimeConstant = 0.78;
                eqFilters[eqFilters.length - 1].connect(analyserNode);

                // Master Gain'''

js, count_dsp = re.subn(old_webaudio_pattern, new_webaudio_chain, js, flags=re.DOTALL)
print(f"assets/js/player.js: WebAudio DSP chain atualizado ({count_dsp} ocorrência)")

# 2.3 Atualizar as funções de controle do equalizador: selectEqPreset, onCustomEqChange, etc.
old_eq_funcs_pattern = r'// CONTROLE DO EQUALIZADOR SPOTIFY\s*function selectEqPreset\(presetKey\)\s*\{.*?function closeEqualizerModal\(e\)\s*\{.*?\}'
new_eq_funcs = '''// CONTROLE DO EQUALIZADOR PROFISSIONAL (10 BANDAS ISO, CURVA EM TEMPO REAL, PRE-AMP)
        const PLAY_SVG_ICON = `<svg class="control-svg-icon" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="display:block; transform: translateX(1px);"><polygon points="7.5,4.5 19.5,12 7.5,19.5"></polygon></svg>`;
        const PAUSE_SVG_ICON = `<svg class="control-svg-icon" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="display:block; margin: 0 auto;"><rect x="5.5" y="4.5" width="4" height="15" rx="1.5"></rect><rect x="14.5" y="4.5" width="4" height="15" rx="1.5"></rect></svg>`;

        function selectEqPreset(presetKey) {
            currentEqPreset = presetKey;
            localStorage.setItem("pref_eq_preset", presetKey);
            const preset = EQ_PRESETS[presetKey] || EQ_PRESETS["padrao"];

            Object.keys(EQ_PRESETS).forEach(k => {
                const card = document.getElementById(`eqCard_${k}`);
                if (card) {
                    if (k === presetKey) card.classList.add("active");
                    else card.classList.remove("active");
                }
            });

            const barEqLabel = document.getElementById("barEqLabel");
            if (barEqLabel) {
                const shortName = preset.name.split('/')[0].split('(')[0].trim();
                barEqLabel.textContent = shortName;
            }

            const activeTag = document.getElementById("eqActivePresetTag");
            if (activeTag) activeTag.textContent = `Preset: ${preset.name}`;

            const freqs = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000];
            freqs.forEach((f, idx) => {
                const s = document.getElementById(`eqSlider_${f}`);
                const l = document.getElementById(`eqVal_${f}`);
                const g = (preset.gains && preset.gains[idx] !== undefined) ? preset.gains[idx] : 0;
                if (s) s.value = g;
                if (l) l.textContent = (g > 0 ? `+${g}` : `${g}`) + " dB";
                if (eqFilters && eqFilters[idx] && audioCtx) {
                    try {
                        eqFilters[idx].gain.setTargetAtTime(g, audioCtx.currentTime, 0.04);
                    } catch (e) {}
                }
            });

            drawEqCurve();
        }

        function onCustomEqChange(index, val) {
            val = parseFloat(val);
            const freqs = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000];
            const f = freqs[index];
            const l = document.getElementById(`eqVal_${f}`);
            if (l) l.textContent = (val > 0 ? `+${val}` : `${val}`) + " dB";
            if (eqFilters && eqFilters[index] && audioCtx) {
                try {
                    eqFilters[index].gain.setTargetAtTime(val, audioCtx.currentTime, 0.04);
                } catch (e) {}
            }

            // Desmarcar presets ativos (customizado)
            Object.keys(EQ_PRESETS).forEach(k => {
                const card = document.getElementById(`eqCard_${k}`);
                if (card) card.classList.remove("active");
            });
            const activeTag = document.getElementById("eqActivePresetTag");
            if (activeTag) activeTag.textContent = "Preset: Personalizado (Custom)";
            const barEqLabel = document.getElementById("barEqLabel");
            if (barEqLabel) barEqLabel.textContent = "Custom";

            drawEqCurve();
        }

        function resetEqToFlat() {
            selectEqPreset("padrao");
            setEqPreAmp(0);
            const preSlider = document.getElementById("eqPreAmpSlider");
            if (preSlider) preSlider.value = 0;
        }

        function setEqPreAmp(dbVal) {
            eqPreAmpValue = parseFloat(dbVal);
            localStorage.setItem("pref_eq_preamp", eqPreAmpValue);
            const lbl = document.getElementById("eqPreAmpVal");
            if (lbl) {
                lbl.textContent = (eqPreAmpValue > 0 ? `+${eqPreAmpValue}` : `${eqPreAmpValue}`) + " dB";
            }
            if (eqPreAmpGain && audioCtx) {
                try {
                    const linearGain = Math.pow(10, eqPreAmpValue / 20);
                    eqPreAmpGain.gain.setTargetAtTime(linearGain, audioCtx.currentTime, 0.04);
                } catch (e) {}
            }
            drawEqCurve();
        }

        function drawEqCurve() {
            const canvas = document.getElementById("eqCurveCanvas");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");
            if (!ctx) return;

            const width = canvas.width;
            const height = canvas.height;
            ctx.clearRect(0, 0, width, height);

            // Linhas de dB (-12, -6, 0, +6, +12)
            const dbSteps = [-12, -6, 0, 6, 12];
            ctx.lineWidth = 1;
            dbSteps.forEach(db => {
                const y = height / 2 - (db / 16) * (height / 2 - 8);
                ctx.strokeStyle = db === 0 ? "rgba(255, 255, 255, 0.22)" : "rgba(255, 255, 255, 0.06)";
                ctx.setLineDash(db === 0 ? [] : [2, 4]);
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();

                if (db === 0 || db === 12 || db === -12) {
                    ctx.fillStyle = "rgba(255, 255, 255, 0.35)";
                    ctx.font = "9px system-ui, sans-serif";
                    ctx.fillText((db > 0 ? `+${db}` : `${db}`) + "dB", 6, y - 2);
                }
            });
            ctx.setLineDash([]);

            // Freq Markers
            const markerFreqs = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000];
            const minF = 20;
            const maxF = 20000;
            const logMin = Math.log10(minF);
            const logMax = Math.log10(maxF);

            markerFreqs.forEach(f => {
                const x = ((Math.log10(f) - logMin) / (logMax - logMin)) * width;
                ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
                ctx.stroke();
            });

            // Resposta de frequência total
            const numPoints = 120;
            const freqs = new Float32Array(numPoints);
            for (let i = 0; i < numPoints; i++) {
                freqs[i] = Math.pow(10, logMin + (i / (numPoints - 1)) * (logMax - logMin));
            }

            const totalDb = new Float32Array(numPoints);
            const preAmpDb = typeof eqPreAmpValue === "number" ? eqPreAmpValue : 0;
            for (let i = 0; i < numPoints; i++) {
                totalDb[i] = preAmpDb;
            }

            if (eqFilters && eqFilters.length === 10 && audioCtx) {
                const magResponse = new Float32Array(numPoints);
                const phaseResponse = new Float32Array(numPoints);
                for (let j = 0; j < eqFilters.length; j++) {
                    eqFilters[j].getFrequencyResponse(freqs, magResponse, phaseResponse);
                    for (let i = 0; i < numPoints; i++) {
                        totalDb[i] += 20 * Math.log10(Math.max(magResponse[i], 1e-4));
                    }
                }
            } else {
                // Cálculo analítico preciso caso o WebAudio ainda não tenha recebido primeiro toque
                const sliderFreqs = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000];
                const sliderGains = sliderFreqs.map(f => {
                    const s = document.getElementById(`eqSlider_${f}`);
                    return s ? parseFloat(s.value) : 0;
                });
                for (let i = 0; i < numPoints; i++) {
                    const f = freqs[i];
                    let g = 0;
                    for (let j = 0; j < sliderFreqs.length; j++) {
                        const dist = Math.abs(Math.log2(f / sliderFreqs[j]));
                        const weight = Math.exp(-dist * dist * 1.5);
                        g += sliderGains[j] * weight;
                    }
                    totalDb[i] += g;
                }
            }

            // Preenchimento com gradiente moderno
            const zeroY = height / 2;
            ctx.beginPath();
            ctx.moveTo(0, zeroY);

            for (let i = 0; i < numPoints; i++) {
                const x = (i / (numPoints - 1)) * width;
                const clampedDb = Math.max(-16, Math.min(16, totalDb[i]));
                const y = height / 2 - (clampedDb / 16) * (height / 2 - 8);
                if (i === 0) ctx.lineTo(0, y);
                else ctx.lineTo(x, y);
            }
            ctx.lineTo(width, zeroY);
            ctx.closePath();

            const fillGrad = ctx.createLinearGradient(0, 0, 0, height);
            fillGrad.addColorStop(0, "rgba(255, 0, 128, 0.25)");
            fillGrad.addColorStop(0.5, "rgba(0, 242, 254, 0.18)");
            fillGrad.addColorStop(1, "rgba(0, 242, 254, 0.02)");
            ctx.fillStyle = fillGrad;
            ctx.fill();

            // Linha suave de resposta
            ctx.beginPath();
            for (let i = 0; i < numPoints; i++) {
                const x = (i / (numPoints - 1)) * width;
                const clampedDb = Math.max(-16, Math.min(16, totalDb[i]));
                const y = height / 2 - (clampedDb / 16) * (height / 2 - 8);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            const strokeGrad = ctx.createLinearGradient(0, 0, width, 0);
            strokeGrad.addColorStop(0, "#00f2fe");
            strokeGrad.addColorStop(0.5, "#4facfe");
            strokeGrad.addColorStop(1, "#ff007f");
            ctx.strokeStyle = strokeGrad;
            ctx.lineWidth = 2.2;
            ctx.stroke();
        }

        function openEqualizerModal() {
            const m = document.getElementById("equalizerModal");
            if (m) m.classList.add("open");
            selectEqPreset(currentEqPreset);
            const preSlider = document.getElementById("eqPreAmpSlider");
            if (preSlider) preSlider.value = eqPreAmpValue;
            const preVal = document.getElementById("eqPreAmpVal");
            if (preVal) preVal.textContent = (eqPreAmpValue > 0 ? `+${eqPreAmpValue}` : `${eqPreAmpValue}`) + " dB";
            updateVolumeUI();
            setTimeout(drawEqCurve, 40);
        }

        function closeEqualizerModal(e) {
            if (e && e.target && e.target.id !== "equalizerModal") return;
            const m = document.getElementById("equalizerModal");
            if (m) m.classList.remove("open");
        }'''

js, count_eq_f = re.subn(old_eq_funcs_pattern, new_eq_funcs, js, flags=re.DOTALL)
print(f"assets/js/player.js: EQ funcs atualizadas ({count_eq_f} ocorrência)")

# 2.4 Atualizar updatePlayPauseButtons com SVG simétrico
old_play_pause_pattern = r'function updatePlayPauseButtons\(isPlaying\)\s*\{.*?updateTurntablesState\(\);\s*\}'
new_play_pause = '''function updatePlayPauseButtons(isPlaying) {
            const barBtn = document.getElementById("barPlayBtn");
            const playIconSpan = document.getElementById("playIconSpan");
            if (barBtn) {
                if (isPlaying) {
                    barBtn.classList.add("is-playing");
                    if (playIconSpan) playIconSpan.innerHTML = PAUSE_SVG_ICON;
                    else barBtn.innerHTML = PAUSE_SVG_ICON;
                } else {
                    barBtn.classList.remove("is-playing");
                    if (playIconSpan) playIconSpan.innerHTML = PLAY_SVG_ICON;
                    else barBtn.innerHTML = PLAY_SVG_ICON;
                }
            }
            updateTurntablesState();
        }'''

js, count_pp = re.subn(old_play_pause_pattern, new_play_pause, js, flags=re.DOTALL)
print(f"assets/js/player.js: updatePlayPauseButtons atualizado ({count_pp} ocorrência)")

# 2.5 Adicionar exports no final de assets/js/player.js
window_exports = '''
window.selectEqPreset = selectEqPreset;
window.onCustomEqChange = onCustomEqChange;
window.resetEqToFlat = resetEqToFlat;
window.setEqPreAmp = setEqPreAmp;
window.drawEqCurve = drawEqCurve;
window.openEqualizerModal = openEqualizerModal;
window.closeEqualizerModal = closeEqualizerModal;
window.updatePlayPauseButtons = updatePlayPauseButtons;
window.EQ_PRESETS = EQ_PRESETS;
'''

if "window.drawEqCurve = drawEqCurve;" not in js:
    js = js.rstrip() + "\n" + window_exports
    print("assets/js/player.js: window exports adicionados")

with open("assets/js/player.js", "w", encoding="utf-8") as f:
    f.write(js)

print("assets/js/player.js atualizado com sucesso!")
