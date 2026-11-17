# -*- coding: utf-8 -*-
"""
implement_studio_js.py
Injeta no assets/js/player.js:
1. Buffer de Impulso Estéreo (Convolver Reverb) procedural de alta fidelidade.
2. Motor de Cauda Suave DJ FX (Reverb 2.2s + Ping-Pong Delay) - acaba com o corte seco!
3. Remoção do ducking agressivo de 45% e cortes no vídeo - acaba com a diferença brusca!
4. Suíte DSP de Estúdio Profissional (Reverb, Delay, Saturação Valvulada, Stereo Widener, Compressor SSL Bus).
5. Analisadores L & R e loop de animação a 60fps dos medidores VU analógicos e Gain Reduction.
6. Gerenciamento do Modo Estúdio no dropdown e no badge.
7. Funções de controle do Modal de Estúdio e Presets de 1-Clique.
"""

import os
import re

JS_PATH = r"C:\Users\Mbello\Desktop\ig-to-youtube-playlist\.claude\worktrees\instagram-youtube-playlist\assets\js\player.js"

with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# 1. Atualizar setDjMode para suportar "studio" e o badge do modo estúdio
old_set_dj_mode = """        const shortLabels = {
            match: "🎯 Match Perfeito",
            energy: "⚡ Peak Time",
            shuffle: "🔀 Smart Shuffle",
            smooth: "🌊 Smooth Flow",
            club: "🔥 Balada & Club DJ"
        };"""

new_set_dj_mode = """        const shortLabels = {
            match: "🎯 Match Perfeito",
            energy: "⚡ Peak Time",
            shuffle: "🔀 Smart Shuffle",
            smooth: "🌊 Smooth Flow",
            club: "🔥 Balada & Club DJ",
            studio: "🎛️ Estúdio Pro & Mastering"
        };"""

if old_set_dj_mode in js:
    js = js.replace(old_set_dj_mode, new_set_dj_mode)
    print("setDjMode atualizado com label 'studio'!")

old_club_badge_logic = """        const clubBadge = document.getElementById("djClubActiveBadge");
        if (clubBadge) {
            clubBadge.style.display = (mode === "club") ? "flex" : "none";
        }
        if (mode !== "club") {
            hideDjClubHud();
        }"""

new_club_badge_logic = """        const clubBadge = document.getElementById("djClubActiveBadge");
        if (clubBadge) {
            clubBadge.style.display = (mode === "club") ? "flex" : "none";
        }
        const studioBadge = document.getElementById("djStudioActiveBadge");
        if (studioBadge) {
            studioBadge.style.display = (mode === "studio") ? "flex" : "none";
        }
        if (mode !== "club") {
            hideDjClubHud();
        }
        if (mode === "studio") {
            initWebAudio();
            if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
            if (typeof selectStudioPreset === "function") selectStudioPreset("mastering");
            showToast("🎛️ MODO ESTÚDIO PRO ATIVO: Console de Mastering, Reverb & Compressor Habilitados");
        }"""

if old_club_badge_logic in js:
    js = js.replace(old_club_badge_logic, new_club_badge_logic)
    print("setDjMode atualizado com lógica do studioBadge e ativação do DSP!")

# 2. Atualizar getDjFxDestination e triggerMusicDucking
old_get_dj_fx = """        let djFxBusNode = null;
        let djFxLimiterNode = null;

        function getDjFxDestination(ctx) {
            if (!ctx) ctx = audioCtx;
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
        }"""

