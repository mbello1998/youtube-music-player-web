import re
from pathlib import Path

file_path = Path("assets/js/player.js")
content = file_path.read_text(encoding="utf-8")

# 1. Atualizar declaração de Silêncio e preferências
old_silence_decl = """        let savedSilence = localStorage.getItem("pref_introSkipSeconds");
        let introSkipSeconds = savedSilence !== null ? parseFloat(savedSilence) : 2.0;"""

new_silence_decl = """        // GERENCIADOR & CATÁLOGO INTELIGENTE DE SILÊNCIO
        let smartSilenceMode = localStorage.getItem("pref_smartSilenceMode") || "auto"; // "auto", "fixed", "off"
        let introSkipFixedSeconds = parseFloat(localStorage.getItem("pref_introSkipSeconds") || "2.0");
        let smartSilenceCatalog = {};
        try {
            const savedCat = localStorage.getItem("smart_silence_catalog");
            if (savedCat) smartSilenceCatalog = JSON.parse(savedCat);
        } catch (e) {
            smartSilenceCatalog = {};
        }

        function getTrackIntroSkip(track) {
            if (!track) return 0.0;
            if (smartSilenceMode === "off") return 0.0;
            if (smartSilenceMode === "fixed") return introSkipFixedSeconds;

            // Modo "auto" (Inteligente):
            const vid = track.video_id;
            if (vid && smartSilenceCatalog[vid] !== undefined) {
                return smartSilenceCatalog[vid].intro_silence || 0.0;
            }

            // Heurística de precisão por estilo musical:
            // Músicas de pista/balada (Funk, Ritmada, Mandelão, Cumbia, Mega Funk, Eletrônica, Remix, Drop, Trap)
            // iniciam instantaneamente no beat (sem silêncio). Preserva o kick/vocal inicial em 0.0s!
            const text = ((track.title || "") + " " + (track.category || "") + " " + (track.artist || "")).toLowerCase();
            if (/ritmada|mandel|funk|mega funk|drop|cumbia|charanga|eletronica|desande|remix|edit|intro direta|rap|trap|batidao/i.test(text)) {
                return 0.0;
            }

            // Clipes ou shows ao vivo que costumam conter falas ou vinhetas antes da música
            if (/clipe oficial|video oficial|dvd|show|en vivo|ao vivo/i.test(text)) {
                return 1.8;
            }

            return 0.0;
        }

        function recordTrackSilence(videoId, introSec, startsInstantly) {
            if (!videoId) return;
            smartSilenceCatalog[videoId] = {
                intro_silence: Math.max(0, parseFloat(introSec) || 0),
                starts_instantly: !!startsInstantly,
                updated_at: Date.now()
            };
            try {
                localStorage.setItem("smart_silence_catalog", JSON.stringify(smartSilenceCatalog));
            } catch (e) {}
        }"""

assert old_silence_decl in content, "old_silence_decl not found"
content = content.replace(old_silence_decl, new_silence_decl, 1)

# 2. Adicionar nós do Crossover 3 Bandas na declaração de variáveis
old_nodes_decl = """        let deckGainA = null;
        let deckGainB = null;
        let eqFilters = [];"""

new_nodes_decl = """        let deckGainA = null;
        let deckGainB = null;

        // DJ 3-BAND CROSSOVER & STEMS NODES (DECK A: BAIXOS, MÉDIOS, AGUDOS)
        let deckFilterLowA = null;
        let deckFilterMidA = null;
        let deckFilterHighA = null;
        let deckGainLowA = null;
        let deckGainMidA = null;
        let deckGainHighA = null;
        let deckSumA = null;

        // DJ 3-BAND CROSSOVER & STEMS NODES (DECK B: BAIXOS, MÉDIOS, AGUDOS)
        let deckFilterLowB = null;
        let deckFilterMidB = null;
        let deckFilterHighB = null;
        let deckGainLowB = null;
        let deckGainMidB = null;
        let deckGainHighB = null;
        let deckSumB = null;

        let eqFilters = [];"""

assert old_nodes_decl in content, "old_nodes_decl not found"
content = content.replace(old_nodes_decl, new_nodes_decl, 1)

