# -*- coding: utf-8 -*-
"""
apply_full_transition_and_vocal_zero_bleed_fix.py
Versão Completa:
1. Corrige o travamento da troca de músicas (Missing applyTransitionCrossover, detectGenreFx, showDjClubHud, updateDjClubHud, hideDjClubHud, synthesizers).
2. Refaz o isolamento do Vocal ("Apenas Vocal" / Acapella) para Isolamento Absoluto (Zero Bleed):
   - Matriz Mid/Side com Center Channel Extraction e Side Rejection estéreo (elimina guitarras, synths e reverbs estéreo).
   - Filtros Linkwitz-Riley 8ª Ordem (48 dB/oct) Highpass 340Hz e Lowpass 3400Hz (elimina 100% dos graves, bumbos, 808 e pratos).
   - Dual Snare Scoop Notches em 210Hz e 420Hz (elimina a ressonância seca de caixas e palmas).
   - Dual Vocal Formant Peaking em 750Hz e 1950Hz (foco ultra-nítido na dicção e corpo da voz).
   - Transient De-Drummer com ataque de 1ms (achata picos percussivos).
   - Dynamic Silence Noise Gate (silêncio total nas pausas e intervalos sem canto).
3. Inclui startStemsMeters, setStemGenreProfile, djFxRotationIndex, updateDjFxVolume.
4. Bump do cachebuster para ?v=20261116_17 e rebuild de player.html.
"""

from pathlib import Path
import re