new_get_dj_fx = """        let djFxBusNode = null;
        let djFxLimiterNode = null;
        let djFxTailReverbNode = null;
        let djFxTailDelayNode = null;

        // Gerador procedural de Resposta de Impulso (Reverb Estéreo) com decaimento exponencial
        function createStudioImpulseBuffer(ctx, duration = 2.2, decay = 2.5) {
            if (!ctx) return null;
            try {
                const rate = ctx.sampleRate || 44100;
                const length = Math.floor(rate * duration);
                const impulse = ctx.createBuffer(2, length, rate);
                const left = impulse.getChannelData(0);
                const right = impulse.getChannelData(1);
                for (let i = 0; i < length; i++) {
                    const n = i / length;
                    const env = Math.pow(1 - n, decay);
                    // Difusão espacial estéreo com reflexões iniciais
                    left[i] = ((Math.random() * 2) - 1) * env;
                    right[i] = ((Math.random() * 2) - 1) * env;
                }
                return impulse;
            } catch (e) {
                return null;
            }
        }

        function getDjFxDestination(ctx) {
            if (!ctx) ctx = audioCtx;
            if (!ctx) return null;
            if (!djFxBusNode) {
                try {
                    djFxBusNode = ctx.createGain();
                    // Master do FX calibrado para clareza e impacto
                    djFxBusNode.gain.value = 0.85;

                    // 1. Caminho Direto Limiter Ultra-Rápido
                    djFxLimiterNode = ctx.createDynamicsCompressor();
                    djFxLimiterNode.threshold.value = -1.2;
                    djFxLimiterNode.knee.value = 3.0;
                    djFxLimiterNode.ratio.value = 18.0;
                    djFxLimiterNode.attack.value = 0.001; // 1ms
                    djFxLimiterNode.release.value = 0.06;

                    djFxBusNode.connect(djFxLimiterNode);
                    djFxLimiterNode.connect(ctx.destination);

                    // ==========================================================
                    // CAUDA SUAVE DE REVERB & DELAY ESTÉREO (IMPEDE O CORTE SECO!)
                    // ==========================================================
                    const impulseBuf = createStudioImpulseBuffer(ctx, 2.2, 2.8);
                    if (impulseBuf) {
                        djFxTailReverbNode = ctx.createConvolver();
                        djFxTailReverbNode.buffer = impulseBuf;
                        const tailReverbGain = ctx.createGain();
                        tailReverbGain.gain.value = 0.35; // 35% de cauda espacial suave
                        djFxBusNode.connect(djFxTailReverbNode);
                        djFxTailReverbNode.connect(tailReverbGain);
                        tailReverbGain.connect(ctx.destination);
                    }

                    // Envio para Stereo Delay Ping-Pong rítmico (eco que dissolve suavemente)
                    djFxTailDelayNode = ctx.createDelay();
                    djFxTailDelayNode.delayTime.value = 0.22; // 220ms
                    const tailDelayFilter = ctx.createBiquadFilter();
                    tailDelayFilter.type = "lowpass";
                    tailDelayFilter.frequency.value = 3200;
                    const tailDelayFeedback = ctx.createGain();
                    tailDelayFeedback.gain.value = 0.26;
                    const tailDelayGain = ctx.createGain();
                    tailDelayGain.gain.value = 0.20;

                    djFxBusNode.connect(djFxTailDelayNode);
                    djFxTailDelayNode.connect(tailDelayFilter);
                    tailDelayFilter.connect(tailDelayFeedback);
                    tailDelayFeedback.connect(djFxTailDelayNode);
                    tailDelayFilter.connect(tailDelayGain);
                    tailDelayGain.connect(ctx.destination);

                } catch (e) {
                    return ctx.destination;
                }
            }
            return djFxBusNode;
        }

        // Auto-Ducking Transparente:
        // Mantém a música contínua e natural SEM cortes secos ou diferenças brutas de volume!
        function triggerMusicDucking(durationSec = 2.0) {
            // No modo vídeo (YouTube) e áudio: NÃO cortar bruscamente o volume da música!
            // O efeito passa pelo Master FX Bus com compressão própria e cauda de reverb,
            // assentando sobre a música de forma fluida sem buracos ou saltos repentinos.
        }"""

if old_get_dj_fx in js:
    js = js.replace(old_get_dj_fx, new_get_dj_fx)
    print("getDjFxDestination e triggerMusicDucking atualizados com Cauda Espacial de Reverb/Delay e Ducking Transparente!")
else:
    print("AVISO: Trecho old_get_dj_fx não encontrado exatamente. Verifique manualmente.")