# 3. Reescrever initWebAudio com Crossover 3 Bandas independente em cada Deck
old_webaudio_block = """                deckGainA = audioCtx.createGain();
                deckGainB = audioCtx.createGain();
                deckGainA.gain.value = 1.0;
                deckGainB.gain.value = 0.0;

                sourceNodeA.connect(deckGainA);
                sourceNodeB.connect(deckGainB);

                const deckMixer = audioCtx.createGain();
                deckGainA.connect(deckMixer);
                deckGainB.connect(deckMixer);

                // DJ STEMS ISOLATOR (3 BANDAS: GRAVE, VOCAL, INSTRUMENTAL)
                stemLowFilter = audioCtx.createBiquadFilter();
                stemLowFilter.type = "lowshelf";
                stemLowFilter.frequency.value = 260;
                stemLowFilter.gain.value = 0;

                stemMidFilter = audioCtx.createBiquadFilter();
                stemMidFilter.type = "peaking";
                stemMidFilter.frequency.value = 1200;
                stemMidFilter.Q.value = 0.8;
                stemMidFilter.gain.value = 0;

                stemHighFilter = audioCtx.createBiquadFilter();
                stemHighFilter.type = "highshelf";
                stemHighFilter.frequency.value = 3400;
                stemHighFilter.gain.value = 0;

                deckMixer.connect(stemLowFilter);
                stemLowFilter.connect(stemMidFilter);
                stemMidFilter.connect(stemHighFilter);

                // 5 Filtros Biquad (60Hz, 230Hz, 910Hz, 3.6kHz, 14kHz)
                const freqs = [60, 230, 910, 3600, 14000];
                const types = ["lowshelf", "peaking", "peaking", "peaking", "highshelf"];
                eqFilters = freqs.map((f, i) => {
                    const filter = audioCtx.createBiquadFilter();
                    filter.type = types[i];
                    filter.frequency.value = f;
                    if (types[i] === "peaking") filter.Q.value = 1.0;
                    filter.gain.value = 0;
                    return filter;
                });

                stemHighFilter.connect(eqFilters[0]);"""

new_webaudio_block = """                // ==========================================================
                // DJ 3-BAND EQUAL-POWER CROSSOVER NETWORK (DECK A)
                // ==========================================================
                deckFilterLowA = audioCtx.createBiquadFilter();
                deckFilterLowA.type = "lowpass";
                deckFilterLowA.frequency.value = 280;

                deckFilterMidA = audioCtx.createBiquadFilter();
                deckFilterMidA.type = "bandpass";
                deckFilterMidA.frequency.value = 1200;
                deckFilterMidA.Q.value = 0.7;

                deckFilterHighA = audioCtx.createBiquadFilter();
                deckFilterHighA.type = "highpass";
                deckFilterHighA.frequency.value = 3200;

                deckGainLowA = audioCtx.createGain();
                deckGainMidA = audioCtx.createGain();
                deckGainHighA = audioCtx.createGain();
                deckGainLowA.gain.value = 1.0;
                deckGainMidA.gain.value = 1.0;
                deckGainHighA.gain.value = 1.0;

                sourceNodeA.connect(deckFilterLowA);
                deckFilterLowA.connect(deckGainLowA);

                sourceNodeA.connect(deckFilterMidA);
                deckFilterMidA.connect(deckGainMidA);

                sourceNodeA.connect(deckFilterHighA);
                deckFilterHighA.connect(deckGainHighA);

                deckSumA = audioCtx.createGain();
                deckGainLowA.connect(deckSumA);
                deckGainMidA.connect(deckSumA);
                deckGainHighA.connect(deckSumA);

                deckGainA = audioCtx.createGain();
                deckGainA.gain.value = (activeDeck === "A") ? 1.0 : 0.0;
                deckSumA.connect(deckGainA);

                // ==========================================================
                // DJ 3-BAND EQUAL-POWER CROSSOVER NETWORK (DECK B)
                // ==========================================================
                deckFilterLowB = audioCtx.createBiquadFilter();
                deckFilterLowB.type = "lowpass";
                deckFilterLowB.frequency.value = 280;

                deckFilterMidB = audioCtx.createBiquadFilter();
                deckFilterMidB.type = "bandpass";
                deckFilterMidB.frequency.value = 1200;
                deckFilterMidB.Q.value = 0.7;

                deckFilterHighB = audioCtx.createBiquadFilter();
                deckFilterHighB.type = "highpass";
                deckFilterHighB.frequency.value = 3200;

                deckGainLowB = audioCtx.createGain();
                deckGainMidB = audioCtx.createGain();
                deckGainHighB = audioCtx.createGain();
                deckGainLowB.gain.value = 1.0;
                deckGainMidB.gain.value = 1.0;
                deckGainHighB.gain.value = 1.0;

                sourceNodeB.connect(deckFilterLowB);
                deckFilterLowB.connect(deckGainLowB);

                sourceNodeB.connect(deckFilterMidB);
                deckFilterMidB.connect(deckGainMidB);

                sourceNodeB.connect(deckFilterHighB);
                deckFilterHighB.connect(deckGainHighB);

                deckSumB = audioCtx.createGain();
                deckGainLowB.connect(deckSumB);
                deckGainMidB.connect(deckSumB);
                deckGainHighB.connect(deckSumB);

                deckGainB = audioCtx.createGain();
                deckGainB.gain.value = (activeDeck === "B") ? 1.0 : 0.0;
                deckSumB.connect(deckGainB);

                // Master Mixer que recebe Deck A e Deck B
                const deckMixer = audioCtx.createGain();
                deckGainA.connect(deckMixer);
                deckGainB.connect(deckMixer);

                // 5 Filtros Biquad Spotify (60Hz, 230Hz, 910Hz, 3.6kHz, 14kHz)
                const freqs = [60, 230, 910, 3600, 14000];
                const types = ["lowshelf", "peaking", "peaking", "peaking", "highshelf"];
                eqFilters = freqs.map((f, i) => {
                    const filter = audioCtx.createBiquadFilter();
                    filter.type = types[i];
                    filter.frequency.value = f;
                    if (types[i] === "peaking") filter.Q.value = 1.0;
                    filter.gain.value = 0;
                    return filter;
                });

                deckMixer.connect(eqFilters[0]);"""

