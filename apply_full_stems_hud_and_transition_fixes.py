# -*- coding: utf-8 -*-
import re
import sys

print('Applying full fixes for Stems, Drop Hunter HUD, and Close Button...')

# 1. Update assets/css/player.css
CSS_PATH = 'assets/css/player.css'
with open(CSS_PATH, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace or insert .eq-close-btn
close_btn_block = """/* ==========================================================================
   BOTÃO FECHAR MODAL / CONSOLE ESTILIZADO (.eq-close-btn) - SLEEK DARK GLASS
   ========================================================================== */
.eq-close-btn {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.20) !important;
    color: #e2e8f0 !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    min-height: 32px !important;
    border-radius: 8px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    padding: 0 !important;
    margin: 0 !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
    outline: none !important;
}

.eq-close-btn svg {
    width: 14px !important;
    height: 14px !important;
    stroke: currentColor !important;
    stroke-width: 2.5px !important;
    display: block !important;
    pointer-events: none !important;
}

.eq-close-btn:hover {
    background: rgba(255, 0, 85, 0.28) !important;
    border-color: #ff0055 !important;
    color: #ff3366 !important;
    transform: scale(1.08) rotate(90deg) !important;
    box-shadow: 0 0 14px rgba(255, 0, 85, 0.5) !important;
}

.eq-close-btn:active {
    transform: scale(0.95) !important;
}

/* EXPANSÃO SUAVE DO CONTAINER DE VÍDEO QUANDO DROP HUNTER ATIVO */
.video-container.has-drop-hud {
    height: 254px !important;
    min-height: 254px !important;
    transition: height 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
"""

if '.eq-close-btn' in css:
    css = re.sub(r'/\* ==+ \s*BOTÃO FECHAR MODAL.*?\.video-container\.has-drop-hud \{[^}]+\}', '', css, flags=re.DOTALL)
    css = re.sub(r'\.eq-close-btn\s*\{[^}]+\}', '', css)
    css = re.sub(r'\.eq-close-btn svg\s*\{[^}]+\}', '', css)
    css = re.sub(r'\.eq-close-btn:hover\s*\{[^}]+\}', '', css)
    css = re.sub(r'\.eq-close-btn:active\s*\{[^}]+\}', '', css)
css += '\n' + close_btn_block

# Ensure .dj-drop-glass-panel has no scrollbars
if '.dj-drop-glass-panel' in css:
    css = re.sub(
        r'(\.dj-drop-glass-panel\s*\{[^}]+)\}',
        r'\1\n    scrollbar-width: none !important;\n    -ms-overflow-style: none !important;\n}',
        css,
        count=1
    )

with open(CSS_PATH, 'w', encoding='utf-8') as f:
    f.write(css)
print('Updated player.css successfully.')

# 2. Update assets/js/player.js
JS_PATH = 'assets/js/player.js'
with open(JS_PATH, 'r', encoding='utf-8') as f:
    js = f.read()

# Ensure top level currentActiveDjFx and transitionWatchdogTimer are declared
if 'let currentActiveDjFx = null;' not in js:
    js = js.replace(
        'let isTransitioning = false;',
        'let isTransitioning = false;\n        let currentActiveDjFx = null;\n        let transitionWatchdogTimer = null;'
    )
    print('Added top-level currentActiveDjFx and transitionWatchdogTimer declaration.')

# Ensure resetDecksContourUI removes all track badges
old_reset = """document.querySelectorAll('.track-card.transition-outgoing, .track-card.transition-incoming, [data-transition-role]').forEach(card => {
                card.style.borderColor = "";
                card.style.boxShadow = "";
                card.style.background = "";
                card.removeAttribute("data-transition-role");
                card.classList.remove("transition-outgoing", "transition-incoming");
            });"""
new_reset = """document.querySelectorAll('.track-card.transition-outgoing, .track-card.transition-incoming, [data-transition-role]').forEach(card => {
                card.style.borderColor = "";
                card.style.boxShadow = "";
                card.style.background = "";
                card.removeAttribute("data-transition-role");
                card.classList.remove("transition-outgoing", "transition-incoming");
            });
            document.querySelectorAll('.badge-outgoing-track, .badge-incoming-track, [data-track-badge]').forEach(b => b.remove());"""
if old_reset in js and 'document.querySelectorAll(\'.badge-outgoing-track, .badge-incoming-track, [data-track-badge]\').forEach(b => b.remove());' not in js:
    js = js.replace(old_reset, new_reset)
    print('Added badge cleanup to resetDecksContourUI.')

# Ensure cancelTransition clears watchdog timer
old_cancel = """function cancelTransition() {
            if (crossfadeTimer) {
                clearInterval(crossfadeTimer);
                crossfadeTimer = null;
            }
            isTransitioning = false;"""
new_cancel = """function cancelTransition() {
            if (crossfadeTimer) {
                clearInterval(crossfadeTimer);
                crossfadeTimer = null;
            }
            if (transitionWatchdogTimer) {
                clearTimeout(transitionWatchdogTimer);
                transitionWatchdogTimer = null;
            }
            isTransitioning = false;"""
if old_cancel in js and 'clearTimeout(transitionWatchdogTimer);' not in js:
    js = js.replace(old_cancel, new_cancel)
    print('Added transitionWatchdogTimer clearing to cancelTransition.')

# Update selectDjActMode to toggle has-drop-hud
old_drop_show = """dropHud.classList.add("hud-visible");
                    dropHud.style.display = "flex";"""
new_drop_show = """dropHud.classList.add("hud-visible");
                    dropHud.style.display = "flex";
                    const vc = document.getElementById("videoContainer");
                    if (vc) vc.classList.add("has-drop-hud");"""
if old_drop_show in js and 'vc.classList.add("has-drop-hud")' not in js:
    js = js.replace(old_drop_show, new_drop_show)
    print('Added has-drop-hud class addition to selectDjActMode.')

old_drop_hide = """dropHud.classList.remove("hud-visible");
                    dropHud.style.display = "none";"""
new_drop_hide = """dropHud.classList.remove("hud-visible");
                    dropHud.style.display = "none";
                    const vc = document.getElementById("videoContainer");
                    if (vc) vc.classList.remove("has-drop-hud");"""
if old_drop_hide in js and 'vc.classList.remove("has-drop-hud")' not in js:
    js = js.replace(old_drop_hide, new_drop_hide)
    print('Added has-drop-hud class removal to selectDjActMode.')

# Ensure stopDropHunterMode also removes has-drop-hud
old_stop_hud = """hud.classList.remove("hud-visible");
            hud.style.display = "none";"""
new_stop_hud = """hud.classList.remove("hud-visible");
            hud.style.display = "none";
            const vc = document.getElementById("videoContainer");
            if (vc) vc.classList.remove("has-drop-hud");"""
if old_stop_hud in js and 'const vc = document.getElementById("videoContainer");' not in js[:js.find('hud.style.display = "none";') + 150]:
    js = js.replace(old_stop_hud, new_stop_hud, 1)
    print('Added has-drop-hud removal to stopDropHunterMode.')

# Add watchdog cleanup on natural transition end
old_timer_init = """if (currentStep >= totalSteps) {
                        clearInterval(crossfadeTimer);
                        crossfadeTimer = null;"""
new_timer_init = """if (currentStep >= totalSteps) {
                        clearInterval(crossfadeTimer);
                        crossfadeTimer = null;
                        if (transitionWatchdogTimer) {
                            clearTimeout(transitionWatchdogTimer);
                            transitionWatchdogTimer = null;
                        }"""
if old_timer_init in js and 'clearTimeout(transitionWatchdogTimer);' not in js[js.find(old_timer_init):js.find(old_timer_init)+200]:
    js = js.replace(old_timer_init, new_timer_init, 1)
    print('Added watchdog cleanup on natural transition end.')

# Add watchdog safety fallback in triggerCrossfade
old_start_xfade = """hasFadedCurrentTrack = true;
            hideToast();"""
new_start_xfade = """hasFadedCurrentTrack = true;
            hideToast();
            if (transitionWatchdogTimer) clearTimeout(transitionWatchdogTimer);
            transitionWatchdogTimer = setTimeout(() => {
                if (isTransitioning) {
                    console.warn("Transição excedeu tempo limite: acionando finalização segura.");
                    if (crossfadeTimer) { clearInterval(crossfadeTimer); crossfadeTimer = null; }
                    hideDjClubHud();
                    activeDeck = (activeDeck === "A") ? "B" : "A";
                    nowPlayingTrack = incomingTrack;
                    updateTrackInfoUI(incomingTrack);
                    hideCrossfadeIndicator();
                    isTransitioning = false;
                    hasFadedCurrentTrack = false;
                    resetDecksContourUI();
                    renderAllActiveLists();
                    updateUpcomingTrackUI();
                }
            }, durationMs + 2500);"""
if old_start_xfade in js and 'Transição excedeu tempo limite' not in js:
    js = js.replace(old_start_xfade, new_start_xfade, 1)
    print('Added transition watchdog timer to triggerCrossfade.')

# 3. Replace Stems DSP Implementation with Pure Native Web Audio Graph
stems_code_to_replace = r'function initStemsDsp\(mixerNode, outNode\) \{.*?(?=function applyProfileFiltersToDsp)'
new_stems_code = """function initStemsDsp(mixerNode, outNode) {
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
                // HARDWARE MID/SIDE DEMATRIXING (C++ DSP, ZERO LATENCY)
                // ==========================================================
                const splitter = audioCtx.createChannelSplitter(2);
                stemsInputGain.connect(splitter);

                // Mid (Mono Center) = (L + R) * 0.5
                stemMidSum = audioCtx.createGain();
                const midL = audioCtx.createGain(); midL.gain.value = 0.5;
                const midR = audioCtx.createGain(); midR.gain.value = 0.5;
                splitter.connect(midL, 0);
                splitter.connect(midR, 1);
                midL.connect(stemMidSum);
                midR.connect(stemMidSum);

                // Side (Stereo Difference): L - Mid, R - Mid
                stemSideMerger = audioCtx.createChannelMerger(2);
                const sideL_plus = audioCtx.createGain(); sideL_plus.gain.value = 0.5;
                const sideL_minus = audioCtx.createGain(); sideL_minus.gain.value = -0.5;
                const sideR_plus = audioCtx.createGain(); sideR_plus.gain.value = 0.5;
                const sideR_minus = audioCtx.createGain(); sideR_minus.gain.value = -0.5;

                splitter.connect(sideL_plus, 0);
                splitter.connect(sideL_minus, 1);
                splitter.connect(sideR_plus, 1);
                splitter.connect(sideR_minus, 0);

                const sideOutL = audioCtx.createGain();
                sideL_plus.connect(sideOutL);
                sideL_minus.connect(sideOutL);
                sideOutL.connect(stemSideMerger, 0, 0);

                const sideOutR = audioCtx.createGain();
                sideR_plus.connect(sideOutR);
                sideR_minus.connect(sideOutR);
                sideOutR.connect(stemSideMerger, 0, 1);

                // ==========================================================
                // STEM 1: VOCAL (ACAPELLA) - PURE NATIVE DSP GRAPH
                // ==========================================================
                stemVocalHp1 = audioCtx.createBiquadFilter(); stemVocalHp1.type = "highpass"; stemVocalHp1.frequency.value = p.vocalHp; stemVocalHp1.Q.value = 0.7071;
                stemVocalHp2 = audioCtx.createBiquadFilter(); stemVocalHp2.type = "highpass"; stemVocalHp2.frequency.value = p.vocalHp; stemVocalHp2.Q.value = 0.7071;
                stemVocalHp3 = audioCtx.createBiquadFilter(); stemVocalHp3.type = "highpass"; stemVocalHp3.frequency.value = p.vocalHp; stemVocalHp3.Q.value = 0.7071;
                stemVocalHp4 = audioCtx.createBiquadFilter(); stemVocalHp4.type = "highpass"; stemVocalHp4.frequency.value = p.vocalHp; stemVocalHp4.Q.value = 0.7071;

                stemVocalLp1 = audioCtx.createBiquadFilter(); stemVocalLp1.type = "lowpass"; stemVocalLp1.frequency.value = p.vocalLp; stemVocalLp1.Q.value = 0.7071;
                stemVocalLp2 = audioCtx.createBiquadFilter(); stemVocalLp2.type = "lowpass"; stemVocalLp2.frequency.value = p.vocalLp; stemVocalLp2.Q.value = 0.7071;
                stemVocalLp3 = audioCtx.createBiquadFilter(); stemVocalLp3.type = "lowpass"; stemVocalLp3.frequency.value = p.vocalLp; stemVocalLp3.Q.value = 0.7071;
                stemVocalLp4 = audioCtx.createBiquadFilter(); stemVocalLp4.type = "lowpass"; stemVocalLp4.frequency.value = p.vocalLp; stemVocalLp4.Q.value = 0.7071;

                stemVocalNotch1 = audioCtx.createBiquadFilter(); stemVocalNotch1.type = "notch"; stemVocalNotch1.frequency.value = 210; stemVocalNotch1.Q.value = 3.5;
                stemVocalNotch2 = audioCtx.createBiquadFilter(); stemVocalNotch2.type = "notch"; stemVocalNotch2.frequency.value = 420; stemVocalNotch2.Q.value = 3.0;

                stemVocalFormant1 = audioCtx.createBiquadFilter(); stemVocalFormant1.type = "peaking"; stemVocalFormant1.frequency.value = 850; stemVocalFormant1.Q.value = 1.6; stemVocalFormant1.gain.value = 3.5;
                stemVocalFormant2 = audioCtx.createBiquadFilter(); stemVocalFormant2.type = "peaking"; stemVocalFormant2.frequency.value = p.vocalFormant; stemVocalFormant2.Q.value = 1.4; stemVocalFormant2.gain.value = 4.5;

                stemVocalDeDrummer = audioCtx.createDynamicsCompressor();
                stemVocalDeDrummer.threshold.value = -16.0;
                stemVocalDeDrummer.knee.value = 6.0;
                stemVocalDeDrummer.ratio.value = 6.0;
                stemVocalDeDrummer.attack.value = 0.003;
                stemVocalDeDrummer.release.value = 0.050;

                // Conectar Mid Center através da cadeia de filtros até o compressor
                stemMidSum.connect(stemVocalHp1);
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

                // Conexão nativa pura sem ScriptProcessor
                stemGain_vocal = audioCtx.createGain(); stemGain_vocal.gain.value = 0.0;
                stemVocalDeDrummer.connect(stemGain_vocal);
                stemGain_vocal.connect(stemsSumBus);

                stemAnalyser_vocal = audioCtx.createAnalyser(); stemAnalyser_vocal.fftSize = 256;
                stemGain_vocal.connect(stemAnalyser_vocal);

                // ==========================================================
                // STEM 2: DRUMS (BATIDA & TRANSIENTES)
                // ==========================================================
                stemDrumsKickBp = audioCtx.createBiquadFilter(); stemDrumsKickBp.type = "bandpass"; stemDrumsKickBp.frequency.value = p.drumsPunch; stemDrumsKickBp.Q.value = 1.4;
                stemDrumsCymbalHp = audioCtx.createBiquadFilter(); stemDrumsCymbalHp.type = "highpass"; stemDrumsCymbalHp.frequency.value = p.drumsSnap; stemDrumsCymbalHp.Q.value = 0.8;
                stemDrumsSnareBp = audioCtx.createBiquadFilter(); stemDrumsSnareBp.type = "bandpass"; stemDrumsSnareBp.frequency.value = 260; stemDrumsSnareBp.Q.value = 2.0;

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

                stemBassBoost = audioCtx.createBiquadFilter(); stemBassBoost.type = "peaking"; stemBassBoost.frequency.value = p.bassBoost; stemBassBoost.Q.value = 1.4; stemBassBoost.gain.value = 3.5;

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
                // STEM 4: MELODY / INSTRUMENTAL - SIDE STEREO + NOTCHED MID
                // ==========================================================
                stemInstBus = audioCtx.createGain();
                stemInstSidesGain = audioCtx.createGain(); stemInstSidesGain.gain.value = 1.15;
                stemSideMerger.connect(stemInstSidesGain);
                stemInstSidesGain.connect(stemInstBus);

                // Complemento de médios centrais com corte profundo das formantes da voz
                stemInstMidNotch1 = audioCtx.createBiquadFilter(); stemInstMidNotch1.type = "peaking"; stemInstMidNotch1.frequency.value = 1800; stemInstMidNotch1.Q.value = 1.4; stemInstMidNotch1.gain.value = -18.0;
                stemInstMidNotch2 = audioCtx.createBiquadFilter(); stemInstMidNotch2.type = "peaking"; stemInstMidNotch2.frequency.value = 850; stemInstMidNotch2.Q.value = 1.6; stemInstMidNotch2.gain.value = -14.0;
                stemInstMidGain = audioCtx.createGain(); stemInstMidGain.gain.value = 0.65;

                stemMidSum.connect(stemInstMidNotch1);
                stemInstMidNotch1.connect(stemInstMidNotch2);
                stemInstMidNotch2.connect(stemInstMidGain);
                stemInstMidGain.connect(stemInstBus);

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
                window.stemDrumsKickBp = stemDrumsKickBp;
                window.stemDrumsCymbalHp = stemDrumsCymbalHp;
                window.stemDrumsSnareBp = stemDrumsSnareBp;
                window.stemDrumsNotch1 = stemDrumsNotch1;
                window.stemDrumsNotch2 = stemDrumsNotch2;
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
        """

js = re.sub(stems_code_to_replace, new_stems_code, js, flags=re.DOTALL)
print('Replaced initStemsDsp with Pure Native Web Audio graph.')

with open(JS_PATH, 'w', encoding='utf-8') as f:
    f.write(js)
print('Saved updated player.js successfully.')

# 4. Bump Cachebuster in player_template.html
TEMPLATE_PATH = 'player_template.html'
with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    template = f.read()

template = re.sub(r'player\.css\?v=[a-zA-Z0-9_]+', 'player.css?v=20261117_03', template)
template = re.sub(r'player\.js\?v=[a-zA-Z0-9_]+', 'player.js?v=20261117_03', template)

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(template)
print('Bumped cachebuster in player_template.html to 20261117_03.')