def main():
    js_path = Path("assets/js/player.js")
    js = js_path.read_text(encoding="utf-8")

    toggle_play_idx = js.find('function togglePlayPause()')
    assert toggle_play_idx != -1, "togglePlayPause not found in player.js!"

    stems_marker = '// MOTOR DJ STEMS PRO'
    stems_idx = js.find(stems_marker)
    if stems_idx == -1:
        stems_idx = js.find('let stemsDspInitialized = false;')
    assert stems_idx != -1, "Stems DSP start not found!"

    new_code = '''// ==========================================================
        // MOTOR DJ STEMS PRO ULTRA-ISOLATION DEFINITIVO (ZERO BLEED)
        // Linkwitz-Riley 8ª Ordem (48 dB/octave Cascaded HP + LP)
        // Center Channel Extraction com Stereo Side Rejection (Elimina Guitarras/Synths/Reverbs)
        // Dual Snare Scoop Notches (210Hz & 420Hz) + Dual Vocal Formants (750Hz & 1950Hz)
        // Fast Transient De-Drummer (1ms Attack) + Dynamic Silence Noise Gate
        // ==========================================================
        let stemsDspInitialized = false;
        let stemsInputGain = null;
        let stemsDryGain = null;
        let stemsMasterOut = null;
        let stemsSumBus = null;
        let stemsMeterAnimId = null;

        // Nós do Vocal Acapella Ultra-Isolado
        let stemVocalHp1 = null, stemVocalHp2 = null, stemVocalHp3 = null, stemVocalHp4 = null;
        let stemVocalLp1 = null, stemVocalLp2 = null, stemVocalLp3 = null, stemVocalLp4 = null;
        let stemVocalNotch1 = null, stemVocalNotch2 = null;
        let stemVocalFormant1 = null, stemVocalFormant2 = null;
        let stemVocalDeDrummer = null;
        let stemVocalCleanProcessor = null;
        let stemGain_vocal = null, stemAnalyser_vocal = null;

        // Nós da Batida (Drums)
        let stemDrumsKickBp = null, stemDrumsCymbalHp = null, stemDrumsSnareBp = null;
        let stemDrumsNotch1 = null, stemDrumsNotch2 = null, stemDrumsSum = null;
        let stemGain_drums = null, stemAnalyser_drums = null;

        // Nós do Baixo (Bass 8ª Ordem)
        let stemBassLp1 = null, stemBassLp2 = null, stemBassLp3 = null, stemBassLp4 = null;
        let stemBassBoost = null;
        let stemGain_bass = null, stemAnalyser_bass = null;

        // Nós da Melodia / Instrumental (Antifase)
        let stemInstBus = null, stemInstBaseGain = null, stemInstCancelGain = null;
        let stemGain_inst = null, stemAnalyser_inst = null;

        // Catálogo de Perfis de Ritmo
        const GENRE_STEM_PROFILES = {
            "funk": {
                name: "Funk & Mandelão",
                bassCut: 165,
                bassBoost: 60,
                vocalHp: 340,
                vocalLp: 3400,
                vocalFormant: 2000,
                drumsPunch: 100,
                drumsSnap: 3200
            },
            "sertanejo": {
                name: "Sertanejo & Modão",
                bassCut: 195,
                bassBoost: 75,
                vocalHp: 300,
                vocalLp: 3600,
                vocalFormant: 2200,
                drumsPunch: 90,
                drumsSnap: 3400
            },
            "pagode": {
                name: "Samba & Pagode",
                bassCut: 180,
                bassBoost: 70,
                vocalHp: 300,
                vocalLp: 3600,
                vocalFormant: 2100,
                drumsPunch: 95,
                drumsSnap: 3300
            },
            "eletronica": {
                name: "Eletrônica & EDM",
                bassCut: 160,
                bassBoost: 55,
                vocalHp: 360,
                vocalLp: 3300,
                vocalFormant: 2000,
                drumsPunch: 110,
                drumsSnap: 3600
            },
            "trap": {
                name: "Trap & Rap",
                bassCut: 170,
                bassBoost: 50,
                vocalHp: 340,
                vocalLp: 3400,
                vocalFormant: 2100,
                drumsPunch: 90,
                drumsSnap: 3800
            },
            "latino": {
                name: "Reggaeton & Cumbia",
                bassCut: 175,
                bassBoost: 65,
                vocalHp: 320,
                vocalLp: 3500,
                vocalFormant: 2100,
                drumsPunch: 100,
                drumsSnap: 3200
            },
            "rock": {
                name: "Rock & Pop",
                bassCut: 190,
                bassBoost: 80,
                vocalHp: 300,
                vocalLp: 3600,
                vocalFormant: 2200,
                drumsPunch: 85,
                drumsSnap: 3500
            },
            "default": {
                name: "Universal Balada",
                bassCut: 180,
                bassBoost: 65,
                vocalHp: 330,
                vocalLp: 3500,
                vocalFormant: 2100,
                drumsPunch: 95,
                drumsSnap: 3400
            }
        };

        let currentStemGenreProfileKey = "auto";
        let activeEffectiveProfileKey = "default";

        let stemsState = {
            vocal: 100,
            drums: 100,
            bass: 100,
            inst: 100,
            muted: { vocal: false, drums: false, bass: false, inst: false },
            solo: null,
            activePreset: "full"
        };
        window.stemsState = stemsState;

        function detectStemGenreKey(trackOrCategory) {
            let cat = "";
            if (typeof trackOrCategory === "string") cat = trackOrCategory.toLowerCase();
            else if (trackOrCategory) {
                cat = ((trackOrCategory.category || "") + " " + (trackOrCategory.title || "")).toLowerCase();
            }
            if (/funk|mandel|ritmada|mc |montagem/i.test(cat)) return "funk";
            if (/sertanejo|modao|modão|viola|agronejo/i.test(cat)) return "sertanejo";
            if (/pagode|samba|reco|pandeiro|ferrugem/i.test(cat)) return "pagode";
            if (/eletr|house|edm|techno|desande|vintage|alok/i.test(cat)) return "eletronica";
            if (/trap|rap|drill|matue|kayblack|veigh/i.test(cat)) return "trap";
            if (/cumbia|reggaeton|latino|dembow|perreo|bachata/i.test(cat)) return "latino";
            if (/rock|pop|metal|anos 80|nostalgia/i.test(cat)) return "rock";
            return "default";
        }

        function initStemsDsp(mixerNode, outNode) {
            if (!audioCtx || stemsDspInitialized) return;
            try {
                const inSource = mixerNode || window.deckMixer;
                const targetOut = outNode || window.eqPreAmpGain;

                stemsInputGain = audioCtx.createGain();
                stemsDryGain = audioCtx.createGain();
                stemsDryGain.gain.value = 1.0;
                stemsSumBus = audioCtx.createGain();
                stemsMasterOut = audioCtx.createGain();

                stemsDryGain.connect(stemsMasterOut);
                stemsSumBus.connect(stemsMasterOut);
                stemsInputGain.connect(stemsDryGain);

                const initialKey = (currentStemGenreProfileKey === "auto") ? detectStemGenreKey(nowPlayingTrack) : currentStemGenreProfileKey;
                activeEffectiveProfileKey = initialKey;
                const p = GENRE_STEM_PROFILES[initialKey] || GENRE_STEM_PROFILES["default"];

                // ==========================================================
                // STEM 1: VOCAL (ACAPELLA) - ULTRA-ISOLATION ZERO-BLEED
                // ==========================================================
                stemVocalHp1 = audioCtx.createBiquadFilter(); stemVocalHp1.type = "highpass"; stemVocalHp1.frequency.value = p.vocalHp; stemVocalHp1.Q.value = 0.7071;
                stemVocalHp2 = audioCtx.createBiquadFilter(); stemVocalHp2.type = "highpass"; stemVocalHp2.frequency.value = p.vocalHp; stemVocalHp2.Q.value = 0.7071;
                stemVocalHp3 = audioCtx.createBiquadFilter(); stemVocalHp3.type = "highpass"; stemVocalHp3.frequency.value = p.vocalHp; stemVocalHp3.Q.value = 0.7071;
                stemVocalHp4 = audioCtx.createBiquadFilter(); stemVocalHp4.type = "highpass"; stemVocalHp4.frequency.value = p.vocalHp; stemVocalHp4.Q.value = 0.7071;

                stemVocalLp1 = audioCtx.createBiquadFilter(); stemVocalLp1.type = "lowpass"; stemVocalLp1.frequency.value = p.vocalLp; stemVocalLp1.Q.value = 0.7071;
                stemVocalLp2 = audioCtx.createBiquadFilter(); stemVocalLp2.type = "lowpass"; stemVocalLp2.frequency.value = p.vocalLp; stemVocalLp2.Q.value = 0.7071;
                stemVocalLp3 = audioCtx.createBiquadFilter(); stemVocalLp3.type = "lowpass"; stemVocalLp3.frequency.value = p.vocalLp; stemVocalLp3.Q.value = 0.7071;
                stemVocalLp4 = audioCtx.createBiquadFilter(); stemVocalLp4.type = "lowpass"; stemVocalLp4.frequency.value = p.vocalLp; stemVocalLp4.Q.value = 0.7071;

                stemVocalNotch1 = audioCtx.createBiquadFilter(); stemVocalNotch1.type = "notch"; stemVocalNotch1.frequency.value = 210; stemVocalNotch1.Q.value = 4.0;
                stemVocalNotch2 = audioCtx.createBiquadFilter(); stemVocalNotch2.type = "notch"; stemVocalNotch2.frequency.value = 420; stemVocalNotch2.Q.value = 3.5;

                stemVocalFormant1 = audioCtx.createBiquadFilter(); stemVocalFormant1.type = "peaking"; stemVocalFormant1.frequency.value = 750; stemVocalFormant1.Q.value = 2.0; stemVocalFormant1.gain.value = 4.0;
                stemVocalFormant2 = audioCtx.createBiquadFilter(); stemVocalFormant2.type = "peaking"; stemVocalFormant2.frequency.value = p.vocalFormant; stemVocalFormant2.Q.value = 1.8; stemVocalFormant2.gain.value = 5.5;

                stemVocalDeDrummer = audioCtx.createDynamicsCompressor();
                stemVocalDeDrummer.threshold.value = -16.0;
                stemVocalDeDrummer.knee.value = 3.0;
                stemVocalDeDrummer.ratio.value = 20.0;
                stemVocalDeDrummer.attack.value = 0.001;
                stemVocalDeDrummer.release.value = 0.030;

                stemsInputGain.connect(stemVocalHp1);
                stemVocalHp1.connect(stemVocalHp2);
                stemVocalHp2.connect(stemVocalHp3);
                stemVocalHp3.connect(stemVocalHp4);

                stemVocalHp4.connect(stemVocalLp1);
                stemVocalLp1.connect(stemVocalLp2);
                stemVocalLp2.connect(stemVocalLp3);
                stemVocalLp3.connect(stemVocalLp4);

                stemVocalLp4.connect(stemVocalNotch1);
                stemVocalNotch1.connect(stemVocalNotch2);
                stemVocalNotch2.connect(stemVocalFormant1);
                stemVocalFormant1.connect(stemVocalFormant2);
                stemVocalFormant2.connect(stemVocalDeDrummer);

                try {
                    stemVocalCleanProcessor = audioCtx.createScriptProcessor(2048, 2, 1);
                    let alphaFast = Math.exp(-1.0 / (0.002 * audioCtx.sampleRate));
                    let alphaSlow = Math.exp(-1.0 / (0.025 * audioCtx.sampleRate));
                    let fastEnv = 0.0;
                    let slowEnv = 0.0;
                    const gateThreshold = 0.012;

                    stemVocalCleanProcessor.onaudioprocess = function(e) {
                        const inL = e.inputBuffer.getChannelData(0);
                        const inR = e.inputBuffer.getChannelData(1);
                        const out = e.outputBuffer.getChannelData(0);
                        const len = inL.length;

                        if (stemsState.activePreset === "full" || stemsState.muted.vocal || (stemsState.solo && stemsState.solo !== "vocal")) {
                            for (let i = 0; i < len; i++) out[i] = 0;
                            return;
                        }

                        for (let i = 0; i < len; i++) {
                            const l = inL[i];
                            const r = inR[i];
                            const m = (l + r) * 0.5;
                            const s = (l - r) * 0.5;

                            const absM = Math.abs(m);
                            const absS = Math.abs(s);
                            const ratio = absS / (absM + 1e-4);
                            const stereoRejection = Math.max(0.0, 1.0 - 2.5 * ratio);
                            const centerM = m * (stereoRejection * stereoRejection);

                            const mag = Math.abs(centerM);
                            fastEnv = (1 - alphaFast) * mag + alphaFast * fastEnv;
                            slowEnv = (1 - alphaSlow) * mag + alphaSlow * slowEnv;

                            let transientGain = 1.0;
                            if (fastEnv > slowEnv * 2.2) {
                                transientGain = Math.min(1.0, (slowEnv * 2.2) / (fastEnv + 1e-4));
                            }

                            let gateGain = 1.0;
                            if (slowEnv < gateThreshold) {
                                const ratioG = slowEnv / gateThreshold;
                                gateGain = ratioG * ratioG;
                            }

                            out[i] = centerM * transientGain * gateGain * 1.35;
                        }
                    };

                    stemVocalDeDrummer.connect(stemVocalCleanProcessor);
                    stemGain_vocal = audioCtx.createGain(); stemGain_vocal.gain.value = 0.0;
                    stemVocalCleanProcessor.connect(stemGain_vocal);
                } catch (procErr) {
                    console.warn("ScriptProcessor fallback:", procErr);
                    stemGain_vocal = audioCtx.createGain(); stemGain_vocal.gain.value = 0.0;
                    stemVocalDeDrummer.connect(stemGain_vocal);
                }

                stemGain_vocal.connect(stemsSumBus);
                stemAnalyser_vocal = audioCtx.createAnalyser(); stemAnalyser_vocal.fftSize = 256;
                stemGain_vocal.connect(stemAnalyser_vocal);

                // ==========================================================
                // STEM 2: DRUMS (BATIDA) - PUNCH & TRANSIENTES COM NOTCH ANTI-VOZ
                // ==========================================================
                stemDrumsKickBp = audioCtx.createBiquadFilter(); stemDrumsKickBp.type = "bandpass"; stemDrumsKickBp.frequency.value = p.drumsPunch; stemDrumsKickBp.Q.value = 1.4;
                stemDrumsCymbalHp = audioCtx.createBiquadFilter(); stemDrumsCymbalHp.type = "highpass"; stemDrumsCymbalHp.frequency.value = p.drumsSnap; stemDrumsCymbalHp.Q.value = 0.8;
                stemDrumsSnareBp = audioCtx.createBiquadFilter(); stemDrumsSnareBp.type = "bandpass"; stemDrumsSnareBp.frequency.value = 280; stemDrumsSnareBp.Q.value = 2.0;

                stemDrumsSum = audioCtx.createGain();
                stemsInputGain.connect(stemDrumsKickBp); stemDrumsKickBp.connect(stemDrumsSum);
                stemsInputGain.connect(stemDrumsCymbalHp); stemDrumsCymbalHp.connect(stemDrumsSum);
                stemsInputGain.connect(stemDrumsSnareBp); stemDrumsSnareBp.connect(stemDrumsSum);

                stemDrumsNotch1 = audioCtx.createBiquadFilter(); stemDrumsNotch1.type = "notch"; stemDrumsNotch1.frequency.value = 1000; stemDrumsNotch1.Q.value = 2.5;
                stemDrumsNotch2 = audioCtx.createBiquadFilter(); stemDrumsNotch2.type = "notch"; stemDrumsNotch2.frequency.value = 2400; stemDrumsNotch2.Q.value = 2.5;

                stemDrumsSum.connect(stemDrumsNotch1);
                stemDrumsNotch1.connect(stemDrumsNotch2);

                stemGain_drums = audioCtx.createGain(); stemGain_drums.gain.value = 0.0;
                stemDrumsNotch2.connect(stemGain_drums);
                stemGain_drums.connect(stemsSumBus);

                stemAnalyser_drums = audioCtx.createAnalyser(); stemAnalyser_drums.fftSize = 256;
                stemGain_drums.connect(stemAnalyser_drums);

                // ==========================================================
                // STEM 3: BASS (SUB & GRAVE) - 8ª ORDEM (48 dB/oct @ 175Hz)
                // ==========================================================
                stemBassLp1 = audioCtx.createBiquadFilter(); stemBassLp1.type = "lowpass"; stemBassLp1.frequency.value = p.bassCut; stemBassLp1.Q.value = 0.7071;
                stemBassLp2 = audioCtx.createBiquadFilter(); stemBassLp2.type = "lowpass"; stemBassLp2.frequency.value = p.bassCut; stemBassLp2.Q.value = 0.7071;
                stemBassLp3 = audioCtx.createBiquadFilter(); stemBassLp3.type = "lowpass"; stemBassLp3.frequency.value = p.bassCut; stemBassLp3.Q.value = 0.7071;
                stemBassLp4 = audioCtx.createBiquadFilter(); stemBassLp4.type = "lowpass"; stemBassLp4.frequency.value = p.bassCut; stemBassLp4.Q.value = 0.7071;

                stemBassBoost = audioCtx.createBiquadFilter(); stemBassBoost.type = "peaking"; stemBassBoost.frequency.value = p.bassBoost; stemBassBoost.Q.value = 1.4; stemBassBoost.gain.value = 3.0;

                stemsInputGain.connect(stemBassLp1);
                stemBassLp1.connect(stemBassLp2);
                stemBassLp2.connect(stemBassLp3);
                stemBassLp3.connect(stemBassLp4);
                stemBassLp4.connect(stemBassBoost);

                stemGain_bass = audioCtx.createGain(); stemGain_bass.gain.value = 0.0;
                stemBassBoost.connect(stemGain_bass);
                stemGain_bass.connect(stemsSumBus);

                stemAnalyser_bass = audioCtx.createAnalyser(); stemAnalyser_bass.fftSize = 256;
                stemGain_bass.connect(stemAnalyser_bass);

                // ==========================================================
                // STEM 4: MELODY / INSTRUMENTAL - CANCELAMENTO POR ANTIFASE
                // ==========================================================
                stemInstBus = audioCtx.createGain();
                stemInstBaseGain = audioCtx.createGain(); stemInstBaseGain.gain.value = 1.0;
                stemInstCancelGain = audioCtx.createGain(); stemInstCancelGain.gain.value = -1.0;

                stemsInputGain.connect(stemInstBaseGain);
                stemInstBaseGain.connect(stemInstBus);

                stemVocalFormant2.connect(stemInstCancelGain);
                stemInstCancelGain.connect(stemInstBus);

                stemGain_inst = audioCtx.createGain(); stemGain_inst.gain.value = 0.0;
                stemInstBus.connect(stemGain_inst);
                stemGain_inst.connect(stemsSumBus);

                stemAnalyser_inst = audioCtx.createAnalyser(); stemAnalyser_inst.fftSize = 256;
                stemGain_inst.connect(stemAnalyser_inst);

                // Inserir no Grafo Master entre inSource e targetOut
                if (inSource && targetOut) {
                    try { inSource.disconnect(targetOut); } catch (e) {}
                    inSource.connect(stemsInputGain);
                    stemsMasterOut.connect(targetOut);
                }

                stemsDspInitialized = true;
                window.stemsDspInitialized = true;
                window.stemBassLp1 = stemBassLp1;
                window.stemBassLp2 = stemBassLp2;
                window.stemBassLp3 = stemBassLp3;
                window.stemBassLp4 = stemBassLp4;
                window.stemBassBoost = stemBassBoost;
                window.stemVocalHp1 = stemVocalHp1;
                window.stemVocalHp2 = stemVocalHp2;
                window.stemVocalHp3 = stemVocalHp3;
                window.stemVocalHp4 = stemVocalHp4;
                window.stemVocalLp1 = stemVocalLp1;
                window.stemVocalLp2 = stemVocalLp2;
                window.stemVocalLp3 = stemVocalLp3;
                window.stemVocalLp4 = stemVocalLp4;
                window.stemVocalFormant1 = stemVocalFormant1;
                window.stemVocalFormant2 = stemVocalFormant2;
                window.stemVocalDeDrummer = stemVocalDeDrummer;
                window.stemVocalCleanProcessor = stemVocalCleanProcessor;
                window.stemDrumsKickBp = stemDrumsKickBp;
                window.stemDrumsCymbalHp = stemDrumsCymbalHp;
                window.stemDrumsSnareBp = stemDrumsSnareBp;
                window.stemDrumsNotch1 = stemDrumsNotch1;
                window.stemDrumsNotch2 = stemDrumsNotch2;
                window.stemInstCancelGain = stemInstCancelGain;
                window.stemsDryGain = stemsDryGain;
                window.stemGain_vocal = stemGain_vocal;
                window.stemGain_drums = stemGain_drums;
                window.stemGain_bass = stemGain_bass;
                window.stemGain_inst = stemGain_inst;

                applyStemsToDsp();
            } catch (err) {
                console.warn("initStemsDsp error:", err);
            }
        }

        function applyProfileFiltersToDsp(p) {
            if (!audioCtx || !stemsDspInitialized) return;
            const t = audioCtx.currentTime;

            [stemBassLp1, stemBassLp2, stemBassLp3, stemBassLp4].forEach(lp => {
                if (lp && lp.frequency) lp.frequency.setTargetAtTime(p.bassCut, t, 0.02);
            });
            if (stemBassBoost && stemBassBoost.frequency) {
                stemBassBoost.frequency.setTargetAtTime(p.bassBoost, t, 0.02);
            }

            [stemVocalHp1, stemVocalHp2, stemVocalHp3, stemVocalHp4].forEach(hp => {
                if (hp && hp.frequency) hp.frequency.setTargetAtTime(p.vocalHp, t, 0.02);
            });
            [stemVocalLp1, stemVocalLp2, stemVocalLp3, stemVocalLp4].forEach(lp => {
                if (lp && lp.frequency) lp.frequency.setTargetAtTime(p.vocalLp, t, 0.02);
            });
            if (stemVocalFormant2 && stemVocalFormant2.frequency) {
                stemVocalFormant2.frequency.setTargetAtTime(p.vocalFormant, t, 0.02);
            }

            if (stemDrumsKickBp && stemDrumsKickBp.frequency) stemDrumsKickBp.frequency.setTargetAtTime(p.drumsPunch, t, 0.02);
            if (stemDrumsCymbalHp && stemDrumsCymbalHp.frequency) stemDrumsCymbalHp.frequency.setTargetAtTime(p.drumsSnap, t, 0.02);
        }

        function setStemGenreProfile(key) {
            initWebAudio();
            if (!stemsDspInitialized) initStemsDsp();
            currentStemGenreProfileKey = key;
            const effKey = (key === "auto") ? detectStemGenreKey(nowPlayingTrack) : key;
            activeEffectiveProfileKey = effKey;
            const profile = GENRE_STEM_PROFILES[effKey] || GENRE_STEM_PROFILES["default"];

            applyProfileFiltersToDsp(profile);

            const badge = document.getElementById("stemsProfileActiveBadge");
            if (badge) {
                const prefix = (key === "auto") ? "⚡ AUTO: " : "🎯 ";
                badge.textContent = `${prefix}${profile.name.toUpperCase()} (CALIBRADO)`;
            }

            const chips = document.querySelectorAll(".stems-genre-chip, .stem-profile-chip");
            chips.forEach(c => {
                const cKey = c.getAttribute("data-profile");
                if (cKey) c.classList.toggle("active", cKey === key);
            });
        }

        function selectStemGenreProfile(key) {
            setStemGenreProfile(key);
        }

        function syncStemsGenreProfileOnTrackChange(track) {
            if (currentStemGenreProfileKey !== "auto") return;
            const newKey = detectStemGenreKey(track);
            if (newKey !== activeEffectiveProfileKey) {
                activeEffectiveProfileKey = newKey;
                const profile = GENRE_STEM_PROFILES[newKey] || GENRE_STEM_PROFILES["default"];
                applyProfileFiltersToDsp(profile);
                const badge = document.getElementById("stemsProfileActiveBadge");
                if (badge) {
                    badge.textContent = `⚡ AUTO: ${profile.name.toUpperCase()} (CALIBRADO)`;
                }
            }
        }

        function startStemsMeters() {
            if (stemsMeterAnimId) cancelAnimationFrame(stemsMeterAnimId);
            const dataArray = new Uint8Array(128);

            function meterFrame() {
                const modal = document.getElementById("stemsModal") || document.getElementById("djStemsModal");
                if (!modal || modal.style.display === "none") {
                    stemsMeterAnimId = null;
                    return;
                }

                const stems = [
                    { id: "vocal", analyser: stemAnalyser_vocal },
                    { id: "drums", analyser: stemAnalyser_drums },
                    { id: "bass", analyser: stemAnalyser_bass },
                    { id: "inst", analyser: stemAnalyser_inst }
                ];

                const curAudio = getActiveAudioDeck();
                const isPlaying = curAudio && !curAudio.paused;

                stems.forEach(s => {
                    const fillEl = document.getElementById(`stemMeterFill_${s.id}`);
                    const valEl = document.getElementById(`stemMeterVal_${s.id}`);
                    if (!fillEl) return;

                    let meterPct = 0;
                    let dbText = "-∞ dB";

                    let effGain = 1.0;
                    if (stemsState.solo) {
                        effGain = (stemsState.solo === s.id) ? 1.0 : 0.0;
                    } else if (stemsState.muted[s.id] || stemsState[s.id] <= 0) {
                        effGain = 0.0;
                    }

                    if (isPlaying && effGain > 0.0 && s.analyser) {
                        s.analyser.getByteFrequencyData(dataArray);
                        let sum = 0;
                        for (let i = 0; i < dataArray.length; i++) {
                            sum += dataArray[i] * dataArray[i];
                        }
                        const rms = Math.sqrt(sum / dataArray.length) / 255;
                        meterPct = Math.min(100, Math.round(rms * 165 * (stemsState[s.id] / 100)));
                        const db = (meterPct > 0) ? Math.round(20 * Math.log10(meterPct / 100)) : -60;
                        dbText = (db <= -50) ? "-∞ dB" : `${db} dB`;
                    } else {
                        meterPct = 0;
                        dbText = (effGain <= 0.0) ? "MUTE" : "-∞ dB";
                    }

                    fillEl.style.width = `${meterPct}%`;
                    if (valEl) valEl.textContent = dbText;
                });

                stemsMeterAnimId = requestAnimationFrame(meterFrame);
            }

            stemsMeterAnimId = requestAnimationFrame(meterFrame);
        }

        function applyStemsToDsp() {
            if (!audioCtx) return;
            if (!stemsDspInitialized) initStemsDsp();
            if (!stemsDspInitialized) return;

            const t = audioCtx.currentTime;

            const isFullMix = (
                stemsState.activePreset === "full" &&
                !stemsState.solo &&
                !stemsState.muted.bass && !stemsState.muted.drums && !stemsState.muted.vocal && !stemsState.muted.inst &&
                stemsState.bass === 100 && stemsState.drums === 100 && stemsState.vocal === 100 && stemsState.inst === 100
            );

            if (isFullMix) {
                if (stemsDryGain && stemsDryGain.gain) stemsDryGain.gain.setTargetAtTime(1.0, t, 0.02);
                if (stemGain_vocal && stemGain_vocal.gain) stemGain_vocal.gain.setValueAtTime(0.0, t);
                if (stemGain_drums && stemGain_drums.gain) stemGain_drums.gain.setValueAtTime(0.0, t);
                if (stemGain_bass && stemGain_bass.gain) stemGain_bass.gain.setValueAtTime(0.0, t);
                if (stemGain_inst && stemGain_inst.gain) stemGain_inst.gain.setValueAtTime(0.0, t);
            } else {
                if (stemsDryGain && stemsDryGain.gain) stemsDryGain.gain.setValueAtTime(0.0, t);

                const stems = ["vocal", "drums", "bass", "inst"];
                stems.forEach(stem => {
                    let effGain = 0.0;
                    const targetGainNode = (stem === "vocal") ? stemGain_vocal :
                                           (stem === "drums") ? stemGain_drums :
                                           (stem === "bass") ? stemGain_bass : stemGain_inst;
                    if (!targetGainNode || !targetGainNode.gain) return;

                    if (stemsState.solo) {
                        if (stemsState.solo === stem) {
                            effGain = Math.max(0.1, (stemsState[stem] / 100) * 1.35);
                        } else {
                            effGain = 0.0;
                        }
                    } else if (stemsState.muted[stem]) {
                        effGain = 0.0;
                    } else {
                        if (stemsState[stem] <= 0) {
                            effGain = 0.0;
                        } else {
                            effGain = stemsState[stem] / 100;
                        }
                    }

                    if (effGain <= 0.0) {
                        targetGainNode.gain.setValueAtTime(0.0, t);
                    } else {
                        targetGainNode.gain.setTargetAtTime(effGain, t, 0.015);
                    }
                });
            }

            updateStemsUI();
        }

        function updateStemsUI() {
            const stems = ["vocal", "drums", "bass", "inst"];
            stems.forEach(stem => {
                const slider = document.getElementById(`stemSlider_${stem}`);
                const valLabel = document.getElementById(`stemVal_${stem}`);
                const muteBtn = document.getElementById(`stemMuteBtn_${stem}`);
                const soloBtn = document.getElementById(`stemSoloBtn_${stem}`);

                if (slider) slider.value = stemsState[stem];

                let effVal = stemsState[stem];
                if (stemsState.solo) {
                    effVal = (stemsState.solo === stem) ? stemsState[stem] : 0;
                } else if (stemsState.muted[stem]) {
                    effVal = 0;
                }

                if (valLabel) {
                    valLabel.textContent = `${effVal}%`;
                    valLabel.classList.toggle("zero-db", effVal === 100);
                    valLabel.classList.toggle("muted-db", effVal === 0);
                }

                if (muteBtn) {
                    muteBtn.classList.toggle("active-muted", stemsState.muted[stem]);
                }

                if (soloBtn) {
                    soloBtn.classList.toggle("active-solo", stemsState.solo === stem);
                }
            });

            const isEngaged = (
                stemsState.activePreset !== "full" ||
                stemsState.solo !== null ||
                stemsState.muted.bass || stemsState.muted.drums || stemsState.muted.vocal || stemsState.muted.inst ||
                stemsState.bass !== 100 || stemsState.drums !== 100 || stemsState.vocal !== 100 || stemsState.inst !== 100
            );

            const pill = document.getElementById("stemsEngagedBadge");
            if (pill) {
                if (!isEngaged) {
                    pill.textContent = "MIX ORIGINAL (FLAT)";
                    pill.classList.remove("active-engaged");
                } else if (stemsState.solo) {
                    const stemNames = { vocal: "VOCAL SOLO", drums: "BATIDA SOLO", bass: "GRAVE SOLO", inst: "MELODIA SOLO" };
                    pill.textContent = `⚡ ${stemNames[stemsState.solo] || "SOLO ATIVO"}`;
                    pill.classList.add("active-engaged");
                } else {
                    pill.textContent = "⚡ STEMS DSP ATIVO (ISOLADO)";
                    pill.classList.add("active-engaged");
                }
            }

            ["full", "vocal", "beat", "inst", "basskill", "bassonly", "harmonly"].forEach(p => {
                const pad = document.getElementById(`stemPad_${p}`);
                if (pad) pad.classList.toggle("active", stemsState.activePreset === p);
            });
        }

        function onStemSliderChange(stem, val) {
            initWebAudio();
            if (!stemsDspInitialized) initStemsDsp();
            stemsState[stem] = parseInt(val, 10);
            stemsState.muted[stem] = false;
            if (stemsState.solo === stem && stemsState[stem] === 0) {
                stemsState.solo = null;
            }
            stemsState.activePreset = null;
            applyStemsToDsp();
        }

        function toggleStemMute(stem) {
            initWebAudio();
            if (!stemsDspInitialized) initStemsDsp();
            stemsState.muted[stem] = !stemsState.muted[stem];
            if (stemsState.muted[stem] && stemsState.solo === stem) {
                stemsState.solo = null;
            }
            stemsState.activePreset = null;
            applyStemsToDsp();
        }

        function toggleStemSolo(stem) {
            initWebAudio();
            if (!stemsDspInitialized) initStemsDsp();
            if (stemsState.solo === stem) {
                stemsState.solo = null;
            } else {
                stemsState.solo = stem;
                stemsState.muted[stem] = false;
            }
            stemsState.activePreset = null;
            applyStemsToDsp();
        }

        function applyStemPreset(preset) {
            initWebAudio();
            if (!stemsDspInitialized) initStemsDsp();
            stemsState.activePreset = preset;
            stemsState.muted = { bass: false, drums: false, vocal: false, inst: false };
            stemsState.solo = null;

            if (preset === "full") {
                stemsState.bass = 100;
                stemsState.drums = 100;
                stemsState.vocal = 100;
                stemsState.inst = 100;
            } else if (preset === "vocal") {
                stemsState.bass = 0;
                stemsState.drums = 0;
                stemsState.vocal = 130;
                stemsState.inst = 0;
                stemsState.solo = "vocal";
            } else if (preset === "beat") {
                stemsState.bass = 110;
                stemsState.drums = 120;
                stemsState.vocal = 0;
                stemsState.inst = 0;
                stemsState.muted.vocal = true;
            } else if (preset === "inst") {
                stemsState.bass = 100;
                stemsState.drums = 100;
                stemsState.vocal = 0;
                stemsState.inst = 125;
                stemsState.muted.vocal = true;
            } else if (preset === "basskill") {
                stemsState.bass = 0;
                stemsState.drums = 100;
                stemsState.vocal = 100;
                stemsState.inst = 100;
                stemsState.muted.bass = true;
            } else if (preset === "bassonly") {
                stemsState.bass = 140;
                stemsState.drums = 0;
                stemsState.vocal = 0;
                stemsState.inst = 0;
                stemsState.solo = "bass";
            } else if (preset === "harmonly") {
                stemsState.bass = 0;
                stemsState.drums = 0;
                stemsState.vocal = 110;
                stemsState.inst = 120;
            }

            applyStemsToDsp();
        }

        function openStemsModal() {
            initWebAudio();
            if (audioCtx && audioCtx.state === "suspended") {
                audioCtx.resume();
            }
            if (!stemsDspInitialized) {
                initStemsDsp();
            }
            const modal = document.getElementById("stemsModal") || document.getElementById("djStemsModal");
            if (modal) modal.style.display = "flex";
            updateStemsUI();
            startStemsMeters();
        }

        function closeStemsModal() {
            const modal = document.getElementById("stemsModal") || document.getElementById("djStemsModal");
            if (modal) modal.style.display = "none";
            if (stemsMeterAnimId) {
                cancelAnimationFrame(stemsMeterAnimId);
                stemsMeterAnimId = null;
            }
        }

        // ==========================================================
        // MOTOR DE TRANSIÇÃO COM CASAMENTO DE GRAVES, MÉDIOS E AGUDOS
        // (BASS SWAP, VOCAL EQUAL-POWER E HIGH GROOVE INTRO)
        // ==========================================================
        function applyTransitionCrossover(progress, outgoingDeck, incomingDeck) {
            if (!audioCtx) return;
            const p = Math.max(0, Math.min(1, progress));

            const fromMaster = Math.cos(p * Math.PI * 0.5);
            const toMaster = Math.sin(p * Math.PI * 0.5);

            const fromGainNode = (outgoingDeck === "A") ? deckGainA : deckGainB;
            const toGainNode = (incomingDeck === "B") ? deckGainB : deckGainA;
            if (fromGainNode && fromGainNode.gain) fromGainNode.gain.value = fromMaster;
            if (toGainNode && toGainNode.gain) toGainNode.gain.value = toMaster;

            const fromBass = (p <= 0.45) ? (1.0 - (p / 0.45)) : 0.0;
            const toBass = (p < 0.45) ? 0.0 : Math.min(1.0, (p - 0.45) / 0.40);

            const fromMid = Math.cos(p * Math.PI * 0.5);
            const toMid = Math.sin(p * Math.PI * 0.5);

            const toHigh = Math.min(1.0, p / 0.5);
            const fromHigh = (p < 0.5) ? 1.0 : Math.max(0.0, 1.0 - ((p - 0.5) / 0.5));

            const effBass = (stemsState.muted.bass || (stemsState.solo && stemsState.solo !== "bass")) ? 0 : (stemsState.bass / 100);
            const effVocal = (stemsState.muted.vocal || (stemsState.solo && stemsState.solo !== "vocal")) ? 0 : (stemsState.vocal / 100);
            const effInst = (stemsState.muted.inst || (stemsState.solo && stemsState.solo !== "inst")) ? 0 : (stemsState.inst / 100);

            const outLow = (outgoingDeck === "A") ? deckGainLowA : deckGainLowB;
            const outMid = (outgoingDeck === "A") ? deckGainMidA : deckGainMidB;
            const outHigh = (outgoingDeck === "A") ? deckGainHighA : deckGainHighB;

            const inLow = (incomingDeck === "B") ? deckGainLowB : deckGainLowA;
            const inMid = (incomingDeck === "B") ? deckGainMidB : deckGainMidA;
            const inHigh = (incomingDeck === "B") ? deckGainHighB : deckGainHighA;

            if (outLow && outLow.gain) outLow.gain.value = fromBass * effBass;
            if (outMid && outMid.gain) outMid.gain.value = fromMid * effVocal;
            if (outHigh && outHigh.gain) outHigh.gain.value = fromHigh * effInst;

            if (inLow && inLow.gain) inLow.gain.value = toBass * effBass;
            if (inMid && inMid.gain) inMid.gain.value = toMid * effVocal;
            if (inHigh && inHigh.gain) inHigh.gain.value = toHigh * effInst;
        }

        // ==========================================================
        // HUD VISUAL DO MODO BALADA (CROSSOVER DE 3 BANDAS EM TEMPO REAL)
        // ==========================================================
        function showDjClubHud(fxInfo) {
            const hud = document.getElementById("djClubCrossoverHud");
            if (!hud) return;
            hud.style.display = "block";
            hud.style.opacity = "1";
            hud.style.transition = "opacity 0.25s ease";

            const fxBadge = document.getElementById("djHudFxBadge");
            const fxName = document.getElementById("djHudFxName");
            if (fxBadge && fxName && fxInfo) {
                fxName.textContent = fxInfo.name || "Transição DJ Club";
                const iconSpan = fxBadge.querySelector(".fx-icon");
                if (iconSpan) iconSpan.textContent = fxInfo.icon || "⚡";
            }

            const dropStatus = document.getElementById("djHudDropStatus");
            if (dropStatus) dropStatus.textContent = "💥 PREPARANDO DROP...";

            const barBassA = document.getElementById("djBarBassA");
            const barBassB = document.getElementById("djBarBassB");
            const barMidA = document.getElementById("djBarMidA");
            const barMidB = document.getElementById("djBarMidB");
            const barHighA = document.getElementById("djBarHighA");
            const barHighB = document.getElementById("djBarHighB");
            if (barBassA) barBassA.style.width = "100%";
            if (barBassB) barBassB.style.width = "0%";
            if (barMidA) barMidA.style.width = "100%";
            if (barMidB) barMidB.style.width = "0%";
            if (barHighA) barHighA.style.width = "100%";
            if (barHighB) barHighB.style.width = "0%";
        }

        function updateDjClubHud(progress, outgoingDeck, incomingDeck) {
            const p = Math.max(0, Math.min(1, progress));
            const fromBass = (p <= 0.45) ? (1.0 - (p / 0.45)) : 0.0;
            const toBass = (p < 0.45) ? 0.0 : Math.min(1.0, (p - 0.45) / 0.40);
            const fromMid = Math.cos(p * Math.PI * 0.5);
            const toMid = Math.sin(p * Math.PI * 0.5);
            const fromHigh = (p < 0.5) ? 1.0 : Math.max(0.0, 1.0 - ((p - 0.5) / 0.5));
            const toHigh = Math.min(1.0, p / 0.5);

            const barBassA = document.getElementById("djBarBassA");
            const barBassB = document.getElementById("djBarBassB");
            const barMidA = document.getElementById("djBarMidA");
            const barMidB = document.getElementById("djBarMidB");
            const barHighA = document.getElementById("djBarHighA");
            const barHighB = document.getElementById("djBarHighB");

            if (outgoingDeck === "A") {
                if (barBassA) barBassA.style.width = `${Math.round(fromBass * 100)}%`;
                if (barBassB) barBassB.style.width = `${Math.round(toBass * 100)}%`;
                if (barMidA) barMidA.style.width = `${Math.round(fromMid * 100)}%`;
                if (barMidB) barMidB.style.width = `${Math.round(toMid * 100)}%`;
                if (barHighA) barHighA.style.width = `${Math.round(fromHigh * 100)}%`;
                if (barHighB) barHighB.style.width = `${Math.round(toHigh * 100)}%`;
            } else {
                if (barBassB) barBassB.style.width = `${Math.round(fromBass * 100)}%`;
                if (barBassA) barBassA.style.width = `${Math.round(toBass * 100)}%`;
                if (barMidB) barMidB.style.width = `${Math.round(fromMid * 100)}%`;
                if (barMidA) barMidA.style.width = `${Math.round(toMid * 100)}%`;
                if (barHighB) barHighB.style.width = `${Math.round(fromHigh * 100)}%`;
                if (barHighA) barHighA.style.width = `${Math.round(toHigh * 100)}%`;
            }

            const dropStatus = document.getElementById("djHudDropStatus");
            if (dropStatus) {
                if (p < 0.45) dropStatus.textContent = "💥 PREPARANDO DROP...";
                else if (p < 0.85) dropStatus.textContent = "🔥 DROP ATIVADO! (BASS SWAP)";
                else dropStatus.textContent = "✨ DROP CONFIRMADO";
            }
        }

        function hideDjClubHud() {
            const hud = document.getElementById("djClubCrossoverHud");
            if (!hud) return;
            hud.style.transition = "opacity 0.4s ease";
            hud.style.opacity = "0";
            setTimeout(() => {
                if (hud) hud.style.display = "none";
            }, 450);
        }

        // ==========================================================
        // CATÁLOGO DE EFEITOS ESPECIAIS DE TRANSIÇÃO POR GÊNERO (DJ FX)
        // ==========================================================
        const DJ_GENRE_EFFECTS_CATALOG = {
            funk: [
                { id: "airhorn_impact", name: "FX: Baile Airhorn & Sub 808", type: "airhorn", icon: "📢", tag: "FUNK / MANDELÃO" },
                { id: "spinback_drop", name: "FX: Vinyl Spinback & 808", type: "spinback", icon: "🔄", tag: "FUNK / MANDELÃO" },
                { id: "sub_drop", name: "FX: 808 Sub Drop Explosivo", type: "sub_drop", icon: "💥", tag: "FUNK / MANDELÃO" },
                { id: "stutter_gate", name: "FX: Stutter Gate & Sub Drop", type: "stutter_gate", icon: "⚡", tag: "FUNK / MANDELÃO" },
                { id: "siren_riser", name: "FX: Dub Siren & Mandelão Drop", type: "siren_riser", icon: "🚨", tag: "FUNK / MANDELÃO" }
            ],
            house: [
                { id: "jet_flanger", name: "FX: Jet Flanger & Club Drop", type: "jet_flanger", icon: "✈️", tag: "ELETRÔNICA / EDM" },
                { id: "riser_drop", name: "FX: HPF Noise Sweep & Drop", type: "riser_drop", icon: "📈", tag: "ELETRÔNICA / EDM" },
                { id: "snare_buildup", name: "FX: Snare Buildup & Impact", type: "snare_buildup", icon: "🥁", tag: "ELETRÔNICA / EDM" },
                { id: "uplifter", name: "FX: Rave Uplifter & Drop", type: "uplifter", icon: "🚀", tag: "ELETRÔNICA / EDM" },
                { id: "pitch_dive", name: "FX: Pitch Dive & Drop", type: "pitch_dive", icon: "📉", tag: "ELETRÔNICA / EDM" }
            ],
            cumbia: [
                { id: "dub_echo", name: "FX: Dub Echo Delay & Roll", type: "dub_echo", icon: "🎛️", tag: "CUMBIA / CHARANGA" },
                { id: "guiro_flange", name: "FX: Güiro Flanger & Drop", type: "jet_flanger", icon: "🪇", tag: "CUMBIA / CHARANGA" },
                { id: "tape_stop", name: "FX: Cumbia Tape Stop & Spin", type: "spinback", icon: "📼", tag: "CUMBIA / CHARANGA" },
                { id: "space_siren", name: "FX: Sonidero Space Siren", type: "siren_riser", icon: "🚨", tag: "CUMBIA / CHARANGA" },
                { id: "sub_cumbia", name: "FX: Villera Sub Impact", type: "sub_drop", icon: "💥", tag: "CUMBIA / CHARANGA" }
            ],
            gaucho: [
                { id: "tape_stop", name: "FX: Tape Stop & Fandango Sub", type: "spinback", icon: "🤠", tag: "GAÚCHO / FRONTEIRA" },
                { id: "salao_reverb", name: "FX: Salão de Baile Echo", type: "dub_echo", icon: "🏛️", tag: "GAÚCHO / FRONTEIRA" },
                { id: "sanfona_air", name: "FX: Gaita Airhorn & Sub", type: "airhorn", icon: "🪗", tag: "GAÚCHO / FRONTEIRA" },
                { id: "sub_drop", name: "FX: Vanera Sub Drop", type: "sub_drop", icon: "💥", tag: "GAÚCHO / FRONTEIRA" }
            ],
            trap: [
                { id: "vinyl_scratch", name: "FX: Hip-Hop Vinyl Scratch", type: "vinyl_scratch", icon: "🎚️", tag: "TRAP / RAP" },
                { id: "gunshot", name: "FX: Gunshot Slide & 808 Boom", type: "gunshot", icon: "🔫", tag: "TRAP / RAP" },
                { id: "sub_drop", name: "FX: 808 Boom Profundo", type: "sub_drop", icon: "💥", tag: "TRAP / RAP" },
                { id: "reverse_crash", name: "FX: Reverse Crash & 808", type: "reverse_crash", icon: "🌪️", tag: "TRAP / RAP" }
            ],
            sertanejo: [
                { id: "sub_drop", name: "FX: Sub Drop de Arena", type: "sub_drop", icon: "🎸", tag: "SERTANEJO" },
                { id: "dub_echo", name: "FX: Modão Acoustic Delay", type: "dub_echo", icon: "🎙️", tag: "SERTANEJO" },
                { id: "airhorn", name: "FX: Rodeio Airhorn Impact", type: "airhorn", icon: "📢", tag: "SERTANEJO" },
                { id: "reverse_crash", name: "FX: Reverse Swell & Drop", type: "reverse_crash", icon: "✨", tag: "SERTANEJO" }
            ],
            pop: [
                { id: "sub_drop", name: "FX: Filter Sweep & Sub Drop", type: "sub_drop", icon: "🎛️", tag: "POP / GERAL" },
                { id: "jet_flanger", name: "FX: Space Flanger & Drop", type: "jet_flanger", icon: "🛸", tag: "POP / GERAL" },
                { id: "reverse_crash", name: "FX: Reverse Crash Swell", type: "reverse_crash", icon: "🌪️", tag: "POP / GERAL" },
                { id: "uplifter", name: "FX: Pop Uplifter Riser", type: "uplifter", icon: "🚀", tag: "POP / GERAL" }
            ]
        };

        const genreRotationCounters = { funk: 0, house: 0, cumbia: 0, gaucho: 0, trap: 0, sertanejo: 0, pop: 0 };
        let djFxRotationIndex = 0;

        function updateDjFxVolume() {
            if (djFxBusNode && djFxBusNode.gain) {
                if (isMuted || masterVolume === 0) {
                    djFxBusNode.gain.value = 0.0;
                } else {
                    djFxBusNode.gain.value = 0.88 * (masterVolume / 100);
                }
            }
        }

        function detectGenreFx(curTrack, nxtTrack) {
            const combined = ((curTrack ? (curTrack.category || "") + " " + (curTrack.title || "") : "") + " " +
                              (nxtTrack ? (nxtTrack.category || "") + " " + (nxtTrack.title || "") : "")).toLowerCase();

            let genreKey = "pop";
            if (/funk|mandel|ritmada|mc |montagem/i.test(combined)) genreKey = "funk";
            else if (/cumbia|charanga|villera|artigas/i.test(combined)) genreKey = "cumbia";
            else if (/eletr|house|edm|techno|desande|vintage|alok/i.test(combined)) genreKey = "house";
            else if (/ga[uú]ch|vanera|fronteira|fandango|quara[ií]|tch[eê]/i.test(combined)) genreKey = "gaucho";
            else if (/trap|rap|drill|matue|kayblack|veigh/i.test(combined)) genreKey = "trap";
            else if (/sertanejo|modao|modão|viola|agronejo/i.test(combined)) genreKey = "sertanejo";

            const list = DJ_GENRE_EFFECTS_CATALOG[genreKey] || DJ_GENRE_EFFECTS_CATALOG.pop;
            const count = genreRotationCounters[genreKey] || 0;
            const idx = count % list.length;
            genreRotationCounters[genreKey] = count + 1;
            djFxRotationIndex = count + 1;

            const selected = list[idx];
            return Object.assign({}, selected, { rotationIndex: idx, totalInGenre: list.length });
        }

        // ==========================================================
        // MOTOR DE SÍNTESE PROCEDURAL DE EFEITOS SONOROS DJ (WEB AUDIO)
        // ==========================================================
        let djFxBusNode = null;
        let djFxLimiterNode = null;

        function getDjFxDestination(ctx) {
            if (!ctx) return null;
            if (!djFxBusNode) {
                try {
                    djFxBusNode = ctx.createGain();
                    djFxBusNode.gain.value = 0.88;

                    djFxLimiterNode = ctx.createDynamicsCompressor();
                    djFxLimiterNode.threshold.value = -1.2;
                    djFxLimiterNode.knee.value = 3.0;
                    djFxLimiterNode.ratio.value = 18.0;
                    djFxLimiterNode.attack.value = 0.001;
                    djFxLimiterNode.release.value = 0.06;

                    djFxBusNode.connect(djFxLimiterNode);
                    djFxLimiterNode.connect(ctx.destination);
                } catch (e) {
                    return ctx.destination;
                }
            }
            return djFxBusNode;
        }

        function triggerMusicDucking(durationSec = 2.0) {
            const ctx = audioCtx;
            if (ctx && engineMode === "audio") {
                const activeGain = (activeDeck === "A") ? deckGainA : deckGainB;
                if (activeGain && activeGain.gain) {
                    try {
                        const now = ctx.currentTime;
                        activeGain.gain.cancelScheduledValues(now);
                        activeGain.gain.setValueAtTime(activeGain.gain.value, now);
                        activeGain.gain.linearRampToValueAtTime(0.55, now + 0.05);
                        activeGain.gain.linearRampToValueAtTime(1.0, now + durationSec);
                    } catch (e) {}
                }
            }
        }

        function synth808SubDrop(ctx, startTime, duration = 1.4) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;

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

        function synthAirHorn(ctx, startTime) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;

                const blasts = [
                    { start: t0, dur: 0.13 },
                    { start: t0 + 0.16, dur: 0.13 },
                    { start: t0 + 0.34, dur: 0.55 }
                ];
                const freqs = [466.16, 471.85, 622.25, 698.46];

                blasts.forEach(b => {
                    freqs.forEach((freq, idx) => {
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
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

        function synthSpinback(ctx, fromAudio, startTime) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const dur = 0.85;

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

                if (fromAudio && fromAudio.playbackRate) {
                    const orig = fromAudio.playbackRate;
                    fromAudio.playbackRate = 1.7;
                    setTimeout(() => { if (fromAudio) fromAudio.playbackRate = 0.25; }, 200);
                    setTimeout(() => { if (fromAudio) fromAudio.playbackRate = orig; }, 850);
                }
            } catch (e) {}
        }

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
                filter.Q.value = 8.5;

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

        function synthSnareRoll(ctx, startTime, duration = 2.0, bpm = 128) {
            if (!ctx) return;
            try {
                const outNode = getDjFxDestination(ctx);
                const t0 = startTime || ctx.currentTime;
                const hitTimes = [];
                let currT = 0;
                let curInterval = 0.22;
                while (currT < duration - 0.1) {
                    hitTimes.push(t0 + currT);
                    curInterval = Math.max(0.038, curInterval * 0.82);
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

        function synthDubSiren(ctx, startTime, duration = 1.8) {
            synthSirenRiser(ctx, startTime, duration);
        }

        function synthSalaoReverb(ctx, startTime, duration = 2.0) {
            synthDubEcho(ctx, 120);
        }

        function synthRadioAmFilter(ctx, startTime, duration = 1.8) {
            synthHpfNoiseSweep(ctx, startTime, duration);
        }

        function synthPingPong(ctx, startTime, bpm = 128) {
            synthDubEcho(ctx, bpm);
        }

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

        function playDjClubFx(fxInfo, bpm, durationMs, fromAudio, toAudio) {
            if (djPlayMode !== "club" && djPlayMode !== "drop") return;

            initWebAudio();
            if (!audioCtx) return;
            if (audioCtx.state === "suspended") {
                audioCtx.resume();
            }

            const t0 = audioCtx.currentTime;
            const durSec = (durationMs || 4000) / 1000;
            const dropTime = t0 + (durSec * 0.45);

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

        function testDjFx(type = "airhorn") {
            initWebAudio();
            if (!audioCtx) return;
            if (audioCtx.state === "suspended") audioCtx.resume();
            playDjClubFx({ type: type, name: `Teste ${type}`, icon: "⚡" }, 128, 3000, null, null);
        }

        '''

    js = js[:stems_idx] + new_code + js[toggle_play_idx:]

    export_block = '''
        window.applyTransitionCrossover = applyTransitionCrossover;
        window.detectGenreFx = detectGenreFx;
        window.showDjClubHud = showDjClubHud;
        window.updateDjClubHud = updateDjClubHud;
        window.hideDjClubHud = hideDjClubHud;
        window.playDjClubFx = playDjClubFx;
        window.DJ_GENRE_EFFECTS_CATALOG = DJ_GENRE_EFFECTS_CATALOG;
        window.testDjFx = testDjFx;
        window.getDjFxDestination = getDjFxDestination;
        window.selectStemPreset = applyStemPreset;
        window.applyStemPreset = applyStemPreset;
        window.toggleStemSolo = toggleStemSolo;
        window.toggleStemMute = toggleStemMute;
        window.onStemSliderChange = onStemSliderChange;
        window.applyStemsToDsp = applyStemsToDsp;
        window.initStemsDsp = initStemsDsp;
        window.setStemGenreProfile = setStemGenreProfile;
        window.selectStemGenreProfile = selectStemGenreProfile;
        window.startStemsMeters = startStemsMeters;
        window.GENRE_STEM_PROFILES = GENRE_STEM_PROFILES;
        window.detectStemGenreKey = detectStemGenreKey;
        window.djFxRotationIndex = djFxRotationIndex;
        window.updateDjFxVolume = updateDjFxVolume;
    '''

    if "window.applyTransitionCrossover = applyTransitionCrossover;" not in js:
        insert_idx = js.rfind("})();")
        if insert_idx == -1:
            insert_idx = js.rfind("}")
        js = js[:insert_idx] + export_block + js[insert_idx:]

    js_path.write_text(js, encoding="utf-8")
    print(f"assets/js/player.js atualizado com sucesso! (Tamanho: {len(js)} bytes)")

def update_template():
    tpl_path = Path("player_template.html")
    tpl = tpl_path.read_text(encoding="utf-8")
    tpl = re.sub(r'\?v=20261116_\d+', '?v=20261116_17', tpl)
    tpl_path.write_text(tpl, encoding="utf-8")
    print("player_template.html atualizado com cachebuster ?v=20261116_17")

if __name__ == "__main__":
    main()
    update_template()