assert old_webaudio_block in content, "old_webaudio_block not found"
content = content.replace(old_webaudio_block, new_webaudio_block, 1)

# 4. Atualizar triggerTrackPlayback para usar getTrackIntroSkip(track)
old_trigger_skip = """const startSec = Math.max(0, parseFloat(introSkipSeconds) || 0);"""
# Note: we need to replace it in triggerTrackPlayback and triggerCrossfade
content = content.replace(
    """function triggerTrackPlayback(track) {
            if (!track || !track.video_id) return;
            hasFadedCurrentTrack = false;
            nowPlayingTrack = track;
            activePlaybackSource = "Biblioteca";
            const startSec = Math.max(0, parseFloat(introSkipSeconds) || 0);""",
    """function triggerTrackPlayback(track) {
            if (!track || !track.video_id) return;
            hasFadedCurrentTrack = false;
            nowPlayingTrack = track;
            activePlaybackSource = "Biblioteca";
            const startSec = getTrackIntroSkip(track);"""
)

# 5. Atualizar triggerCrossfade para usar getTrackIntroSkip(nextTrack) e a transição 3-bandas
content = content.replace(
    """showCrossfadeIndicator();
            const startSec = Math.max(0, parseFloat(introSkipSeconds) || 0);
            const durationMs = (crossfadeSeconds || 4) * 1000;""",
    """showCrossfadeIndicator();
            const startSec = getTrackIntroSkip(nextTrack);
            const durationMs = (crossfadeSeconds || 4) * 1000;"""
)

# 6. Atualizar o loop do crossfade para usar applyTransitionCrossover
old_fade_loop = """                crossfadeTimer = setInterval(() => {
                    currentStep++;
                    const progress = currentStep / totalSteps;

                    const fromVol = Math.max(0, 1 - progress);
                    const toVol = Math.min(1, progress);
                    if (fromGain) fromGain.gain.value = fromVol;
                    if (toGain) toGain.gain.value = toVol;

                    // Animação contínua e suave dos contornos dos cards, barras e status
                    updateCrossfadeProgressUI(progress, outgoingTrack, incomingTrack);"""

new_fade_loop = """                const outgoingDeckName = activeDeck;
                const incomingDeckName = activeDeck === "A" ? "B" : "A";

                crossfadeTimer = setInterval(() => {
                    currentStep++;
                    const progress = currentStep / totalSteps;

                    // APLICAÇÃO DO CROSSOVER DE 3 BANDAS PROFISSIONAL (BASS SWAP, VOCAL EQUAL-POWER E HIGH GROOVE)
                    applyTransitionCrossover(progress, outgoingDeckName, incomingDeckName);

                    // Animação contínua e suave dos contornos dos cards, barras e status
                    updateCrossfadeProgressUI(progress, outgoingTrack, incomingTrack);"""