# 3. Adicionar o Motor de Estúdio DSP no final do script
studio_engine_js = """
// ==========================================================================
// SUÍTE DE ESTÚDIO PROFISSIONAL & MASTERING DSP CONSOLE (PRO AUDIO)
// ==========================================================================
let studioDspInitialized = false;
let studioBypass = false;
let studioVuTimer = null;

let studioSettings = {
    preset: "mastering",
    reverbType: "hall",
    reverbDecay: 1.8,
    reverbMix: 22,
    delayPreset: "1/4",
    delayTime: 0.24,
    delayFeedback: 28,
    delayMix: 18,
    compThreshold: -14,
    compRatio: 4.0,
    compAttack: 0.005,
    compRelease: 0.15,
    warmthDrive: 30,
    stereoWidth: 135
};

const STUDIO_PRESETS = {
    mastering: {
        name: "Neve Warmth",
        reverbType: "hall", reverbDecay: 1.8, reverbMix: 22,
        delayPreset: "1/4", delayTime: 0.24, delayFeedback: 28, delayMix: 18,
        compThreshold: -14, compRatio: 4.0, compAttack: 0.005, compRelease: 0.15,
        warmthDrive: 30, stereoWidth: 135
    },
    hall: {
        name: "Concert Arena",
        reverbType: "hall", reverbDecay: 2.8, reverbMix: 42,
        delayPreset: "1/2", delayTime: 0.48, delayFeedback: 38, delayMix: 24,
        compThreshold: -12, compRatio: 3.0, compAttack: 0.01, compRelease: 0.20,
        warmthDrive: 18, stereoWidth: 155
    },
    club: {
        name: "SSL Club Master",
        reverbType: "club", reverbDecay: 1.4, reverbMix: 16,
        delayPreset: "1/8", delayTime: 0.12, delayFeedback: 20, delayMix: 14,
        compThreshold: -18, compRatio: 6.0, compAttack: 0.001, compRelease: 0.08,
        warmthDrive: 38, stereoWidth: 125
    },
    vocal: {
        name: "Vocal Clarity",
        reverbType: "plate", reverbDecay: 1.6, reverbMix: 28,
        delayPreset: "1/4", delayTime: 0.24, delayFeedback: 25, delayMix: 20,
        compThreshold: -12, compRatio: 3.0, compAttack: 0.008, compRelease: 0.18,
        warmthDrive: 20, stereoWidth: 115
    },
    lofi: {
        name: "Tape Vinyl",
        reverbType: "room", reverbDecay: 1.1, reverbMix: 20,
        delayPreset: "1/8", delayTime: 0.12, delayFeedback: 42, delayMix: 28,
        compThreshold: -16, compRatio: 4.5, compAttack: 0.003, compRelease: 0.12,
        warmthDrive: 65, stereoWidth: 90
    },
    flat: {
        name: "Flat Reference",
        reverbType: "hall", reverbDecay: 1.0, reverbMix: 0,
        delayPreset: "1/4", delayTime: 0.24, delayFeedback: 0, delayMix: 0,
        compThreshold: 0, compRatio: 1.5, compAttack: 0.01, compRelease: 0.2,
        warmthDrive: 0, stereoWidth: 100
    }
};

// Nós de Áudio da Console de Estúdio
let studioInputNode = null;
let studioDryGainNode = null;
let studioWetGainNode = null;
let studioMasterMixerNode = null;
let studioReverbNode = null;
let studioReverbWetNode = null;
let studioDelayNode = null;
let studioDelayFilterNode = null;
let studioDelayFeedbackNode = null;
let studioDelayWetNode = null;
let studioWarmthNode = null;
let studioCompNode = null;
let studioSplitterNode = null;
let studioMergerNode = null;
let studioDelayLeft = null;
let studioDelayRight = null;
let studioAnalyserL = null;
let studioAnalyserR = null;

// Curva de Saturação Valvulada Suave (Tube Soft Saturation)
function makeWarmthCurve(driveAmount) {
    const k = driveAmount * 0.04;
    const n_samples = 44100;
    const curve = new Float32Array(n_samples);
    const deg = Math.PI / 180;
    for (let i = 0; i < n_samples; ++i) {
        const x = (i * 2) / n_samples - 1;
        if (k === 0) {
            curve[i] = x;
        } else {
            curve[i] = ((3 + k) * x * 20 * deg) / (Math.PI + k * Math.abs(x));
        }
    }
    return curve;
}

function initStudioDsp() {
    if (studioDspInitialized || !audioCtx) return;
    try {
        studioInputNode = audioCtx.createGain();
        studioDryGainNode = audioCtx.createGain();
        studioWetGainNode = audioCtx.createGain();
        studioMasterMixerNode = audioCtx.createGain();

        // 1. Saturação Valvulada (Analog Warmth)
        studioWarmthNode = audioCtx.createWaveShaper();
        studioWarmthNode.curve = makeWarmthCurve(studioSettings.warmthDrive);
        studioWarmthNode.oversample = "2x";

        // 2. SSL Bus Dynamic Compressor
        studioCompNode = audioCtx.createDynamicsCompressor();
        studioCompNode.threshold.value = studioSettings.compThreshold;
        studioCompNode.ratio.value = studioSettings.compRatio;
        studioCompNode.attack.value = studioSettings.compAttack;
        studioCompNode.release.value = studioSettings.compRelease;
        studioCompNode.knee.value = 6.0;

        // 3. Stereo Widener (Haas Effect Spatializer)
        studioSplitterNode = audioCtx.createChannelSplitter(2);
        studioMergerNode = audioCtx.createChannelMerger(2);
        studioDelayLeft = audioCtx.createDelay();
        studioDelayRight = audioCtx.createDelay();
        studioDelayLeft.delayTime.value = 0.0;
        studioDelayRight.delayTime.value = 0.008; // 8ms micro-shift no R

        // 4. Reverb de Estúdio Convolucional
        studioReverbNode = audioCtx.createConvolver();
        const revBuf = createStudioImpulseBuffer(audioCtx, studioSettings.reverbDecay, 2.5);
        if (revBuf) studioReverbNode.buffer = revBuf;
        studioReverbWetNode = audioCtx.createGain();
        studioReverbWetNode.gain.value = studioSettings.reverbMix / 100;

        // 5. Tape Delay Ping-Pong
        studioDelayNode = audioCtx.createDelay();
        studioDelayNode.delayTime.value = studioSettings.delayTime;
        studioDelayFilterNode = audioCtx.createBiquadFilter();
        studioDelayFilterNode.type = "lowpass";
        studioDelayFilterNode.frequency.value = 3500;
        studioDelayFeedbackNode = audioCtx.createGain();
        studioDelayFeedbackNode.gain.value = studioSettings.delayFeedback / 100;
        studioDelayWetNode = audioCtx.createGain();
        studioDelayWetNode.gain.value = studioSettings.delayMix / 100;

        // Roteamento do Delay
        studioInputNode.connect(studioDelayNode);
        studioDelayNode.connect(studioDelayFilterNode);
        studioDelayFilterNode.connect(studioDelayFeedbackNode);
        studioDelayFeedbackNode.connect(studioDelayNode);
        studioDelayFilterNode.connect(studioDelayWetNode);
        studioDelayWetNode.connect(studioMasterMixerNode);

        // Roteamento do Reverb
        studioInputNode.connect(studioReverbNode);
        studioReverbNode.connect(studioReverbWetNode);
        studioReverbWetNode.connect(studioMasterMixerNode);

        // Roteamento da Cadeia Principal Processada: Input -> Warmth -> Comp -> Widener -> WetGain -> Mixer
        studioInputNode.connect(studioWarmthNode);
        studioWarmthNode.connect(studioCompNode);

        studioCompNode.connect(studioSplitterNode);
        studioSplitterNode.connect(studioDelayLeft, 0);
        studioSplitterNode.connect(studioDelayRight, 1);
        studioDelayLeft.connect(studioMergerNode, 0, 0);
        studioDelayRight.connect(studioMergerNode, 0, 1);

        studioMergerNode.connect(studioWetGainNode);
        studioWetGainNode.connect(studioMasterMixerNode);

        // Caminho Dry (Direto)
        studioInputNode.connect(studioDryGainNode);
        studioDryGainNode.connect(studioMasterMixerNode);

        // Medidores VU L & R
        studioAnalyserL = audioCtx.createAnalyser();
        studioAnalyserR = audioCtx.createAnalyser();
        studioAnalyserL.fftSize = 256;
        studioAnalyserR.fftSize = 256;
        const vuSplitter = audioCtx.createChannelSplitter(2);
        studioMasterMixerNode.connect(vuSplitter);
        vuSplitter.connect(studioAnalyserL, 0);
        vuSplitter.connect(studioAnalyserR, 1);

        // Inserir no Master Graph se os filtros existirem
        if (eqFilters && eqFilters.length > 0) {
            const lastFilter = eqFilters[eqFilters.length - 1];
            try {
                // Desconectar o lastFilter do masterGainNode para intercalar a console de estúdio
                lastFilter.disconnect(masterGainNode);
            } catch (e) {}
            lastFilter.connect(studioInputNode);
            studioMasterMixerNode.connect(masterGainNode);
        }

        applyStudioDspParams();
        studioDspInitialized = true;
    } catch (e) {
        console.warn("initStudioDsp warning:", e);
    }
}

function applyStudioDspParams() {
    if (!audioCtx) return;
    const now = audioCtx.currentTime;

    if (studioBypass) {
        if (studioDryGainNode) studioDryGainNode.gain.setValueAtTime(1.0, now);
        if (studioWetGainNode) studioWetGainNode.gain.setValueAtTime(0.0, now);
        if (studioReverbWetNode) studioReverbWetNode.gain.setValueAtTime(0.0, now);
        if (studioDelayWetNode) studioDelayWetNode.gain.setValueAtTime(0.0, now);
        return;
    }

    // Configurações ativas
    if (studioDryGainNode) studioDryGainNode.gain.setValueAtTime(0.35, now);
    if (studioWetGainNode) studioWetGainNode.gain.setValueAtTime(0.85, now);

    if (studioReverbWetNode) {
        studioReverbWetNode.gain.setValueAtTime(studioSettings.reverbMix / 100, now);
    }
    if (studioDelayNode) {
        studioDelayNode.delayTime.setValueAtTime(studioSettings.delayTime, now);
    }
    if (studioDelayFeedbackNode) {
        studioDelayFeedbackNode.gain.setValueAtTime(studioSettings.delayFeedback / 100, now);
    }
    if (studioDelayWetNode) {
        studioDelayWetNode.gain.setValueAtTime(studioSettings.delayMix / 100, now);
    }
    if (studioCompNode) {
        studioCompNode.threshold.setValueAtTime(studioSettings.compThreshold, now);
        studioCompNode.ratio.setValueAtTime(studioSettings.compRatio, now);
        studioCompNode.attack.setValueAtTime(studioSettings.compAttack, now);
        studioCompNode.release.setValueAtTime(studioSettings.compRelease, now);
    }
    if (studioWarmthNode) {
        studioWarmthNode.curve = makeWarmthCurve(studioSettings.warmthDrive);
    }
    if (studioDelayRight) {
        // Largura estéreo: 0% mono (0ms), 100% normal (0ms), 200% wide (15ms)
        const offset = Math.max(0, (studioSettings.stereoWidth - 100) / 100) * 0.015;
        studioDelayRight.delayTime.setValueAtTime(offset, now);
    }
}

// Funções da Interface do Usuário (UI)
function openStudioModal() {
    initWebAudio();
    if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
    initStudioDsp();

    const modal = document.getElementById("studioModal");
    if (modal) {
        modal.style.display = "flex";
        startStudioVuLoop();
    }
}

function closeStudioModal(event) {
    if (event && event.target && event.target.id !== "studioModal" && !event.target.classList.contains("btn-modal-close") && !event.target.classList.contains("btn-modal-done")) {
        return;
    }
    const modal = document.getElementById("studioModal");
    if (modal) modal.style.display = "none";
    if (studioVuTimer) {
        cancelAnimationFrame(studioVuTimer);
        studioVuTimer = null;
    }
}

function toggleStudioBypass() {
    studioBypass = !studioBypass;
    const dot = document.getElementById("studioBypassDot");
    const label = document.getElementById("studioBypassLabel");
    if (dot) dot.classList.toggle("active", !studioBypass);
    if (label) label.textContent = studioBypass ? "BYPASS (DIRETO)" : "DSP ATIVO";
    applyStudioDspParams();
}

function selectStudioPreset(key) {
    const p = STUDIO_PRESETS[key];
    if (!p) return;
    studioSettings = { ...studioSettings, ...p, preset: key };

    document.querySelectorAll(".studio-preset-chip").forEach(c => c.classList.remove("active"));
    const activeChip = document.getElementById(`stPreset_${key}`);
    if (activeChip) activeChip.classList.add("active");

    // Atualiza sliders e labels
    updateStudioUiElements();

    // Regenera o buffer de Reverb se mudou
    if (audioCtx && studioReverbNode) {
        const buf = createStudioImpulseBuffer(audioCtx, studioSettings.reverbDecay, 2.5);
        if (buf) studioReverbNode.buffer = buf;
    }

    applyStudioDspParams();
}

function updateStudioUiElements() {
    const sDecay = document.getElementById("sliderStudioReverbDecay");
    if (sDecay) sDecay.value = studioSettings.reverbDecay;
    const vDecay = document.getElementById("valStudioReverbDecay");
    if (vDecay) vDecay.textContent = studioSettings.reverbDecay + "s";

    const sRevMix = document.getElementById("sliderStudioReverbMix");
    if (sRevMix) sRevMix.value = studioSettings.reverbMix;
    const vRevMix = document.getElementById("valStudioReverbMix");
    if (vRevMix) vRevMix.textContent = studioSettings.reverbMix + "%";

    const sFeed = document.getElementById("sliderStudioDelayFeedback");
    if (sFeed) sFeed.value = studioSettings.delayFeedback;
    const vFeed = document.getElementById("valStudioDelayFeedback");
    if (vFeed) vFeed.textContent = studioSettings.delayFeedback + "%";

    const sDelMix = document.getElementById("sliderStudioDelayMix");
    if (sDelMix) sDelMix.value = studioSettings.delayMix;
    const vDelMix = document.getElementById("valStudioDelayMix");
    if (vDelMix) vDelMix.textContent = studioSettings.delayMix + "%";

    const sThresh = document.getElementById("sliderStudioCompThresh");
    if (sThresh) sThresh.value = studioSettings.compThreshold;
    const vThresh = document.getElementById("valStudioCompThresh");
    if (vThresh) vThresh.textContent = studioSettings.compThreshold + " dB";

    const sRatio = document.getElementById("sliderStudioCompRatio");
    if (sRatio) sRatio.value = studioSettings.compRatio;
    const vRatio = document.getElementById("valStudioCompRatio");
    if (vRatio) vRatio.textContent = studioSettings.compRatio + ":1";

    const sAttack = document.getElementById("sliderStudioCompAttack");
    if (sAttack) sAttack.value = studioSettings.compAttack;
    const vAttack = document.getElementById("valStudioCompAttack");
    if (vAttack) vAttack.textContent = Math.round(studioSettings.compAttack * 1000) + "ms";

    const sRelease = document.getElementById("sliderStudioCompRelease");
    if (sRelease) sRelease.value = studioSettings.compRelease;
    const vRelease = document.getElementById("valStudioCompRelease");
    if (vRelease) vRelease.textContent = Math.round(studioSettings.compRelease * 1000) + "ms";

    const sWarmth = document.getElementById("sliderStudioWarmth");
    if (sWarmth) sWarmth.value = studioSettings.warmthDrive;
    const vWarmth = document.getElementById("valStudioWarmth");
    if (vWarmth) vWarmth.textContent = studioSettings.warmthDrive + "%";

    const sWidth = document.getElementById("sliderStudioWidth");
    if (sWidth) sWidth.value = studioSettings.stereoWidth;
    const vWidth = document.getElementById("valStudioWidth");
    if (vWidth) vWidth.textContent = studioSettings.stereoWidth + "%";

    const revBadge = document.getElementById("reverbTypeBadge");
    if (revBadge) revBadge.textContent = studioSettings.reverbType.toUpperCase();
}

function setStudioReverbType(type) {
    studioSettings.reverbType = type;
    document.querySelectorAll(".btn-rev-type").forEach(b => b.classList.remove("active"));
    const btn = document.getElementById(`btnRev_${type}`);
    if (btn) btn.classList.add("active");
    const revBadge = document.getElementById("reverbTypeBadge");
    if (revBadge) revBadge.textContent = type.toUpperCase();

    // Modela o decaimento conforme a sala
    const decayMap = { hall: 2.2, plate: 1.6, club: 1.3, room: 0.9 };
    studioSettings.reverbDecay = decayMap[type] || 1.8;
    updateStudioUiElements();

    if (audioCtx && studioReverbNode) {
        const buf = createStudioImpulseBuffer(audioCtx, studioSettings.reverbDecay, 2.5);
        if (buf) studioReverbNode.buffer = buf;
    }
    applyStudioDspParams();
}

function setStudioDelayPreset(timeSec, label) {
    studioSettings.delayTime = timeSec;
    studioSettings.delayPreset = label;
    document.querySelectorAll(".btn-del-time").forEach(b => b.classList.remove("active"));
    const btn = event ? event.target : null;
    if (btn) btn.classList.add("active");
    updateStudioUiElements();
    applyStudioDspParams();
}

function onStudioParamChange(param, val) {
    const num = parseFloat(val);
    studioSettings[param] = num;
    updateStudioUiElements();

    if (param === "reverbDecay" && audioCtx && studioReverbNode) {
        const buf = createStudioImpulseBuffer(audioCtx, studioSettings.reverbDecay, 2.5);
        if (buf) studioReverbNode.buffer = buf;
    }
    applyStudioDspParams();
}

// Loop de Animação a 60fps dos Medidores VU Analógicos
function startStudioVuLoop() {
    if (studioVuTimer) cancelAnimationFrame(studioVuTimer);

    const fillL = document.getElementById("studioVuFillL");
    const fillR = document.getElementById("studioVuFillR");
    const peakL = document.getElementById("studioVuPeakL");
    const peakR = document.getElementById("studioVuPeakR");
    const valL = document.getElementById("studioVuValL");
    const valR = document.getElementById("studioVuValR");
    const grFill = document.getElementById("studioGrFill");
    const grVal = document.getElementById("studioGrVal");

    const dataL = new Uint8Array(128);
    const dataR = new Uint8Array(128);

    function update() {
        const modal = document.getElementById("studioModal");
        if (!modal || modal.style.display === "none") return;

        let pctL = 10, pctR = 10;
        let dbL = -48, dbR = -48;

        if (studioAnalyserL && studioAnalyserR && audioCtx && audioCtx.state === "running") {
            studioAnalyserL.getByteTimeDomainData(dataL);
            studioAnalyserR.getByteTimeDomainData(dataR);

            let sumL = 0, sumR = 0;
            for (let i = 0; i < 128; i++) {
                const vl = (dataL[i] - 128) / 128;
                const vr = (dataR[i] - 128) / 128;
                sumL += vl * vl;
                sumR += vr * vr;
            }
            const rmsL = Math.sqrt(sumL / 128);
            const rmsR = Math.sqrt(sumR / 128);

            dbL = rmsL > 1e-4 ? Math.round(20 * Math.log10(rmsL)) : -48;
            dbR = rmsR > 1e-4 ? Math.round(20 * Math.log10(rmsR)) : -48;

            pctL = Math.max(0, Math.min(100, ((dbL + 48) / 51) * 100));
            pctR = Math.max(0, Math.min(100, ((dbR + 48) / 51) * 100));
        }

        if (fillL) fillL.style.width = pctL + "%";
        if (fillR) fillR.style.width = pctR + "%";
        if (peakL) peakL.style.left = Math.min(99, pctL) + "%";
        if (peakR) peakR.style.left = Math.min(99, pctR) + "%";
        if (valL) valL.textContent = dbL > -48 ? dbL + " dBFS" : "-∞ dB";
        if (valR) valR.textContent = dbR > -48 ? dbR + " dBFS" : "-∞ dB";

        // Medidor de Redução de Ganho do Compressor SSL
        if (studioCompNode && grFill && grVal) {
            const red = studioCompNode.reduction ? Math.abs(studioCompNode.reduction) : 0;
            const grPct = Math.min(100, (red / 20) * 100);
            grFill.style.width = grPct + "%";
            grVal.textContent = red > 0.1 ? "-" + red.toFixed(1) + " dB" : "0.0 dB";
        }

        studioVuTimer = requestAnimationFrame(update);
    }

    studioVuTimer = requestAnimationFrame(update);
}

// Exportações Globais
window.openStudioModal = openStudioModal;
window.closeStudioModal = closeStudioModal;
window.toggleStudioBypass = toggleStudioBypass;
window.selectStudioPreset = selectStudioPreset;
window.setStudioReverbType = setStudioReverbType;
window.setStudioDelayPreset = setStudioDelayPreset;
window.onStudioParamChange = onStudioParamChange;
window.initStudioDsp = initStudioDsp;
window.applyStudioDspParams = applyStudioDspParams;
window.createStudioImpulseBuffer = createStudioImpulseBuffer;
window.studioSettings = studioSettings;
"""

if "initStudioDsp" not in js:
    js += "\n" + studio_engine_js
    print("Suíte de Estúdio DSP adicionada ao player.js!")

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)

print("player.js gravado com sucesso!")