assert old_fade_loop in content, "old_fade_loop not found"
content = content.replace(old_fade_loop, new_fade_loop, 1)

# Na finalização do crossfade: restaurar stems
old_fade_end = """                        activeDeck = activeDeck === "A" ? "B" : "A";
                        if (fromAudio) {
                            fromAudio.pause();
                            fromAudio.currentTime = 0;
                        }

                        nowPlayingTrack = incomingTrack;"""

new_fade_end = """                        activeDeck = activeDeck === "A" ? "B" : "A";
                        if (fromAudio) {
                            fromAudio.pause();
                            fromAudio.currentTime = 0;
                        }

                        applyStemsToDsp();

                        nowPlayingTrack = incomingTrack;"""

assert old_fade_end in content, "old_fade_end not found"
content = content.replace(old_fade_end, new_fade_end, 1)

# 7. Atualizar Stems e adicionar applyTransitionCrossover
old_stems_dsp = """        function applyStemsToDsp() {
            if (!audioCtx) return;

            let effBass = stemsState.bass;
            let effVocal = stemsState.vocal;
            let effInst = stemsState.inst;

            if (stemsState.solo) {
                if (stemsState.solo !== "bass") effBass = 0;
                if (stemsState.solo !== "vocal") effVocal = 0;
                if (stemsState.solo !== "inst") effInst = 0;
            } else {
                if (stemsState.muted.bass) effBass = 0;
                if (stemsState.muted.vocal) effVocal = 0;
                if (stemsState.muted.inst) effInst = 0;
            }

            const bassDb = stemPercentToDb(effBass);
            const vocalDb = stemPercentToDb(effVocal);
            const instDb = stemPercentToDb(effInst);

            const t = audioCtx.currentTime;
            if (stemLowFilter) {
                stemLowFilter.gain.setTargetAtTime(bassDb, t, 0.02);
            }
            if (stemMidFilter) {
                stemMidFilter.gain.setTargetAtTime(vocalDb, t, 0.02);
            }
            if (stemHighFilter) {
                stemHighFilter.gain.setTargetAtTime(instDb, t, 0.02);
            }

            updateStemsUI();
        }"""

new_stems_dsp = """        function applyStemsToDsp() {
            if (!audioCtx) return;

            let effBass = stemsState.bass;
            let effVocal = stemsState.vocal;
            let effInst = stemsState.inst;

            if (stemsState.solo) {
                if (stemsState.solo !== "bass") effBass = 0;
                if (stemsState.solo !== "vocal") effVocal = 0;
                if (stemsState.solo !== "inst") effInst = 0;
            } else {
                if (stemsState.muted.bass) effBass = 0;
                if (stemsState.muted.vocal) effVocal = 0;
                if (stemsState.muted.inst) effInst = 0;
            }

            // Converte porcentagem para ganho linear de precisão (0% = 0.0 absoluto sem vazamentos)
            const lowGain = (effBass <= 0) ? 0.0 : Math.max(0.0, effBass / 100);
            const midGain = (effVocal <= 0) ? 0.0 : Math.max(0.0, effVocal / 100);
            const highGain = (effInst <= 0) ? 0.0 : Math.max(0.0, effInst / 100);

            const t = audioCtx.currentTime;
            
            // Aplica os ganhos nos filtros de 3 bandas do Deck Ativo
            if (activeDeck === "A") {
                if (deckGainLowA) deckGainLowA.gain.setTargetAtTime(lowGain, t, 0.02);
                if (deckGainMidA) deckGainMidA.gain.setTargetAtTime(midGain, t, 0.02);
                if (deckGainHighA) deckGainHighA.gain.setTargetAtTime(highGain, t, 0.02);
                if (!isTransitioning && deckGainA) deckGainA.gain.setTargetAtTime(1.0, t, 0.02);
                if (!isTransitioning && deckGainB) deckGainB.gain.setTargetAtTime(0.0, t, 0.02);
            } else {
                if (deckGainLowB) deckGainLowB.gain.setTargetAtTime(lowGain, t, 0.02);
                if (deckGainMidB) deckGainMidB.gain.setTargetAtTime(midGain, t, 0.02);
                if (deckGainHighB) deckGainHighB.gain.setTargetAtTime(highGain, t, 0.02);
                if (!isTransitioning && deckGainB) deckGainB.gain.setTargetAtTime(1.0, t, 0.02);
                if (!isTransitioning && deckGainA) deckGainA.gain.setTargetAtTime(0.0, t, 0.02);
            }

            updateStemsUI();
        }

        // ==========================================================
        // MOTOR DJ DE TRANSIÇÃO COM CASAMENTO DE BAIXOS, MÉDIOS E AGUDOS
        // (BASS SWAP, VOCAL HARMONIC BLEND E HIGH GROOVE INTRO)
        // ==========================================================
        function applyTransitionCrossover(progress, outgoingDeck, incomingDeck) {
            if (!audioCtx) return;
            const p = Math.max(0, Math.min(1, progress));

            // Curvas de Ganho Master Equal-Power (Preserva potência sonora sem quedas de 3dB no meio)
            const fromMaster = Math.cos(p * Math.PI * 0.5);
            const toMaster = Math.sin(p * Math.PI * 0.5);

            const fromGainNode = (outgoingDeck === "A") ? deckGainA : deckGainB;
            const toGainNode = (incomingDeck === "B") ? deckGainB : deckGainA;
            if (fromGainNode) fromGainNode.gain.value = fromMaster;
            if (toGainNode) toGainNode.gain.value = toMaster;

            // 1. BAIXOS / GRAVE (BASS SWAP - EVITA CHOQUE DE KICKS E CANCELAMENTO DE FASE):
            // Deck que sai: o grave cai suavemente de 0.0 a 0.45 até zerar totalmente
            const fromBass = (p <= 0.45) ? (1.0 - (p / 0.45)) : 0.0;
            // Deck que entra: o grave fica em silêncio absoluto até 0.45, depois entra firme de 0.45 a 0.85
            const toBass = (p < 0.45) ? 0.0 : Math.min(1.0, (p - 0.45) / 0.40);

            // 2. MÉDIOS / VOCAL & HARMONIA:
            // Transição equal-power suave para casar melodias e vozes sem colisão áspera
            const fromMid = Math.cos(p * Math.PI * 0.5);
            const toMid = Math.sin(p * Math.PI * 0.5);

            // 3. AGUDOS / CHIMBAIS, PRATOS & AIR:
            // Deck que entra introduz os agudos mais cedo (0.1 a 0.5) para casar o ritmo com beatmatch
            const toHigh = Math.min(1.0, p / 0.5);
            // Deck que sai esvazia agudos a partir do meio da transição (0.5 a 1.0)
            const fromHigh = (p < 0.5) ? 1.0 : Math.max(0.0, 1.0 - ((p - 0.5) / 0.5));

            // Fator de ganho dos Stems ativos configurados pelo usuário
            const effBass = (stemsState.muted.bass || (stemsState.solo && stemsState.solo !== "bass")) ? 0 : (stemsState.bass / 100);
            const effVocal = (stemsState.muted.vocal || (stemsState.solo && stemsState.solo !== "vocal")) ? 0 : (stemsState.vocal / 100);
            const effInst = (stemsState.muted.inst || (stemsState.solo && stemsState.solo !== "inst")) ? 0 : (stemsState.inst / 100);

            const outLow = (outgoingDeck === "A") ? deckGainLowA : deckGainLowB;
            const outMid = (outgoingDeck === "A") ? deckGainMidA : deckGainMidB;
            const outHigh = (outgoingDeck === "A") ? deckGainHighA : deckGainHighB;

            const inLow = (incomingDeck === "B") ? deckGainLowB : deckGainLowA;
            const inMid = (incomingDeck === "B") ? deckGainMidB : deckGainMidA;
            const inHigh = (incomingDeck === "B") ? deckGainHighB : deckGainHighA;

            if (outLow) outLow.gain.value = fromBass * effBass;
            if (outMid) outMid.gain.value = fromMid * effVocal;
            if (outHigh) outHigh.gain.value = fromHigh * effInst;

            if (inLow) inLow.gain.value = toBass * effBass;
            if (inMid) inMid.gain.value = toMid * effVocal;
            if (inHigh) inHigh.gain.value = toHigh * effInst;
        }"""

assert old_stems_dsp in content, "old_stems_dsp not found"
content = content.replace(old_stems_dsp, new_stems_dsp, 1)

# 8. Atualizar toggleIntroSkip e updateSettingsUI para o silêncio inteligente
old_toggle_skip = """        function toggleIntroSkip() {
            if (introSkipSeconds === 0) introSkipSeconds = 1.5;
            else if (introSkipSeconds === 1.5) introSkipSeconds = 2.0;
            else if (introSkipSeconds === 2.0) introSkipSeconds = 3.0;
            else introSkipSeconds = 0;

            localStorage.setItem("pref_introSkipSeconds", introSkipSeconds.toString());
            updateSettingsUI();
            showToast(introSkipSeconds === 0 ? "Pulo de silêncio desativado" : `Pulo de silêncio inicial: ${introSkipSeconds}s`);
        }"""

new_toggle_skip = """        function toggleIntroSkip() {
            if (smartSilenceMode === "auto") {
                smartSilenceMode = "fixed";
                introSkipFixedSeconds = 2.0;
                showToast("⚡ Silêncio: Fixo (2.0s cortados em todas as faixas)");
            } else if (smartSilenceMode === "fixed") {
                smartSilenceMode = "off";
                showToast("⚡ Silêncio: Desativado (Início padrão em 0.0s)");
            } else {
                smartSilenceMode = "auto";
                showToast("⚡ Silêncio: Inteligente (Catalogado & Auto-detecção)");
            }

            localStorage.setItem("pref_smartSilenceMode", smartSilenceMode);
            localStorage.setItem("pref_introSkipSeconds", introSkipFixedSeconds.toString());
            updateSettingsUI();
        }"""

assert old_toggle_skip in content, "old_toggle_skip not found"
content = content.replace(old_toggle_skip, new_toggle_skip, 1)

# Atualizar botão no updateSettingsUI
old_intro_ui = """            const btnIntro = document.getElementById("barIntroSkipBtn");
            if (btnIntro) {
                btnIntro.innerHTML = `⚡ Silêncio: ${introSkipSeconds}s`;
                btnIntro.className = `bar-pill-btn ${introSkipSeconds > 0 ? "active" : ""}`;
            }"""

new_intro_ui = """            const btnIntro = document.getElementById("barIntroSkipBtn");
            if (btnIntro) {
                if (smartSilenceMode === "auto") {
                    btnIntro.innerHTML = `⚡ Silêncio: Auto`;
                    btnIntro.className = "bar-pill-btn active";
                    btnIntro.title = "Silêncio Inteligente: Cataloga e detecta faixas sem silêncio (0s) e com silêncio";
                } else if (smartSilenceMode === "fixed") {
                    btnIntro.innerHTML = `⚡ Silêncio: Fixo 2s`;
                    btnIntro.className = "bar-pill-btn active";
                    btnIntro.title = "Silêncio Fixo: Corta 2 segundos no início de todas as faixas";
                } else {
                    btnIntro.innerHTML = `⚡ Silêncio: 0s`;
                    btnIntro.className = "bar-pill-btn";
                    btnIntro.title = "Silêncio Desativado: Inicia no segundo 0.0";
                }
            }"""

assert old_intro_ui in content, "old_intro_ui not found"
content = content.replace(old_intro_ui, new_intro_ui, 1)

# 9. Adicionar filtro fronteira no filterSpotifyPlaylistsByGenre
old_filter_cumbia = """cumbia: (id, p) => /cumbia|villera|santafesina|chicha|sonidera|cuarteto|palmeras|damas|pibes|mattioli|gilda|fuego|marama|rombai|konga|luck/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "") + " " + (p.meta?.desc || "")),"""

new_filter_cumbia = """cumbia: (id, p) => /cumbia|villera|santafesina|chicha|sonidera|cuarteto|palmeras|damas|pibes|mattioli|gilda|fuego|marama|rombai|konga|luck/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "") + " " + (p.meta?.desc || "")),
                fronteira: (id, p) => /quarai|artigas|fronteira|miriam britos|sonido profesional|chacho ramos|mano lima|baitaca|joca martins|marenco|lucas sugo|valdez|charanga|gaucho/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "") + " " + (p.meta?.desc || "")),"""

assert old_filter_cumbia in content, "old_filter_cumbia not found"
content = content.replace(old_filter_cumbia, new_filter_cumbia, 1)

file_path.write_text(content, encoding="utf-8")
print("assets/js/player.js atualizado com sucesso!")
