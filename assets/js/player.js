const DEFAULT_COVER_SVG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Crect width='120' height='120' rx='16' fill='%23121524'/%3E%3Ccircle cx='60' cy='60' r='42' fill='%230a0c14' stroke='%2300f2fe' stroke-width='2' stroke-opacity='0.4'/%3E%3Ccircle cx='60' cy='60' r='28' fill='%23151928' stroke='%23ff0055' stroke-width='1.5' stroke-opacity='0.4'/%3E%3Ccircle cx='60' cy='60' r='14' fill='%2300f2fe' opacity='0.8'/%3E%3Ccircle cx='60' cy='60' r='4' fill='%23000'/%3E%3C/svg%3E";
        window.DEFAULT_COVER_SVG = DEFAULT_COVER_SVG;
        const DATA = window.DATA || {};
        const ICONS = window.ICONS || {};
        const CATEGORIES = window.CATEGORIES || [];
        const SPOTIFY_PLAYLISTS = window.SPOTIFY_PLAYLISTS || {};
        let activeSpotifyPlaylist = "top_brasil";
        let spotifySearchQuery = "";

        // CONFIGURAÇÕES DE EQUALIZADOR PROFISSIONAL (10 BANDAS ISO & 14 PRESETS)
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
        let eqPreAmpValue = parseFloat(localStorage.getItem("pref_eq_preamp") || "0");

        // CARREGAR PREFERÊNCIAS SALVAS DO USUÁRIO (localStorage)
        let savedFade = localStorage.getItem("pref_crossfadeSeconds");
        let crossfadeSeconds = savedFade !== null ? parseInt(savedFade, 10) : 4;

        // GERENCIADOR & CATÁLOGO INTELIGENTE DE SILÊNCIO
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
        }

        let savedVol = localStorage.getItem("pref_masterVolume");
        let masterVolume = savedVol !== null ? parseInt(savedVol, 10) : 100;
        let prevMasterVolume = masterVolume > 0 ? masterVolume : 100;

        let savedAuto = localStorage.getItem("pref_autoPlay");
        let isAutoPlayEnabled = savedAuto !== null ? (savedAuto === "true") : true;

        let savedRepeat = localStorage.getItem("pref_repeat_mode");
        let repeatMode = savedRepeat || "off"; // "off", "one" (repetir a mesma música), "all" (repetir playlist)

        let savedShuff = localStorage.getItem("pref_shuffle");
        let isShuffleEnabled = savedShuff !== null ? (savedShuff === "true") : false;

        let currentEqPreset = localStorage.getItem("pref_eq_preset") || "grave";
        let engineMode = localStorage.getItem("pref_engine_mode") || "audio"; // "audio" ou "video"
        let lastAddedVideoId = localStorage.getItem("pref_last_added_id") || "";

        // NAVEGAÇÃO
        let browseView = "library";
        let browseCategory = CATEGORIES[0];
        let currentSuggestionCategory = CATEGORIES[0];
        let isRadioActive = false;

        // REPRODUÇÃO PERSISTENTE
        let nowPlayingQueue = DATA[CATEGORIES[0]] || [];
        let nowPlayingIndex = 0;
        let nowPlayingTrack = nowPlayingQueue.length > 0 ? nowPlayingQueue[0] : null;
        let nowPlayingCategoryName = CATEGORIES[0];

        // DUAL-DECK PLAYERS (YOUTUBE IFRAME)
        let playerA = null;
        let playerB = null;
        let activeDeck = "A"; // "A" ou "B"
        let isPlayerAReady = false;
        let isPlayerBReady = false;

        // WEB AUDIO HD ENGINE
        let audioCtx = null;
        let audioDeckA = null;
        let audioDeckB = null;
        let sourceNodeA = null;
        let sourceNodeB = null;
        let deckGainA = null;
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

        let eqFilters = [];
        let compressorNode = null;
        let masterGainNode = null;
        let analyserNode = null;
        let transitionOutgoingTrack = null;
        let transitionIncomingTrack = null;
        let transitionProgress = 0;
        let animFrameId = null;

        let isMuted = false;
        let isTransitioning = false;
        let currentActiveDjFx = null;
        let transitionWatchdogTimer = null;
        let crossfadeTimer = null;
        let hasFadedCurrentTrack = false;
        let timeMonitorInterval = null;
        let searchDebounceTimer = null;
        let trackDurations = {};
        let prewarmedUpcomingId = "";

        // Cache de sugestões por gênero e por rádio de música
        let suggestionsByGenre = {};
        let radioSuggestionsCache = {};
        let pendingQueue = [];

        // Inicializar Web Audio HD Engine
        function initWebAudio() {
            if (audioCtx) return;
            try {
                const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
                audioCtx = new AudioCtxClass();
                window.audioCtx = audioCtx;

                audioDeckA = new Audio();
                audioDeckA.crossOrigin = "anonymous";
                audioDeckA.preload = "auto";

                audioDeckB = new Audio();
                audioDeckB.crossOrigin = "anonymous";
                audioDeckB.preload = "auto";

                sourceNodeA = audioCtx.createMediaElementSource(audioDeckA);
                sourceNodeB = audioCtx.createMediaElementSource(audioDeckB);

                // ==========================================================
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

                // Pre-Amp Gain (-6 a +6 dB)
                eqPreAmpGain = audioCtx.createGain();
                const initPreAmpLin = Math.pow(10, eqPreAmpValue / 20);
                eqPreAmpGain.gain.value = initPreAmpLin;

                window.deckMixer = deckMixer;
                window.eqPreAmpGain = eqPreAmpGain;

                // Conecta o Motor Master DJ Stems DSP 4-Band de alta precisão
                if (typeof initStemsDsp === "function") {
                    initStemsDsp(deckMixer, eqPreAmpGain);
                } else {
                    deckMixer.connect(eqPreAmpGain);
                }

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

                // Master Gain (Super Volume VLC 0% a 200%)
                masterGainNode = audioCtx.createGain();
                const initVol = isMuted ? 0 : (masterVolume / 100);
                masterGainNode.gain.value = initVol;
                eqFilters[eqFilters.length - 1].connect(masterGainNode);

                // Compressor & Brickwall Peak Limiter (Protege caixas de som e fones contra distorção mesmo a 200% VLC)
                compressorNode = audioCtx.createDynamicsCompressor();
                compressorNode.threshold.value = -0.5; // Limita rigorosamente em -0.5 dBFS
                compressorNode.knee.value = 4.0;
                compressorNode.ratio.value = 20.0; // Brickwall Limiter
                compressorNode.attack.value = 0.001; // Resposta ultrarrápida (1ms) evita qualquer estouro de transiente
                compressorNode.release.value = 0.08;
                masterGainNode.connect(compressorNode);
                compressorNode.connect(audioCtx.destination);

                // Configura ouvintes dos decks HTML5
                setupAudioEvents(audioDeckA, "A");
                setupAudioEvents(audioDeckB, "B");

                selectEqPreset(currentEqPreset);
                applyStemsToDsp();
                startVisualizerLoop();

                window.deckGainLowA = deckGainLowA;
                window.deckGainMidA = deckGainMidA;
                window.deckGainHighA = deckGainHighA;
                window.deckGainLowB = deckGainLowB;
                window.deckGainMidB = deckGainMidB;
                window.deckGainHighB = deckGainHighB;
                window.deckGainA = deckGainA;
                window.deckGainB = deckGainB;
            } catch (err) {
                console.warn("Web Audio API:", err);
            }
        }

        function setupAudioEvents(audioEl, deckName) {
            audioEl.addEventListener("play", () => {
                if (deckName === activeDeck && engineMode === "audio") {
                    updatePlayPauseButtons(true);
                    hideToast();
                }
            });
            audioEl.addEventListener("pause", () => {
                if (deckName === activeDeck && engineMode === "audio" && !isTransitioning) {
                    updatePlayPauseButtons(false);
                }
            });
            audioEl.addEventListener("seeked", () => {
                if (deckName === activeDeck && engineMode === "audio" && !isJumpingMix && !isTransitioning) {
                    if (typeof recalculateContextOnSeek === "function") {
                        recalculateContextOnSeek(audioEl.currentTime, audioEl.duration || 0);
                    }
                }
            });
            audioEl.addEventListener("ended", () => {
                if (deckName === activeDeck && engineMode === "audio") {
                    if (isAutoPlayEnabled && !hasFadedCurrentTrack && !isTransitioning) {
                        hasFadedCurrentTrack = true;
                        autoAdvanceWithFade();
                    }
                }
            });
            audioEl.addEventListener("error", (e) => {
                console.warn(`Deck ${deckName} erro de streaming.`, e);
                if (deckName === activeDeck && !isTransitioning) {
                    showToast("⚠️ Faixa indisponível no YouTube. Avançando para a próxima...");
                    setTimeout(() => {
                        autoAdvanceWithFade();
                    }, 1200);
                }
            });
        }

        // ==========================================================
        // CONTROLE DE VELOCIDADE DE REPRODUÇÃO (0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x, 4x)
        // ==========================================================
        let currentPlaybackSpeed = 1.0;
        const AVAILABLE_SPEEDS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 4.0];

        function setPlaybackSpeed(speed) {
            currentPlaybackSpeed = parseFloat(speed) || 1.0;

            if (audioDeckA) {
                audioDeckA.playbackRate = currentPlaybackSpeed;
                audioDeckA.preservesPitch = true;
            }
            if (audioDeckB) {
                audioDeckB.playbackRate = currentPlaybackSpeed;
                audioDeckB.preservesPitch = true;
            }

            try {
                const activeP = getActivePlayer();
                if (activeP && typeof activeP.setPlaybackRate === "function") {
                    const ytRate = Math.min(2.0, currentPlaybackSpeed);
                    activeP.setPlaybackRate(ytRate);
                }
            } catch (e) {}

            const labelEl = document.getElementById("barSpeedLabel");
            if (labelEl) labelEl.textContent = `⚡ ${currentPlaybackSpeed}x`;
            const djBadge = document.getElementById("djSpeedBadge");
            if (djBadge) {
                djBadge.textContent = `⚡ ${currentPlaybackSpeed}x`;
                if (currentPlaybackSpeed !== 1.0) djBadge.classList.add("custom-speed");
                else djBadge.classList.remove("custom-speed");
            }

            document.querySelectorAll(".speed-opt-btn").forEach(btn => {
                const sp = parseFloat(btn.getAttribute("data-speed"));
                if (sp === currentPlaybackSpeed) btn.classList.add("active");
                else btn.classList.remove("active");
            });

            closeSpeedMenu();
            updateTurntablesState();
            updateLiveBpmPanel();
            showToast(`⚡ Velocidade ajustada para ${currentPlaybackSpeed}x`);
        }

        function cyclePlaybackSpeed() {
            const idx = AVAILABLE_SPEEDS.indexOf(currentPlaybackSpeed);
            const nextIdx = (idx + 1) % AVAILABLE_SPEEDS.length;
            setPlaybackSpeed(AVAILABLE_SPEEDS[nextIdx]);
        }

        function toggleSpeedMenu(event) {
            if (event) event.stopPropagation();
            const dropdown = document.getElementById("speedMenuDropdown");
            if (dropdown) dropdown.classList.toggle("show");
        }

        function closeSpeedMenu() {
            const dropdown = document.getElementById("speedMenuDropdown");
            if (dropdown) dropdown.classList.remove("show");
        }

        document.addEventListener("click", (e) => {
            if (!e.target.closest(".speed-control-wrapper")) {
                closeSpeedMenu();
            }
        });

        // Alternar modo de reprodução: Áudio HD vs Clipe YouTube
        function toggleEngineMode() {
            const curAudio = getActiveAudioDeck();
            const activeP = getActivePlayer();
            const isPlaying = (engineMode === "audio" && curAudio && !curAudio.paused && curAudio.currentTime > 0) || 
                              (engineMode === "video" && activeP && typeof activeP.getPlayerState === "function" && 
                               (activeP.getPlayerState() === YT.PlayerState.PLAYING || activeP.getPlayerState() === YT.PlayerState.BUFFERING));
            setEngineMode(engineMode === "audio" ? "video" : "audio", isPlaying);
        }

        function setEngineMode(mode, autoPlay = false) {
            engineMode = mode;
            localStorage.setItem("pref_engine_mode", mode);
            
            const btnBar = document.getElementById("barEngineModeBtn");
            const visScreen = document.getElementById("visualizerScreen");
            const ytOverlay = document.getElementById("ytWaveOverlay");

            if (btnBar) {
                btnBar.innerHTML = mode === "audio" ? "🎵 Áudio HD" : "🎬 Clipe";
                btnBar.className = `bar-pill-btn ${mode === "audio" ? "active" : ""}`;
            }
            updateVolumeUI();

            if (mode === "audio") {
                if (visScreen) visScreen.style.display = "flex";
                if (ytOverlay) ytOverlay.style.display = "none";
                if (playerA && typeof playerA.pauseVideo === "function") {
                    try { playerA.pauseVideo(); playerA.setVolume(0); } catch (e) {}
                }
                if (playerB && typeof playerB.pauseVideo === "function") {
                    try { playerB.pauseVideo(); playerB.setVolume(0); } catch (e) {}
                }
                showToast("🎵 Áudio HD ativo: Equalizador Spotify, 200% VLC e ZERO bloqueios!");
            } else {
                if (visScreen) visScreen.style.display = "none";
                if (ytOverlay) ytOverlay.style.display = "block";
                if (audioDeckA) audioDeckA.pause();
                if (audioDeckB) audioDeckB.pause();
                showToast("🎬 Modo Clipe ativo: Exibindo vídeo oficial com Waveform.");
            }

            if (nowPlayingTrack) {
                updateTrackInfoUI(nowPlayingTrack);
                if (autoPlay) {
                    playTrackInstant(nowPlayingTrack);
                }
            }
        }

        // ==========================================================
        // LOOP DO VISUALIZADOR DE ONDA ULTRA-PRECISO & ESPECTRO AMBIENTE
        // ==========================================================
        const VIS_BAR_COUNT = 48;
        const visPeaks = new Float32Array(VIS_BAR_COUNT);
        const visPeakHold = new Int32Array(VIS_BAR_COUNT);
        let visSyntheticPhase = 0;

        // ==========================================================
        // MOTOR DE CHUVA DE METEOROS COM PARTÍCULAS (ULTRA-LEVE < 0.2% CPU)
        // ==========================================================
        const METEOR_COUNT = 22;
        const meteorList = [];
        for (let i = 0; i < METEOR_COUNT; i++) {
            meteorList.push({
                x: Math.random() * 420 - 20,
                y: Math.random() * 220 - 40,
                len: 20 + Math.random() * 26,
                speed: 2.2 + Math.random() * 3.2,
                angle: 0.95, // ~54 graus diagonal descendente
                size: 1.2 + Math.random() * 1.2,
                alpha: 0.4 + Math.random() * 0.5,
                color: (i % 3 === 0) ? "#00f2fe" : ((i % 3 === 1) ? "#a855f7" : "#ffaa00"),
                trailAlpha: 0.2 + Math.random() * 0.25
            });
        }

        function renderMeteorShower(canvas, isPlaying) {
            const ctx = canvas.getContext("2d");
            if (!ctx) return;
            const w = canvas.width;
            const h = canvas.height;
            ctx.clearRect(0, 0, w, h);

            if (!isPlaying) return;

            for (let i = 0; i < METEOR_COUNT; i++) {
                const m = meteorList[i];
                m.x += Math.cos(m.angle) * m.speed;
                m.y += Math.sin(m.angle) * m.speed;

                if (m.y > h + 30 || m.x > w + 30) {
                    m.x = Math.random() * (w + 100) - 100;
                    m.y = -20 - Math.random() * 40;
                    m.speed = 2.2 + Math.random() * 3.2;
                    m.len = 20 + Math.random() * 26;
                }

                const tailX = m.x - Math.cos(m.angle) * m.len;
                const tailY = m.y - Math.sin(m.angle) * m.len;

                // Rastro gradiente luminoso
                const grad = ctx.createLinearGradient(tailX, tailY, m.x, m.y);
                grad.addColorStop(0, "rgba(0, 0, 0, 0)");
                grad.addColorStop(0.7, m.color === "#00f2fe" ? "rgba(0, 242, 254, 0.4)" : (m.color === "#a855f7" ? "rgba(168, 85, 247, 0.4)" : "rgba(255, 170, 0, 0.4)"));
                grad.addColorStop(1, m.color);

                ctx.beginPath();
                ctx.moveTo(tailX, tailY);
                ctx.lineTo(m.x, m.y);
                ctx.strokeStyle = grad;
                ctx.lineWidth = m.size;
                ctx.lineCap = "round";
                ctx.stroke();

                // Cabeça brilhante do meteoro
                ctx.beginPath();
                ctx.arc(m.x, m.y, m.size * 1.2, 0, Math.PI * 2);
                ctx.fillStyle = "#ffffff";
                ctx.shadowBlur = 5;
                ctx.shadowColor = m.color;
                ctx.fill();
                ctx.shadowBlur = 0;

                // Micro-partículas de poeira estelar
                if (i % 2 === 0) {
                    const sparkX = tailX + (Math.random() - 0.5) * 6;
                    const sparkY = tailY + (Math.random() - 0.5) * 6;
                    ctx.beginPath();
                    ctx.arc(sparkX, sparkY, 0.8, 0, Math.PI * 2);
                    ctx.fillStyle = m.color;
                    ctx.globalAlpha = m.trailAlpha;
                    ctx.fill();
                    ctx.globalAlpha = 1.0;
                }
            }
        }

        function startVisualizerLoop() {
            if (animFrameId) cancelAnimationFrame(animFrameId);
            const visCanvas = document.getElementById("visCanvas");
            const ytCanvas = document.getElementById("ytWaveOverlay");
            const ambientCanvas = document.getElementById("videoAmbientGlow");
            const videoContainer = document.getElementById("videoContainer");
            const bufferLength = analyserNode ? analyserNode.frequencyBinCount : 128;
            const dataArray = new Uint8Array(bufferLength);

            function draw() {
                animFrameId = requestAnimationFrame(draw);

                const activeCanvas = (engineMode === "audio") ? visCanvas : ytCanvas;
                if (!activeCanvas) return;

                // Ajusta resolução DPR para renderização ultra-nítida sem borrões
                const rect = activeCanvas.getBoundingClientRect();
                const dpr = window.devicePixelRatio || 1;
                const targetW = Math.round(rect.width * dpr);
                const targetH = Math.round(rect.height * dpr);
                if (targetW > 0 && (activeCanvas.width !== targetW || activeCanvas.height !== targetH)) {
                    activeCanvas.width = targetW;
                    activeCanvas.height = targetH;
                }

                const ctx = activeCanvas.getContext("2d");
                if (!ctx) return;
                ctx.save();
                ctx.scale(dpr, dpr);

                const w = rect.width;
                const h = rect.height;
                ctx.clearRect(0, 0, w, h);

                const curAudio = getActiveAudioDeck();
                const activeP = getActivePlayer();
                const isPlaying = (engineMode === "audio" && curAudio && !curAudio.paused && curAudio.currentTime > 0) || 
                                  (engineMode === "video" && activeP && typeof activeP.getPlayerState === "function" && 
                                   (activeP.getPlayerState() === YT.PlayerState.PLAYING || activeP.getPlayerState() === YT.PlayerState.BUFFERING));

                if (engineMode === "audio" && analyserNode) {
                    analyserNode.getByteFrequencyData(dataArray);
                } else if (isPlaying) {
                    // MOTOR PROCEDURAL DJ DE BATIDAS, BUILD-UPS E DROPS (VÍDEO YOUTUBE)
                    visSyntheticPhase += 0.09 * currentPlaybackSpeed;
                    const bpm = (nowPlayingTrack && nowPlayingTrack.bpm) ? nowPlayingTrack.bpm : 130;
                    const beatPhase = (visSyntheticPhase * (bpm / 130)) % 32; // Ciclo rítmico musical de 32 batidas
                    
                    // Detecção de DROP:
                    // Batidas 24 a 30: Build-up subindo em crescendo
                    // Batidas 30.5 a 31.9: O DROP (silêncio / tensão onde as barras caem lá embaixo!)
                    // Batidas 0 a 8: O IMPACTO DO DROP (explosão de graves e agudos no topo!)
                    let dropMod = 1.0;
                    if (beatPhase >= 30.5 && beatPhase < 31.9) {
                        dropMod = 0.12; // MÚSICA CAIU NO DROP (Barras descem quase a zero!)
                    } else if (beatPhase < 8) {
                        dropMod = 1.25; // IMPACTO DO DROP (Barras sobem e pulsam com força!)
                    } else if (beatPhase >= 24 && beatPhase < 30.5) {
                        dropMod = 0.85 + Math.sin((beatPhase - 24) * Math.PI) * 0.28; // Crescendo
                    }

                    const kickHit = Math.pow(Math.max(0, Math.cos((visSyntheticPhase * (bpm / 130)) * Math.PI)), 8);
                    
                    for (let i = 0; i < VIS_BAR_COUNT; i++) {
                        const normI = i / (VIS_BAR_COUNT - 1);
                        // Grave (barras 0 a 14): pulsa vigorosamente com o bumbo/808 e despenca no drop
                        const bWeight = Math.max(0, 1 - normI * 2.2);
                        const bass = (bWeight * (kickHit * 0.90 + 0.10));

                        // Médio (barras 12 a 32): vocais, sintetizadores e caixas
                        const mWeight = Math.sin(normI * Math.PI);
                        const mid = mWeight * (Math.sin(visSyntheticPhase * 3.2 + i * 0.55) * 0.45 + 0.5) * 0.60;

                        // Agudo (barras 28 a 47): pratos, chimbal e transientes
                        const tWeight = Math.max(0, (normI - 0.45) / 0.55);
                        const treble = tWeight * (Math.cos(visSyntheticPhase * 6.5 + i * 1.15) * 0.5 + 0.5) * 0.65;

                        // Variação orgânica entre barras para eliminar qualquer linha reta/pente
                        const barVariation = 0.80 + Math.sin(i * 1.7) * 0.20;

                        const rawHeight = (bass + mid + treble) * dropMod * barVariation;
                        dataArray[i] = Math.max(6, Math.min(240, rawHeight * 255));
                    }
                } else {
                    for (let i = 0; i < VIS_BAR_COUNT; i++) {
                        dataArray[i] = Math.max(0, dataArray[i] * 0.85 - 2);
                    }
                }

                // Renderiza chuva de meteoros atrás da capa da música
                const meteorCanvas = document.getElementById("meteorShowerCanvas");
                if (meteorCanvas) {
                    renderMeteorShower(meteorCanvas, isPlaying);
                }

                // Renderiza o Efeito de Espectro Ambiente Atrás do Vídeo (Ambilight Aura 360)
                if (ambientCanvas) {
                    const aCtx = ambientCanvas.getContext("2d");
                    if (aCtx) {
                        const aw = ambientCanvas.width;
                        const ah = ambientCanvas.height;
                        aCtx.clearRect(0, 0, aw, ah);
                        if (isPlaying) {
                            let bSum = 0, mSum = 0, hSum = 0;
                            for (let k = 0; k < 10; k++) bSum += (dataArray[k] || 0);
                            for (let k = 10; k < 28; k++) mSum += (dataArray[k] || 0);
                            for (let k = 28; k < VIS_BAR_COUNT; k++) hSum += (dataArray[k] || 0);

                            const bN = bSum / (10 * 255);
                            const mN = mSum / (18 * 255);
                            const hN = hSum / ((VIS_BAR_COUNT - 28) * 255);
                            const pulse = 0.55 + bN * 0.55;

                            // Brilho Ciano Neon central inferior
                            const g1 = aCtx.createRadialGradient(aw * 0.5, ah * 0.9, 10, aw * 0.5, ah * 0.9, aw * 0.7);
                            g1.addColorStop(0, `rgba(0, 242, 254, ${(0.6 * pulse).toFixed(2)})`);
                            g1.addColorStop(0.5, `rgba(0, 242, 254, ${(0.25 * pulse).toFixed(2)})`);
                            g1.addColorStop(1, "transparent");
                            aCtx.fillStyle = g1;
                            aCtx.fillRect(0, 0, aw, ah);

                            // Brilho Rosa/Magenta lateral esquerdo (pulsa com grave)
                            const g2 = aCtx.createRadialGradient(aw * 0.15, ah * 0.45, 10, aw * 0.15, ah * 0.45, aw * 0.6);
                            g2.addColorStop(0, `rgba(255, 0, 85, ${(0.65 * pulse).toFixed(2)})`);
                            g2.addColorStop(0.6, `rgba(255, 0, 85, ${(0.2 * pulse).toFixed(2)})`);
                            g2.addColorStop(1, "transparent");
                            aCtx.fillStyle = g2;
                            aCtx.fillRect(0, 0, aw, ah);

                            // Brilho Violeta/Dourado lateral direito (pulsa com agudos/médios)
                            const g3 = aCtx.createRadialGradient(aw * 0.85, ah * 0.35, 10, aw * 0.85, ah * 0.35, aw * 0.6);
                            const tPulse = 0.45 + hN * 0.6;
                            g3.addColorStop(0, `rgba(168, 85, 247, ${(0.6 * tPulse).toFixed(2)})`);
                            g3.addColorStop(0.5, `rgba(255, 170, 0, ${(0.32 * mN).toFixed(2)})`);
                            g3.addColorStop(1, "transparent");
                            aCtx.fillStyle = g3;
                            aCtx.fillRect(0, 0, aw, ah);

                            // Brilho Neon superior / Aurora de Espectro no topo do vídeo
                            const g4 = aCtx.createRadialGradient(aw * 0.5, 0, 5, aw * 0.5, 0, aw * 0.55);
                            g4.addColorStop(0, `rgba(0, 242, 254, ${(0.45 * tPulse).toFixed(2)})`);
                            g4.addColorStop(0.5, `rgba(121, 40, 202, ${(0.22 * mN).toFixed(2)})`);
                            g4.addColorStop(1, "transparent");
                            aCtx.fillStyle = g4;
                            aCtx.fillRect(0, 0, aw, ah);

                            // Pulsação sincronizada no VU Meter do Deck Ativo
                            const activeMeter = activeDeck === "A" ? document.getElementById("meterA") : document.getElementById("meterB");
                            if (activeMeter && !isTransitioning) {
                                activeMeter.style.width = Math.min(100, Math.max(25, Math.round(pulse * 95))) + "%";
                            }
                        }
                    }
                }

                // =========================================================================
                // VISUALIZADOR DE ESPECTRO AUDIO APERFEIÇOADO (ESTILO ADOBE AFTER EFFECTS)
                // Conforme referência oficial do usuário: barras simétricas em arco-íris,
                // linha de contorno dourada no topo, onda harmônica e curva inferior pontilhada.
                // Obediência estrita ao Volume (0% a 200% VLC) e dinâmica de drops/batidas.
                // =========================================================================
                const centerY = h / 2;
                const maxHalfHeight = (h * 0.44); // Headroom de segurança para nunca travar no teto

                const barWidth = Math.max(2.5, (w / VIS_BAR_COUNT) * 0.68);
                const gap = (w - (barWidth * VIS_BAR_COUNT)) / (VIS_BAR_COUNT + 1);

                // Fator de escala dinâmico 100% obediente ao volume atual e ao VLC Super Volume (0% a 200%)
                const currentVolNorm = (isMuted || masterVolume === 0) ? 0 : (masterVolume / 100);
                let volScale = 0;
                if (currentVolNorm > 0) {
                    if (masterVolume <= 100) {
                        volScale = Math.pow(currentVolNorm, 0.75); // Resposta suave de volume
                    } else {
                        // 101% a 200% VLC Super Volume: expansão rica e potente com headroom controlado
                        volScale = 1.0 + ((masterVolume - 100) / 100) * 0.40;
                    }
                }

                // Faixa audível útil (bins 1 a 68 = ~150Hz até ~12.8kHz)
                const maxActiveBin = Math.min(bufferLength - 1, 68);
                const minActiveBin = 1;

                const pointsTop = [];
                const pointsBottom = [];
                const barHalfHeights = [];

                for (let i = 0; i < VIS_BAR_COUNT; i++) {
                    const normI = i / (VIS_BAR_COUNT - 1);
                    let normalized = 0;
                    if (engineMode === "audio") {
                        // Mapeamento logarítmico concentrado no espectro musical
                        const binIdx = Math.min(maxActiveBin, minActiveBin + Math.floor(Math.pow(normI, 1.35) * (maxActiveBin - minActiveBin)));
                        const bCurr = dataArray[binIdx] || 0;
                        
                        // Compensação de estúdio (ruído rosa natural)
                        const freqWeight = 0.85 + Math.pow(normI, 0.75) * 0.70;
                        const scaledVal = Math.max(0, (bCurr / 255) * freqWeight);
                        
                        // Expansão dinâmica (Power Curve 1.55) obedecendo ao volume e batidas
                        const expandedVal = Math.pow(scaledVal, 1.45);
                        normalized = (isPlaying && volScale > 0) ? Math.min(0.92, expandedVal * 1.20 * volScale) : 0;
                    } else {
                        // Modo Vídeo YouTube (Diretamente do Motor Procedural de Batidas, Drops & Volume)
                        const rawNorm = (dataArray[i] || 0) / 255;
                        normalized = (isPlaying && volScale > 0) ? Math.min(0.92, Math.pow(rawNorm, 1.30) * 1.05 * volScale) : 0;
                    }

                    // Tapering orgânico suave nas bordas externas (espectro afunila elegantemente nos extremos)
                    const edgeTaper = 0.40 + Math.sin(normI * Math.PI) * 0.60;
                    const barHalf = Math.max(1.8, normalized * maxHalfHeight * edgeTaper);
                    barHalfHeights.push(barHalf);

                    // Indicador de pico (Peak Hold & Gravity Falloff)
                    if (barHalf >= visPeaks[i]) {
                        visPeaks[i] = barHalf;
                        visPeakHold[i] = 8;
                    } else {
                        if (visPeakHold[i] > 0) {
                            visPeakHold[i]--;
                        } else {
                            visPeaks[i] = Math.max(1.8, visPeaks[i] - 0.7);
                        }
                    }
                }

                // 1. Gradiente Espectral Horizontal (Arco-Íris Neon do After Effects: Violeta -> Magenta -> Laranja -> Ouro -> Lima)
                const spectrumGrad = ctx.createLinearGradient(0, 0, w, 0);
                spectrumGrad.addColorStop(0.00, "#9d4edd"); // Violeta elétrico
                spectrumGrad.addColorStop(0.20, "#e02695"); // Rosa / Magenta vivo
                spectrumGrad.addColorStop(0.48, "#ff5400"); // Coral / Laranja flutuante
                spectrumGrad.addColorStop(0.72, "#ffb703"); // Âmbar Dourado
                spectrumGrad.addColorStop(1.00, "#aacc00"); // Verde Lima Neon

                // 2. Renderização das Barras Simétricas Centradas (Crescem para Cima e para Baixo do Meio)
                ctx.save();
                ctx.strokeStyle = spectrumGrad;
                ctx.lineWidth = barWidth;
                ctx.lineCap = "round";
                ctx.beginPath();
                let curX = gap;
                for (let i = 0; i < VIS_BAR_COUNT; i++) {
                    const bx = curX + barWidth / 2;
                    const bHalf = barHalfHeights[i];
                    ctx.moveTo(bx, centerY - bHalf);
                    ctx.lineTo(bx, centerY + bHalf);

                    pointsTop.push({ x: bx, y: centerY - bHalf * 1.15 - 2 });
                    pointsBottom.push({ x: bx, y: centerY + bHalf * 1.12 + 2 });
                    curX += barWidth + gap;
                }
                ctx.stroke();
                ctx.restore();

                // 3. Fita Superior Dourada / Laranja Fluorescente (Envelope Curvo Suave nos Picos)
                if (pointsTop.length > 1 && isPlaying) {
                    ctx.save();
                    ctx.beginPath();
                    ctx.moveTo(pointsTop[0].x, pointsTop[0].y);
                    for (let i = 1; i < pointsTop.length; i++) {
                        const midX = (pointsTop[i - 1].x + pointsTop[i].x) / 2;
                        const midY = (pointsTop[i - 1].y + pointsTop[i].y) / 2;
                        ctx.quadraticCurveTo(pointsTop[i - 1].x, pointsTop[i - 1].y, midX, midY);
                    }
                    ctx.strokeStyle = "rgba(255, 150, 0, 0.95)";
                    ctx.lineWidth = 1.8;
                    ctx.shadowBlur = 6;
                    ctx.shadowColor = "rgba(255, 120, 0, 0.75)";
                    ctx.stroke();
                    ctx.restore();
                }

                // 4. Onda Harmônica Secundária Flutuante (Fita Magenta/Rosa em fase senoidal orgânica)
                if (pointsTop.length > 1 && isPlaying) {
                    ctx.save();
                    ctx.beginPath();
                    const phase = visSyntheticPhase * 2.4;
                    for (let i = 0; i < pointsTop.length; i++) {
                        const p = pointsTop[i];
                        const norm = i / (pointsTop.length - 1);
                        const offset = Math.sin(phase + norm * 6.5) * 3.5;
                        const hy = centerY - (centerY - p.y) * 0.65 + offset;
                        if (i === 0) ctx.moveTo(p.x, hy);
                        else {
                            const prev = pointsTop[i - 1];
                            const prevOffset = Math.sin(phase + (i - 1) / (pointsTop.length - 1) * 6.5) * 3.5;
                            const prevHy = centerY - (centerY - prev.y) * 0.65 + prevOffset;
                            const midX = (prev.x + p.x) / 2;
                            const midY = (prevHy + hy) / 2;
                            ctx.quadraticCurveTo(prev.x, prevHy, midX, midY);
                        }
                    }
                    ctx.strokeStyle = "rgba(247, 37, 133, 0.78)";
                    ctx.lineWidth = 1.2;
                    ctx.stroke();
                    ctx.restore();
                }

                // 5. Linha Inferior Espelhada Pontilhada (Dotted Waveform em Verde Lima / Ciano)
                if (pointsBottom.length > 1 && isPlaying) {
                    ctx.save();
                    ctx.setLineDash([2, 4]); // Padrão pontilhado do After Effects
                    ctx.beginPath();
                    ctx.moveTo(pointsBottom[0].x, pointsBottom[0].y);
                    for (let i = 1; i < pointsBottom.length; i++) {
                        const midX = (pointsBottom[i - 1].x + pointsBottom[i].x) / 2;
                        const midY = (pointsBottom[i - 1].y + pointsBottom[i].y) / 2;
                        ctx.quadraticCurveTo(pointsBottom[i - 1].x, pointsBottom[i - 1].y, midX, midY);
                    }
                    ctx.strokeStyle = "rgba(170, 240, 40, 0.85)";
                    ctx.lineWidth = 1.4;
                    ctx.shadowBlur = 4;
                    ctx.shadowColor = "rgba(170, 240, 40, 0.4)";
                    ctx.stroke();
                    ctx.restore();
                }

                // 6. Pontos Fluorescentes de Pico nos Saltos de Batida
                ctx.save();
                for (let i = 0; i < VIS_BAR_COUNT; i += 2) {
                    if (visPeakHold[i] > 2 && visPeaks[i] > 4) {
                        const px = pointsTop[i].x;
                        const py = centerY - visPeaks[i] * 1.15;
                        ctx.beginPath();
                        ctx.arc(px, py, 1.2, 0, Math.PI * 2);
                        ctx.fillStyle = "#ffdd00";
                        ctx.shadowBlur = 4;
                        ctx.shadowColor = "#ffaa00";
                        ctx.fill();
                    }
                }
                ctx.restore();

                ctx.restore();
            }
            draw();
        }

        function getUpcomingTrack() {
            // MODO DE REPETIÇÃO 'ONE': A PRÓXIMA MÚSICA É A MESMA MÚSICA ATUAL!
            if (repeatMode === "one" && nowPlayingTrack) {
                return nowPlayingTrack;
            }
            // PRIORIDADE MÁXIMA: Fila de Espera do Usuário (Spotify Priority Queue)
            // A próxima música SEMPRE será o primeiro item que o usuário adicionou à fila!
            if (pendingQueue && pendingQueue.length > 0) {
                return pendingQueue[0];
            }
            // Modo DJ Ativo (Match Perfeito, Peak Time, Smart Shuffle, Smooth Flow)
            if (djModeNextTrack && (!nowPlayingTrack || djModeNextTrack.video_id !== nowPlayingTrack.video_id)) {
                return djModeNextTrack;
            }
            // Se ainda não calculado para o modo atual, calcula dinamicamente
            if (typeof calculateDjModeNextTrack === "function") {
                const calculated = calculateDjModeNextTrack();
                if (calculated) return calculated;
            }
            // Se a fila do usuário estiver vazia, avança na playlist/categoria ativa
            if (nowPlayingQueue && nowPlayingQueue.length > 0) {
                const nextIdx = (nowPlayingIndex + 1) % nowPlayingQueue.length;
                if (!isShuffleEnabled && repeatMode === "off" && (nowPlayingIndex + 1) >= nowPlayingQueue.length) {
                    return null; // Não repete playlist ao final se a repetição estiver desativada
                }
                return nowPlayingQueue[nextIdx] || null;
            }
            return null;
        }

        // Atualiza UI da faixa atual e da próxima faixa
        
        // ==========================================================================
        // TITULO LIMPO SEM FEAT & JUNK PARA STATUS BAR
        // ==========================================================================
        function cleanTrackTitleForBar(rawTitle, rawArtist) {
            if (!rawTitle) return "";
            let clean = String(rawTitle).trim();

            // 1. Remove bracketed / parenthesized content completely: [ ... ], ( ... ), { ... }
            clean = clean.replace(/[\(\[\{][^\)\]\}]*[\)\]\}]/gi, " ");

            // 2. Remove feat / ft / featuring / part: e.g. 'feat. ...', 'ft ...', 'part. ...'
            clean = clean.replace(/\b(?:feat\.?|ft\.?|featuring|part\.?|participação)\b.*$/gi, "");
            clean = clean.replace(/\s*(?:feat\.?|ft\.?|featuring|part\.?)\s+[^\-\–\—\|]+[\-\–\—]\s*/gi, " - ");

            // 3. Remove common promo words and delimiters
            clean = clean.replace(/\b(?:video\s*oficial|clipe?\s*oficial|official\s*music\s*video|official\s*video|lyric\s*video|audio\s*oficial|official\s*audio|en\s*vivo|ao\s*vivo|hd|4k)\b/gi, "");

            // 4. Split by primary delimiters like '|' or '//' first to isolate main track title
            if (clean.includes("|")) {
                const parts = clean.split("|");
                if (parts[0].trim().length >= 4) clean = parts[0].trim();
            }
            if (clean.includes("//")) {
                const parts = clean.split("//");
                if (parts[0].trim().length >= 4) clean = parts[0].trim();
            }

            // 5. If title has ' - ', handle 'Artist - Title' or 'Title - Subtitle'
            if (clean.includes(" - ")) {
                const parts = clean.split(" - ");
                if (rawArtist && parts[0].toLowerCase().trim() === rawArtist.toLowerCase().trim()) {
                    clean = parts.slice(1).join(" - ").trim();
                } else if (parts[0].trim().length >= 6) {
                    clean = parts[0].trim();
                }
            }

            // 6. Strip emojis and decorative symbols
            clean = clean.replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{27BF}\u{1F1E0}-\u{1F1FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}•*~–—]/gu, " ");

            // 7. Collapse spaces and trim
            clean = clean.replace(/\s+/g, " ").trim();

            // 8. Clamp to 28 characters
            if (clean.length > 28) {
                clean = clean.slice(0, 27).trim() + "…";
            }
            return clean;
        }

        // ==========================================================================
        // DROP HUNTER & WAVE ANALYSIS ENGINE (PREDITIVO, PREVENÇÃO DE SILÊNCIO & FX POR GÊNERO)
        // ==========================================================================
        let dropHunterTimer = null;
        let dropActiveSeconds = 0;
        let dropWindowManualBase = 75; // Janela base ajustável pelo usuário (30s a 180s)
        let dropTargetSeconds = 75; // Janela ideal de festa (dinâmica e adaptativa)
        let dropHunterThreshold = 60; // % de energia para considerar Drop Ativo
        let isAutoDropEnabled = true; // Modo 100% automático (pula intro e corta no drop da próxima)
        let consecutiveLowEnergyCount = 0;
        let consecutiveSilenceCount = 0; // Detecção de silêncio real
        let consecutivePredictedDropCount = 0; // Detecção de queda preditiva
        let dropEnergyHistory = []; // Amostras recentes de energia (últimos 2s)
        let mixSegmentCount = 0;
        let maxMixSegmentsBeforeNext = 3; // Em mixes longos, curte até 3 saltos de refrão antes de trocar de faixa
        let isJumpingMix = false; // Flag de proteção contra interrupções/conflitos durante o salto no mix
        try {
            Object.defineProperty(window, 'isJumpingMix', {
                get: () => isJumpingMix,
                set: (v) => { isJumpingMix = v; },
                configurable: true
            });
        } catch (e) {}

        // Ajuste manual da Janela do Refrão (+10s / -10s)
        function adjustDropWindow(deltaSeconds) {
            dropWindowManualBase = Math.max(30, Math.min(180, dropWindowManualBase + deltaSeconds));
            dropTargetSeconds = dropWindowManualBase;
            showToast(`⏱️ Janela do Refrão ajustada para ${dropWindowManualBase}s`);
            const timerVal = document.getElementById("dropTimerVal");
            if (timerVal) {
                const elapsed = Math.floor(dropActiveSeconds);
                const target = Math.floor(dropTargetSeconds);
                const m = String(Math.floor(elapsed / 60)).padStart(2, "0");
                const s = String(elapsed % 60).padStart(2, "0");
                const tm = String(Math.floor(target / 60)).padStart(2, "0");
                const ts = String(target % 60).padStart(2, "0");
                timerVal.textContent = `${m}:${s} / ${tm}:${ts}s`;
            }
        }
        window.adjustDropWindow = adjustDropWindow;

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
            if (djPlayMode !== "drop") {
                stopDropHunterAnalyzer();
                return;
            }
            if (dropHunterTimer) clearInterval(dropHunterTimer);
            dropActiveSeconds = 0;
            dropTargetSeconds = isTrackLongMix(nowPlayingTrack) ? (dropWindowManualBase + 15) : dropWindowManualBase;
            consecutiveLowEnergyCount = 0;
            consecutiveSilenceCount = 0;
            consecutivePredictedDropCount = 0;
            dropEnergyHistory = [];
            mixSegmentCount = 0;
            isJumpingMix = false;

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
            isJumpingMix = false;
            dropEnergyHistory = [];
            const hud = document.getElementById("djDropHunterHud");
            if (hud) {
                hud.classList.remove("hud-visible");
                hud.style.display = "none";
            }
            const dropBadge = document.getElementById("djDropActiveBadge");
            if (dropBadge && djPlayMode !== "drop") {
                dropBadge.style.display = "none";
            }
        }

        function toggleAutoDropMode() {
            isAutoDropEnabled = !isAutoDropEnabled;
            const btn = document.getElementById("btnAutoDropToggle");
            if (btn) {
                btn.classList.toggle("active", isAutoDropEnabled);
                btn.textContent = isAutoDropEnabled ? "🤖 Auto: ON" : "⏸️ Auto: OFF";
            }
            showToast(isAutoDropEnabled ? "🤖 Auto DJ LIGADO: Toca o refrão no ápice e corta com efeitos DJ!" : "⏸️ Auto DJ em pausa: Você controla os cortes!");
        }

        function updateDropHunterMetrics() {
            if (isJumpingMix) return; // Não processa métricas durante a rampa do salto

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
                    footerText.innerHTML = `🔀 <strong>Mix Longo:</strong> O DJ toca cada canção por 90s e pula suave pro próximo refrão! (${mixSegmentCount + 1}/${maxMixSegmentsBeforeNext + 1})`;
                } else {
                    footerText.innerHTML = `💡 <strong>Refrão Preditivo:</strong> Ajuste livre (➖/➕), antecipa queda da onda e evita silêncio!`;
                }
            }

            let energy = 0;
            if (window._simulatedDropEnergy !== undefined && window._simulatedDropEnergy !== null) {
                energy = window._simulatedDropEnergy;
            } else if (analyserNode) {
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

            // Buffer histórico de energia para cálculo preditivo de onda (2 segundos = 20 amostras a cada 100ms)
            dropEnergyHistory.push(energy);
            if (dropEnergyHistory.length > 20) dropEnergyHistory.shift();

            // Cálculo da inclinação / tendência da onda (ΔE/Δt em % por segundo)
            let energyTrend = 0;
            if (dropEnergyHistory.length >= 8) {
                const half = Math.floor(dropEnergyHistory.length / 2);
                let oldSum = 0;
                for (let i = 0; i < half; i++) oldSum += dropEnergyHistory[i];
                const oldAvg = oldSum / half;

                let newSum = 0;
                for (let i = half; i < dropEnergyHistory.length; i++) newSum += dropEnergyHistory[i];
                const newAvg = newSum / (dropEnergyHistory.length - half);

                energyTrend = (newAvg - oldAvg); // Positivo = Subindo; Negativo = Caindo
            }

            // 1. DETECÇÃO DE TÉRMINO DA MÚSICA & SILÊNCIO (Evita cortes atrasados ou momentos mortos)
            const curAudio = (engineMode === "audio") ? getActiveAudioDeck() : null;
            let remainingTrackSec = 999;
            if (curAudio && curAudio.duration && !isNaN(curAudio.duration)) {
                remainingTrackSec = curAudio.duration - (curAudio.currentTime || 0);
            } else if (nowPlayingTrack && nowPlayingTrack.duration) {
                const dur = parseFloat(nowPlayingTrack.duration) || 180;
                const activeP = (typeof getActivePlayer === "function") ? getActivePlayer() : null;
                const curTime = (activeP && typeof activeP.getCurrentTime === "function") ? (activeP.getCurrentTime() || 0) : 0;
                if (curTime > 0) remainingTrackSec = dur - curTime;
            }

            if (energy <= 12) {
                consecutiveSilenceCount++;
            } else {
                consecutiveSilenceCount = 0;
            }

            // Se a música está acabando (faltando <= 7.0s) ou entrou em silêncio real (>0.8s e já tocou ao menos 25s)
            if (isAutoDropEnabled && !isTransitioning && !isJumpingMix) {
                if (dropActiveSeconds >= 25 && (remainingTrackSec <= 7.0 || consecutiveSilenceCount >= 8)) {
                    smartCutToNextDrop("silence_or_outro");
                    return;
                }
            }

            // 2. ANÁLISE PREDITIVA DE ONDA & JANELA DO REFRÃO
            const safeChorusPlay = Math.max(38, dropWindowManualBase * 0.60);

            // PREVISÃO DE QUEDA ANTECIPADA: Se o refrão já tocou o bastante e a onda está despencando
            if (dropActiveSeconds >= safeChorusPlay && energyTrend <= -5 && energy < dropHunterThreshold) {
                consecutivePredictedDropCount++;
                if (consecutivePredictedDropCount >= 5) { // 0.5s de queda antecipada confirmada
                    if (statusPill) {
                        statusPill.className = "drop-status-pill cutting";
                        statusPill.innerHTML = "⚡ ANTECIPANDO QUEDA (VIRANDO NO ÁPICE)";
                    }
                    if (isAutoDropEnabled && !isTransitioning && !isJumpingMix) {
                        smartCutToNextDrop("predictive_fall");
                        return;
                    }
                }
            } else {
                consecutivePredictedDropCount = 0;
            }

            if (energy >= dropHunterThreshold) {
                // DROP ATIVO!
                dropActiveSeconds += 0.1;
                consecutiveLowEnergyCount = 0;

                // PREVISÃO DE SUBIDA: se a onda está subindo rápido (trend >= +4) ou no ápice (>= 75%)
                if (energyTrend >= 4 || energy >= 75) {
                    const maxAllowed = isLongMix ? (dropWindowManualBase + 35) : (dropWindowManualBase + 20);
                    dropTargetSeconds = Math.min(maxAllowed, dropTargetSeconds + 0.1);
                    if (statusPill) {
                        statusPill.className = "drop-status-pill drop-active";
                        statusPill.innerHTML = "🔥 ÁPICE SUBINDO! (ALTA)";
                    }
                } else {
                    if (statusPill) {
                        statusPill.className = "drop-status-pill drop-active";
                        statusPill.innerHTML = "💥 DROP ATIVO! (FERVENDO)";
                    }
                }
            } else if (energy >= 42) {
                // Buildup / Subindo Energia
                dropActiveSeconds += 0.08;
                if (statusPill && !statusPill.classList.contains("cutting")) {
                    statusPill.className = "drop-status-pill buildup";
                    statusPill.innerHTML = "⚡ Subindo Energia (Buildup)";
                }
            } else {
                // Energia baixa (Vocal, respiro ou breakdown)
                if (dropActiveSeconds >= safeChorusPlay) {
                    consecutiveLowEnergyCount++;
                    if (consecutiveLowEnergyCount >= 30) {
                        // Queda prolongada pós-refrão: antecipa o corte para não estagnar a pista
                        const minFloor = isLongMix ? (dropWindowManualBase + 10) : dropWindowManualBase;
                        dropTargetSeconds = Math.max(minFloor, Math.round(dropActiveSeconds));
                    }
                }

                if (statusPill && !statusPill.classList.contains("cutting")) {
                    statusPill.className = "drop-status-pill analyzing";
                    statusPill.innerHTML = "🔍 Analisando Sinal...";
                }
            }

            // Atualiza barra de tempo do Drop e da Janela do Refrão
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

            // 3. DISPARO DO CORTE AUTOMÁTICO DE FESTA (SÓ APÓS O REFRÃO COMPLETO!)
            if (isAutoDropEnabled && dropActiveSeconds >= dropTargetSeconds && !isTransitioning && !isJumpingMix) {
                if (isLongMix && mixSegmentCount < maxMixSegmentsBeforeNext) {
                    smartMixSegmentJump();
                } else {
                    smartCutToNextDrop("target_reached");
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
            dropTargetSeconds = isTrackLongMix(nowPlayingTrack) ? 90 : 75;
            consecutiveLowEnergyCount = 0;
            showToast("⚡ Pulo Inteligente: Saltando intro direto para a parte boa / Drop!");
        }

        // Salto Suave para o próximo refrão dentro de um mix longo (+80s com Quick-Duck)
        function smartMixSegmentJump() {
            if (isJumpingMix || isTransitioning) return;
            isJumpingMix = true;

            mixSegmentCount++;
            dropActiveSeconds = 0;
            dropTargetSeconds = 85;
            consecutiveLowEnergyCount = 0;

            const statusPill = document.getElementById("dropStatusPill");
            if (statusPill) {
                statusPill.className = "drop-status-pill mix-jumping";
                statusPill.innerHTML = `🔀 FADE NO MIX (${mixSegmentCount}/${maxMixSegmentsBeforeNext + 1})`;
            }

            showToast(`🔀 Mix Jumper: Fade suave para o próximo refrão! (${mixSegmentCount + 1}/${maxMixSegmentsBeforeNext + 1})`);

            if (engineMode === "audio") {
                const curAudio = getActiveAudioDeck();
                const activeGain = (activeDeck === "A") ? deckGainA : deckGainB;

                if (curAudio && activeGain && audioCtx) {
                    const now = audioCtx.currentTime;
                    // FADE OUT SUAVE PROFISSIONAL (600ms) - Elimina corte seco no mix
                    activeGain.gain.cancelScheduledValues(now);
                    activeGain.gain.setValueAtTime(activeGain.gain.value, now);
                    activeGain.gain.linearRampToValueAtTime(0.01, now + 0.60);

                    setTimeout(() => {
                        const dur = curAudio.duration || 1800;
                        const nextTime = Math.min(dur - 40, (curAudio.currentTime || 0) + 80);

                        let seekHandled = false;
                        const onSeekedDone = () => {
                            if (seekHandled) return;
                            seekHandled = true;
                            curAudio.removeEventListener("seeked", onSeekedDone);
                            curAudio.play().catch(() => {});
                            if (activeGain && audioCtx) {
                                const resumeNow = audioCtx.currentTime;
                                activeGain.gain.cancelScheduledValues(resumeNow);
                                activeGain.gain.setValueAtTime(0.01, resumeNow);
                                activeGain.gain.linearRampToValueAtTime(1.0, resumeNow + 0.70);
                            }
                            setTimeout(() => { isJumpingMix = false; }, 350);
                        };

                        curAudio.addEventListener("seeked", onSeekedDone, { once: true });
                        curAudio.currentTime = nextTime;

                        // Fallback seguro caso seeked não dispare no tempo
                        setTimeout(() => {
                            if (!seekHandled) onSeekedDone();
                        }, 550);
                    }, 620);
                } else if (curAudio) {
                    const dur = curAudio.duration || 1800;
                    curAudio.currentTime = Math.min(dur - 40, (curAudio.currentTime || 0) + 80);
                    curAudio.play().catch(() => {});
                    setTimeout(() => { isJumpingMix = false; }, 800);
                }
            } else {
                const activeP = getActivePlayer();
                if (activeP && typeof activeP.seekTo === "function") {
                    const origVol = (typeof activeP.getVolume === "function") ? (activeP.getVolume() || 100) : 100;
                    let s = 0;
                    const fadeOutInterval = setInterval(() => {
                        s++;
                        const v = Math.max(5, origVol * (1 - s / 5));
                        try { activeP.setVolume(v); } catch(e) {}
                        if (s >= 5) {
                            clearInterval(fadeOutInterval);
                            const dur = (typeof activeP.getDuration === "function") ? (activeP.getDuration() || 1800) : 1800;
                            const cur = (typeof activeP.getCurrentTime === "function") ? (activeP.getCurrentTime() || 0) : 0;
                            const nextTime = Math.min(dur - 40, cur + 80);
                            activeP.seekTo(nextTime, true);
                            setTimeout(() => {
                                let ins = 0;
                                const fadeInInterval = setInterval(() => {
                                    ins++;
                                    const iv = Math.min(origVol, origVol * (ins / 5));
                                    try { activeP.setVolume(iv); } catch(e) {}
                                    if (ins >= 5) {
                                        clearInterval(fadeInInterval);
                                        isJumpingMix = false;
                                    }
                                }, 70);
                            }, 250);
                        }
                    }, 70);
                } else {
                    setTimeout(() => { isJumpingMix = false; }, 800);
                }
            }
        }

        // Corte no Drop da próxima música (com transição profissional e FX de Gênero)
        function smartCutToNextDrop(reason = "target_reached") {
            mixSegmentCount = 0;
            dropActiveSeconds = 0;
            dropTargetSeconds = dropWindowManualBase;
            consecutiveLowEnergyCount = 0;
            consecutiveSilenceCount = 0;
            consecutivePredictedDropCount = 0;
            dropEnergyHistory = [];
            isJumpingMix = false;

            // Se for mix longo, garante crossfade suave de pelo menos 6 segundos para não cortar seco!
            if (isTrackLongMix(nowPlayingTrack)) {
                crossfadeSeconds = Math.max(crossfadeSeconds || 4, 6);
            }

            const statusPill = document.getElementById("dropStatusPill");
            if (statusPill) {
                statusPill.className = "drop-status-pill cutting";
                statusPill.innerHTML = "✂️ CORTE NO DROP! VIRANDO...";
            }

            const nextTrack = getUpcomingTrack();
            const fxInfo = (typeof detectGenreFx === "function") ? detectGenreFx(nowPlayingTrack, nextTrack) : null;
            const fxLabel = fxInfo ? `${fxInfo.icon} ${fxInfo.name}` : "⚡ Drop FX";

            if (reason === "predictive_fall") {
                showToast(`⚡ Virada Preditiva: Antecipei a queda da onda! Virando com ${fxLabel}!`);
            } else if (reason === "silence_or_outro") {
                showToast(`✂️ Silêncio Evitado: Pista segue no topo com ${fxLabel}!`);
            } else {
                showToast(`✂️ Corte no Drop: Virando no ápice com ${fxLabel}!`);
            }
            autoAdvanceWithFade();
        }

function updateUpcomingTrackUI() {
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
                                <span class="status-badge-next" title="Próxima Faixa (${tagLabel})">⏭️ A Seguir:</span>
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
        }

        // Inicializar Abas da Biblioteca
        function initTabs() {
            const tabsContainer = document.getElementById("tabsContainer");
            if (!tabsContainer) return;
            tabsContainer.innerHTML = "";
            CATEGORIES.forEach(cat => {
                const list = DATA[cat] || [];
                if (list.length === 0) return;
                const btn = document.createElement("button");
                btn.className = `tab-btn ${cat === browseCategory ? "active" : ""}`;
                btn.innerHTML = `<span>${ICONS[cat] || "🎵"} ${cat}</span><span class="count-badge">${list.length}</span>`;
                btn.onclick = () => selectCategoryToBrowse(cat);
                tabsContainer.appendChild(btn);
            });
        }

        function updateLibraryCounters() {
            let total = 0;
            CATEGORIES.forEach(cat => {
                total += (DATA[cat] || []).length;
            });
            const navText = document.getElementById("navLibraryText");
            if (navText) navText.textContent = `📚 Minha Biblioteca (${total})`;
            initTabs();
        }

        function setupTabsAutoScroll(wrapperId, leftBtnId, rightBtnId) {
            const wrapper = document.getElementById(wrapperId);
            const leftBtn = document.getElementById(leftBtnId);
            const rightBtn = document.getElementById(rightBtnId);
            if (!wrapper) return;

            let scrollInterval = null;
            function startScroll(speed) {
                if (scrollInterval) clearInterval(scrollInterval);
                scrollInterval = setInterval(() => {
                    wrapper.scrollLeft += speed;
                }, 16);
            }
            function stopScroll() {
                if (scrollInterval) {
                    clearInterval(scrollInterval);
                    scrollInterval = null;
                }
            }

            if (leftBtn) {
                leftBtn.onmouseenter = () => startScroll(-8);
                leftBtn.onmouseleave = stopScroll;
                leftBtn.onclick = () => { wrapper.scrollLeft -= 180; };
            }
            if (rightBtn) {
                rightBtn.onmouseenter = () => startScroll(8);
                rightBtn.onmouseleave = stopScroll;
                rightBtn.onclick = () => { wrapper.scrollLeft += 180; };
            }

            wrapper.addEventListener("mousemove", (e) => {
                const rect = wrapper.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const edgeZone = 40;
                if (mouseX < edgeZone) {
                    const ratio = 1 - (mouseX / edgeZone);
                    startScroll(-Math.round(4 + ratio * 8));
                } else if (mouseX > rect.width - edgeZone) {
                    const ratio = 1 - ((rect.width - mouseX) / edgeZone);
                    startScroll(Math.round(4 + ratio * 8));
                } else {
                    stopScroll();
                }
            });
            wrapper.addEventListener("mouseleave", stopScroll);
            wrapper.addEventListener("wheel", (e) => {
                if (e.deltaY !== 0) {
                    e.preventDefault();
                    wrapper.scrollLeft += e.deltaY;
                }
            }, { passive: false });
        }

        function setupListVerticalAutoScroll(listId) {
            const listEl = document.getElementById(listId);
            if (!listEl) return;

            let scrollInterval = null;
            function startScroll(speed) {
                if (scrollInterval) clearInterval(scrollInterval);
                scrollInterval = setInterval(() => {
                    listEl.scrollTop += speed;
                }, 16);
            }
            function stopScroll() {
                if (scrollInterval) {
                    clearInterval(scrollInterval);
                    scrollInterval = null;
                }
            }

            listEl.addEventListener("mousemove", (e) => {
                const rect = listEl.getBoundingClientRect();
                const mouseY = e.clientY - rect.top;
                const edgeZone = 60;

                if (mouseY < edgeZone && listEl.scrollTop > 0) {
                    const intensity = 1 - (mouseY / edgeZone);
                    startScroll(-Math.round(4 + intensity * 12));
                } else if (mouseY > rect.height - edgeZone && (listEl.scrollTop + listEl.clientHeight < listEl.scrollHeight - 5)) {
                    const intensity = 1 - ((rect.height - mouseY) / edgeZone);
                    startScroll(Math.round(4 + intensity * 12));
                } else {
                    stopScroll();
                }
            });
            listEl.addEventListener("mouseleave", stopScroll);
        }

        function selectCategoryToBrowse(category) {
            browseCategory = category;
            const container = document.getElementById("tabsContainer");
            if (container) {
                const btns = container.querySelectorAll(".tab-btn");
                btns.forEach(b => {
                    b.classList.toggle("active", b.textContent.includes(category));
                });
                const activeBtn = container.querySelector(".tab-btn.active");
                if (activeBtn) {
                    activeBtn.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
                }
            }
            const searchInput = document.getElementById("searchInput");
            if (searchInput && searchInput.value.trim() !== "") {
                handleLibrarySearch(searchInput.value);
            } else {
                renderList();
            }
        }

        function initSuggestionsTabs() {
            const container = document.getElementById("suggestionsTabsContainer");
            if (!container) return;
            container.innerHTML = "";
            CATEGORIES.forEach(cat => {
                const btn = document.createElement("button");
                btn.className = `tab-btn ${cat === currentSuggestionCategory ? "active" : ""}`;
                btn.innerHTML = `<span>${ICONS[cat] || "🎵"} ${cat}</span>`;
                btn.onclick = () => selectSuggestionCategory(cat);
                container.appendChild(btn);
            });
        }

        function selectSuggestionCategory(category) {
            isRadioActive = false;
            radioActiveTrack = null;
            currentSuggestionCategory = category;
            const container = document.getElementById("suggestionsTabsContainer");
            if (container) {
                const btns = container.querySelectorAll(".tab-btn");
                btns.forEach(b => {
                    b.classList.toggle("active", b.textContent.includes(category));
                });
                const activeBtn = container.querySelector(".tab-btn.active");
                if (activeBtn) {
                    activeBtn.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
                }
            }
            updateSuggestionHeader();
            if (suggestionsByGenre[category] && suggestionsByGenre[category].length > 0) {
                renderSuggestionsList(suggestionsByGenre[category]);
            } else {
                fetchFreshSuggestionsForCurrentGenre();
            }
        }

        let radioActiveTrack = null;
        let isFetchingSimilar = false;

        // Rádio da Faixa: Buscar Faixas Parecidas com IA baseado no ritmo e BPM
        async function openRadioForCurrentTrack() {
            const track = nowPlayingTrack || (nowPlayingQueue && nowPlayingQueue[nowPlayingIndex]);
            if (!track) {
                showToast("Selecione ou reproduza uma música primeiro para buscar faixas parecidas.");
                return;
            }
            await findSimilarToTrack(track);
        }

        async function findSimilarToTrack(track) {
            if (!track || !track.title) return;
            if (isFetchingSimilar) return;

            const bpm = track.bpm || detectBpmJs(track.title, track.category);
            const title = track.title;
            const artist = track.artist || "";
            const category = track.category || "Personalizada";
            const videoId = track.video_id || "";

            radioActiveTrack = track;
            isRadioActive = true;
            showToast(`📻 Buscando faixas parecidas com "${title}" (${bpm} BPM)...`);

            switchView("suggestions");

            const headerTitle = document.getElementById("suggestionActiveGenreTitle");
            const headerSub = document.getElementById("suggestionSubtext");
            const badge = document.getElementById("suggestionCountBadge");
            const btn = document.getElementById("btnRefreshSuggestions");

            if (headerTitle) headerTitle.innerHTML = `📻 Faixas Parecidas: <em>${escapeHtml(title)}</em>`;
            if (headerSub) headerSub.innerHTML = `Músicas no mesmo ritmo e gênero (<strong>${bpm} BPM</strong> • ${escapeHtml(category)}).`;
            if (badge) badge.textContent = "Minerando com IA...";
            if (btn) {
                btn.innerHTML = `<span>🔄 Buscar Mais no Mesmo Ritmo (${bpm} BPM)</span>`;
                btn.onclick = () => {
                    const cacheKey = (videoId || title) + "_rhythm";
                    delete radioSuggestionsCache[cacheKey];
                    findSimilarToTrack(track);
                };
            }

            const cacheKey = (videoId || title) + "_rhythm";
            if (radioSuggestionsCache[cacheKey] && radioSuggestionsCache[cacheKey].length > 0) {
                renderSuggestionsList(radioSuggestionsCache[cacheKey]);
                if (badge) badge.textContent = `${radioSuggestionsCache[cacheKey].length} faixas parecidas (${bpm} BPM)`;
                return;
            }

            showSuggestionsSkeleton();
            isFetchingSimilar = true;

            try {
                const res = await fetch(`/api/suggestions/related?title=${encodeURIComponent(title)}&artist=${encodeURIComponent(artist)}&category=${encodeURIComponent(category)}&video_id=${encodeURIComponent(videoId)}&bpm=${bpm}`);
                const data = await res.json();
                const tracks = data.tracks || [];

                radioSuggestionsCache[cacheKey] = tracks;
                renderSuggestionsList(tracks);
                if (badge) badge.textContent = `${tracks.length} faixas parecidas (${bpm} BPM)`;
            } catch (e) {
                console.error("Erro ao buscar faixas parecidas:", e);
                const container = document.getElementById("suggestionsList");
                if (container) {
                    container.innerHTML = `<div style="color: #ff5555; text-align: center; padding: 25px;">Erro ao buscar faixas parecidas. <button class="btn-sync-yt" style="margin-top:10px;" id="btnRetrySimilar">Tentar Novamente</button></div>`;
                    const retryBtn = document.getElementById("btnRetrySimilar");
                    if (retryBtn) retryBtn.onclick = () => findSimilarToTrack(track);
                }
            } finally {
                isFetchingSimilar = false;
            }
        }

        async function fetchRadioSuggestions() {
            if (radioActiveTrack && !isFetchingSimilar) {
                await findSimilarToTrack(radioActiveTrack);
            }
        }

        let isFetchingSuggestions = false;

        function updateSuggestionHeader() {
            const titleEl = document.getElementById("suggestionActiveGenreTitle");
            const subEl = document.getElementById("suggestionSubtext");
            const badge = document.getElementById("suggestionCountBadge");
            const btn = document.getElementById("btnRefreshSuggestions");

            if (isRadioActive) return;

            if (titleEl) titleEl.textContent = `✨ Novidades: ${currentSuggestionCategory}`;
            if (subEl) subEl.innerHTML = `Músicas buscadas em tempo real no YouTube para este estilo e ritmo. <strong>Nunca se repetem</strong>.`;
            const currentList = suggestionsByGenre[currentSuggestionCategory] || [];
            if (badge) {
                if (isFetchingSuggestions) {
                    badge.textContent = "Buscando...";
                } else if (currentList.length > 0) {
                    badge.textContent = `${currentList.length} inéditas`;
                } else {
                    badge.textContent = "0 inéditas";
                }
            }
            if (btn) btn.innerHTML = `<span>🔄 Buscar Mais Novas Músicas (Sem Repetir)</span>`;
        }

        function showSuggestionsSkeleton() {
            const container = document.getElementById("suggestionsList");
            if (!container) return;
            container.innerHTML = `
                <div class="skeleton-card"></div>
                <div class="skeleton-card"></div>
                <div class="skeleton-card"></div>
                <div class="skeleton-card"></div>
                <div class="skeleton-card"></div>
            `;
        }

        // Buscar sugestões sem repetição para o gênero atual
        async function fetchFreshSuggestionsForCurrentGenre() {
            if (isRadioActive) {
                delete radioSuggestionsCache[(nowPlayingTrack.video_id || nowPlayingTrack.title) + "_rhythm"];
                openRadioForCurrentTrack();
                return;
            }

            if (isFetchingSuggestions) return;
            isFetchingSuggestions = true;

            const container = document.getElementById("suggestionsList");
            const badge = document.getElementById("suggestionCountBadge");
            const btn = document.getElementById("btnRefreshSuggestions");

            if (badge) badge.textContent = "Buscando...";
            if (btn) btn.innerHTML = `<span>⏳ Buscando no YouTube...</span>`;
            showSuggestionsSkeleton();

            try {
                const res = await fetch("/api/suggestions/discover", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ category: currentSuggestionCategory })
                });
                const data = await res.json();
                const freshTracks = data.tracks || [];

                suggestionsByGenre[currentSuggestionCategory] = freshTracks;
                renderSuggestionsList(freshTracks);

                if (badge) badge.textContent = freshTracks.length > 0 ? `${freshTracks.length} inéditas` : "0 inéditas";
            } catch (e) {
                if (badge) badge.textContent = "0 inéditas";
                if (container) container.innerHTML = `<div style="color: #ff5555; text-align: center; padding: 25px;">Erro ao carregar sugestões. Clique no botão acima para tentar novamente.</div>`;
            } finally {
                isFetchingSuggestions = false;
                if (btn) btn.innerHTML = `<span>🔄 Buscar Mais Novas Músicas (Sem Repetir)</span>`;
            }
        }

        async function resetSeenHistory() {
            if (confirm("Deseja resetar o histórico de músicas vistas? As sugestões passadas poderão voltar a ser exibidas.")) {
                try {
                    await fetch("/api/suggestions/reset-seen", { method: "POST" });
                    showToast("Histórico de sugestões resetado!");
                    if (isRadioActive) openRadioForCurrentTrack();
                    else fetchFreshSuggestionsForCurrentGenre();
                } catch (e) {}
            }
        }

        // ==========================================================
        // SISTEMA DE PLAYLISTS OFICIAIS DO SPOTIFY (BRASIL & MUNDO)
        // ==========================================================
        function updateSpotifyNavBadge() {
            const pill = document.getElementById("spotifyBadgePill");
            if (pill && window.SPOTIFY_PLAYLISTS) {
                const count = Object.keys(window.SPOTIFY_PLAYLISTS).length;
                pill.textContent = `${count} Playlists`;
                const allChip = document.getElementById("spChip_all");
                if (allChip) allChip.textContent = `Todas (${count})`;
            }
        }

        function initSpotifyTabs() {
            updateSpotifyNavBadge();
            const tabsContainer = document.getElementById("spotifyTabsContainer");
            if (!tabsContainer || !SPOTIFY_PLAYLISTS) return;
            tabsContainer.innerHTML = "";

            Object.keys(SPOTIFY_PLAYLISTS).forEach(plId => {
                const pl = SPOTIFY_PLAYLISTS[plId];
                const meta = pl.meta || {};
                const tracks = pl.tracks || [];
                const btn = document.createElement("button");
                btn.className = `tab-btn ${plId === activeSpotifyPlaylist ? "active" : ""}`;
                btn.id = `spTab_${plId}`;
                btn.innerHTML = `<span>${meta.icon || "🟢"} ${escapeHtml(meta.name || plId)}</span><span class="count-badge">${tracks.length}</span>`;
                btn.onclick = () => selectSpotifyPlaylist(plId);
                tabsContainer.appendChild(btn);
            });

            setupTabsAutoScroll("spotifyTabsWrapper", "spotifyTabsScrollLeft", "spotifyTabsScrollRight");
            renderSpotifyPlaylist();
        }

        function initSpotifyView() {
            initSpotifyTabs();
        }

        function selectSpotifyPlaylist(plId) {
            activeSpotifyPlaylist = plId;
            document.querySelectorAll("#spotifyTabsContainer .tab-btn").forEach(btn => {
                btn.classList.toggle("active", btn.id === `spTab_${plId}`);
            });
            renderSpotifyPlaylist();
        }

        function handleSpotifySearch(query) {
            spotifySearchQuery = (query || "").trim().toLowerCase();
            const clearBtn = document.getElementById("btnSpotifySearchClear");
            if (clearBtn) clearBtn.style.display = spotifySearchQuery ? "block" : "none";
            renderSpotifyPlaylist();
        }

        function clearSpotifySearch() {
            const input = document.getElementById("spotifySearchInput");
            if (input) input.value = "";
            handleSpotifySearch("");
        }

        function updateQueueUI() {
            updateAllQueueBadges();
            if (browseView === "queue") loadQueue();
            updateUpcomingTrackUI();
            const modal = document.getElementById("spotifyQueueModal");
            if (modal && modal.style.display === "flex") {
                renderSpotifyQueueModalContent();
            }
        }

        // ==========================================================
        // DETECTOR ROBUSTO DE BPM POR TÍTULO E GÊNERO MUSICAL
        // ==========================================================
        function detectBpmJs(title = "", category = "") {
            const text = `${title} ${category}`.toLowerCase();
            const match = text.match(/(\d{2,3})\s*bpm/i);
            if (match) {
                const val = parseInt(match[1], 10);
                if (val >= 60 && val <= 200) return val;
            }
            if (text.includes("mega funk") || text.includes("ritmada")) return 130;
            if (text.includes("funk")) return 130;
            if (text.includes("eletronica") || text.includes("electronic") || text.includes("house") || text.includes("tech house")) return 126;
            if (text.includes("techno") || text.includes("trance") || text.includes("hardstyle")) return 138;
            if (text.includes("trap") || text.includes("hip hop") || text.includes("rap")) return 140;
            if (text.includes("sertanejo") || text.includes("modao")) return 118;
            if (text.includes("pagode") || text.includes("samba")) return 105;
            if (text.includes("piseiro") || text.includes("forro") || text.includes("arrocha")) return 145;
            if (text.includes("reggae")) return 80;
            if (text.includes("pop") || text.includes("hits")) return 120;
            if (text.includes("rock")) return 124;
            return 128;
        }

        // ==========================================================
        // CÁLCULO E ASSISTENTE DE PRÓXIMA MÚSICA IDEAL (BEATMATCH & HARMONIA)
        // ==========================================================
        let currentIdealTrack = null;
        let djModeNextTrack = null;

        function calculateIdealNextTrackScore(candidate, current) {
            if (!candidate || !current) return 75;
            const curBpm = parseFloat(current.bpm) || detectBpmJs(current.title, current.category) || 128;
            const candBpm = parseFloat(candidate.bpm) || detectBpmJs(candidate.title, candidate.category) || 128;
            const diff = Math.abs(curBpm - candBpm);
            
            // Proximidade de BPM: penalidade suave por desvio
            let score = Math.max(50, Math.round(100 - (diff * 3.5)));
            
            // Gênero bloqueado tem prioridade máxima absoluta
            const targetGenre = (currentLockedGenre || current.category || "").toLowerCase();
            const candGenre = (candidate.category || "").toLowerCase();
            if (targetGenre && candGenre) {
                const targetKey = targetGenre.split('&')[0].trim();
                if (candGenre.includes(targetKey) || targetGenre.includes(candGenre)) {
                    score = Math.min(99, score + 8);
                } else if (targetGenre.includes("funk") && candGenre.includes("funk")) {
                    score = Math.min(99, score + 6);
                } else if (targetGenre.includes("sertanejo") && candGenre.includes("sertanejo")) {
                    score = Math.min(99, score + 6);
                }
            }
            
            // Bônus se os artistas forem semelhantes ou mesmo artista
            if (candidate.artist && current.artist && candidate.artist.toLowerCase() === current.artist.toLowerCase()) {
                score = Math.min(99, score + 4);
            }

            // Ajustes específicos por modo DJ
            if (djPlayMode === "energy") {
                if (candBpm > curBpm && candBpm <= curBpm + 8) {
                    score = Math.min(99, score + 8);
                } else if (candBpm < curBpm) {
                    score = Math.max(45, score - 6);
                }
            } else if (djPlayMode === "smooth") {
                if (diff <= 2) {
                    score = Math.min(99, score + 8);
                }
            }
            return Math.min(99, Math.max(50, score));
        }

        // ==========================================================
        // HISTÓRICO DE REPRODUÇÃO & FILTRO ANTI-REPETIÇÃO INTELIGENTE
        // ==========================================================
        let recentPlaybackHistoryIds = [];
        window.recentPlaybackHistoryIds = recentPlaybackHistoryIds;

        function recordTrackInRecentHistory(videoId) {
            if (!videoId) return;
            recentPlaybackHistoryIds = recentPlaybackHistoryIds.filter(id => id !== videoId);
            recentPlaybackHistoryIds.push(videoId);
            if (recentPlaybackHistoryIds.length > 50) recentPlaybackHistoryIds.shift();
            window.recentPlaybackHistoryIds = recentPlaybackHistoryIds;
        }
        window.recordTrackInRecentHistory = recordTrackInRecentHistory;

        function detectCategoryFromTrack(track) {
            if (!track) return currentLockedGenre || "Mega Funk & Ritmadas";
            const text = ((track.title || "") + " " + (track.artist || "") + " " + (track.category || "")).toLowerCase();
            if (/cumbia|villera|santafesina|chicha|sonidera|cuarteto|palmeras|damas|pibes|mattioli|gilda|fuego|marama|rombai|ke personajes/i.test(text)) {
                return "Cumbia";
            }
            if (/mega funk|ritmada/i.test(text)) return "Mega Funk & Ritmadas";
            if (/mandel|funk/i.test(text)) return "Funk Paulista, BH & Mandelão";
            if (/sertanejo|modao|sofrencia|piseiro|pisadinha|arrocha/i.test(text)) return "Sertanejo Universitário & Atual";
            if (/eletr|house|bass|desande|edm|techno/i.test(text)) return "Eletrônica, House & Desande";
            if (/reggaeton|cachengue|rkt|dembow|perreo|latino/i.test(text)) return "Reggaeton, Cachengue & Latino";
            if (/rap|trap|drill|hip/i.test(text)) return "Trap & Rap Nacional";
            if (/pagode|samba/i.test(text)) return "Samba & Pagode";
            if (/rock|mpb/i.test(text)) return "Rock & Pop Nostalgia";
            return track.category || currentLockedGenre || "Mega Funk & Ritmadas";
        }

        // MOTOR PRINCIPAL DE ESCOLHA DA PRÓXIMA FAIXA CONFORME O MODO DE ATUAÇÃO
        function calculateDjModeNextTrack(curTrack) {
            if (!curTrack) curTrack = nowPlayingTrack;
            if (!curTrack) return null;

            const curBpm = parseFloat(curTrack.bpm) || detectBpmJs(curTrack.title, curTrack.category) || 128;
            const targetGenre = (currentLockedGenre || curTrack.category || "").toLowerCase();
            const detectedStyle = detectCategoryFromTrack(curTrack);

            // Coleta faixas da fila atual que ainda NÃO foram tocadas recentemente
            const unplayedInQueue = (nowPlayingQueue || []).filter(t => 
                t && t.video_id && t.video_id !== curTrack.video_id && !recentPlaybackHistoryIds.includes(t.video_id)
            );

            // Condição: se a lista tiver 2 ou menos faixas, OU se todas as faixas da lista já foram tocadas
            // (passou da 2ª), pesquisa FORA da lista para não repetir a mesma música em loop!
            const shouldSearchOutside = (!nowPlayingQueue || nowPlayingQueue.length <= 2 || unplayedInQueue.length === 0);

            let pool = [];

            if (!shouldSearchOutside && unplayedInQueue.length > 0) {
                // Ainda existem faixas inéditas na lista atual
                pool = unplayedInQueue.slice();
            } else {
                // PESQUISA FORA DA LISTA (Biblioteca Completa + 144 Playlists Spotify + Sugestões)
                // 1. Categoria detectada ou bloqueada na biblioteca
                if (window.DATA) {
                    if (window.DATA[detectedStyle]) {
                        pool = pool.concat(window.DATA[detectedStyle]);
                    }
                    if (currentLockedGenre && window.DATA[currentLockedGenre] && currentLockedGenre !== detectedStyle) {
                        pool = pool.concat(window.DATA[currentLockedGenre]);
                    }
                    // Adiciona categorias com nome similar
                    Object.keys(window.DATA).forEach(cat => {
                        const catLow = cat.toLowerCase();
                        if (catLow.includes(detectedStyle.toLowerCase()) || detectedStyle.toLowerCase().includes(catLow)) {
                            pool = pool.concat(window.DATA[cat]);
                        }
                    });
                }

                // 2. Playlists do Spotify compatíveis com o estilo/gênero da faixa
                if (window.SPOTIFY_PLAYLISTS) {
                    const isCumbia = (detectedStyle === "Cumbia") || /cumbia|villera|santafesina|chicha|sonidera|cuarteto|palmeras|damas|ke personajes/i.test(curTrack.title + " " + (curTrack.artist || ""));
                    const isFunk = /funk|mandel|ritmada/i.test(detectedStyle + " " + curTrack.title);
                    const isSertanejo = /sertanejo|modao|sofrencia|piseiro/i.test(detectedStyle + " " + curTrack.title);
                    const isEletronica = /eletr|bass|desande|house/i.test(detectedStyle + " " + curTrack.title);
                    const isLatino = /reggaeton|latino|cachengue/i.test(detectedStyle + " " + curTrack.title);
                    const isRap = /rap|trap/i.test(detectedStyle + " " + curTrack.title);
                    const isPagode = /pagode|samba/i.test(detectedStyle + " " + curTrack.title);

                    Object.values(window.SPOTIFY_PLAYLISTS).forEach(pl => {
                        const pName = (pl.meta?.name || "").toLowerCase();
                        const pGenre = (pl.meta?.genre || "").toLowerCase();
                        const pDesc = (pl.meta?.desc || "").toLowerCase();
                        const fullPlText = `${pName} ${pGenre} ${pDesc}`;

                        let match = false;
                        if (isCumbia && /cumbia|villera|santafesina|chicha|sonidera|cuarteto|palmeras|damas|ke personajes|gilda/i.test(fullPlText)) match = true;
                        else if (isFunk && /funk|mandel|ritmada|fluxo|favela/i.test(fullPlText)) match = true;
                        else if (isSertanejo && /sertanejo|modao|sofrencia|piseiro|pisadinha|agro/i.test(fullPlText)) match = true;
                        else if (isEletronica && /eletronica|bass|desande|house|edm|club/i.test(fullPlText)) match = true;
                        else if (isLatino && /reggaeton|latino|cachengue|rkt|perreo/i.test(fullPlText)) match = true;
                        else if (isRap && /rap|trap|drill|hip/i.test(fullPlText)) match = true;
                        else if (isPagode && /pagode|samba|resenha/i.test(fullPlText)) match = true;

                        if (match && pl.tracks && pl.tracks.length > 0) {
                            pool = pool.concat(pl.tracks);
                        }
                    });
                }

                // 3. Sugestões por gênero
                if (suggestionsByGenre && suggestionsByGenre[detectedStyle]) {
                    pool = pool.concat(suggestionsByGenre[detectedStyle]);
                }

                // 4. Se o pool ainda estiver pequeno, usa toda a biblioteca e playlists
                if (pool.length < 15 && window.DATA) {
                    Object.values(window.DATA).forEach(list => {
                        if (Array.isArray(list)) pool = pool.concat(list);
                    });
                }
                if (pool.length < 15 && window.SPOTIFY_PLAYLISTS) {
                    Object.values(window.SPOTIFY_PLAYLISTS).forEach(pl => {
                        if (pl.tracks) pool = pool.concat(pl.tracks.slice(0, 5));
                    });
                }
            }

            // Deduplica e remove a faixa que já está tocando e as TOCADAS RECENTEMENTE (FILTRO ANTI-REPETIÇÃO)
            const seen = new Set();
            if (curTrack.video_id) seen.add(curTrack.video_id);
            const candidates = [];

            for (const t of pool) {
                if (!t || !t.video_id || seen.has(t.video_id)) continue;
                // NÃO REPETE FAIXAS TOCADAS RECENTEMENTE SE HOUVER OPÇÕES
                if (recentPlaybackHistoryIds.includes(t.video_id)) continue;
                seen.add(t.video_id);
                if (!t.bpm) t.bpm = detectBpmJs(t.title, t.category) || 128;
                candidates.push(t);
            }

            // Se todas as faixas do pool já foram tocadas (pool esgotado), relaxa o filtro para as mais antigas
            if (candidates.length === 0) {
                for (const t of pool) {
                    if (!t || !t.video_id || t.video_id === curTrack.video_id || seen.has(t.video_id)) continue;
                    seen.add(t.video_id);
                    if (!t.bpm) t.bpm = detectBpmJs(t.title, t.category) || 128;
                    candidates.push(t);
                }
            }

            if (candidates.length === 0) {
                return null;
            }

            let chosenTrack = null;
            let chosenScore = 0;

            if (djPlayMode === "match") {
                // MATCH PERFEITO: Harmonia máxima e BPM mais compatível
                let bestScore = -1;
                candidates.forEach(t => {
                    const score = calculateIdealNextTrackScore(t, curTrack);
                    if (score > bestScore) {
                        bestScore = score;
                        chosenTrack = t;
                        chosenScore = score;
                    }
                });
            } else if (djPlayMode === "energy") {
                // PEAK TIME: Eleva o BPM (+2 a +8 BPM acima da atual) para aumentar a energia
                let bestScore = -999;
                candidates.forEach(t => {
                    const candBpm = parseFloat(t.bpm) || 128;
                    const diff = candBpm - curBpm; // positivo = acelera
                    let energyScore = 50;
                    if (diff >= 2 && diff <= 8) {
                        energyScore = 95 + (8 - Math.abs(diff - 4));
                    } else if (diff > 8 && diff <= 14) {
                        energyScore = 88;
                    } else if (diff > 0 && diff < 2) {
                        energyScore = 78;
                    } else if (diff === 0) {
                        energyScore = 70;
                    } else {
                        energyScore = Math.max(30, 60 + diff * 2);
                    }

                    const candCat = (t.category || "").toLowerCase();
                    if (targetGenre && candCat && (candCat.includes(targetGenre.split('&')[0].trim()) || targetGenre.includes(candCat))) {
                        energyScore += 10;
                    }

                    if (energyScore > bestScore) {
                        bestScore = energyScore;
                        chosenTrack = t;
                        chosenScore = Math.min(99, energyScore);
                    }
                });
            } else if (djPlayMode === "shuffle") {
                // SMART SHUFFLE: Aleatório harmônico respeitando o gênero
                const compatible = candidates.filter(t => {
                    const candBpm = parseFloat(t.bpm) || 128;
                    return Math.abs(candBpm - curBpm) <= 14;
                });
                const listToPick = compatible.length >= 2 ? compatible : candidates;
                const rndIndex = Math.floor(Math.random() * listToPick.length);
                chosenTrack = listToPick[rndIndex];
                chosenScore = calculateIdealNextTrackScore(chosenTrack, curTrack);
            } else if (djPlayMode === "smooth") {
                // SMOOTH FLOW: Menor desvio de BPM (diff <= 2) para transições suaves de 8s
                let bestDiff = 999;
                let bestScore = -1;
                candidates.forEach(t => {
                    const candBpm = parseFloat(t.bpm) || 128;
                    const diff = Math.abs(curBpm - candBpm);
                    const score = calculateIdealNextTrackScore(t, curTrack);
                    if (diff < bestDiff || (diff === bestDiff && score > bestScore)) {
                        bestDiff = diff;
                        bestScore = score;
                        chosenTrack = t;
                        chosenScore = score;
                    }
                });
            } else if (djPlayMode === "club") {
                // BALADA & CLUB DJ: Foco na pista de dança, BPM compatível (diff <= 5), alto impacto e transição explosiva
                let bestClubScore = -999;
                candidates.forEach(t => {
                    const candBpm = parseFloat(t.bpm) || 128;
                    const diff = Math.abs(curBpm - candBpm);
                    let clubScore = 65;

                    // Compatibilidade de BPM para mixagem ao vivo de balada
                    if (diff <= 3) {
                        clubScore += 30;
                    } else if (diff <= 6) {
                        clubScore += 22;
                    } else if (diff <= 10) {
                        clubScore += 12;
                    } else {
                        clubScore -= (diff - 10) * 2;
                    }

                    // Bônus de gênero compatível ou mesmo estilo
                    const candCat = (t.category || "").toLowerCase();
                    const candTitle = (t.title || "").toLowerCase();
                    if (targetGenre && candCat && (candCat.includes(targetGenre.split('&')[0].trim()) || targetGenre.includes(candCat))) {
                        clubScore += 15;
                    }

                    // Bônus para faixas de alta energia / remixes / batidas marcadas para pistas
                    if (/remix|edit|vip|drop|baile|mandel|desande|rave|club|bass|pista|fest|charanga/i.test(candTitle)) {
                        clubScore += 8;
                    }

                    if (clubScore > bestClubScore) {
                        bestClubScore = clubScore;
                        chosenTrack = t;
                        chosenScore = Math.min(99, Math.max(76, clubScore));
                    }
                });
            }

            if (chosenTrack) {
                currentIdealTrack = chosenTrack;
                djModeNextTrack = chosenTrack;
                if (shouldSearchOutside) {
                    chosenTrack._isExternalDiscovery = true;
                }
            }
            return chosenTrack;
        }

        function updateDjIdealHelper(curTrack) {
            const helper = document.getElementById("djIdealHelper");
            const nameEl = document.getElementById("djIdealTrackName");
            let badgeEl = document.getElementById("djIdealMatchBadge") || document.getElementById("djIdealScoreBadge");
            if (!helper || !nameEl) return;

            if (!curTrack) {
                helper.style.display = "none";
                return;
            }

            const targetTrack = djModeNextTrack || currentIdealTrack || calculateDjModeNextTrack(curTrack);
            if (targetTrack) {
                currentIdealTrack = targetTrack;
                const candBpm = targetTrack.bpm || 128;
                nameEl.textContent = `${targetTrack.title} • ${candBpm} BPM`;

                if (badgeEl) {
                    if (djPlayMode === "match") {
                        const score = calculateIdealNextTrackScore(targetTrack, curTrack);
                        badgeEl.textContent = `🎯 ${score}% Match`;
                        badgeEl.className = score >= 93 ? "dj-ideal-match-badge" : "dj-ideal-match-badge match-great";
                    } else if (djPlayMode === "energy") {
                        const curBpm = parseFloat(curTrack.bpm) || 128;
                        const diff = Math.round(candBpm - curBpm);
                        const diffStr = diff >= 0 ? `+${diff}` : `${diff}`;
                        badgeEl.textContent = `⚡ Peak Time (${diffStr} BPM)`;
                        badgeEl.className = "dj-ideal-match-badge";
                    } else if (djPlayMode === "shuffle") {
                        badgeEl.textContent = `🔀 Smart Shuffle`;
                        badgeEl.className = "dj-ideal-match-badge match-great";
                    } else if (djPlayMode === "smooth") {
                        badgeEl.textContent = `🌊 Smooth Flow`;
                        badgeEl.className = "dj-ideal-match-badge";
                    }
                }
                helper.style.display = "flex";
            } else {
                helper.style.display = "none";
                currentIdealTrack = null;
            }
        }

        function playIdealNextTrack() {
            if (!currentIdealTrack) {
                showToast("Nenhuma faixa ideal calculada no momento.");
                return;
            }
            showToast(`🎯 Faixa ideal selecionada: ${currentIdealTrack.title.slice(0, 30)}...`);
            const existsIdx = pendingQueue.findIndex(q => q.video_id === currentIdealTrack.video_id);
            if (existsIdx !== -1) {
                pendingQueue.splice(existsIdx, 1);
            }
            pendingQueue.unshift(currentIdealTrack);
            updateUpcomingTrackUI();
            updateDjMixerUI();
            
            if (nowPlayingTrack && nowPlayingTrack.video_id !== currentIdealTrack.video_id) {
                triggerCrossfade(currentIdealTrack);
            } else {
                playTrackInstantWithFadeIn(currentIdealTrack);
            }
        }
        window.playIdealNextTrack = playIdealNextTrack;

        function renderSpotifyPlaylist() {
            const featuredCard = document.getElementById("spotifyFeaturedCard");
            const listContainer = document.getElementById("spotifyTrackList");
            if (!listContainer || !SPOTIFY_PLAYLISTS) return;

            const plData = SPOTIFY_PLAYLISTS[activeSpotifyPlaylist] || Object.values(SPOTIFY_PLAYLISTS)[0];
            if (!plData) {
                listContainer.innerHTML = '<div style="color: var(--text-dim); text-align: center; padding: 25px;">Nenhuma playlist do Spotify encontrada.</div>';
                return;
            }

            const meta = plData.meta || {};
            const allTracks = plData.tracks || [];

            // 1. Renderiza o Card de Destaque da Playlist
            if (featuredCard) {
                featuredCard.innerHTML = `
                    <div class="featured-card-content">
                        <div class="featured-card-left">
                            <div class="featured-card-icon">${meta.icon || "🟢"}</div>
                            <div class="featured-card-info">
                                <div class="featured-card-title">
                                    <span>${escapeHtml(meta.name)}</span>
                                    <span class="featured-meta-chip">${escapeHtml(meta.genre || "Hit")}</span>
                                </div>
                                <div class="featured-card-desc">${escapeHtml(meta.desc || "")}</div>
                                <div class="featured-card-meta">
                                    <span class="featured-meta-chip">🔥 ${allTracks.length} Faixas Oficiais</span>
                                    <span class="featured-meta-chip">⚡ ~${meta.bpm || 130} BPM</span>
                                    <span class="featured-meta-chip" style="color: #1ed760; border-color: rgba(30,215,96,0.4);">✓ Sincronizado</span>
                                </div>
                            </div>
                        </div>
                        <div class="featured-card-actions">
                            <button class="btn-spotify-play-top10" onclick="playSpotifyTop10('${meta.id}')" title="Tocar os 10 maiores sucessos em sequência contínua com transições">
                                ▶ Tocar Top 10 (Sequência)
                            </button>
                            <button class="btn-spotify-play-all" onclick="playSpotifyPlaylistAll('${meta.id}')" title="Tocar todas as faixas da playlist com DJ crossfade">
                                ▶ Tocar Todas
                            </button>
                            <button class="btn-spotify-queue-all" onclick="queueSpotifyAll('${meta.id}')" title="Adicionar todas à fila de reprodução">
                                + Fila Completa
                            </button>
                        </div>
                    </div>
                `;
            }

            // 2. Filtra faixas pela barra de busca
            let filtered = allTracks;
            if (spotifySearchQuery) {
                filtered = allTracks.filter(t => 
                    (t.title && t.title.toLowerCase().includes(spotifySearchQuery)) ||
                    (t.artist && t.artist.toLowerCase().includes(spotifySearchQuery)) ||
                    (t.category && t.category.toLowerCase().includes(spotifySearchQuery))
                );
            }

            const badge = document.getElementById("spotifySearchBadgeCount");
            if (badge) badge.textContent = spotifySearchQuery ? `${filtered.length} encontradas` : "";

            // 3. Renderiza lista de faixas
            listContainer.innerHTML = "";
            if (filtered.length === 0) {
                let globalMatches = [];
                if (window.SPOTIFY_PLAYLISTS && spotifySearchQuery) {
                    Object.keys(window.SPOTIFY_PLAYLISTS).forEach(plKey => {
                        const pl = window.SPOTIFY_PLAYLISTS[plKey];
                        const plName = pl.meta?.name || plKey;
                        (pl.tracks || []).forEach(t => {
                            if ((t.title && t.title.toLowerCase().includes(spotifySearchQuery)) ||
                                (t.artist && t.artist.toLowerCase().includes(spotifySearchQuery))) {
                                if (!globalMatches.some(m => m.video_id === t.video_id)) {
                                    globalMatches.push({ ...t, playlistName: plName, playlistKey: plKey });
                                }
                            }
                        });
                    });
                }

                listContainer.innerHTML = `
                    <div style="text-align: center; padding: 35px 20px; color: var(--text-dim); max-width: 520px; margin: 0 auto;">
                        <div style="font-size: 32px; margin-bottom: 8px;">🔍</div>
                        <div style="font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 6px;">Nenhuma faixa com "<strong>${escapeHtml(spotifySearchQuery)}</strong>" nesta playlist.</div>
                        <div style="font-size: 12px; margin-bottom: 16px;">Esta playlist possui apenas ${allTracks.length} faixas. Você pode buscar nas outras 111 playlists ou na Pesquisa Livre do YouTube!</div>
                        <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
                            ${globalMatches.length > 0 ? `
                                <button class="btn-sync-yt" onclick="renderGlobalSpotifySearchResults('${escapeQuotes(spotifySearchQuery)}')" style="margin: 0; background: linear-gradient(135deg, #1ed760, #00b0ff); color: #000; font-weight: 700; font-size: 12px; padding: 8px 14px;">
                                    🟢 Ver ${globalMatches.length} músicas em outras Playlists Spotify
                                </button>
                            ` : ''}
                            <button class="btn-sync-yt" onclick="goToFreeSearch('${escapeQuotes(spotifySearchQuery)}')" style="margin: 0; background: rgba(0, 242, 254, 0.15); border: 1px solid rgba(0, 242, 254, 0.4); color: var(--accent); font-size: 12px; padding: 8px 14px;">
                                ⚡ Buscar no YouTube / Pesquisa Livre
                            </button>
                        </div>
                    </div>
                `;
                return;
            }

            const currentVideoId = nowPlayingTrack ? nowPlayingTrack.video_id : null;
            const upcomingTrack = getUpcomingTrack();
            const upcomingVideoId = upcomingTrack ? upcomingTrack.video_id : null;

            filtered.forEach((track, index) => {
                const meta = getTrackTransitionCardMeta(track, currentVideoId, upcomingVideoId, (!isTransitioning && (track.video_id === lastAddedVideoId || track.addedJustNow)));
                const queueIdx = (pendingQueue || []).findIndex(q => q.video_id === track.video_id);
                const isInQueue = queueIdx !== -1;
                const queuePosText = isInQueue ? (queueIdx === 0 ? "✓ Fila #1 (Próxima)" : `✓ Fila #${queueIdx + 1}`) : "";

                let cardClasses = "track-card" + meta.cardExtraClass;
                if (!meta.isOutgoing && !meta.isIncoming) {
                    if (meta.isPlaying) cardClasses += " playing";
                    else if (meta.isNext) cardClasses += " upcoming-next";
                }

                const card = document.createElement("div");
                card.className = cardClasses;
                card.id = `card_sp_${track.video_id}`;
                card.setAttribute("data-video-id", track.video_id);
                if (meta.transitionRole) card.setAttribute("data-transition-role", meta.transitionRole);

                let rankClass = "spotify-rank-normal";
                if (track.rank === 1) rankClass = "spotify-rank-1";
                else if (track.rank === 2) rankClass = "spotify-rank-2";
                else if (track.rank === 3) rankClass = "spotify-rank-3";

                const rankText = track.rank ? `#${track.rank}` : `#${index + 1}`;

                let statusBadge = "";
                if (meta.statusBadgeHtml) {
                    statusBadge = meta.statusBadgeHtml;
                } else if (isInQueue) {
                    statusBadge = `<span class="track-status-pill status-queue">${queuePosText}</span>`;
                } else if (meta.isPlaying) {
                    statusBadge = '<span class="track-status-pill status-playing">▶ TOCANDO AGORA</span>';
                } else if (meta.isNext) {
                    statusBadge = '<span class="track-status-pill status-next">⏭️ A SEGUIR</span>';
                }

                const durMin = Math.floor((track.duration || 180) / 60);
                const durSec = String((track.duration || 180) % 60).padStart(2, "0");

                let idealBadgeHtml = "";
                if (nowPlayingTrack && track.video_id !== nowPlayingTrack.video_id) {
                    const score = calculateIdealNextTrackScore(track, nowPlayingTrack);
                    if (score >= 93) {
                        idealBadgeHtml = `<span class="badge-ideal-track match-perfect" title="Harmonia e BPM ideais para mixagem">🎯 ${score}% Match</span>`;
                        cardClasses += " ideal-match-highlight";
                    } else if (score >= 86) {
                        idealBadgeHtml = `<span class="badge-ideal-track match-great" title="Excelente sincronia de mix">⚡ ${score}% Mix</span>`;
                    }
                }
                card.className = cardClasses;

                card.innerHTML = `
                    <div class="track-left-content">
                        <span class="spotify-rank-pill ${rankClass}">${rankText}</span>
                        <div class="track-thumb-box" onclick="playSpotifyTrackByIndex(${index})">
                            <img src="https://img.youtube.com/vi/${track.video_id}/hqdefault.jpg" class="track-thumb" loading="lazy" alt="Thumb" onerror="this.onerror=null; this.src='https://img.youtube.com/vi/${track.video_id}/mqdefault.jpg';">
                            <div class="thumb-play-overlay">▶</div>
                        </div>
                        <div class="track-main-info" onclick="playSpotifyTrackByIndex(${index})">
                            <div class="track-title">${escapeHtml(track.title)}</div>
                            <div class="track-artist-row">
                                ${statusBadge}
                                ${idealBadgeHtml}
                                <span class="track-artist">${escapeHtml(track.artist || meta.name)}</span>
                                <span class="badge-bpm-chip">⚡ ${track.bpm || 130} BPM</span>
                                <span class="track-duration-pill">⏱️ ${durMin}:${durSec}</span>
                                <span class="spotify-inline-tag" title="Fonte Oficial: Spotify ${escapeHtml(meta.name)}">🟢 Spotify</span>
                            </div>
                        </div>
                    </div>
                    <div class="track-actions-right">
                        <button class="btn-card-action btn-card-play" onclick="playSpotifyTrackByIndex(${index})" title="Tocar esta música imediatamente">
                            ▶ Tocar
                        </button>
                        <button class="btn-card-action btn-card-queue" onclick="queueSpotifyTrackByIndex(${index})" title="Adicionar à fila Spotify">
                            ${isInQueue ? "✓ Na Fila" : "+ Fila"}
                        </button>
                    </div>
                `;

                listContainer.appendChild(card);
            });
        }

        function playTrack(track, sourceCategory = "Spotify") {
            if (!track) return;
            const cat = sourceCategory || track.category || "Spotify";
            playFromList([track], 0, "spotify", cat);
        }

        function playSpotifyTrackByIndex(index) {
            const plData = SPOTIFY_PLAYLISTS[activeSpotifyPlaylist];
            if (!plData || !plData.tracks || !plData.tracks[index]) return;
            const tracks = plData.tracks;
            playFromList(tracks, index, "spotify", `Spotify - ${plData.meta?.name || "Hits"}`);
        }

        async function queueSpotifyTrackByIndex(index) {
            const plData = SPOTIFY_PLAYLISTS[activeSpotifyPlaylist];
            if (!plData || !plData.tracks || !plData.tracks[index]) return;
            const track = plData.tracks[index];
            await addToQueue(track);
            renderSpotifyPlaylist();
        }

        window.addToPendingQueue = addToQueue;

        async function playSpotifyTop10(plId) {
            const plData = SPOTIFY_PLAYLISTS[plId] || SPOTIFY_PLAYLISTS[activeSpotifyPlaylist];
            if (!plData || !plData.tracks || plData.tracks.length === 0) return;
            const tracks = plData.tracks;
            const plName = plData.meta?.name || "Top Brasil";

            // Limpa a fila existente
            await fetch("/api/queue/clear", { method: "POST" });
            pendingQueue = [];

            // Enfileira da faixa 2 até a 10 em sequência exata
            const topTracks = tracks.slice(0, 10);
            for (let i = 1; i < topTracks.length; i++) {
                await fetch("/api/queue/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(topTracks[i])
                });
                pendingQueue.push(topTracks[i]);
            }

            updateQueueUI();
            playTrack(topTracks[0], `Spotify - ${plName}`);
            showToast(`🟢 Tocando Top 10 de ${plName} em sequência contínua!`);
            renderSpotifyPlaylist();
        }

        async function playSpotifyPlaylistAll(plId) {
            const plData = SPOTIFY_PLAYLISTS[plId] || SPOTIFY_PLAYLISTS[activeSpotifyPlaylist];
            if (!plData || !plData.tracks || plData.tracks.length === 0) return;
            const tracks = plData.tracks;
            const plName = plData.meta?.name || "Spotify";

            await fetch("/api/queue/clear", { method: "POST" });
            pendingQueue = [];

            for (let i = 1; i < tracks.length; i++) {
                await fetch("/api/queue/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(tracks[i])
                });
                pendingQueue.push(tracks[i]);
            }

            updateQueueUI();
            playTrack(tracks[0], `Spotify - ${plName}`);
            showToast(`🟢 Tocando playlist completa: ${plName} (${tracks.length} músicas)!`);
            renderSpotifyPlaylist();
        }

        async function queueSpotifyAll(plId) {
            const plData = SPOTIFY_PLAYLISTS[plId] || SPOTIFY_PLAYLISTS[activeSpotifyPlaylist];
            if (!plData || !plData.tracks) return;
            const tracks = plData.tracks;
            const plName = plData.meta?.name || "Spotify";

            for (const t of tracks) {
                await fetch("/api/queue/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(t)
                });
                pendingQueue.push(t);
            }

            updateQueueUI();
            showToast(`📋 ${tracks.length} músicas de ${plName} adicionadas à fila!`);
            renderSpotifyPlaylist();
        }

        function renderGlobalSpotifySearchResults(query) {
            const listContainer = document.getElementById("spotifyTrackList");
            if (!listContainer || !window.SPOTIFY_PLAYLISTS) return;
            const q = (query || "").trim().toLowerCase();
            if (!q) return;

            let globalMatches = [];
            Object.keys(window.SPOTIFY_PLAYLISTS).forEach(plKey => {
                const pl = window.SPOTIFY_PLAYLISTS[plKey];
                const plName = pl.meta?.name || plKey;
                (pl.tracks || []).forEach(t => {
                    if ((t.title && t.title.toLowerCase().includes(q)) ||
                        (t.artist && t.artist.toLowerCase().includes(q))) {
                        if (!globalMatches.some(m => m.video_id === t.video_id)) {
                            globalMatches.push({ ...t, playlistName: plName, playlistKey: plKey });
                        }
                    }
                });
            });

            const badge = document.getElementById("spotifySearchBadgeCount");
            if (badge) badge.textContent = `${globalMatches.length} em todo Spotify`;

            listContainer.innerHTML = "";
            if (globalMatches.length === 0) {
                listContainer.innerHTML = `<div style="text-align:center; padding: 30px; color: var(--text-dim);">Nenhuma música encontrada em nenhuma das 111 playlists para "${escapeHtml(q)}". <br><button class="btn-sync-yt" onclick="goToFreeSearch('${escapeQuotes(q)}')" style="margin-top:12px;">⚡ Buscar no YouTube</button></div>`;
                return;
            }

            const currentVideoId = nowPlayingTrack ? nowPlayingTrack.video_id : null;
            const upcomingTrack = getUpcomingTrack();
            const upcomingVideoId = upcomingTrack ? upcomingTrack.video_id : null;

            globalMatches.forEach((track, index) => {
                const meta = getTrackTransitionCardMeta(track, currentVideoId, upcomingVideoId, (!isTransitioning && (track.video_id === lastAddedVideoId || track.addedJustNow)));
                const bpm = track.bpm || detectBpmJs(track.title, track.category);
                const card = document.createElement("div");
                card.className = "track-card" + meta.cardExtraClass;
                card.id = `spGlobalTrack_${track.video_id}`;
                card.innerHTML = `
                    <div class="track-left-content">
                        <span class="spotify-rank-pill" style="background: rgba(30, 215, 96, 0.2); color: #1ed760;">#${index + 1}</span>
                        <div class="track-thumb-box" onclick="playCustomTrack('${track.video_id}', '${escapeQuotes(track.title)}', '${escapeQuotes(track.artist || '')}', '${escapeQuotes(track.category || '')}', 'Spotify: ${escapeQuotes(track.playlistName)}', ${bpm})">
                            <img src="https://i.ytimg.com/vi/${track.video_id}/mqdefault.jpg" class="track-thumb" loading="lazy" alt="Thumb" onerror="this.src=window.DEFAULT_COVER_SVG">
                            <div class="thumb-play-overlay">▶</div>
                        </div>
                        <div class="track-main-info" onclick="playCustomTrack('${track.video_id}', '${escapeQuotes(track.title)}', '${escapeQuotes(track.artist || '')}', '${escapeQuotes(track.category || '')}', 'Spotify: ${escapeQuotes(track.playlistName)}', ${bpm})">
                            <div class="track-title">${escapeHtml(track.title)}</div>
                            <div class="track-artist-row">
                                ${meta.statusBadgeHtml}
                                <span class="track-artist">${escapeHtml(track.artist || "Spotify")}</span>
                                <span class="badge-bpm-chip">⚡ ${bpm} BPM</span>
                                <span class="badge-bpm-chip" style="background: rgba(30,215,96,0.15); border-color: rgba(30,215,96,0.4); color: #1ed760;">🟢 ${escapeHtml(track.playlistName)}</span>
                            </div>
                        </div>
                    </div>
                    <div class="track-actions">
                        <button class="track-action-btn btn-add-q" onclick="addCustomTrackToQueue('${track.video_id}', '${escapeQuotes(track.title)}', '${escapeQuotes(track.artist || '')}', '${escapeQuotes(track.category || '')}', 'Spotify: ${escapeQuotes(track.playlistName)}', ${bpm})" title="Adicionar à fila">+ Fila</button>
                    </div>
                `;
                listContainer.appendChild(card);
            });
        }
        window.renderGlobalSpotifySearchResults = renderGlobalSpotifySearchResults;

        function switchView(view) {
            browseView = view;
            const navLib = document.getElementById("navLibrary");
            const navSpotify = document.getElementById("navSpotify");
            const navSearch = document.getElementById("navSearch");
            const navSugg = document.getElementById("navSuggestions");
            const navQ = document.getElementById("navQueue");

            if (navLib) navLib.className = `nav-btn ${view === "library" ? "active" : ""}`;
            if (navSpotify) navSpotify.className = `nav-btn ${view === "spotify" ? "active" : ""}`;
            if (navSearch) navSearch.className = `nav-btn ${view === "search" ? "active" : ""}`;
            if (navSugg) navSugg.className = `nav-btn ${view === "suggestions" ? "active" : ""}`;
            if (navQ) navQ.className = `nav-btn ${view === "queue" ? "active" : ""}`;

            const paneLib = document.getElementById("paneLibrary");
            const paneSpotify = document.getElementById("paneSpotify");
            const paneSearch = document.getElementById("paneSearch");
            const paneSugg = document.getElementById("paneSuggestions");
            const paneQ = document.getElementById("paneQueue");

            if (paneLib) paneLib.style.display = view === "library" ? "flex" : "none";
            if (paneSpotify) paneSpotify.style.display = view === "spotify" ? "flex" : "none";
            if (paneSearch) paneSearch.style.display = view === "search" ? "flex" : "none";
            if (paneSugg) paneSugg.style.display = view === "suggestions" ? "flex" : "none";
            if (paneQ) paneQ.style.display = view === "queue" ? "flex" : "none";

            setupListVerticalAutoScroll("suggestionsList");
            setupListVerticalAutoScroll("searchResultsList");
            setupListVerticalAutoScroll("spotifyTrackList");

            if (view === "library") {
                renderList();
            } else if (view === "spotify") {
                renderSpotifyPlaylist();
            } else if (view === "search") {
                renderSearchResults();
                setTimeout(() => {
                    const input = document.getElementById("freeSearchInput");
                    if (input && !input.value) input.focus();
                }, 50);
            } else if (view === "suggestions") {
                initSuggestionsTabs();
                if (isRadioActive) {
                    const cacheKey = (radioActiveTrack?.video_id || radioActiveTrack?.title || "") + "_rhythm";
                    if (cacheKey && radioSuggestionsCache[cacheKey] && radioSuggestionsCache[cacheKey].length > 0) {
                        renderSuggestionsList(radioSuggestionsCache[cacheKey]);
                    } else {
                        isRadioActive = false;
                    }
                }
                if (!isRadioActive) {
                    updateSuggestionHeader();
                    if (!suggestionsByGenre[currentSuggestionCategory] || suggestionsByGenre[currentSuggestionCategory].length === 0) {
                        fetchFreshSuggestionsForCurrentGenre();
                    } else {
                        renderSuggestionsList(suggestionsByGenre[currentSuggestionCategory]);
                    }
                }
            } else if (view === "queue") {
                loadQueue();
            }
        }

        // Renderiza a lista de músicas exibindo:
        // 1. Status 'TOCANDO AGORA' com animação na música atual
        // 2. Status '✨ ADICIONADA AGORA' na última música que foi favoritada
        // 3. Status 'A SEGUIR (PRÓXIMA)' na próxima música a ser tocada
        function renderList(filteredTracks = null) {
            currentFilteredLibraryTracks = filteredTracks;
            const listContainer = document.getElementById("trackList");
            if (!listContainer) return;
            listContainer.innerHTML = "";
            const tracks = filteredTracks !== null ? filteredTracks : (DATA[browseCategory] || []);

            if (tracks.length === 0) {
                listContainer.innerHTML = '<div style="color: var(--text-dim); text-align: center; padding: 25px;">Nenhuma música encontrada.</div>';
                return;
            }

            const currentVideoId = nowPlayingTrack ? nowPlayingTrack.video_id : null;
            const upcomingTrack = getUpcomingTrack();
            const upcomingVideoId = upcomingTrack ? upcomingTrack.video_id : null;
            const queuedIds = new Set(pendingQueue.map(t => t.video_id));

            tracks.forEach((t, index) => {
                const isQueued = queuedIds.has(t.video_id);
                const meta = getTrackTransitionCardMeta(t, currentVideoId, upcomingVideoId, (!isTransitioning && (t.video_id === lastAddedVideoId || t.addedJustNow)));

                let cardClasses = "track-card" + meta.cardExtraClass;
                const card = document.createElement("div");
                card.id = `libCard_${t.video_id}`;
                card.className = cardClasses;
                card.setAttribute("data-video-id", t.video_id);
                if (meta.transitionRole) card.setAttribute("data-transition-role", meta.transitionRole);

                let statusBadgeHtml = meta.statusBadgeHtml;

                const bpmVal = t.bpm || detectBpmJs(t.title, t.category);
                const bpmBadgeHtml = `<span class="badge-bpm-chip">⚡ ${bpmVal} BPM</span>`;

                let idealBadgeHtml = "";
                if (nowPlayingTrack && t.video_id !== nowPlayingTrack.video_id) {
                    const score = calculateIdealNextTrackScore(t, nowPlayingTrack);
                    if (score >= 93) {
                        idealBadgeHtml = `<span class="badge-ideal-track match-perfect" title="Harmonia e BPM ideais para mixagem">🎯 ${score}% Match</span>`;
                        cardClasses += " ideal-match-highlight";
                    } else if (score >= 86) {
                        idealBadgeHtml = `<span class="badge-ideal-track match-great" title="Excelente sincronia de mix">⚡ ${score}% Mix</span>`;
                    }
                }
                card.className = cardClasses;

                const artistText = t.artist ? t.artist + " • " + (t.source || "") : (t.source || "");

                card.innerHTML = `
                    <div class="track-meta" onclick="playLibraryTrack('${browseCategory}', ${index})">
                        <div class="track-card-title">
                            <span>${index + 1}. ${escapeHtml(t.title)}</span>
                        </div>
                        <div class="track-card-subrow">
                            ${statusBadgeHtml}
                            ${idealBadgeHtml}
                            <span class="track-card-artist" title="${escapeHtml(artistText)}">${escapeHtml(artistText)}</span>
                            ${bpmBadgeHtml}
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn-similar-card" onclick="findSimilarToLibraryTrack('${browseCategory}', ${index})" title="Buscar músicas semelhantes no mesmo ritmo e BPM com IA">
                            📻 Parecidas
                        </button>
                        <button class="btn-move-card" onclick="openMovePlaylistModal('${browseCategory}', ${index}, '${t.video_id}')" title="Mover para outra playlist / gênero">
                            📂 Mover
                        </button>
                        <button class="btn-remove-lib-card" onclick="removeLibraryTrackPrompt('${browseCategory}', ${index}, '${t.video_id}')" title="Remover da biblioteca">
                            🗑️
                        </button>
                        ${(() => {
                            const qIdx = pendingQueue.findIndex(q => q.video_id === t.video_id);
                            if (qIdx !== -1) {
                                return `<button class="btn-add-queue added" onclick="removeFromQueue('${t.video_id}')" title="Clique para remover da fila (#${qIdx + 1})">✓ Fila #${qIdx + 1}${qIdx === 0 ? " (Próxima)" : ""}</button>`;
                            } else {
                                return `<button class="btn-add-queue" onclick="addLibraryTrackToQueue('${browseCategory}', ${index})">+ Fila</button>`;
                            }
                        })()}
                    </div>
                `;
                listContainer.appendChild(card);
            });

            updateUpcomingTrackUI();
        }

        function mapTrackToLibraryCategory(track, fallbackCategory) {
            const text = ((track?.title || "") + " " + (track?.artist || "") + " " + (track?.category || "")).toLowerCase();
            
            if (/cumbia|villera|santafesina|charanga|chicha|cuarteto|reggaeton|latino|dembow|perreo|bachata|sonido profesional|fiestero|cachengue|el reja/i.test(text)) {
                return "Reggaeton, Cachengue & Latino";
            }
            if (/megafunk|mega funk|ritmada|eletrofunk|eletro funk/i.test(text)) {
                return "Mega Funk & Ritmadas";
            }
            if (/funk|mandel|bh|fluxo|favela|kondzilla|gr6|mc |montagem/i.test(text)) {
                return "Funk Paulista, BH & Mandelão";
            }
            if (/eletr|house|desande|edm|techno|trance|psy|rave|alok|vintage/i.test(text)) {
                return "Eletrônica, House & Desande";
            }
            if (/sertanejo|universit|agronejo|modao|modão|gusttavo|jorge|marilia|zeneto/i.test(text)) {
                return "Sertanejo Universitário & Atual";
            }
            if (/samba|pagode|ferrugem|dilsinho|sorriso maroto|turma do pagode/i.test(text)) {
                return "Samba & Pagode";
            }
            if (/trap|rap|drill|hip hop|hip-hop|matue|kayblack|veigh|filipe ret/i.test(text)) {
                return "Trap & Rap Nacional";
            }
            if (/rock|pop|nostalgia|anos 80|anos 90|anos 2000/i.test(text)) {
                return "Rock & Pop Nostalgia";
            }
            
            if (CATEGORIES && CATEGORIES.includes(fallbackCategory)) {
                return fallbackCategory;
            }
            return "Outros";
        }

        // ADICIONAR MÚSICA À PLAYLIST COM ANIMAÇÃO FLY-OUT E STATUS DINÂMICO
        async function addTrackToPlaylist(track, cardElement) {
            if (!track || !track.video_id) return;

            const isSearchCard = cardElement && cardElement.id && cardElement.id.startsWith("searchCard_");
            const isQueueCard = cardElement && cardElement.id && cardElement.id.startsWith("queueCard_");

            // Garante classificação em categoria oficial da biblioteca (nunca 'Personalizada' ou órfã)
            let targetCategory = track.category;
            if (!targetCategory || targetCategory === "Personalizada" || !CATEGORIES.includes(targetCategory)) {
                targetCategory = mapTrackToLibraryCategory(track, currentSuggestionCategory || browseCategory);
            }
            track.category = targetCategory;

            // 1. Efeito visual: animação fly-out APENAS para cards de recomendação/sugestão (não para busca nem fila)
            if (cardElement && !isSearchCard && !isQueueCard) {
                cardElement.classList.add("card-fly-out");
            } else if (isSearchCard) {
                // Atualização visual imediata in-loco para feedback tátil instantâneo sem sumir com a música da tela
                const btnFav = cardElement.querySelector(".btn-add-playlist");
                if (btnFav) {
                    btnFav.classList.add("in-library");
                    btnFav.removeAttribute("onclick");
                    btnFav.style.background = "rgba(0, 230, 118, 0.15)";
                    btnFav.style.borderColor = "rgba(0, 230, 118, 0.4)";
                    btnFav.style.color = "#00e676";
                    btnFav.title = `Salva na sua biblioteca (Aba: ${targetCategory})`;
                    btnFav.innerHTML = "❤️ Na Playlist";
                }
                const badgeSource = cardElement.querySelector(".badge-source");
                if (badgeSource) {
                    badgeSource.style.background = "rgba(0, 230, 118, 0.15)";
                    badgeSource.style.color = "#00e676";
                    badgeSource.style.border = "1px solid rgba(0, 230, 118, 0.3)";
                    badgeSource.textContent = "✓ Na Biblioteca";
                }
            }

            try {
                // 2. Salva no complete_library.json no backend
                const res = await fetch("/api/library/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        video_id: track.video_id,
                        title: track.title,
                        artist: track.artist || "",
                        category: targetCategory,
                        source: "Sugestões (Favoritada)"
                    })
                });
                const data = await res.json();

                // 3. Adiciona na biblioteca frontend DATA[targetCategory] no topo
                if (!DATA[targetCategory]) DATA[targetCategory] = [];
                if (!DATA[targetCategory].some(t => t.video_id === track.video_id)) {
                    const newTrackObj = {
                        title: track.title,
                        artist: track.artist || "",
                        category: targetCategory,
                        video_id: track.video_id,
                        source: "Favoritada",
                        addedJustNow: true
                    };
                    DATA[targetCategory].unshift(newTrackObj);
                }

                // 4. Marca o ID desta música como a última adicionada
                lastAddedVideoId = track.video_id;
                localStorage.setItem("pref_last_added_id", lastAddedVideoId);

                // 5. Atualiza status no frontend
                if (!isSearchCard && !isQueueCard) {
                    setTimeout(() => {
                        if (cardElement && cardElement.parentNode) {
                            cardElement.parentNode.removeChild(cardElement);
                        }
                        if (suggestionsByGenre[currentSuggestionCategory]) {
                            suggestionsByGenre[currentSuggestionCategory] = suggestionsByGenre[currentSuggestionCategory].filter(t => t.video_id !== track.video_id);
                            updateSuggestionHeader();
                        }
                    }, 380);
                }

                // Marca na busca livre também e sincroniza os filtros
                if (freeSearchResults && freeSearchResults.tracks) {
                    const st = freeSearchResults.tracks.find(t => t.video_id === track.video_id);
                    if (st) st.in_library = true;
                    track.in_library = true;
                    if (!freeSearchResults.library_tracks) freeSearchResults.library_tracks = [];
                    if (!freeSearchResults.library_tracks.some(t => t.video_id === track.video_id)) {
                        freeSearchResults.library_tracks.unshift(track);
                    }
                    if (freeSearchResults.youtube_tracks) {
                        freeSearchResults.youtube_tracks = freeSearchResults.youtube_tracks.filter(t => t.video_id !== track.video_id);
                    }
                }

                // Atualiza contadores das abas de busca
                updateSearchFilterCounters();

                // 6. Atualiza contadores da biblioteca
                updateLibraryCounters();
                renderList();

                // Se a visualização de busca estiver ativa em filtros específicos, atualiza a exibição
                if (browseView === "search" && (freeSearchFilter === "library" || freeSearchFilter === "new")) {
                    renderSearchResults();
                }

                showToast(`⭐ "${track.title}" salva na sua biblioteca! Acesse na aba "${targetCategory}".`, 5000);
            } catch (err) {
                console.error("Erro ao adicionar faixa à biblioteca:", err);
                showToast("Erro ao adicionar faixa. Tente novamente.");
            }
        }

        // ==========================================================================
        // ==========================================================================
        // GERENCIAMENTO ROBUSTO DE BIBLIOTECA: MOVER E REMOVER EM TEMPO REAL
        // ==========================================================================
        let currentTrackToMove = null;
        let currentSourceCategory = null;
        let selectedDestinationCategory = null;
        let currentTrackToRemove = null;

        // Resolvedor universal de faixa para garantir que nunca falhe independente da ordem de argumentos
        function resolveLibraryTrack(arg1, arg2, arg3) {
            let track = null;
            let category = null;
            let videoId = null;

            if (arg1 && typeof arg1 === "object") {
                track = arg1;
                videoId = track.video_id;
                category = track.category;
            } else if (typeof arg1 === "string" && typeof arg2 === "number") {
                category = arg1;
                if (DATA[category] && DATA[category][arg2]) {
                    track = DATA[category][arg2];
                    videoId = track.video_id;
                }
                if (!videoId && arg3) videoId = arg3;
            } else if (typeof arg1 === "string") {
                if (CATEGORIES.includes(arg1) && arg2 && typeof arg2 === "string") {
                    category = arg1;
                    videoId = arg2;
                } else {
                    videoId = arg1;
                    if (arg2 && CATEGORIES.includes(arg2)) category = arg2;
                }
            }

            if (!track && videoId) {
                for (const cat of Object.keys(DATA)) {
                    const found = (DATA[cat] || []).find(t => t.video_id === videoId);
                    if (found) {
                        track = found;
                        if (!category) category = cat;
                        break;
                    }
                }
            }
            return { track, videoId, category };
        }

        // --- MODAL DE MOVER PLAYLIST ---
        function openMovePlaylistModal(sourceCategory, trackOrIndex, videoId) {
            const resolved = resolveLibraryTrack(sourceCategory, trackOrIndex, videoId);
            const track = resolved.track;
            const fromCat = resolved.category || sourceCategory;

            if (!track) {
                showToast("⚠️ Música não encontrada para mover.");
                return;
            }

            currentTrackToMove = track;
            currentSourceCategory = fromCat || track.category || browseCategory;
            selectedDestinationCategory = null;

            const modal = document.getElementById("movePlaylistModal");
            const titleEl = document.getElementById("moveModalTrackTitle");
            const artistEl = document.getElementById("moveModalTrackArtist");
            const curCatEl = document.getElementById("moveModalCurrentCat");
            const inputNew = document.getElementById("inputNewPlaylistName");
            const grid = document.getElementById("movePlaylistsGrid");

            if (titleEl) titleEl.textContent = track.title || "Sem Título";
            if (artistEl) artistEl.textContent = track.artist || "Artista Desconhecido";
            if (curCatEl) curCatEl.textContent = currentSourceCategory;
            if (inputNew) inputNew.value = "";

            if (grid) {
                grid.innerHTML = "";
                CATEGORIES.forEach(cat => {
                    const count = (DATA[cat] || []).length;
                    const icon = ICONS[cat] || "🎵";
                    const isCurrent = (cat === currentSourceCategory);

                    const optCard = document.createElement("div");
                    optCard.className = `move-playlist-opt-card ${isCurrent ? "is-current-cat" : ""}`;
                    optCard.id = `moveOptCat_${cat.replace(/[^a-zA-Z0-9]/g, "_")}`;
                    optCard.onclick = () => selectDestinationCategory(cat);

                    optCard.innerHTML = `
                        <div class="move-playlist-opt-left">
                            <span class="move-playlist-opt-icon">${icon}</span>
                            <span class="move-playlist-opt-name" title="${escapeHtml(cat)}">${escapeHtml(cat)} ${isCurrent ? '<small style="color: var(--accent);">(Atual)</small>' : ''}</span>
                        </div>
                        <span class="move-playlist-opt-count">${count} faixas</span>
                    `;
                    grid.appendChild(optCard);
                });
            }

            if (modal) {
                modal.style.display = "flex";
                modal.classList.add("open");
            }
        }
        window.openMovePlaylistModal = openMovePlaylistModal;

        function openMovePlaylistModalByVideoId(videoId, title) {
            openMovePlaylistModal(null, null, videoId);
        }
        window.openMovePlaylistModalByVideoId = openMovePlaylistModalByVideoId;

        function closeMovePlaylistModal(e) {
            if (e && e.target && e.target !== document.getElementById("movePlaylistModal")) return;
            const modal = document.getElementById("movePlaylistModal");
            if (modal) {
                modal.style.display = "none";
                modal.classList.remove("open");
            }
            currentTrackToMove = null;
            currentSourceCategory = null;
            selectedDestinationCategory = null;
        }
        window.closeMovePlaylistModal = closeMovePlaylistModal;

        function selectDestinationCategory(catName) {
            selectedDestinationCategory = catName;
            document.querySelectorAll(".move-playlist-opt-card").forEach(c => c.classList.remove("selected"));
            const selectedEl = document.getElementById(`moveOptCat_${catName.replace(/[^a-zA-Z0-9]/g, "_")}`);
            if (selectedEl) selectedEl.classList.add("selected");
        }
        window.selectDestinationCategory = selectDestinationCategory;

        async function executeMovePlaylist() {
            if (!currentTrackToMove || !selectedDestinationCategory) {
                showToast("⚠️ Selecione uma playlist de destino primeiro!");
                return;
            }
            if (selectedDestinationCategory === currentSourceCategory) {
                showToast(`ℹ️ Esta música já está na playlist "${currentSourceCategory}".`);
                return;
            }

            const track = currentTrackToMove;
            const oldCat = currentSourceCategory;
            const newCat = selectedDestinationCategory;

            // 1. Animação de saída imediata do card atual em tempo real
            const cardEl = document.getElementById(`libCard_${track.video_id}`) || document.querySelector(`[data-video-id="${track.video_id}"]`);
            if (cardEl) {
                cardEl.classList.add("anim-moving");
            }

            // 2. Atualização atômica em memória (DATA)
            for (const c of Object.keys(DATA)) {
                if (Array.isArray(DATA[c])) {
                    DATA[c] = DATA[c].filter(t => t.video_id !== track.video_id);
                }
            }
            if (!DATA[newCat]) DATA[newCat] = [];
            track.category = newCat;
            DATA[newCat].unshift(track);

            if (!CATEGORIES.includes(newCat)) {
                CATEGORIES.push(newCat);
            }

            // 3. Atualização visual de contadores e listas em tempo real
            closeMovePlaylistModal();
            updateLibraryCounters();
            renderList();
            renderAllActiveLists();
            showToast(`📂 "${track.title.slice(0, 30)}..." movida com sucesso para "${newCat}"!`, 4500);

            // 4. Persistência no backend (complete_library.json e rebuild de player.html)
            try {
                await fetch("/api/library/move", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        video_id: track.video_id,
                        old_category: oldCat,
                        new_category: newCat
                    })
                });
            } catch (err) {
                console.warn("Aviso ao persistir movimento de playlist no servidor:", err);
            }
        }
        window.executeMovePlaylist = executeMovePlaylist;

        async function createAndMoveToNewPlaylist() {
            const input = document.getElementById("inputNewPlaylistName");
            const newName = (input ? input.value : "").trim();
            if (!newName) {
                showToast("⚠️ Digite um nome para a nova playlist.");
                return;
            }
            selectedDestinationCategory = newName;
            await executeMovePlaylist();
        }
        window.createAndMoveToNewPlaylist = createAndMoveToNewPlaylist;

        // --- MODAL DE REMOÇÃO DA BIBLIOTECA (IN-APP E SEM BLOQUEIOS) ---
        function openConfirmRemoveModal(category, index, videoId) {
            const resolved = resolveLibraryTrack(category, index, videoId);
            const track = resolved.track;

            if (!track && !resolved.videoId) {
                showToast("⚠️ Música não localizada para remoção.");
                return;
            }

            currentTrackToRemove = {
                track: track,
                videoId: resolved.videoId || (track ? track.video_id : null),
                category: resolved.category || (track ? track.category : null)
            };

            const modal = document.getElementById("confirmRemoveModal");
            const titleEl = document.getElementById("removeModalTrackTitle");
            const artistEl = document.getElementById("removeModalTrackArtist");
            const catEl = document.getElementById("removeModalCurrentCat");
            const thumbEl = document.getElementById("removeModalThumb");

            const displayTitle = track ? track.title : "Música Selecionada";
            const displayArtist = track ? (track.artist || "Artista") : "";
            const displayCat = currentTrackToRemove.category || "Biblioteca";
            const vid = currentTrackToRemove.videoId;

            if (titleEl) titleEl.textContent = displayTitle;
            if (artistEl) artistEl.textContent = displayArtist;
            if (catEl) catEl.textContent = displayCat;
            if (thumbEl && vid) {
                thumbEl.src = `https://i.ytimg.com/vi/${vid}/mqdefault.jpg`;
            }

            if (modal) {
                modal.style.display = "flex";
                modal.classList.add("open");
            }
        }
        window.openConfirmRemoveModal = openConfirmRemoveModal;
        window.removeLibraryTrackPrompt = openConfirmRemoveModal; // Retrocompatibilidade

        function closeConfirmRemoveModal(e) {
            if (e && e.target && e.target !== document.getElementById("confirmRemoveModal")) return;
            const modal = document.getElementById("confirmRemoveModal");
            if (modal) {
                modal.style.display = "none";
                modal.classList.remove("open");
            }
            currentTrackToRemove = null;
        }
        window.closeConfirmRemoveModal = closeConfirmRemoveModal;

        async function executeRemoveLibraryTrack() {
            if (!currentTrackToRemove || !currentTrackToRemove.videoId) {
                closeConfirmRemoveModal();
                return;
            }

            const { track, videoId, category } = currentTrackToRemove;
            const title = track ? track.title : "Faixa";

            // 1. Animação de saída imediata do card no DOM em tempo real
            const cardEl = document.getElementById(`libCard_${videoId}`) || 
                           document.getElementById(`historyCard_${videoId}`) || 
                           document.querySelector(`[data-video-id="${videoId}"]`);
            if (cardEl) {
                cardEl.classList.add("anim-removing");
            }

            // 2. Remoção em memória imediata de todas as categorias
            for (const c of Object.keys(DATA)) {
                if (Array.isArray(DATA[c])) {
                    DATA[c] = DATA[c].filter(t => t.video_id !== videoId);
                }
            }

            // 3. Atualização visual de contadores e listas em tempo real
            closeConfirmRemoveModal();
            updateLibraryCounters();
            renderList();
            renderAllActiveLists();
            showToast(`🗑️ "${title.slice(0, 32)}..." removida da biblioteca em tempo real!`, 4000);

            // 4. Persistência no backend (complete_library.json e rebuild de player.html)
            try {
                await fetch("/api/library/remove", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        video_id: videoId,
                        category: category
                    })
                });
            } catch (err) {
                console.warn("Aviso ao persistir remoção no servidor:", err);
            }
        }
        window.executeRemoveLibraryTrack = executeRemoveLibraryTrack;

        // SINCRONIZAR COM O YOUTUBE (FAB FLUTUANTE)
        async function triggerYouTubeSync() {
            const btn = document.getElementById("floatingSyncBtn");
            const btnText = document.getElementById("syncBtnText");

            if (btn) btn.classList.add("syncing");
            if (btnText) btnText.textContent = "Sincronizando...";
            showToast("🔄 Sincronizando com sua playlist no YouTube...");

            try {
                const res = await fetch("/api/sync-youtube", { method: "POST" });
                const data = await res.json();
                
                if (data.success || data.playlist_url) {
                    showToast("✅ Playlist sincronizada com o YouTube com sucesso!", 3500);
                } else {
                    showToast("Erro na sincronização: " + (data.message || "Tente novamente."));
                }
            } catch (e) {
                showToast("Erro na sincronização. Tente novamente.");
            } finally {
                setTimeout(() => {
                    if (btn) btn.classList.remove("syncing");
                    if (btnText) btnText.textContent = "Sincronizar com YouTube";
                }, 1500);
            }
        }

        // Iniciar reprodução com Crossfade suave quando já houver música tocando
        function startPlaybackFromLibrary(categoryName, index) {
            const queue = DATA[categoryName] || [];
            if (index < 0 || index >= queue.length) return;
            
            nowPlayingQueue = queue;
            nowPlayingCategoryName = categoryName;
            nowPlayingIndex = index;
            const nextTrack = queue[index];

            initWebAudio();
            if (audioCtx && audioCtx.state === "suspended") {
                audioCtx.resume();
            }

            const activeP = getActivePlayer();
            const isCurrentlyPlaying = (engineMode === "audio" && audioDeckA && !audioDeckA.paused) || 
                (engineMode === "video" && activeP && typeof activeP.getPlayerState === "function" && 
                 (activeP.getPlayerState() === YT.PlayerState.PLAYING || activeP.getPlayerState() === YT.PlayerState.BUFFERING));

            if (isCurrentlyPlaying && crossfadeSeconds > 0 && nowPlayingTrack && nowPlayingTrack.video_id !== nextTrack.video_id) {
                triggerCrossfade(nextTrack);
            } else {
                playTrackInstant(nextTrack);
            }
            renderAllActiveLists();
        }

        // Faixa customizada (Sugestões ou Fila) com Crossfade suave
        function playCustomTrack(videoId, title, artist, category, source) {
            const customTrack = {
                video_id: videoId,
                title: title,
                artist: artist,
                category: category || "Personalizada",
                source: source || "Geral"
            };
            nowPlayingQueue = [customTrack];
            nowPlayingIndex = 0;
            nowPlayingCategoryName = category || "Personalizada";

            initWebAudio();
            if (audioCtx && audioCtx.state === "suspended") {
                audioCtx.resume();
            }

            const activeP = getActivePlayer();
            const isCurrentlyPlaying = (engineMode === "audio" && audioDeckA && !audioDeckA.paused) || 
                (engineMode === "video" && activeP && typeof activeP.getPlayerState === "function" && 
                 (activeP.getPlayerState() === YT.PlayerState.PLAYING || activeP.getPlayerState() === YT.PlayerState.BUFFERING));

            if (isCurrentlyPlaying && crossfadeSeconds > 0 && nowPlayingTrack && nowPlayingTrack.video_id !== customTrack.video_id) {
                triggerCrossfade(customTrack);
            } else {
                playTrackInstant(customTrack);
            }
            renderAllActiveLists();
        }

        // Retorna o player ativo e o standby
        function getActivePlayer() {
            return activeDeck === "A" ? playerA : playerB;
        }

        function getStandbyPlayer() {
            return activeDeck === "A" ? playerB : playerA;
        }

        function getActiveDeckEl() {
            return document.getElementById(activeDeck === "A" ? "deckA" : "deckB");
        }

        function getStandbyDeckEl() {
            return document.getElementById(activeDeck === "A" ? "deckB" : "deckA");
        }

        function getActiveAudioDeck() {
            return activeDeck === "A" ? audioDeckA : audioDeckB;
        }

        function getStandbyAudioDeck() {
            return activeDeck === "A" ? audioDeckB : audioDeckA;
        }

        function cancelTransition() {
            if (crossfadeTimer) {
                clearInterval(crossfadeTimer);
                crossfadeTimer = null;
            }
            if (transitionWatchdogTimer) {
                clearTimeout(transitionWatchdogTimer);
                transitionWatchdogTimer = null;
            }
            isTransitioning = false;
            hideCrossfadeIndicator();
            resetDecksContourUI();
        }

        // Executar faixa instantânea
        function playTrackInstant(track) {
            if (!track) return;
            recordTrackInRecentHistory(track.video_id);
            hideToast();
            cancelTransition();

            hasFadedCurrentTrack = false;
            prewarmedUpcomingId = "";
            nowPlayingTrack = track;
            updateTrackInfoUI(track);

            if (track && track.video_id && !trackDurations[track.video_id]) {
                fetch(`/api/audio/info?id=${track.video_id}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data && data.duration) {
                            trackDurations[track.video_id] = data.duration;
                            if (nowPlayingTrack && nowPlayingTrack.video_id === track.video_id) {
                                nowPlayingTrack.duration = data.duration;
                            }
                        }
                    }).catch(() => {});
            }

            const startSec = (djPlayMode === "drop") ? getTrackDropStartTime(track) : getTrackIntroSkip(track);

            // Modo Áudio HD (Equalizador + 200% VLC + Zero Restrições)
            if (engineMode === "audio") {
                initWebAudio();
                if (audioCtx && audioCtx.state === "suspended") {
                    audioCtx.resume();
                }

                const curAudio = getActiveAudioDeck();
                const stdAudio = getStandbyAudioDeck();

                if (stdAudio) {
                    stdAudio.pause();
                    stdAudio.currentTime = 0;
                }

                if (deckGainA && deckGainB && audioCtx) {
                    const now = audioCtx.currentTime;
                    if (activeDeck === "A") {
                        deckGainA.gain.cancelScheduledValues(now);
                        deckGainA.gain.setValueAtTime(0.0, now);
                        deckGainA.gain.linearRampToValueAtTime(1.0, now + 0.15);
                        deckGainB.gain.cancelScheduledValues(now);
                        deckGainB.gain.setValueAtTime(0.0, now);
                    } else {
                        deckGainB.gain.cancelScheduledValues(now);
                        deckGainB.gain.setValueAtTime(0.0, now);
                        deckGainB.gain.linearRampToValueAtTime(1.0, now + 0.15);
                        deckGainA.gain.cancelScheduledValues(now);
                        deckGainA.gain.setValueAtTime(0.0, now);
                    }
                }

                if (curAudio) {
                    curAudio.src = `/api/audio/stream?id=${track.video_id}`;
                    curAudio.currentTime = startSec;
                    const initialRate = currentPitchAdjustment !== 0 ? (currentPlaybackSpeed * (1.0 + currentPitchAdjustment / 100)) : currentPlaybackSpeed;
                    curAudio.playbackRate = initialRate;
                    curAudio.preservesPitch = true;
                    curAudio.play().then(() => {
                        if (startSec > 0 && Math.abs(curAudio.currentTime - startSec) > 0.6) {
                            curAudio.currentTime = startSec;
                        }
                        curAudio.playbackRate = initialRate;
                        curAudio.preservesPitch = true;
                        updatePlayPauseButtons(true);
                        if (currentPitchAdjustment !== 0) {
                            rampBpmToOriginal(curAudio, initialRate, currentPlaybackSpeed, track.bpm || 128, 3500);
                        } else {
                            updateLiveBpmPanel();
                        }
                    }).catch(err => {
                        console.warn("Autoplay aguardando interação do usuário:", err);
                    });
                }

                // Pausa YouTube IFrame
                const activeP = getActivePlayer();
                if (activeP && typeof activeP.pauseVideo === "function") {
                    try { activeP.pauseVideo(); activeP.setVolume(0); } catch (e) {}
                }

                const visScreen = document.getElementById("visualizerScreen");
                if (visScreen) visScreen.style.display = "flex";
            } else {
                // Modo Vídeo Clipe YouTube
                if (audioDeckA) audioDeckA.pause();
                if (audioDeckB) audioDeckB.pause();

                const visScreen = document.getElementById("visualizerScreen");
                if (visScreen) visScreen.style.display = "none";

                const activeP = getActivePlayer();
                const standbyP = getStandbyPlayer();
                const activeEl = getActiveDeckEl();
                const standbyEl = getStandbyDeckEl();

                try {
                    if (standbyP && typeof standbyP.pauseVideo === "function") {
                        standbyP.pauseVideo();
                        standbyP.setVolume(0);
                    }
                } catch (e) {}

                if (activeEl) {
                    activeEl.style.opacity = "1";
                    activeEl.style.zIndex = "2";
                }
                if (standbyEl) {
                    standbyEl.style.opacity = "0";
                    standbyEl.style.zIndex = "1";
                }

                if (activeP && typeof activeP.loadVideoById === "function") {
                    try {
                        if (isMuted) activeP.mute();
                        else {
                            activeP.unMute();
                            activeP.setVolume(Math.min(100, masterVolume));
                        }
                        activeP.loadVideoById(track.video_id, startSec);
                        if (startSec > 0 && typeof activeP.seekTo === "function") {
                            try { activeP.seekTo(startSec, true); } catch (e) {}
                        }
                        if (typeof activeP.setPlaybackRate === "function") {
                            try { activeP.setPlaybackRate(Math.min(2.0, currentPlaybackSpeed)); } catch (e) {}
                        }
                        activeP.playVideo();
                    } catch (e) {}
                }
            }

            startTimeMonitor();
            if (typeof recordTrackInHistory === "function") recordTrackInHistory(track);
            if (typeof calculateDjModeNextTrack === "function") calculateDjModeNextTrack(track);
            updateUpcomingTrackUI();
            updateTurntablesState();
            updateDjMixerUI();
            renderAllActiveLists();
        }

        // Transição Dupla Crossfade
                // Helper para escapar HTML em strings de texto
        function escapeHtml(str) {
            if (!str) return "";
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        // Helper centralizado para definir status, badges e contorno suave dos cards de faixas nas listas durante transições
        function getTrackTransitionCardMeta(trackItem, currentVideoId, upcomingVideoId, isLastAdded = false) {
            const isOutgoing = (isTransitioning && transitionOutgoingTrack && trackItem && trackItem.video_id === transitionOutgoingTrack.video_id);
            const isIncoming = (isTransitioning && transitionIncomingTrack && trackItem && trackItem.video_id === transitionIncomingTrack.video_id);
            const isPlaying = (!isTransitioning && trackItem && trackItem.video_id === currentVideoId);
            const isNext = (!isTransitioning && !isPlaying && !isLastAdded && trackItem && trackItem.video_id === upcomingVideoId);

            let cardExtraClass = "";
            let statusBadgeHtml = "";
            let transitionRole = "";
            const pct = Math.round(transitionProgress * 100);
            const pctOut = Math.max(0, 100 - pct);
            const pctIn = Math.min(100, pct);

            if (isOutgoing) {
                cardExtraClass = " transition-outgoing";
                transitionRole = "outgoing";
                statusBadgeHtml = `
                    <div class="badge-outgoing-track" data-track-badge="outgoing">
                        <span>📤 SAINDO (${pctOut}%)</span>
                    </div>
                `;
            } else if (isIncoming) {
                cardExtraClass = " transition-incoming";
                transitionRole = "incoming";
                statusBadgeHtml = `
                    <div class="badge-incoming-track" data-track-badge="incoming">
                        <span>📥 ENTRANDO (${pctIn}%)</span>
                    </div>
                `;
            } else if (isPlaying) {
                cardExtraClass = " playing-now";
                statusBadgeHtml = `
                    <div class="badge-now-playing">
                        <span class="eq-anim-bars"><span></span><span></span><span></span></span>
                        <span>TOCANDO AGORA</span>
                    </div>
                `;
            } else if (isLastAdded) {
                cardExtraClass = " next-up";
                statusBadgeHtml = `
                    <div class="badge-added-now">
                        <span>✨ ADICIONADA AGORA</span>
                    </div>
                `;
            } else if (isNext) {
                cardExtraClass = " next-up";
                statusBadgeHtml = `
                    <div class="badge-next-up">
                        <span>⏭️ A SEGUIR (PRÓXIMA)</span>
                    </div>
                `;
            }

            return { isOutgoing, isIncoming, isPlaying, isNext, cardExtraClass, statusBadgeHtml, transitionRole };
        }

        // Restaura contorno e bordas padrão dos cards de Deck e das Listas
        function resetDecksContourUI() {
            transitionOutgoingTrack = null;
            transitionIncomingTrack = null;
            transitionProgress = 0;

            const deckACard = document.getElementById("djDeckACard");
            const deckBCard = document.getElementById("djDeckBCard");
            const nowPlayingPill = document.getElementById("trackNowPlayingPill");

            if (deckACard) {
                deckACard.style.borderColor = "";
                deckACard.style.boxShadow = "";
                deckACard.style.background = "";
            }
            if (deckBCard) {
                deckBCard.style.borderColor = "";
                deckBCard.style.boxShadow = "";
                deckBCard.style.background = "";
            }
            if (nowPlayingPill) {
                nowPlayingPill.classList.remove("in-transition");
                nowPlayingPill.innerHTML = `● Tocando`;
                nowPlayingPill.style.background = "";
                nowPlayingPill.style.border = "";
                nowPlayingPill.style.color = "";
                nowPlayingPill.style.boxShadow = "";
            }

            // Restaura contorno padrão dos cards nas listas (Pesquisa, Biblioteca, Fila, Sugestões, Spotify)
            document.querySelectorAll('.track-card.transition-outgoing, .track-card.transition-incoming, [data-transition-role]').forEach(card => {
                card.style.borderColor = "";
                card.style.boxShadow = "";
                card.style.background = "";
                card.removeAttribute("data-transition-role");
                card.classList.remove("transition-outgoing", "transition-incoming");
            });
            document.querySelectorAll('.badge-outgoing-track, .badge-incoming-track, [data-track-badge]').forEach(b => b.remove());

            const searchBanner = document.getElementById("searchTransitionBanner");
            if (searchBanner) searchBanner.style.display = "none";
            const spotifyBanner = document.getElementById("spotifyTransitionBanner");
            if (spotifyBanner) spotifyBanner.style.display = "none";
        }

        // Atualização em tempo real do Contorno dos Cards e dos Status "Saindo" e "Entrando"
        function updateCrossfadeProgressUI(progress, outgoingTrack, incomingTrack) {
            const fromVol = Math.max(0, 1 - progress);
            const toVol = Math.min(1, progress);

            const deckACard = document.getElementById("djDeckACard");
            const deckBCard = document.getElementById("djDeckBCard");
            const deckATag = document.getElementById("deckATag");
            const deckBTag = document.getElementById("deckBTag");
            const deckATitle = document.getElementById("deckATitle");
            const deckAArtist = document.getElementById("deckAArtist");
            const deckBTitle = document.getElementById("deckBTitle");
            const deckBArtist = document.getElementById("deckBArtist");
            const faderKnob = document.getElementById("djFaderKnob");
            const faderFill = document.getElementById("djFaderFill");
            const balanceText = document.getElementById("crossfaderBalanceText");
            const meterA = document.getElementById("meterA");
            const meterB = document.getElementById("meterB");
            const crossfadeInd = document.getElementById("crossfadeIndicator");
            const barStatus = document.getElementById("barStatusText");
            const nowPlayingPill = document.getElementById("trackNowPlayingPill");

            const outTitle = outgoingTrack ? outgoingTrack.title : "Música Atual";
            const inTitle = incomingTrack ? incomingTrack.title : "Próxima Música";
            const pct = Math.round(progress * 100);
            const pctOut = Math.max(0, 100 - pct);
            const pctIn = Math.min(100, pct);

            // Animação contínua da barra do fader e medidores
            const knobPct = (activeDeck === "A") ? (progress * 100) : ((1 - progress) * 100);
            if (faderKnob) faderKnob.style.left = `${knobPct}%`;
            if (faderFill) faderFill.style.width = `${knobPct}%`;

            const pctA = Math.round((activeDeck === "A" ? fromVol : toVol) * 100);
            const pctB = Math.round((activeDeck === "A" ? toVol : fromVol) * 100);
            if (balanceText) {
                balanceText.textContent = `Deck A ${pctA}% ➔ ${pctB}% Deck B`;
            }

            if (meterA && meterB) {
                meterA.style.width = `${(activeDeck === "A" ? fromVol : toVol) * 100}%`;
                meterB.style.width = `${(activeDeck === "A" ? toVol : fromVol) * 100}%`;
            }

            // Indicador flutuante elegante sobre o vídeo
            if (crossfadeInd) {
                crossfadeInd.innerHTML = `🎚️ <span style="color:#ff5500; font-weight:800;">Saindo:</span> ${escapeHtml(outTitle.slice(0, 24))} ➔ <span style="color:#00f2fe; font-weight:800;">Entrando:</span> ${escapeHtml(inTitle.slice(0, 24))} <strong style="color:#00f2fe; margin-left:4px;">${pct}%</strong>`;
            }

            if (nowPlayingPill) {
                nowPlayingPill.classList.add("in-transition");
                nowPlayingPill.innerHTML = `🎚️ Transição <strong style="color:#00f2fe; margin-left:3px;">${pct}%</strong>`;
            }

            if (barStatus) {
                barStatus.innerHTML = `🎚️ <span style="color:#ffaa00; font-weight:700;">Saindo:</span> ${escapeHtml(outTitle)} • <span style="color:#00f2fe; font-weight:700;">Entrando:</span> ${escapeHtml(inTitle)} (${pct}%)`;
            }

            // Atualização dos banners de transição (Pesquisa e Spotify)
            const searchBanner = document.getElementById("searchTransitionBanner");
            if (searchBanner) {
                if (browseView === "search") {
                    searchBanner.style.display = "flex";
                    const pctEl = document.getElementById("searchTransitionPct");
                    const outEl = document.getElementById("searchOutgoingTrackInfo");
                    const inEl = document.getElementById("searchIncomingTrackInfo");
                    const fillEl = document.getElementById("searchTransitionFill");
                    if (pctEl) pctEl.textContent = `${pctIn}%`;
                    if (outEl) outEl.textContent = `📤 SAINDO: ${outTitle} (${pctOut}%)`;
                    if (inEl) inEl.textContent = `📥 ENTRANDO: ${inTitle} (${pctIn}%)`;
                    if (fillEl) fillEl.style.width = `${pctIn}%`;
                } else {
                    searchBanner.style.display = "none";
                }
            }

            const spotifyBanner = document.getElementById("spotifyTransitionBanner");
            if (spotifyBanner) {
                if (browseView === "spotify") {
                    spotifyBanner.style.display = "flex";
                    const pctEl = document.getElementById("spotifyTransitionPct");
                    const outEl = document.getElementById("spotifyOutgoingTrackInfo");
                    const inEl = document.getElementById("spotifyIncomingTrackInfo");
                    const fillEl = document.getElementById("spotifyTransitionFill");
                    if (pctEl) pctEl.textContent = `${pctIn}%`;
                    if (outEl) outEl.textContent = `📤 SAINDO: ${outTitle} (${pctOut}%)`;
                    if (inEl) inEl.textContent = `📥 ENTRANDO: ${inTitle} (${pctIn}%)`;
                    if (fillEl) fillEl.style.width = `${pctIn}%`;
                } else {
                    spotifyBanner.style.display = "none";
                }
            }

            // Identifica qual deck está saindo e qual está entrando
            const cardOutgoing = (activeDeck === "A") ? deckACard : deckBCard;
            const cardIncoming = (activeDeck === "A") ? deckBCard : deckACard;
            const tagOutgoing = (activeDeck === "A") ? deckATag : deckBTag;
            const tagIncoming = (activeDeck === "A") ? deckBTag : deckATag;
            const artistOutgoing = (activeDeck === "A") ? deckAArtist : deckBArtist;
            const artistIncoming = (activeDeck === "A") ? deckBArtist : deckAArtist;

            // Tags de status suaves com animação visual
            if (tagOutgoing) {
                tagOutgoing.className = "deck-tag outgoing";
                tagOutgoing.textContent = `${activeDeck === "A" ? "DECK A" : "DECK B"} 📤 ${pctOut}%`;
            }
            if (tagIncoming) {
                tagIncoming.className = "deck-tag incoming";
                tagIncoming.textContent = `${activeDeck === "A" ? "DECK B" : "DECK A"} 📥 ${pctIn}%`;
            }

            if (artistOutgoing) artistOutgoing.innerHTML = `<span style="color:#ff8800; font-weight:700;">📤 Saindo da música atual...</span>`;
            if (artistIncoming) artistIncoming.innerHTML = `<span style="color:#00e676; font-weight:700;">📥 Entrando na próxima música...</span>`;

            // CONTORNO SUAVE DOS CARDS CONFORME A BARRA VAI SAINDO E ENTRANDO
            if (cardOutgoing) {
                const outBorderAlpha = (0.06 + fromVol * 0.45).toFixed(2);
                const outGlowSize = (fromVol * 14).toFixed(1);
                const outGlowAlpha = (fromVol * 0.35).toFixed(2);
                const outBgAlpha = (fromVol * 0.10).toFixed(2);
                cardOutgoing.style.borderColor = `rgba(255, 85, 0, ${outBorderAlpha})`;
                cardOutgoing.style.boxShadow = `0 0 ${outGlowSize}px rgba(255, 85, 0, ${outGlowAlpha})`;
                cardOutgoing.style.background = `linear-gradient(135deg, rgba(255, 85, 0, ${outBgAlpha}), rgba(0, 0, 0, 0.4))`;
            }

            if (cardIncoming) {
                const inBorderAlpha = (0.06 + toVol * 0.55).toFixed(2);
                const inGlowSize = (toVol * 16).toFixed(1);
                const inGlowAlpha = (toVol * 0.45).toFixed(2);
                const inBgAlpha = (toVol * 0.12).toFixed(2);
                cardIncoming.style.borderColor = `rgba(0, 242, 254, ${inBorderAlpha})`;
                cardIncoming.style.boxShadow = `0 0 ${inGlowSize}px rgba(0, 242, 254, ${inGlowAlpha})`;
                cardIncoming.style.background = `linear-gradient(135deg, rgba(0, 242, 254, ${inBgAlpha}), rgba(0, 0, 0, 0.4))`;
            }

            // ATUALIZAÇÃO SINCRONIZADA EM TEMPO REAL NOS CARDS DAS LISTAS (Pesquisa, Biblioteca, Fila, Sugestões, Spotify)
            transitionProgress = progress;
            transitionOutgoingTrack = outgoingTrack;
            transitionIncomingTrack = incomingTrack;

            // Vincula badges e classes nos cards correspondentes em todas as listas abertas
            if (outgoingTrack && outgoingTrack.video_id) {
                document.querySelectorAll(`[data-video-id="${outgoingTrack.video_id}"]`).forEach(c => {
                    if (!c.classList.contains("transition-outgoing")) {
                        c.classList.remove("playing-now", "next-up", "transition-incoming", "playing");
                        c.classList.add("transition-outgoing");
                        c.setAttribute("data-transition-role", "outgoing");
                        const oldBadge = c.querySelector('.badge-now-playing, .badge-next-up, .badge-added-now, .badge-incoming-track, .status-playing, .status-next');
                        if (oldBadge) oldBadge.remove();
                        if (!c.querySelector('[data-track-badge="outgoing"]')) {
                            const subrow = c.querySelector('.track-card-subrow, .track-artist-row');
                            if (subrow) {
                                const b = document.createElement("div");
                                b.className = "badge-outgoing-track";
                                b.setAttribute("data-track-badge", "outgoing");
                                b.innerHTML = `<span>📤 SAINDO (${pctOut}%)</span>`;
                                subrow.insertBefore(b, subrow.firstChild);
                            }
                        }
                    }
                });
            }

            if (incomingTrack && incomingTrack.video_id) {
                document.querySelectorAll(`[data-video-id="${incomingTrack.video_id}"]`).forEach(c => {
                    if (!c.classList.contains("transition-incoming")) {
                        c.classList.remove("playing-now", "next-up", "transition-outgoing", "playing");
                        c.classList.add("transition-incoming");
                        c.setAttribute("data-transition-role", "incoming");
                        const oldBadge = c.querySelector('.badge-now-playing, .badge-next-up, .badge-added-now, .badge-outgoing-track, .status-playing, .status-next');
                        if (oldBadge) oldBadge.remove();
                        if (!c.querySelector('[data-track-badge="incoming"]')) {
                            const subrow = c.querySelector('.track-card-subrow, .track-artist-row');
                            if (subrow) {
                                const b = document.createElement("div");
                                b.className = "badge-incoming-track";
                                b.setAttribute("data-track-badge", "incoming");
                                b.innerHTML = `<span>📥 ENTRANDO (${pctIn}%)</span>`;
                                subrow.insertBefore(b, subrow.firstChild);
                            }
                        }
                    }
                });
            }

            // Anima contorno e brilho neon suave dos cards de lista conforme o fader avança
            const listOutCards = document.querySelectorAll('.track-card.transition-outgoing, [data-transition-role="outgoing"]');
            listOutCards.forEach(c => {
                const outBorderAlpha = (0.06 + fromVol * 0.45).toFixed(2);
                const outGlowSize = (fromVol * 14).toFixed(1);
                const outGlowAlpha = (fromVol * 0.35).toFixed(2);
                const outBgAlpha = (fromVol * 0.10).toFixed(2);
                c.style.borderColor = `rgba(255, 85, 0, ${outBorderAlpha})`;
                c.style.boxShadow = `0 0 ${outGlowSize}px rgba(255, 85, 0, ${outGlowAlpha})`;
                c.style.background = `linear-gradient(135deg, rgba(255, 85, 0, ${outBgAlpha}), rgba(0, 0, 0, 0.4))`;
                const badgeSpan = c.querySelector('[data-track-badge="outgoing"] span');
                if (badgeSpan) badgeSpan.textContent = `📤 SAINDO (${pctOut}%)`;
            });

            const listInCards = document.querySelectorAll('.track-card.transition-incoming, [data-transition-role="incoming"]');
            listInCards.forEach(c => {
                const inBorderAlpha = (0.06 + toVol * 0.55).toFixed(2);
                const inGlowSize = (toVol * 16).toFixed(1);
                const inGlowAlpha = (toVol * 0.45).toFixed(2);
                const inBgAlpha = (toVol * 0.12).toFixed(2);
                c.style.borderColor = `rgba(0, 242, 254, ${inBorderAlpha})`;
                c.style.boxShadow = `0 0 ${inGlowSize}px rgba(0, 242, 254, ${inGlowAlpha})`;
                c.style.background = `linear-gradient(135deg, rgba(0, 242, 254, ${inBgAlpha}), rgba(0, 0, 0, 0.4))`;
                const badgeSpan = c.querySelector('[data-track-badge="incoming"] span');
                if (badgeSpan) badgeSpan.textContent = `📥 ENTRANDO (${pctIn}%)`;
            });
        }

function triggerCrossfade(nextTrack) {
            if (!nextTrack) return;
            if (isTransitioning) cancelTransition();
            cancelTransition();

            const outgoingTrack = nowPlayingTrack;
            const incomingTrack = nextTrack;
            const durationMs = (crossfadeSeconds || 4) * 1000;
            const startSec = (djPlayMode === "drop") ? getTrackDropStartTime(nextTrack) : getTrackIntroSkip(nextTrack);

            isTransitioning = true;
            hasFadedCurrentTrack = true;
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
            }, durationMs + 2500);

            showCrossfadeIndicator();

            // Prepara a UI dos dois Decks para o crossfade
            const deckATitle = document.getElementById("deckATitle");
            const deckAArtist = document.getElementById("deckAArtist");
            const deckABpm = document.getElementById("deckABpm");
            const deckBTitle = document.getElementById("deckBTitle");
            const deckBArtist = document.getElementById("deckBArtist");
            const deckBBpm = document.getElementById("deckBBpm");
            const vinylA = document.getElementById("vinylA");
            const vinylB = document.getElementById("vinylB");
            const syncBadge = document.getElementById("djBpmSyncBadge");

            if (vinylA) vinylA.classList.add("spinning");
            if (vinylB) vinylB.classList.add("spinning");
            updateTurntablesState();

            const curBpm = (outgoingTrack && outgoingTrack.bpm) ? outgoingTrack.bpm : 135;
            const incBpm = (incomingTrack && incomingTrack.bpm) ? incomingTrack.bpm : curBpm;
            if (syncBadge) syncBadge.textContent = `⚡ Mixando: ~${incBpm} BPM`;

            if (activeDeck === "A") {
                if (deckATitle) deckATitle.textContent = outgoingTrack ? outgoingTrack.title : "Deck A";
                if (deckABpm) deckABpm.textContent = `${curBpm} BPM`;
                if (deckBTitle) deckBTitle.textContent = incomingTrack ? incomingTrack.title : "Deck B";
                if (deckBBpm) deckBBpm.textContent = `${incBpm} BPM`;
            } else {
                if (deckBTitle) deckBTitle.textContent = outgoingTrack ? outgoingTrack.title : "Deck B";
                if (deckBBpm) deckBBpm.textContent = `${curBpm} BPM`;
                if (deckATitle) deckATitle.textContent = incomingTrack ? incomingTrack.title : "Deck A";
                if (deckABpm) deckABpm.textContent = `${incBpm} BPM`;
            }

            // Inicia o contorno e status suave imediatamente no frame 0
            updateCrossfadeProgressUI(0, outgoingTrack, incomingTrack);

            renderAllActiveLists();

            if (nextTrack && nextTrack.video_id && !trackDurations[nextTrack.video_id]) {
                fetch(`/api/audio/info?id=${nextTrack.video_id}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data && data.duration) trackDurations[nextTrack.video_id] = data.duration;
                    }).catch(() => {});
            }

            // DETECÇÃO DE EFEITO ESPECIAL DE TRANSIÇÃO (DJ FX)
            const fxInfo = detectGenreFx(outgoingTrack, incomingTrack);
            currentActiveDjFx = fxInfo;

            // O HUD visual e os Efeitos de DJ SÓ DEVEM FUNCIONAR NO MODO BALADA & CLUB DJ!
            if (djPlayMode === "club") {
                showDjClubHud(fxInfo);
            } else {
                hideDjClubHud();
            }

            if (engineMode === "audio") {
                initWebAudio();
                if (audioCtx && audioCtx.state === "suspended") {
                    audioCtx.resume();
                }

                const fromAudio = getActiveAudioDeck();
                const toAudio = getStandbyAudioDeck();
                const fromGain = activeDeck === "A" ? deckGainA : deckGainB;
                const toGain = activeDeck === "A" ? deckGainB : deckGainA;

                // Garante que o deck que entra comece em 0 e o atual em 1 suavemente
                if (fromGain && audioCtx) {
                    fromGain.gain.cancelScheduledValues(audioCtx.currentTime);
                    fromGain.gain.setValueAtTime(1.0, audioCtx.currentTime);
                }
                if (toGain && audioCtx) {
                    toGain.gain.cancelScheduledValues(audioCtx.currentTime);
                    toGain.gain.setValueAtTime(0.0, audioCtx.currentTime);
                }

                let beatmatchRate = currentPlaybackSpeed;
                if (isAutoBeatmatchEnabled && curBpm > 0 && incBpm > 0) {
                    const ratio = curBpm / incBpm;
                    beatmatchRate = Math.max(0.85, Math.min(1.15, currentPlaybackSpeed * ratio));
                }

                if (toAudio) {
                    toAudio.src = `/api/audio/stream?id=${nextTrack.video_id}`;
                    toAudio.currentTime = startSec;
                    toAudio.playbackRate = beatmatchRate;
                    toAudio.preservesPitch = true;
                    toAudio.play().then(() => {
                        if (startSec > 0 && Math.abs(toAudio.currentTime - startSec) > 0.6) {
                            toAudio.currentTime = startSec;
                        }
                        toAudio.playbackRate = beatmatchRate;
                        toAudio.preservesPitch = true;
                    }).catch(() => {});
                }

                // Dispara efeitos sonoros DJ FX quando o Modo Balada & Club DJ ou Modo Drop Hunter estiver ativo!
                if (djPlayMode === "club" || djPlayMode === "drop") {
                    playDjClubFx(fxInfo, incBpm, durationMs, fromAudio, toAudio);
                }

                const stepInterval = 40;
                const totalSteps = Math.max(1, durationMs / stepInterval);
                let currentStep = 0;

                const outgoingDeckName = activeDeck;
                const incomingDeckName = activeDeck === "A" ? "B" : "A";

                crossfadeTimer = setInterval(() => {
                    currentStep++;
                    const progress = currentStep / totalSteps;

                    // APLICAÇÃO DO CROSSOVER DE 3 BANDAS PROFISSIONAL (BASS SWAP, VOCAL EQUAL-POWER E HIGH GROOVE)
                    applyTransitionCrossover(progress, outgoingDeckName, incomingDeckName);

                    // Atualiza o HUD visual de 3 bandas no player em tempo real SOMENTE no Modo Balada
                    if (djPlayMode === "club") {
                        updateDjClubHud(progress, outgoingDeckName, incomingDeckName);
                    }

                    // Animação contínua e suave dos contornos dos cards, barras e status
                    updateCrossfadeProgressUI(progress, outgoingTrack, incomingTrack);

                    if (currentStep >= totalSteps) {
                        clearInterval(crossfadeTimer);
                        crossfadeTimer = null;
                        if (transitionWatchdogTimer) {
                            clearTimeout(transitionWatchdogTimer);
                            transitionWatchdogTimer = null;
                        }

                        // Oculta ordenadamente o HUD visual após o drop
                        hideDjClubHud();

                        activeDeck = activeDeck === "A" ? "B" : "A";
                        if (fromAudio) {
                            fromAudio.pause();
                            fromAudio.currentTime = 0;
                        }

                        applyStemsToDsp();

                        nowPlayingTrack = incomingTrack;
                        updateTrackInfoUI(incomingTrack);

                        // Se houve beatmatch automático temporário ou pitch ajustado, rampa suavemente de volta ao BPM original com atualização visual em tempo real!
                        if (toAudio && Math.abs(beatmatchRate - currentPlaybackSpeed) > 0.015) {
                            rampBpmToOriginal(toAudio, beatmatchRate, currentPlaybackSpeed, incBpm, 4000);
                        } else if (currentPitchAdjustment !== 0 && toAudio) {
                            const curEff = currentPlaybackSpeed * (1.0 + currentPitchAdjustment / 100);
                            rampBpmToOriginal(toAudio, curEff, currentPlaybackSpeed, incBpm, 3500);
                        } else {
                            updateLiveBpmPanel();
                        }
                        hideCrossfadeIndicator();
                        isTransitioning = false;
                        hasFadedCurrentTrack = false;
                        prewarmedUpcomingId = "";
                        resetDecksContourUI();
                        startTimeMonitor();
                        if (typeof recordTrackInHistory === "function") recordTrackInHistory(incomingTrack);
                        if (typeof calculateDjModeNextTrack === "function") calculateDjModeNextTrack(incomingTrack);
                        renderAllActiveLists();
                        updateUpcomingTrackUI();
                        updateTurntablesState();
                        updateDjMixerUI();
                    }
                }, stepInterval);

            } else {
                // YouTube Crossfade
                const fromPlayer = getActivePlayer();
                const toPlayer = getStandbyPlayer();
                const fromDeckEl = getActiveDeckEl();
                const toDeckEl = getStandbyDeckEl();

                try {
                    toPlayer.unMute();
                    toPlayer.setVolume(0);
                    if (typeof toPlayer.loadVideoById === "function") {
                        toPlayer.loadVideoById(nextTrack.video_id, startSec);
                        if (startSec > 0 && typeof toPlayer.seekTo === "function") {
                            try { toPlayer.seekTo(startSec, true); } catch (e) {}
                        }
                        if (typeof toPlayer.setPlaybackRate === "function") {
                            try { toPlayer.setPlaybackRate(Math.min(2.0, currentPlaybackSpeed)); } catch (e) {}
                        }
                        toPlayer.playVideo();
                    }
                } catch (e) {}

                // Dispara efeitos sonoros procedurais no YouTube também quando em modo Club DJ
                if (djPlayMode === "club") {
                    playDjClubFx(fxInfo, incBpm, durationMs, null, null);
                }

                const ytMaxVol = Math.min(100, masterVolume);
                const stepInterval = 40;
                const totalSteps = Math.max(1, durationMs / stepInterval);
                let currentStep = 0;

                const outgoingDeckName = activeDeck;
                const incomingDeckName = activeDeck === "A" ? "B" : "A";

                if (toDeckEl) toDeckEl.style.zIndex = "2";
                if (fromDeckEl) fromDeckEl.style.zIndex = "1";

                crossfadeTimer = setInterval(() => {
                    currentStep++;
                    const progress = currentStep / totalSteps;

                    const volFrom = Math.round(ytMaxVol * (1 - progress));
                    const volTo = Math.round(ytMaxVol * progress);

                    try {
                        if (!isMuted) {
                            fromPlayer.setVolume(Math.max(0, volFrom));
                            toPlayer.setVolume(Math.min(ytMaxVol, volTo));
                        }
                        if (fromDeckEl) fromDeckEl.style.opacity = (1 - progress).toFixed(2);
                        if (toDeckEl) toDeckEl.style.opacity = progress.toFixed(2);
                    } catch (e) {}

                    // Atualiza o HUD visual de 3 bandas no player em tempo real (YouTube)
                    updateDjClubHud(progress, outgoingDeckName, incomingDeckName);

                    // Animação contínua e suave dos contornos dos cards, barras e status (YouTube)
                    updateCrossfadeProgressUI(progress, outgoingTrack, incomingTrack);

                    if (currentStep >= totalSteps) {
                        clearInterval(crossfadeTimer);
                        crossfadeTimer = null;
                        
                        // Oculta ordenadamente o HUD visual após o drop
                        hideDjClubHud();

                        activeDeck = activeDeck === "A" ? "B" : "A";
                        if (fromDeckEl) fromDeckEl.style.opacity = "0";
                        if (toDeckEl) toDeckEl.style.opacity = "1";

                        try {
                            fromPlayer.pauseVideo();
                            fromPlayer.setVolume(0);
                            if (isMuted) toPlayer.mute();
                            else {
                                toPlayer.unMute();
                                toPlayer.setVolume(ytMaxVol);
                            }
                        } catch (e) {}

                        nowPlayingTrack = incomingTrack;
                        updateTrackInfoUI(incomingTrack);
                        hideCrossfadeIndicator();
                        isTransitioning = false;
                        hasFadedCurrentTrack = false;
                        prewarmedUpcomingId = "";
                        resetDecksContourUI();
                        startTimeMonitor();
                        if (typeof recordTrackInHistory === "function") recordTrackInHistory(incomingTrack);
                        if (typeof calculateDjModeNextTrack === "function") calculateDjModeNextTrack(incomingTrack);
                        renderAllActiveLists();
                        updateUpcomingTrackUI();
                        updateTurntablesState();
                        updateDjMixerUI();
                    }
                }, stepInterval);
            }
        }

        // SELEÇÃO DA PARTE DA MÚSICA (SEEK BAR) NO PLAYER PRINCIPAL
        
        // SPOTIFY DJ MIXER INTERFACE CONTROLLER
        // Helper para obter URL da capa do álbum com fallback inteligente
        function getTrackThumbnailUrl(track) {
            if (!track) return "";
            if (track.thumbnail) return track.thumbnail;
            if (track.video_id) return `https://i.ytimg.com/vi/${track.video_id}/mqdefault.jpg`;
            return "";
        }

        // Sincroniza o estado de rotação física dos toca-discos (Auto DJ Platters)
        function updateTurntablesState() {
            const vinylA = document.getElementById("vinylA");
            const vinylB = document.getElementById("vinylB");
            const tonearmA = document.getElementById("tonearmA");
            const tonearmB = document.getElementById("tonearmB");
            const strobeA = document.getElementById("strobeA");
            const strobeB = document.getElementById("strobeB");

            const spinDuration = (1.8 / currentPlaybackSpeed) + "s";
            if (vinylA) vinylA.style.animationDuration = spinDuration;
            if (vinylB) vinylB.style.animationDuration = spinDuration;

            const curAudio = getActiveAudioDeck();
            const activeP = getActivePlayer();
            const isPlaying = (engineMode === "audio" && curAudio && !curAudio.paused && curAudio.currentTime > 0) || 
                              (engineMode === "video" && activeP && typeof activeP.getPlayerState === "function" && 
                               (activeP.getPlayerState() === YT.PlayerState.PLAYING || activeP.getPlayerState() === YT.PlayerState.BUFFERING));

            if (isTransitioning) {
                if (vinylA) {
                    vinylA.classList.add("spinning");
                    vinylA.style.animationPlayState = isPlaying ? "running" : "paused";
                }
                if (vinylB) {
                    vinylB.classList.add("spinning");
                    vinylB.style.animationPlayState = isPlaying ? "running" : "paused";
                }
                if (tonearmA) tonearmA.classList.toggle("active", isPlaying);
                if (tonearmB) tonearmB.classList.toggle("active", isPlaying);
                if (strobeA) strobeA.classList.toggle("active-strobe", isPlaying);
                if (strobeB) strobeB.classList.toggle("active-strobe", isPlaying);
            } else {
                if (activeDeck === "A") {
                    if (vinylA) {
                        vinylA.classList.add("spinning");
                        vinylA.style.animationPlayState = isPlaying ? "running" : "paused";
                    }
                    if (vinylB) {
                        vinylB.classList.remove("spinning");
                        vinylB.style.animationPlayState = "paused";
                    }
                    if (tonearmA) tonearmA.classList.toggle("active", isPlaying);
                    if (tonearmB) tonearmB.classList.remove("active");
                    if (strobeA) strobeA.classList.toggle("active-strobe", isPlaying);
                    if (strobeB) strobeB.classList.remove("active-strobe");
                } else {
                    if (vinylB) {
                        vinylB.classList.add("spinning");
                        vinylB.style.animationPlayState = isPlaying ? "running" : "paused";
                    }
                    if (vinylA) {
                        vinylA.classList.remove("spinning");
                        vinylA.style.animationPlayState = "paused";
                    }
                    if (tonearmB) tonearmB.classList.toggle("active", isPlaying);
                    if (tonearmA) tonearmA.classList.remove("active");
                    if (strobeB) strobeB.classList.toggle("active-strobe", isPlaying);
                    if (strobeA) strobeA.classList.remove("active-strobe");
                }
            }
        }

        function updateDjMixerUI() {
            const deckACard = document.getElementById("djDeckACard");
            const deckBCard = document.getElementById("djDeckBCard");
            const deckATag = document.getElementById("deckATag");
            const deckBTag = document.getElementById("deckBTag");
            const deckATitle = document.getElementById("deckATitle");
            const deckAArtist = document.getElementById("deckAArtist");
            const deckABpm = document.getElementById("deckABpm");
            const deckBTitle = document.getElementById("deckBTitle");
            const deckBArtist = document.getElementById("deckBArtist");
            const deckBBpm = document.getElementById("deckBBpm");
            const meterA = document.getElementById("meterA");
            const meterB = document.getElementById("meterB");
            const faderKnob = document.getElementById("djFaderKnob");
            const faderFill = document.getElementById("djFaderFill");
            const syncBadge = document.getElementById("djBpmSyncBadge");
            const balanceText = document.getElementById("crossfaderBalanceText");

            const upcoming = getUpcomingTrack();
            const curBpm = (nowPlayingTrack && nowPlayingTrack.bpm) ? nowPlayingTrack.bpm : 135;
            const nextBpm = (upcoming && upcoming.bpm) ? upcoming.bpm : curBpm;

            // Atualiza Capas dos Discos de Vinil (Arte Animada Auto DJ)
            const vinylCoverA = document.getElementById("vinylCoverA");
            const vinylCoverB = document.getElementById("vinylCoverB");
            const vinylFallbackA = document.getElementById("vinylFallbackA");
            const vinylFallbackB = document.getElementById("vinylFallbackB");

            const coverNow = getTrackThumbnailUrl(nowPlayingTrack);
            const coverNext = getTrackThumbnailUrl(upcoming);

            if (activeDeck === "A") {
                if (deckACard) deckACard.classList.add("active-deck");
                if (deckBCard) deckBCard.classList.remove("active-deck");
                if (!isTransitioning) {
                    if (deckATag) { deckATag.className = "deck-tag active"; deckATag.textContent = "DECK A"; }
                    if (deckBTag) { deckBTag.className = "deck-tag"; deckBTag.textContent = "DECK B"; }
                }

                if (vinylCoverA) {
                    if (coverNow) {
                        vinylCoverA.src = coverNow;
                        vinylCoverA.style.display = "block";
                        if (vinylFallbackA) vinylFallbackA.style.display = "none";
                    } else {
                        vinylCoverA.style.display = "none";
                        if (vinylFallbackA) vinylFallbackA.style.display = "flex";
                    }
                }
                if (vinylCoverB) {
                    if (coverNext) {
                        vinylCoverB.src = coverNext;
                        vinylCoverB.style.display = "block";
                        if (vinylFallbackB) vinylFallbackB.style.display = "none";
                    } else {
                        vinylCoverB.style.display = "none";
                        if (vinylFallbackB) vinylFallbackB.style.display = "flex";
                    }
                }

                if (deckATitle) deckATitle.textContent = nowPlayingTrack ? nowPlayingTrack.title : "Tocando agora";
                if (deckAArtist) deckAArtist.textContent = nowPlayingTrack ? (nowPlayingTrack.artist || nowPlayingTrack.category) : "-";
                if (deckABpm) deckABpm.textContent = `${curBpm} BPM`;

                if (!isTransitioning) {
                    if (deckBTitle) deckBTitle.textContent = upcoming ? upcoming.title : "Fim da fila";
                    if (deckBArtist) deckBArtist.textContent = upcoming ? (upcoming.artist || upcoming.category) : "-";
                    if (deckBBpm) deckBBpm.textContent = `${nextBpm} BPM`;
                    if (meterA) meterA.style.width = "100%";
                    if (meterB) meterB.style.width = "0%";
                    if (faderKnob) faderKnob.style.left = "0%";
                    if (faderFill) faderFill.style.width = "0%";
                    if (balanceText) balanceText.textContent = `Deck A 100% • Crossfade: ${crossfadeSeconds}s`;
                }
            } else {
                if (deckBCard) deckBCard.classList.add("active-deck");
                if (deckACard) deckACard.classList.remove("active-deck");
                if (!isTransitioning) {
                    if (deckBTag) { deckBTag.className = "deck-tag active"; deckBTag.textContent = "DECK B"; }
                    if (deckATag) { deckATag.className = "deck-tag"; deckATag.textContent = "DECK A"; }
                }

                if (vinylCoverB) {
                    if (coverNow) {
                        vinylCoverB.src = coverNow;
                        vinylCoverB.style.display = "block";
                        if (vinylFallbackB) vinylFallbackB.style.display = "none";
                    } else {
                        vinylCoverB.style.display = "none";
                        if (vinylFallbackB) vinylFallbackB.style.display = "flex";
                    }
                }
                if (vinylCoverA) {
                    if (coverNext) {
                        vinylCoverA.src = coverNext;
                        vinylCoverA.style.display = "block";
                        if (vinylFallbackA) vinylFallbackA.style.display = "none";
                    } else {
                        vinylCoverA.style.display = "none";
                        if (vinylFallbackA) vinylFallbackA.style.display = "flex";
                    }
                }

                if (deckBTitle) deckBTitle.textContent = nowPlayingTrack ? nowPlayingTrack.title : "Tocando agora";
                if (deckBArtist) deckBArtist.textContent = nowPlayingTrack ? (nowPlayingTrack.artist || nowPlayingTrack.category) : "-";
                if (deckBBpm) deckBBpm.textContent = `${curBpm} BPM`;

                if (!isTransitioning) {
                    if (deckATitle) deckATitle.textContent = upcoming ? upcoming.title : "Fim da fila";
                    if (deckAArtist) deckAArtist.textContent = upcoming ? (upcoming.artist || upcoming.category) : "-";
                    if (deckABpm) deckABpm.textContent = `${nextBpm} BPM`;
                    if (meterB) meterB.style.width = "100%";
                    if (meterA) meterA.style.width = "0%";
                    if (faderKnob) faderKnob.style.left = "100%";
                    if (faderFill) faderFill.style.width = "100%";
                    if (balanceText) balanceText.textContent = `Deck B 100% • Crossfade: ${crossfadeSeconds}s`;
                }
            }

            if (syncBadge && !isTransitioning) {
                syncBadge.textContent = `⚡ Sincronia: ~${curBpm} BPM`;
            }
            const stemsTitle = document.getElementById("stemsTrackNowTitle");
            const stemsBpm = document.getElementById("stemsTrackNowBpm");
            if (stemsTitle && nowPlayingTrack) stemsTitle.textContent = nowPlayingTrack.title;
            if (stemsBpm) stemsBpm.textContent = `⚡ ${curBpm} BPM`;

            updateTurntablesState();
        }

        function playTrackInstantWithFadeIn(track) {
            playTrackInstant(track);
            if (engineMode === "audio" && audioCtx) {
                const curGain = (activeDeck === "A" ? deckGainA : deckGainB);
                if (curGain) {
                    curGain.gain.setValueAtTime(0.0, audioCtx.currentTime);
                    curGain.gain.linearRampToValueAtTime(1.0, audioCtx.currentTime + 0.8);
                }
            }
            updateDjMixerUI();
        }

        // ==========================================================
        // GERENCIADOR DE REPRODUÇÃO CENTRALIZADO (CONTROLE DE LISTAS ATIVAS)
        // ==========================================================
        let activePlaybackSource = "library"; // "library", "search", "suggestions", "queue"
        let currentFilteredLibraryTracks = null;

        function triggerTrackPlayback(track) {
            if (!track) return;
            recordTrackInRecentHistory(track.video_id);
            initWebAudio();
            if (audioCtx && audioCtx.state === "suspended") {
                audioCtx.resume();
            }
            const curAudio = getActiveAudioDeck();
            const activeP = getActivePlayer();
            const isPlaying = (engineMode === "audio" && curAudio && !curAudio.paused && curAudio.currentTime > 0) || 
                              (engineMode === "video" && activeP && typeof activeP.getPlayerState === "function" && 
                               (activeP.getPlayerState() === YT.PlayerState.PLAYING || activeP.getPlayerState() === YT.PlayerState.BUFFERING));

            if (isPlaying && crossfadeSeconds > 0 && nowPlayingTrack && nowPlayingTrack.video_id !== track.video_id) {
                triggerCrossfade(track);
            } else {
                playTrackInstantWithFadeIn(track);
            }
        }

        function playFromList(queueList, index, sourceName, categoryName) {
            if (!queueList || queueList.length === 0 || index < 0 || index >= queueList.length) return;
            activePlaybackSource = sourceName;
            nowPlayingQueue = queueList.slice();
            nowPlayingIndex = index;
            nowPlayingCategoryName = categoryName || queueList[index].category || "Fila";

            const track = nowPlayingQueue[index];
            if (track) {
                setLockedGenre(track.category || categoryName || "Personalizada");
            }
            triggerTrackPlayback(track);
            renderAllActiveLists();
        }

        function playSearchTrack(index) {
            let displayTracks = (freeSearchFilter === "library") ? freeSearchResults.library_tracks :
                                (freeSearchFilter === "new") ? freeSearchResults.youtube_tracks : freeSearchResults.tracks;
            if (!displayTracks || displayTracks.length === 0 || index < 0 || index >= displayTracks.length) return;
            playFromList(displayTracks, index, "search", "Pesquisa: " + (lastFreeSearchQuery || "Geral"));
        }

        function playSuggestionTrack(index) {
            if (!currentActiveSuggestions || currentActiveSuggestions.length === 0 || index < 0 || index >= currentActiveSuggestions.length) return;
            const catName = isRadioActive ? "Faixas Parecidas" : (currentSuggestionCategory || "Sugestões");
            playFromList(currentActiveSuggestions, index, "suggestions", catName);
        }

        function playLibraryTrack(categoryName, index) {
            const list = currentFilteredLibraryTracks !== null ? currentFilteredLibraryTracks : (DATA[categoryName] || []);
            if (!list || list.length === 0 || index < 0 || index >= list.length) return;
            playFromList(list, index, "library", categoryName);
        }

        function playQueueTrack(index) {
            if (!pendingQueue || pendingQueue.length === 0 || index < 0 || index >= pendingQueue.length) return;
            playFromList(pendingQueue, index, "queue", "Minha Fila");
        }

        function playTrackByObject(track) {
            if (!track) return;
            const cat = track.category || browseCategory;
            if (DATA[cat]) {
                const list = DATA[cat];
                const foundIdx = list.findIndex(t => t.video_id === track.video_id);
                playFromList(list, foundIdx !== -1 ? foundIdx : 0, "library", cat);
            } else {
                playFromList([track], 0, "custom", "Personalizada");
            }
        }

        function playTrackByVideoId(videoId) {
            let found = null;
            CATEGORIES.forEach(cat => {
                if (!found && DATA[cat]) {
                    found = DATA[cat].find(t => t.video_id === videoId);
                }
            });
            if (!found && pendingQueue) {
                found = pendingQueue.find(t => t.video_id === videoId);
            }
            if (!found && suggestionsByGenre[currentSuggestionCategory]) {
                found = suggestionsByGenre[currentSuggestionCategory].find(t => t.video_id === videoId);
            }
            if (found) {
                playTrackByObject(found);
            }
        }

        function startPlaybackFromLibrary(categoryName, index) {
            playLibraryTrack(categoryName, index);
        }

        function playCustomTrack(videoId, title, artist, category, source, bpm) {
            const customTrack = {
                video_id: videoId,
                title: title,
                artist: artist,
                category: category || "Personalizada",
                source: source || "Geral",
                bpm: bpm || 135
            };
            triggerTrackPlayback(customTrack);
        }

        function recalculateContextOnSeek(targetTime, dur) {
            const dropStartSec = (typeof getTrackDropStartTime === "function") ? getTrackDropStartTime(nowPlayingTrack) : 22.0;
            hasFadedCurrentTrack = false;
            consecutiveSilenceCount = 0;
            consecutiveLowEnergyCount = 0;
            consecutivePredictedDropCount = 0;
            dropEnergyHistory = [];

            // Se o usuário voltou para o início (< 12s) ou antes do drop para repetir
            if (targetTime <= dropStartSec || targetTime < 12) {
                dropActiveSeconds = 0;
                dropTargetSeconds = (typeof dropWindowManualBase === "number") ? dropWindowManualBase : 75;
                showToast("🔄 Repetindo/Início: Contexto do Drop e análise reiniciados!");
            } else {
                // Recalcula o tempo já decorrido do drop relativo à nova posição da barra
                dropActiveSeconds = Math.max(0, targetTime - dropStartSec);
                const base = (typeof dropWindowManualBase === "number") ? dropWindowManualBase : 75;
                dropTargetSeconds = Math.max(dropActiveSeconds + 35, base);
                showToast(`📍 Contexto sincronizado na posição ${formatTime(targetTime)}!`);
            }

            if (typeof updateDropHunterMetrics === "function") {
                updateDropHunterMetrics();
            }
        }
        window.recalculateContextOnSeek = recalculateContextOnSeek;

        function handleSeekClick(e) {
            const track = document.getElementById("progressTrack");
            if (!track) return;
            const rect = track.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const percentage = Math.max(0, Math.min(1, clickX / rect.width));
            seekToPercentage(percentage);
        }

        function seekToPercentage(pct) {
            let dur = 0;
            let targetTime = 0;
            if (engineMode === "audio") {
                const curAudio = getActiveAudioDeck();
                if (curAudio && curAudio.duration) {
                    dur = curAudio.duration;
                    targetTime = pct * dur;
                    curAudio.currentTime = targetTime;
                }
            } else {
                const activeP = getActivePlayer();
                if (activeP && typeof activeP.getDuration === "function") {
                    dur = activeP.getDuration() || 0;
                    targetTime = pct * dur;
                    if (dur > 0 && typeof activeP.seekTo === "function") {
                        activeP.seekTo(targetTime, true);
                    }
                }
            }
            updateProgressUI(targetTime, dur);
            recalculateContextOnSeek(targetTime, dur);
        }

        function formatTime(sec) {
            if (isNaN(sec) || sec < 0) return "0:00";
            const m = Math.floor(sec / 60);
            const s = Math.floor(sec % 60);
            return `${m}:${s < 10 ? "0" : ""}${s}`;
        }

        function updateProgressUI(curr, dur) {
            const fill = document.getElementById("progressFill");
            const scrubber = document.getElementById("progressScrubber");
            const curLabel = document.getElementById("timeCurrent");
            const durLabel = document.getElementById("timeDuration");

            if (curLabel) curLabel.textContent = formatTime(curr);
            if (durLabel) durLabel.textContent = formatTime(dur);

            if (dur > 0) {
                const pct = Math.max(0, Math.min(100, (curr / dur) * 100));
                if (fill) fill.style.width = `${pct}%`;
                if (scrubber) scrubber.style.left = `${pct}%`;
            } else {
                if (fill) fill.style.width = "0%";
                if (scrubber) scrubber.style.left = "0%";
            }
        }

        // CONTROLE MASTER DE VOLUME (0 a 200% VLC) & PERSISTÊNCIA
        function setMasterVolume(val) {
            masterVolume = parseInt(val, 10);
            if (isNaN(masterVolume)) masterVolume = 100;
            masterVolume = Math.max(0, Math.min(200, masterVolume));

            isMuted = (masterVolume === 0);
            if (masterVolume > 0) prevMasterVolume = masterVolume;

            localStorage.setItem("pref_masterVolume", masterVolume.toString());
            updateVolumeUI();

            // Aplica no Web Audio HD (0.0 até 2.0 = 200% VLC)
            if (masterGainNode && audioCtx) {
                const targetGain = isMuted ? 0.0 : (masterVolume / 100);
                masterGainNode.gain.setTargetAtTime(targetGain, audioCtx.currentTime, 0.02);
            }

            // OBRIGATÓRIO: Atualiza todos os Efeitos Sonoros DJ e caudas para obedecer rigorosamente ao volume!
            if (typeof updateDjFxVolume === "function") {
                updateDjFxVolume();
            }

            // Se o YouTube IFrame estiver ativo, aplica com limite de 100
            if (!isTransitioning) {
                const activeP = getActivePlayer();
                if (activeP && typeof activeP.setVolume === "function") {
                    try {
                        if (isMuted) {
                            activeP.mute();
                        } else {
                            activeP.unMute();
                            activeP.setVolume(Math.min(100, masterVolume));
                        }
                    } catch (e) {}
                }
            }
        }

        function cycleVlcBoost() {
            if (masterVolume < 100) setMasterVolume(100);
            else if (masterVolume === 100) setMasterVolume(125);
            else if (masterVolume === 125) setMasterVolume(150);
            else if (masterVolume === 150) setMasterVolume(200);
            else setMasterVolume(100);
            showToast(`Volume VLC: ${masterVolume}%`);
        }

        function toggleMute() {
            if (masterVolume > 0) {
                prevMasterVolume = masterVolume;
                setMasterVolume(0);
            } else {
                setMasterVolume(prevMasterVolume > 0 ? prevMasterVolume : 100);
            }
            if (typeof updateDjFxVolume === "function") {
                updateDjFxVolume();
            }
        }

        function updateVolumeUI() {
            const slider = document.getElementById("volumeSlider");
            const text = document.getElementById("volText");
            const barMute = document.getElementById("barMuteBtn");
            const eqSlider = document.getElementById("eqVolumeSlider");
            const eqText = document.getElementById("eqBoostText");

            let volLabel = `${masterVolume}%`;
            let volColor = "var(--text-dim)";
            if (masterVolume > 140) {
                volLabel = `🔥 ${masterVolume}%`;
                volColor = "#ff0055";
            } else if (masterVolume > 100) {
                volLabel = `⚡ ${masterVolume}%`;
                volColor = "#ffaa00";
            }

            const icon = (isMuted || masterVolume === 0) ? "🔇" : (masterVolume < 50 ? "🔉" : (masterVolume <= 100 ? "🔊" : "📢"));

            if (slider) slider.value = masterVolume;
            if (text) {
                text.textContent = volLabel;
                text.style.color = volColor;
            }
            if (barMute) barMute.textContent = icon;

            if (eqSlider) eqSlider.value = masterVolume;
            if (eqText) {
                eqText.textContent = volLabel;
                eqText.style.color = volColor;
            }

            // Atualiza a tag indicadora de status e volume no Player do YouTube
            const visTag = document.getElementById("visTagText");
            if (visTag) {
                if (isMuted || masterVolume === 0) {
                    visTag.textContent = engineMode === "audio" ? "ÁUDIO HD • 🔇 MUDO" : "CLIPE YT • 🔇 MUDO";
                } else {
                    const modePrefix = engineMode === "audio" ? "ÁUDIO HD" : "CLIPE YT";
                    const vlcExtra = masterVolume > 100 ? " VLC" : "";
                    visTag.textContent = `${modePrefix} • ${masterVolume}%${vlcExtra}`;
                }
            }
        }

        // CONTROLE DO EQUALIZADOR PROFISSIONAL (10 BANDAS ISO, CURVA EM TEMPO REAL, PRE-AMP)
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
        }

        // ==========================================================
        // DJ STEMS ENGINE (ISOLAMENTO DE VOCAL, BEAT E GRAVE EM TEMPO REAL)
        // ==========================================================
        // ==========================================================
        // ==========================================================
        // ==========================================================
        // ==========================================================
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
                vocalHp: 320,
                vocalLp: 3600,
                vocalFormant: 2100,
                drumsPunch: 100,
                drumsSnap: 3200
            },
            "sertanejo": {
                name: "Sertanejo & Modão",
                bassCut: 195,
                bassBoost: 75,
                vocalHp: 260,
                vocalLp: 4000,
                vocalFormant: 2400,
                drumsPunch: 90,
                drumsSnap: 3400
            },
            "pagode": {
                name: "Samba & Pagode",
                bassCut: 175,
                bassBoost: 70,
                vocalHp: 285,
                vocalLp: 3800,
                vocalFormant: 2200,
                drumsPunch: 95,
                drumsSnap: 3300
            },
            "eletronica": {
                name: "Eletrônica & House",
                bassCut: 150,
                bassBoost: 55,
                vocalHp: 340,
                vocalLp: 4200,
                vocalFormant: 2200,
                drumsPunch: 120,
                drumsSnap: 3600
            },
            "trap": {
                name: "Trap & Rap",
                bassCut: 165,
                bassBoost: 50,
                vocalHp: 310,
                vocalLp: 3800,
                vocalFormant: 2200,
                drumsPunch: 110,
                drumsSnap: 3800
            },
            "latino": {
                name: "Reggaeton & Cumbia",
                bassCut: 180,
                bassBoost: 65,
                vocalHp: 290,
                vocalLp: 3900,
                vocalFormant: 2200,
                drumsPunch: 105,
                drumsSnap: 3200
            },
            "rock": {
                name: "Rock & Pop",
                bassCut: 200,
                bassBoost: 80,
                vocalHp: 280,
                vocalLp: 4200,
                vocalFormant: 2300,
                drumsPunch: 85,
                drumsSnap: 3500
            },
            "default": {
                name: "Universal Balada",
                bassCut: 180,
                bassBoost: 65,
                vocalHp: 280,
                vocalLp: 3800,
                vocalFormant: 2200,
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

            const allKeys = ["auto", "funk", "sertanejo", "pagode", "eletronica", "trap", "latino", "rock"];
            allKeys.forEach(k => {
                const chip = document.getElementById(`stProfile_${k}`);
                if (chip) chip.classList.toggle("active", k === key);
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

        function togglePlayPause() {
            initWebAudio();
            if (audioCtx && audioCtx.state === "suspended") {
                audioCtx.resume();
            }

            if (engineMode === "audio") {
                const curAudio = getActiveAudioDeck();
                if (!curAudio) return;
                if (curAudio.paused) {
                    curAudio.play();
                    updatePlayPauseButtons(true);
                } else {
                    curAudio.pause();
                    updatePlayPauseButtons(false);
                }
            } else {
                const activeP = getActivePlayer();
                if (!activeP || typeof activeP.getPlayerState !== "function") return;
                const state = activeP.getPlayerState();
                if (state === YT.PlayerState.PLAYING) {
                    activeP.pauseVideo();
                    updatePlayPauseButtons(false);
                } else {
                    activeP.playVideo();
                    updatePlayPauseButtons(true);
                }
            }
        }

        function updatePlayPauseButtons(isPlaying) {
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
        }

        // Avanço automático com crossfade (Spotify Priority Queue + Modos DJ)
        function autoAdvanceWithFade() {
            let nextTrack = null;
            // Modo de Repetição: Se 'one', repete a mesma música atual
            if (repeatMode === "one" && nowPlayingTrack) {
                nextTrack = nowPlayingTrack;
            } else if (pendingQueue && pendingQueue.length > 0) {
                nextTrack = pendingQueue.shift();
                fetch("/api/queue/remove", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ video_id: nextTrack.video_id })
                }).catch(() => {});
                updateAllQueueBadges();
            } else {
                nextTrack = getUpcomingTrack();
                if (nextTrack && nowPlayingQueue) {
                    const idx = nowPlayingQueue.findIndex(t => t.video_id === nextTrack.video_id);
                    if (idx !== -1) {
                        nowPlayingIndex = idx;
                    } else {
                        nowPlayingQueue.push(nextTrack);
                        nowPlayingIndex = nowPlayingQueue.length - 1;
                        showToast(`🌐 Descoberta Fora da Lista: ${nextTrack.title.slice(0, 26)}...`);
                    }
                }
            }

            if (nextTrack) {
                recordTrackInRecentHistory(nextTrack.video_id);
                djModeNextTrack = null;
                triggerCrossfade(nextTrack);
                setTimeout(() => {
                    if (typeof calculateDjModeNextTrack === "function") calculateDjModeNextTrack(nextTrack);
                    updateUpcomingTrackUI();
                    updateTurntablesState();
                    renderAllActiveLists();
                }, 800);
            }
        }

        // Transição Manual (Spotify Priority Queue + Modos DJ)
        function manualTransition(dir) {
            let nextTrack = null;
            if (dir === "next") {
                if (pendingQueue && pendingQueue.length > 0) {
                    nextTrack = pendingQueue.shift();
                    fetch("/api/queue/remove", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ video_id: nextTrack.video_id })
                    }).catch(() => {});
                    updateAllQueueBadges();
                } else {
                    nextTrack = getUpcomingTrack();
                    if (nextTrack && nowPlayingQueue) {
                        const idx = nowPlayingQueue.findIndex(t => t.video_id === nextTrack.video_id);
                        if (idx !== -1) {
                            nowPlayingIndex = idx;
                        } else {
                            nowPlayingQueue.push(nextTrack);
                            nowPlayingIndex = nowPlayingQueue.length - 1;
                            showToast(`🌐 Descoberta Fora da Lista: ${nextTrack.title.slice(0, 26)}...`);
                        }
                    }
                }
            } else {
                const list = nowPlayingQueue;
                if (!list || list.length === 0) return;
                nowPlayingIndex = (nowPlayingIndex - 1 + list.length) % list.length;
                nextTrack = list[nowPlayingIndex];
            }
            if (nextTrack) {
                recordTrackInRecentHistory(nextTrack.video_id);
                djModeNextTrack = null;
                if (crossfadeSeconds > 0) {
                    triggerCrossfade(nextTrack);
                } else {
                    playTrackInstant(nextTrack);
                }
                setTimeout(() => {
                    if (typeof calculateDjModeNextTrack === "function") calculateDjModeNextTrack(nextTrack);
                    updateUpcomingTrackUI();
                    updateTurntablesState();
                    renderAllActiveLists();
                }, 800);
            }
        }

        // Monitor de tempo para crossfade antecipado & atualização da seek bar
        function startTimeMonitor() {
            if (timeMonitorInterval) clearInterval(timeMonitorInterval);
            timeMonitorInterval = setInterval(() => {
                if (isTransitioning) return;

                let curr = 0;
                let dur = 0;

                if (engineMode === "audio") {
                    const curAudio = getActiveAudioDeck();
                    if (curAudio && !curAudio.paused) {
                        curr = curAudio.currentTime || 0;
                        dur = curAudio.duration || 0;
                    }
                } else {
                    const activeP = getActivePlayer();
                    if (activeP && typeof activeP.getCurrentTime === "function" && typeof activeP.getDuration === "function") {
                        try {
                            curr = activeP.getCurrentTime() || 0;
                            dur = activeP.getDuration() || 0;
                        } catch (e) {}
                    }
                }

                updateProgressUI(curr, dur);

                if (dur >= 25 && curr >= 12 && crossfadeSeconds > 0) {
                    const remaining = dur - curr;
                    if (remaining <= crossfadeSeconds && !hasFadedCurrentTrack && isAutoPlayEnabled) {
                        hasFadedCurrentTrack = true;
                        autoAdvanceWithFade();
                    }
                }
            }, 400);
        }

        function toggleCrossfadeSetting() {
            if (crossfadeSeconds === 0) crossfadeSeconds = 2;
            else if (crossfadeSeconds === 2) crossfadeSeconds = 4;
            else if (crossfadeSeconds === 4) crossfadeSeconds = 6;
            else if (crossfadeSeconds === 6) crossfadeSeconds = 8;
            else crossfadeSeconds = 0;

            localStorage.setItem("pref_crossfadeSeconds", crossfadeSeconds.toString());
            updateSettingsUI();
            showToast(crossfadeSeconds === 0 ? "Fade desligado" : `Fade configurado para ${crossfadeSeconds}s`);
        }

        function toggleIntroSkip() {
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
        }

        function toggleAutoPlay() {
            isAutoPlayEnabled = !isAutoPlayEnabled;
            localStorage.setItem("pref_autoPlay", isAutoPlayEnabled.toString());
            updateSettingsUI();
            showToast(isAutoPlayEnabled ? "Autoplay ativado" : "Autoplay pausado");
        }

        function toggleShuffle() {
            isShuffleEnabled = !isShuffleEnabled;
            localStorage.setItem("pref_shuffle", isShuffleEnabled.toString());
            updateSettingsUI();
            updateUpcomingTrackUI();
            renderList();
            showToast(isShuffleEnabled ? "Modo aleatório ativado" : "Ordem normal ativada");
        }

        function toggleRepeatMode() {
            if (repeatMode === "off") {
                repeatMode = "one";
                showToast("🔂 Modo Repetir: A MESMA MÚSICA em loop contínuo!");
            } else if (repeatMode === "one") {
                repeatMode = "all";
                showToast("🔁 Modo Repetir: TODA A PLAYLIST em loop contínuo!");
            } else {
                repeatMode = "off";
                showToast("➡️ Modo Repetir: DESATIVADO (Avanço normal)");
            }
            localStorage.setItem("pref_repeat_mode", repeatMode);
            updateSettingsUI();
            updateUpcomingTrackUI();
        }

        function updateRepeatButtonUI() {
            const btn = document.getElementById("barRepeatBtn");
            if (!btn) return;
            if (repeatMode === "one") {
                btn.className = "bar-pill-btn active";
                btn.innerHTML = "🔂 Repetir: 1";
                btn.title = "Modo Ativo: Repetindo a MESMA música em loop contínuo (Clique para alternar: Todas / Desativar)";
            } else if (repeatMode === "all") {
                btn.className = "bar-pill-btn active";
                btn.innerHTML = "🔁 Repetir: Todas";
                btn.title = "Modo Ativo: Repetindo a PLAYLIST inteira (Clique para alternar: Desativar)";
            } else {
                btn.className = "bar-pill-btn";
                btn.innerHTML = "🔂 Repetir";
                btn.title = "Modo de Repetição Desativado (Clique para repetir a mesma música em loop)";
            }
        }

        function updateSettingsUI() {
            const btnCross = document.getElementById("barCrossfadeBtn");
            if (btnCross) {
                btnCross.innerHTML = `🎚️ Fade: ${crossfadeSeconds}s`;
                btnCross.className = `bar-pill-btn ${crossfadeSeconds > 0 ? "fade-active" : ""}`;
            }

            const btnIntro = document.getElementById("barIntroSkipBtn");
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
            }

            const btnAuto = document.getElementById("barAutoPlayBtn");
            if (btnAuto) {
                btnAuto.className = `bar-pill-btn ${isAutoPlayEnabled ? "active" : ""}`;
            }

            const btnShuff = document.getElementById("barShuffleBtn");
            if (btnShuff) {
                btnShuff.className = `bar-pill-btn ${isShuffleEnabled ? "active" : ""}`;
            }

            const btnMode = document.getElementById("barEngineModeBtn");
            if (btnMode) {
                btnMode.innerHTML = engineMode === "audio" ? "🎵 Áudio HD" : "🎬 Clipe";
                btnMode.className = `bar-pill-btn ${engineMode === "audio" ? "active" : ""}`;
            }

            updateRepeatButtonUI();
        }

        function updateTrackInfoUI(track) {
            if (!track) return;
            const tTitle = document.getElementById("trackTitle");
            const tArtist = document.getElementById("trackArtist");
            const tSource = document.getElementById("trackSource");
            const bTitle = document.getElementById("barTitle");
            const bArtist = document.getElementById("barArtist");
            const bThumb = document.getElementById("barThumb");

            const visArt = document.getElementById("visAlbumArt");
            const visBlur = document.getElementById("visBgBlur");

            const thumbUrl = (track && track.video_id) ? `https://i.ytimg.com/vi/${track.video_id}/mqdefault.jpg` : DEFAULT_COVER_SVG;

            if (tTitle) tTitle.textContent = track.title || "Central de Músicas";
            if (tArtist) tArtist.textContent = track.artist || track.category || "";
            if (tSource) {
                const rawSource = (track.source || nowPlayingCategoryName || "Fila Ativa").trim();
                let displaySource = rawSource;
                if (rawSource.toLowerCase().includes("instagram")) {
                    displaySource = "📷 Instagram";
                    tSource.style.borderColor = "rgba(255, 0, 128, 0.4)";
                    tSource.style.background = "rgba(255, 0, 128, 0.12)";
                    tSource.style.color = "#ff4081";
                } else if (rawSource.toLowerCase().includes("spotify")) {
                    displaySource = "🟢 Spotify";
                    tSource.style.borderColor = "rgba(30, 215, 96, 0.4)";
                    tSource.style.background = "rgba(30, 215, 96, 0.12)";
                    tSource.style.color = "#1ed760";
                } else if (rawSource.toLowerCase().includes("youtube")) {
                    displaySource = "🔴 YouTube";
                    tSource.style.borderColor = "rgba(255, 68, 68, 0.4)";
                    tSource.style.background = "rgba(255, 68, 68, 0.12)";
                    tSource.style.color = "#ff5252";
                } else {
                    displaySource = `⚡ ${rawSource}`;
                    tSource.style.borderColor = "rgba(0, 242, 254, 0.35)";
                    tSource.style.background = "rgba(0, 242, 254, 0.12)";
                    tSource.style.color = "var(--accent)";
                }
                tSource.textContent = displaySource;
                tSource.title = `Origem: ${rawSource}`;
            }
            if (bTitle) bTitle.textContent = track.title || "Central de Músicas";
            if (bArtist) bArtist.textContent = track.artist || track.category || "";
            if (bThumb) {
                bThumb.onerror = function() { this.onerror = null; this.src = DEFAULT_COVER_SVG; };
                bThumb.src = thumbUrl;
            }

            if (visArt) {
                visArt.onerror = function() { this.onerror = null; this.src = DEFAULT_COVER_SVG; };
                visArt.src = thumbUrl;
            }
            if (visBlur) visBlur.style.backgroundImage = (track && track.video_id) ? `url('${thumbUrl}')` : "none";

            const btnYt = document.getElementById("btnYt");
            if (btnYt) btnYt.href = `https://www.youtube.com/watch?v=${track.video_id}`;
            const btnYtMusic = document.getElementById("btnYtMusic");
            if (btnYtMusic) btnYtMusic.href = `https://music.youtube.com/watch?v=${track.video_id}`;

            updateUpcomingTrackUI();
            updateLiveBpmPanel();
            updateDjIdealHelper(track);
            recordTrackInHistory(track);
        }

        function showToast(msg) {
            const t = document.getElementById("toastNotify");
            if (!t) return;
            t.textContent = msg;
            t.style.display = "block";
            setTimeout(() => {
                t.style.display = "none";
            }, 3500);
        }

        function hideToast() {
            const t = document.getElementById("toastNotify");
            if (t) t.style.display = "none";
        }

        function showCrossfadeIndicator() {
            const ind = document.getElementById("crossfadeIndicator");
            if (ind) ind.style.display = "block";
        }

        function hideCrossfadeIndicator() {
            const ind = document.getElementById("crossfadeIndicator");
            if (ind) ind.style.display = "none";
        }

        // Busca com Debounce na Biblioteca
        function handleLibrarySearch(query) {
            if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
            searchDebounceTimer = setTimeout(() => {
                executeLibrarySearch(query);
            }, 120);
        }

        function clearLibrarySearch() {
            const input = document.getElementById("searchInput");
            if (input) input.value = "";
            executeLibrarySearch("");
        }

        function removeAccents(str) {
            return (str || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
        }

        function escapeHtml(str) {
            return (str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
        }

        function executeLibrarySearch(query) {
            const rawQ = (query || "").trim();
            const q = removeAccents(rawQ);
            const clearBtn = document.getElementById("btnClearSearch");
            const badge = document.getElementById("searchBadgeCount");
            const listContainer = document.getElementById("trackList");

            if (!rawQ) {
                if (clearBtn) clearBtn.style.display = "none";
                if (badge) badge.textContent = "";
                renderList(DATA[browseCategory] || []);
                return;
            }

            if (clearBtn) clearBtn.style.display = "block";

            // Busca em TODA a biblioteca completa (todas as 725+ faixas)
            const allTracks = [];
            const seenIds = new Set();
            CATEGORIES.forEach(cat => {
                (DATA[cat] || []).forEach(t => {
                    if (!seenIds.has(t.video_id)) {
                        seenIds.add(t.video_id);
                        allTracks.push(t);
                    }
                });
            });

            const queryWords = q.split(/\s+/).filter(w => w.length > 0);

            const filtered = allTracks.filter(t => {
                const titleNorm = removeAccents(t.title);
                const artistNorm = removeAccents(t.artist);
                const catNorm = removeAccents(t.category);
                const bpmStr = (t.bpm || "").toString();

                return queryWords.every(word => 
                    titleNorm.includes(word) || 
                    artistNorm.includes(word) || 
                    catNorm.includes(word) ||
                    bpmStr === word ||
                    (word.endsWith("bpm") && bpmStr === word.replace("bpm", ""))
                );
            });

            if (badge) {
                badge.textContent = `${filtered.length} na biblioteca`;
            }

            if (filtered.length > 0) {
                renderList(filtered);
            } else {
                listContainer.innerHTML = `
                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 12px; padding: 30px 20px; text-align: center; margin-top: 15px;">
                        <div style="font-size: 32px; margin-bottom: 10px;">🔍</div>
                        <div style="font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 6px;">
                            Nenhuma música com "<em>${escapeHtml(rawQ)}</em>" na sua biblioteca
                        </div>
                        <div style="font-size: 12px; color: var(--text-dim); margin-bottom: 18px;">
                            Quer que a IA busque novas músicas com esse nome, ritmo ou artista no YouTube?
                        </div>
                        <button class="btn-sync-yt" onclick="searchExternalYouTube('${escapeQuotes(rawQ)}')" style="display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #ff0055, #ff5500); padding: 10px 22px; font-size: 13px; font-weight: 800; border-radius: 24px; box-shadow: 0 4px 15px rgba(255, 0, 85, 0.4); margin: 0 auto;">
                            <span>✨ Buscar "${escapeHtml(rawQ)}" no YouTube com IA</span>
                        </button>
                    </div>
                `;
            }
        }

        function searchExternalYouTube(query) {
            switchView("suggestions");
            const input = document.getElementById("suggSearchInput");
            if (input) input.value = query;
            executeCustomSuggestionSearch(query);
        }

        async function executeCustomSuggestionSearch(query) {
            const q = (query || "").trim();
            if (!q) return;
            const container = document.getElementById("suggestionsList");
            const badge = document.getElementById("suggestionCountBadge");
            const titleEl = document.getElementById("suggestionActiveGenreTitle");
            const subEl = document.getElementById("suggestionSubtext");

            if (badge) badge.textContent = "Buscando com IA...";
            if (titleEl) titleEl.innerHTML = `🔍 Busca com IA: <em>${escapeHtml(q)}</em>`;
            if (subEl) subEl.innerHTML = `Buscando novidades no YouTube baseadas no ritmo, BPM e estilo de <strong>${escapeHtml(q)}</strong>.`;
            showSuggestionsSkeleton();

            try {
                const res = await fetch("/api/search", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query: q, category: currentSuggestionCategory })
                });
                const data = await res.json();
                const tracks = data.tracks || (Array.isArray(data) ? data : []);

                renderSuggestionsList(tracks);
                if (badge) badge.textContent = `${tracks.length} encontradas`;
            } catch (e) {
                if (container) container.innerHTML = `<div style="color: #ff5555; text-align: center; padding: 25px;">Erro ao buscar novidades no YouTube. Tente novamente.</div>`;
            }
        }

        function escapeQuotes(str) {
            return (str || "").replace(/'/g, "\\'").replace(/"/g, '&quot;');
        }

        function openDirectQueueUrl() {
            if (pendingQueue.length === 0) return;
            const ids = pendingQueue.map(t => t.video_id).filter(Boolean).slice(0, 50).join(",");
            window.open(`https://www.youtube.com/watch_videos?video_ids=${ids}`, "_blank");
        }

        function updateQueueButton() {
            const tracks = DATA[browseCategory] || [];
            if (tracks.length === 0) return;
            const ids = tracks.map(t => t.video_id).filter(Boolean).slice(0, 50).join(",");
            const btn = document.getElementById("btnQueue");
            if (btn) btn.href = `https://www.youtube.com/watch_videos?video_ids=${ids}`;
        }

        // Gerenciamento da Fila de Reprodução
        async function loadQueue() {
            try {
                const res = await fetch("/api/queue");
                pendingQueue = await res.json() || [];
                renderQueueList();
                updateAllQueueBadges();
            } catch (e) {
                pendingQueue = [];
                updateAllQueueBadges();
            }
        }

        async function saveQueue(queue) {
            pendingQueue = queue;
            const badge = document.getElementById("queueBadgeCount");
            if (badge) badge.textContent = pendingQueue.length;
            const paneBadge = document.getElementById("queueCountBadge");
            if (paneBadge) paneBadge.textContent = `${pendingQueue.length} músicas`;
            updateUpcomingTrackUI();
        }

        // Atualiza contadores de fila em todos os pontos do Player
        function updateAllQueueBadges() {
            const count = pendingQueue.length;
            const b1 = document.getElementById("queueBadgeCount");
            if (b1) b1.textContent = count;
            const b2 = document.getElementById("playerQueueCount");
            if (b2) b2.textContent = count;
            const b3 = document.getElementById("barQueueCountBadge");
            if (b3) b3.textContent = count;
            const b4 = document.getElementById("modalQueueBadgeCount");
            if (b4) b4.textContent = `${count} músicas`;
            const paneBadge = document.getElementById("queueCountBadge");
            if (paneBadge) paneBadge.textContent = `${count} músicas`;
            updateUpcomingTrackUI();
            renderSpotifyQueueModalContent();
        }

        function openSpotifyQueueModal() {
            const m = document.getElementById("spotifyQueueModal");
            if (m) {
                m.style.display = "flex";
                renderSpotifyQueueModalContent();
            }
        }

        function closeSpotifyQueueModal(e) {
            if (e && e.target && e.target.id !== "spotifyQueueModal") return;
            const m = document.getElementById("spotifyQueueModal");
            if (m) m.style.display = "none";
        }

        function renderSpotifyQueueModalContent() {
            const npContainer = document.getElementById("queueModalNowPlaying");
            const itemsContainer = document.getElementById("queueModalItems");
            if (!npContainer || !itemsContainer) return;

            // Renderiza Tocando Agora
            if (nowPlayingTrack) {
                npContainer.innerHTML = `
                    <div class="queue-item-left">
                        <span class="eq-anim-bars"><span></span><span></span><span></span></span>
                        <div class="queue-item-meta">
                            <div class="queue-item-title">${escapeHtml(nowPlayingTrack.title)}</div>
                            <div class="queue-item-sub">${escapeHtml(nowPlayingTrack.artist || nowPlayingTrack.category || '')} • ⚡ ${nowPlayingTrack.bpm || 135} BPM</div>
                        </div>
                    </div>
                    <span class="badge-source" style="background: rgba(0,230,118,0.15); color: #00e676; border: 1px solid rgba(0,230,118,0.3);">▶ Tocando Agora</span>
                `;
            } else {
                npContainer.innerHTML = `<div style="color: var(--text-dim); font-size: 11px;">Nenhuma música tocando no momento.</div>`;
            }

            // Renderiza Próximas da Fila do Usuário com números #1, #2, #3...
            if (pendingQueue.length === 0) {
                itemsContainer.innerHTML = `
                    <div style="color: var(--text-dim); text-align: center; padding: 25px; font-size: 11.5px;">
                        Sua fila de espera está vazia.<br>
                        <span style="font-size: 10px; color: var(--accent);">Clique em "+ Fila" em qualquer música para adicionar!</span>
                    </div>
                `;
                return;
            }

            itemsContainer.innerHTML = "";
            pendingQueue.forEach((item, idx) => {
                const row = document.createElement("div");
                row.className = "queue-modal-item";
                row.innerHTML = `
                    <div class="queue-item-left">
                        <span class="queue-item-pos">#${idx + 1}${idx === 0 ? " (Próxima)" : ""}</span>
                        <div class="queue-item-meta">
                            <div class="queue-item-title">${idx + 1}. ${escapeHtml(item.title)}</div>
                            <div class="queue-item-sub">${escapeHtml(item.artist || item.category || '')} • ⚡ ${item.bpm || 135} BPM</div>
                        </div>
                    </div>
                    <div class="queue-item-actions">
                        <button class="btn-play-queue-item" onclick="playQueuedItemInstantly(${idx})" title="Tocar esta música agora com fade">▶ Tocar</button>
                        <button class="btn-remove-queue-item" onclick="removeFromQueue('${item.video_id}')" title="Remover da fila">🗑️</button>
                    </div>
                `;
                itemsContainer.appendChild(row);
            });
        }

        function playQueuedItemInstantly(idx) {
            if (!pendingQueue || !pendingQueue[idx]) return;
            const track = pendingQueue.splice(idx, 1)[0];
            fetch("/api/queue/remove", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ video_id: track.video_id })
            }).catch(() => {});
            updateAllQueueBadges();
            closeSpotifyQueueModal();
            triggerTrackPlayback(track);
            renderAllActiveLists();
        }

        async function addToQueue(track) {
            try {
                const res = await fetch("/api/queue/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(track)
                });
                const data = await res.json();
                if (data.queue) {
                    pendingQueue = data.queue;
                    updateAllQueueBadges();
                    renderAllActiveLists();
                    showToast(`"${track.title}" adicionada à Fila #${pendingQueue.length}!`);
                }
            } catch (e) {}
        }

        async function removeFromQueue(videoId) {
            try {
                const res = await fetch("/api/queue/remove", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ video_id: videoId })
                });
                const data = await res.json();
                if (data.queue) {
                    pendingQueue = data.queue;
                    updateAllQueueBadges();
                    renderAllActiveLists();
                    showToast("Música removida da fila!");
                }
            } catch (e) {}
        }

        async function clearAllQueue() {
            if (confirm("Deseja realmente limpar toda a sua fila?")) {
                try {
                    await fetch("/api/queue/clear", { method: "POST" });
                    loadQueue();
                    renderList();
                    showToast("Fila limpa com sucesso!");
                } catch (e) {}
            }
        }

        function renderQueueList() {
            const container = document.getElementById("queueList");
            if (!container) return;
            container.innerHTML = "";
            if (pendingQueue.length === 0) {
                container.innerHTML = '<div style="color: var(--text-dim); text-align: center; padding: 25px;">Sua fila está vazia. Adicione músicas para tocar!</div>';
                return;
            }

            const currentVideoId = nowPlayingTrack ? nowPlayingTrack.video_id : null;
            const upcomingTrack = getUpcomingTrack();
            const upcomingVideoId = upcomingTrack ? upcomingTrack.video_id : null;

            // Checagem de faixas existentes na biblioteca
            const libVideoIds = new Set();
            CATEGORIES.forEach(cat => {
                (DATA[cat] || []).forEach(t => { if (t.video_id) libVideoIds.add(t.video_id); });
            });

            pendingQueue.forEach((item, idx) => {
                const inLibrary = item.in_library || libVideoIds.has(item.video_id);
                const meta = getTrackTransitionCardMeta(item, currentVideoId, upcomingVideoId, (!isTransitioning && (item.video_id === lastAddedVideoId || item.addedJustNow)));

                let cardClasses = "track-card" + meta.cardExtraClass;
                let statusBadgeHtml = meta.statusBadgeHtml;

                const bpm = item.bpm || detectBpmJs(item.title, item.category);
                const bpmBadgeHtml = `<span class="badge-bpm-chip">⚡ ${bpm} BPM</span>`;
                const catBadgeHtml = item.category ? `<span class="badge-bpm-chip" style="background: rgba(0,242,254,0.1); border-color: rgba(0,242,254,0.3); color: var(--accent);">🏷️ ${item.category}</span>` : "";

                const card = document.createElement("div");
                card.id = `queueCard_${item.video_id}`;
                card.className = cardClasses;
                card.setAttribute("data-video-id", item.video_id);
                if (meta.transitionRole) card.setAttribute("data-transition-role", meta.transitionRole);
                card.innerHTML = `
                    <div class="track-meta" onclick="playQueueTrack(${idx})">
                        <div class="track-card-title">
                            <span>${idx + 1}. ${escapeHtml(item.title)}</span>
                        </div>
                        <div class="track-card-subrow">
                            ${statusBadgeHtml}
                            <span class="track-card-artist" title="${escapeHtml(item.artist || item.category || '')}">${escapeHtml(item.artist || item.category || '')}</span>
                            ${bpmBadgeHtml}
                            ${catBadgeHtml}
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn-similar-card" onclick="findSimilarToQueueTrack(${idx})" title="Buscar músicas semelhantes no mesmo ritmo e BPM com IA">
                            📻 Parecidas
                        </button>
                        ${inLibrary 
                            ? `<button class="btn-add-playlist in-library" style="background: rgba(0, 230, 118, 0.15); border-color: rgba(0, 230, 118, 0.4); color: #00e676;" title="Esta música já está salva na sua biblioteca">❤️ Na Playlist</button>`
                            : `<button class="btn-add-playlist" onclick="addQueueTrackToPlaylist(${idx})" title="Salvar permanentemente na sua Playlist/Biblioteca">⭐ Favoritar</button>`
                        }
                        <button class="btn-add-queue" onclick="removeFromQueue('${item.video_id}')" title="Remover da fila">Remover</button>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        let currentActiveSuggestions = [];

        // Renderiza lista de sugestões com badges ao vivo (TOCANDO AGORA, A SEGUIR, ADICIONADA AGORA) e todas as ferramentas
        function renderSuggestionsList(tracks) {
            currentActiveSuggestions = tracks || [];
            const container = document.getElementById("suggestionsList");
            if (!container) return;
            container.innerHTML = "";
            if (!tracks || tracks.length === 0) {
                container.innerHTML = `
                    <div style="color: var(--text-dim); text-align: center; padding: 40px 20px;">
                        <div style="font-size: 28px; margin-bottom: 8px;">✨</div>
                        <div style="font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 6px;">Nenhuma sugestão carregada no momento para este gênero.</div>
                        <div style="font-size: 12px; margin-bottom: 14px;">Clique no botão abaixo para buscar músicas inéditas em tempo real no YouTube!</div>
                        <button class="btn-sync-yt" onclick="fetchFreshSuggestionsForCurrentGenre()" style="margin: 0 auto; display: inline-flex; background: linear-gradient(135deg, #00f2fe, #4facfe); color: #000; font-weight: 700; font-size: 12px; padding: 8px 16px;">
                            🔄 Buscar Novidades com IA Agora
                        </button>
                    </div>
                `;
                return;
            }

            const currentVideoId = nowPlayingTrack ? nowPlayingTrack.video_id : null;
            const upcomingTrack = getUpcomingTrack();
            const upcomingVideoId = upcomingTrack ? upcomingTrack.video_id : null;
            const queuedIds = new Set(pendingQueue.map(t => t.video_id));

            tracks.forEach((item, idx) => {
                const isQueued = queuedIds.has(item.video_id);
                const meta = getTrackTransitionCardMeta(item, currentVideoId, upcomingVideoId, (!isTransitioning && (item.video_id === lastAddedVideoId || item.addedJustNow)));

                let cardClasses = "track-card" + meta.cardExtraClass;
                let statusBadgeHtml = meta.statusBadgeHtml;

                const bpm = item.bpm || detectBpmJs(item.title, item.category);
                const bpmBadgeHtml = `<span class="badge-bpm-chip">⚡ ${bpm} BPM</span>`;
                const catBadgeHtml = item.category ? `<span class="badge-bpm-chip" style="background: rgba(0,242,254,0.1); border-color: rgba(0,242,254,0.3); color: var(--accent);">🏷️ ${item.category}</span>` : "";

                let idealBadgeHtml = "";
                if (nowPlayingTrack && item.video_id !== nowPlayingTrack.video_id) {
                    const score = calculateIdealNextTrackScore(item, nowPlayingTrack);
                    if (score >= 93) {
                        idealBadgeHtml = `<span class="badge-ideal-track match-perfect" title="Harmonia e BPM ideais para mixagem">🎯 ${score}% Match</span>`;
                        cardClasses += " ideal-match-highlight";
                    } else if (score >= 86) {
                        idealBadgeHtml = `<span class="badge-ideal-track match-great" title="Excelente sincronia de mix">⚡ ${score}% Mix</span>`;
                    }
                }

                const card = document.createElement("div");
                card.id = `suggCard_${item.video_id}`;
                card.className = cardClasses;
                card.setAttribute("data-video-id", item.video_id);
                if (meta.transitionRole) card.setAttribute("data-transition-role", meta.transitionRole);
                card.innerHTML = `
                    <div class="track-meta" onclick="playSuggestionTrack(${idx})">
                        <div class="track-card-title">
                            <span>${idx + 1}. ${escapeHtml(item.title)}</span>
                        </div>
                        <div class="track-card-subrow">
                            ${statusBadgeHtml}
                            ${idealBadgeHtml}
                            <span class="track-card-artist" title="${escapeHtml(item.artist || item.category || '')}">${escapeHtml(item.artist || item.category || '')}</span>
                            ${bpmBadgeHtml}
                            ${catBadgeHtml}
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn-similar-card" onclick="findSimilarToSuggestionTrack(${idx})" title="Buscar músicas semelhantes no mesmo ritmo e BPM com IA">
                            📻 Parecidas
                        </button>
                        <button class="btn-add-playlist" onclick="addSuggestionTrackToPlaylist(${idx})" title="Salvar permanentemente na sua Playlist/Biblioteca">
                            ⭐ + Playlist
                        </button>
                        ${(() => {
                            const qIdx = pendingQueue.findIndex(q => q.video_id === item.video_id);
                            if (qIdx !== -1) {
                                return `<button class="btn-add-queue added" onclick="removeFromQueue('${item.video_id}')" title="Clique para remover da fila (#${qIdx + 1})">✓ Fila #${qIdx + 1}${qIdx === 0 ? " (Próxima)" : ""}</button>`;
                            } else {
                                return `<button class="btn-add-queue" onclick="addSuggestionTrackToQueue(${idx})">+ Fila</button>`;
                            }
                        })()}
                    </div>
                `;
                container.appendChild(card);
            });
        }

        
        // ==========================================================
        // MÓDULO DE PESQUISA LIVRE (BIBLIOTECA COMPLETA + YOUTUBE IA)
        // ==========================================================
        let lastFreeSearchQuery = "";
        let freeSearchDebounceTimer = null;
        let freeSearchResults = {
            library_tracks: [],
            youtube_tracks: [],
            tracks: []
        };
        let freeSearchFilter = "all"; // "all", "library", "new"
        let isSearchingFree = false;

        function goToFreeSearch(initialQuery) {
            switchView("search");
            const input = document.getElementById("freeSearchInput");
            if (input) {
                input.value = initialQuery || "";
                executeFreeSearch(initialQuery);
            }
        }

        function handleFreeSearchInput(query) {
            const btnClear = document.getElementById("btnFreeSearchClear");
            if (btnClear) btnClear.style.display = query ? "block" : "none";
            if (!query.trim()) {
                clearFreeSearch();
                return;
            }
            if (freeSearchDebounceTimer) clearTimeout(freeSearchDebounceTimer);
            freeSearchDebounceTimer = setTimeout(() => {
                executeFreeSearch(query);
            }, 300);
        }

        function clearFreeSearch() {
            const input = document.getElementById("freeSearchInput");
            const btnClear = document.getElementById("btnFreeSearchClear");
            if (input) input.value = "";
            if (btnClear) btnClear.style.display = "none";
            freeSearchResults = { library_tracks: [], youtube_tracks: [], tracks: [] };
            updateSearchFilterCounters();
            renderSearchResults();
        }

        function updateSearchFilterCounters() {
            if (!freeSearchResults) return;
            const cntAll = document.getElementById("countSearchAll");
            const cntLib = document.getElementById("countSearchLib");
            const cntNew = document.getElementById("countSearchNew");
            if (cntAll && freeSearchResults.tracks) cntAll.textContent = freeSearchResults.tracks.length;
            if (cntLib && freeSearchResults.library_tracks) cntLib.textContent = freeSearchResults.library_tracks.length;
            if (cntNew && freeSearchResults.youtube_tracks) cntNew.textContent = freeSearchResults.youtube_tracks.length;
        }

        function quickBpmSearch(bpmOrStyle) {
            const input = document.getElementById("freeSearchInput");
            if (input) input.value = bpmOrStyle;
            executeFreeSearch(bpmOrStyle);
        }

        function setSearchFilter(filterType) {
            freeSearchFilter = filterType;
            const tabAll = document.getElementById("tabFilterAll");
            const tabLib = document.getElementById("tabFilterLib");
            const tabNew = document.getElementById("tabFilterNew");

            if (tabAll) tabAll.className = `filter-tab-btn ${filterType === "all" ? "active" : ""}`;
            if (tabLib) tabLib.className = `filter-tab-btn ${filterType === "library" ? "active" : ""}`;
            if (tabNew) tabNew.className = `filter-tab-btn ${filterType === "new" ? "active" : ""}`;

            renderSearchResults();
        }

        let freeSearchRequestId = 0;

        async function executeFreeSearch(query) {
            if (freeSearchDebounceTimer) clearTimeout(freeSearchDebounceTimer);
            query = (query || "").trim();
            if (!query) return;
            lastFreeSearchQuery = query;

            const thisReqId = ++freeSearchRequestId;
            isSearchingFree = true;
            const container = document.getElementById("searchResultsList");
            if (container) {
                container.innerHTML = `
                    <div class="search-empty-state">
                        <div class="search-empty-icon" style="animation: pulseDot 1s infinite;">🔍</div>
                        <div class="search-empty-title">Pesquisando "${query}"...</div>
                        <div class="search-empty-desc">Procurando na biblioteca e minerando novidades no YouTube com IA...</div>
                    </div>
                `;
            }

            try {
                const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                if (thisReqId !== freeSearchRequestId) return; // descarta se outra busca mais recente foi disparada
                freeSearchResults = data;
                isSearchingFree = false;

                // Atualiza contadores dos filtros
                updateSearchFilterCounters();

                renderSearchResults();
            } catch (err) {
                if (thisReqId !== freeSearchRequestId) return;
                console.error("Erro na busca livre:", err);
                isSearchingFree = false;
                if (container) {
                    container.innerHTML = `
                        <div class="search-empty-state">
                            <div class="search-empty-icon" style="color: #ff5555;">⚠️</div>
                            <div class="search-empty-title">Erro ao buscar músicas</div>
                            <div class="search-empty-desc">Verifique a conexão com o servidor local e tente novamente.</div>
                        </div>
                    `;
                }
            }
        }

        
        function findSimilarToSearchTrack(idx) {
            let displayTracks = (freeSearchFilter === "library") ? freeSearchResults.library_tracks :
                                (freeSearchFilter === "new") ? freeSearchResults.youtube_tracks : freeSearchResults.tracks;
            if (displayTracks && displayTracks[idx]) {
                findSimilarToTrack(displayTracks[idx]);
            }
        }

        function addSearchTrackToPlaylist(idx) {
            let displayTracks = (freeSearchFilter === "library") ? freeSearchResults.library_tracks :
                                (freeSearchFilter === "new") ? freeSearchResults.youtube_tracks : freeSearchResults.tracks;
            if (displayTracks && displayTracks[idx]) {
                const item = displayTracks[idx];
                const cardEl = document.getElementById("searchCard_" + item.video_id);
                addTrackToPlaylist(item, cardEl);
            }
        }

        function addSearchTrackToQueue(idx) {
            let displayTracks = (freeSearchFilter === "library") ? freeSearchResults.library_tracks :
                                (freeSearchFilter === "new") ? freeSearchResults.youtube_tracks : freeSearchResults.tracks;
            if (displayTracks && displayTracks[idx]) {
                addToQueue(displayTracks[idx]);
            }
        }

        function findSimilarToSuggestionTrack(idx) {
            if (currentActiveSuggestions && currentActiveSuggestions[idx]) {
                findSimilarToTrack(currentActiveSuggestions[idx]);
            }
        }

        function addSuggestionTrackToPlaylist(idx) {
            if (currentActiveSuggestions && currentActiveSuggestions[idx]) {
                const item = currentActiveSuggestions[idx];
                const cardEl = document.getElementById("suggCard_" + item.video_id);
                addTrackToPlaylist(item, cardEl);
            }
        }

        function addSuggestionTrackToQueue(idx) {
            if (currentActiveSuggestions && currentActiveSuggestions[idx]) {
                addToQueue(currentActiveSuggestions[idx]);
            }
        }

        function findSimilarToQueueTrack(idx) {
            if (pendingQueue && pendingQueue[idx]) {
                findSimilarToTrack(pendingQueue[idx]);
            }
        }

        function addQueueTrackToPlaylist(idx) {
            if (pendingQueue && pendingQueue[idx]) {
                const item = pendingQueue[idx];
                const cardEl = document.getElementById("queueCard_" + item.video_id);
                addTrackToPlaylist(item, cardEl);
            }
        }

        function findSimilarToLibraryTrack(cat, idx) {
            const list = currentFilteredLibraryTracks !== null ? currentFilteredLibraryTracks : (DATA[cat] || []);
            if (list && list[idx]) {
                findSimilarToTrack(list[idx]);
            }
        }

        function addLibraryTrackToQueue(cat, idx) {
            const list = currentFilteredLibraryTracks !== null ? currentFilteredLibraryTracks : (DATA[cat] || []);
            if (list && list[idx]) {
                addToQueue(list[idx]);
            }
        }

        function renderSearchResults() {
            const container = document.getElementById("searchResultsList");
            if (!container) return;
            if (isSearchingFree) return;

            let displayTracks = [];
            if (freeSearchFilter === "library") {
                displayTracks = freeSearchResults.library_tracks || [];
            } else if (freeSearchFilter === "new") {
                displayTracks = freeSearchResults.youtube_tracks || [];
            } else {
                displayTracks = freeSearchResults.tracks || [];
            }

            if (displayTracks.length === 0) {
                const hasSearched = (document.getElementById("freeSearchInput") && document.getElementById("freeSearchInput").value);
                container.innerHTML = `
                    <div class="search-empty-state">
                        <div class="search-empty-icon">${hasSearched ? "🔎" : "🔍"}</div>
                        <div class="search-empty-title">${hasSearched ? "Nenhuma música encontrada" : "Pesquisa Livre & Descobertas"}</div>
                        <div class="search-empty-desc">${hasSearched ? "Tente buscar por outro termo, nome de DJ, ritmo ou BPM." : "Digite qualquer música, ritmo ou BPM acima para buscar com IA e ouvir com Crossfade!"}</div>
                    </div>
                `;
                return;
            }

            container.innerHTML = "";
            const currentVideoId = nowPlayingTrack ? nowPlayingTrack.video_id : null;
            const upcomingTrack = getUpcomingTrack();
            const upcomingVideoId = upcomingTrack ? upcomingTrack.video_id : null;
            const queuedIds = new Set(pendingQueue.map(t => t.video_id));

            // Checagem de faixas existentes na biblioteca
            const libVideoIds = new Set();
            CATEGORIES.forEach(cat => {
                (DATA[cat] || []).forEach(t => { if (t.video_id) libVideoIds.add(t.video_id); });
            });

            displayTracks.forEach((item, idx) => {
                const isQueued = queuedIds.has(item.video_id);
                const inLibrary = item.in_library || libVideoIds.has(item.video_id);
                const meta = getTrackTransitionCardMeta(item, currentVideoId, upcomingVideoId, (!isTransitioning && (item.video_id === lastAddedVideoId || item.addedJustNow)));

                let cardClasses = "track-card" + meta.cardExtraClass;
                let statusBadgeHtml = meta.statusBadgeHtml;

                const bpm = item.bpm || detectBpmJs(item.title, item.category);
                const bpmBadgeHtml = `<span class="badge-bpm-chip">⚡ ${bpm} BPM</span>`;
                const catBadgeHtml = item.category ? `<span class="badge-bpm-chip" style="background: rgba(0,242,254,0.1); border-color: rgba(0,242,254,0.3); color: var(--accent);">🏷️ ${item.category}</span>` : "";
                const sourceBadge = inLibrary 
                    ? `<span class="badge-source" style="background: rgba(0, 230, 118, 0.15); color: #00e676; border: 1px solid rgba(0, 230, 118, 0.3);">✓ Na Biblioteca</span>`
                    : `<span class="badge-source" style="background: rgba(0, 242, 254, 0.15); color: var(--accent);">✨ YouTube Novidade</span>`;

                let idealBadgeHtml = "";
                if (nowPlayingTrack && item.video_id !== nowPlayingTrack.video_id) {
                    const score = calculateIdealNextTrackScore(item, nowPlayingTrack);
                    if (score >= 93) {
                        idealBadgeHtml = `<span class="badge-ideal-track match-perfect" title="Harmonia e BPM ideais para mixagem">🎯 ${score}% Match</span>`;
                        cardClasses += " ideal-match-highlight";
                    } else if (score >= 86) {
                        idealBadgeHtml = `<span class="badge-ideal-track match-great" title="Excelente sincronia de mix">⚡ ${score}% Mix</span>`;
                    }
                }

                const card = document.createElement("div");
                card.id = `searchCard_${item.video_id}`;
                card.className = cardClasses;
                card.setAttribute("data-video-id", item.video_id);
                if (meta.transitionRole) card.setAttribute("data-transition-role", meta.transitionRole);
                card.innerHTML = `
                    <div class="track-meta" onclick="playSearchTrack(${idx})">
                        <div class="track-card-title">
                            <span>${idx + 1}. ${escapeHtml(item.title)}</span>
                        </div>
                        <div class="track-card-subrow">
                            ${statusBadgeHtml}
                            ${idealBadgeHtml}
                            <span class="track-card-artist" title="${escapeHtml(item.artist || item.category || '')}">${escapeHtml(item.artist || item.category || '')}</span>
                            ${bpmBadgeHtml}
                            ${catBadgeHtml}
                            ${sourceBadge}
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn-similar-card" onclick="findSimilarToSearchTrack(${idx})" title="Buscar músicas semelhantes no mesmo ritmo e BPM com IA">
                            📻 Parecidas
                        </button>
                        ${inLibrary 
                            ? `<button class="btn-add-playlist" style="background: rgba(0, 230, 118, 0.15); border-color: rgba(0, 230, 118, 0.4); color: #00e676;" title="Esta música já está salva na sua biblioteca">❤️ Na Playlist</button>`
                            : `<button class="btn-add-playlist" onclick="addSearchTrackToPlaylist(${idx})" title="Salvar permanentemente na sua Playlist/Biblioteca">⭐ Favoritar</button>`
                        }
                        ${(() => {
                            const qIdx = pendingQueue.findIndex(q => q.video_id === item.video_id);
                            if (qIdx !== -1) {
                                return `<button class="btn-add-queue added" onclick="removeFromQueue('${item.video_id}')" title="Clique para remover da fila (#${qIdx + 1})">✓ Fila #${qIdx + 1}${qIdx === 0 ? " (Próxima)" : ""}</button>`;
                            } else {
                                return `<button class="btn-add-queue" onclick="addSearchTrackToQueue(${idx})">+ Fila</button>`;
                            }
                        })()}
                    </div>
                `;
                container.appendChild(card);
            });
        }

        // ==========================================================
        // ATUALIZAÇÃO SINCRONIZADA DE TODAS AS TELAS ATIVAS
        // ==========================================================
        function renderAllActiveLists() {
            renderList();
            if (browseView === "spotify") {
                renderSpotifyPlaylist();
            }
            if (browseView === "suggestions" && currentActiveSuggestions.length > 0) {
                renderSuggestionsList(currentActiveSuggestions);
            }
            if (browseView === "search") {
                renderSearchResults();
            }
            if (browseView === "queue") {
                loadQueue();
            }
            updateUpcomingTrackUI();
            updateDjMixerUI();
        }

        // ==========================================================
        // EFEITO RIPPLE E PULSO AO CLICAR EM QUALQUER ELEMENTO/BOTÃO
        // ==========================================================
        document.addEventListener("click", function(e) {
            const target = e.target.closest("button, .btn-action, .bar-btn, .bar-pill-btn, .btn-dj-mix, .btn-radio-now, .vlc-chip-btn, .nav-btn, .category-tab, .floating-sync-btn, .chip-bpm, .filter-tab-btn");
            if (!target) return;

            const rect = target.getBoundingClientRect();
            const ripple = document.createElement("span");
            ripple.className = "click-ripple-effect";
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
            ripple.style.top = `${e.clientY - rect.top - size / 2}px`;

            const prevPos = window.getComputedStyle(target).position;
            if (prevPos === "static") target.style.position = "relative";
            target.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 450);
        }, true);


        // YouTube IFrame API Callback
        function onYouTubeIframeAPIReady() {
            const initialId = nowPlayingTrack ? nowPlayingTrack.video_id : "u3IErhAXL3w";
            const secondId = (nowPlayingQueue.length > 1) ? nowPlayingQueue[1].video_id : initialId;
            const startSec = getTrackIntroSkip(nowPlayingTrack);

            playerA = new YT.Player("deckA", {
                height: "100%",
                width: "100%",
                videoId: initialId,
                playerVars: {
                    "autoplay": 0,
                    "start": Math.round(startSec),
                    "rel": 0,
                    "modestbranding": 1,
                    "enablejsapi": 1
                },
                events: {
                    "onReady": (e) => {
                        isPlayerAReady = true;
                        updateVolumeUI();
                        updateSettingsUI();
                        if (nowPlayingTrack) {
                            updateTrackInfoUI(nowPlayingTrack);
                        }
                        loadQueue();
                    },
                    "onStateChange": (e) => onDeckStateChange(e, "A"),
                    "onError": (e) => onDeckError(e, "A")
                }
            });

            playerB = new YT.Player("deckB", {
                height: "100%",
                width: "100%",
                videoId: secondId,
                playerVars: {
                    "autoplay": 0,
                    "start": Math.round(startSec),
                    "rel": 0,
                    "modestbranding": 1,
                    "enablejsapi": 1
                },
                events: {
                    "onReady": (e) => {
                        isPlayerBReady = true;
                        try {
                            playerB.pauseVideo();
                            playerB.setVolume(0);
                        } catch (err) {}
                    },
                    "onStateChange": (e) => onDeckStateChange(e, "B"),
                    "onError": (e) => onDeckError(e, "B")
                }
            });
        }

        function onDeckStateChange(event, deckName) {
            if (engineMode !== "video") return;
            if (deckName === activeDeck && !isTransitioning) {
                if (event.data === YT.PlayerState.PLAYING) {
                    updatePlayPauseButtons(true);
                    hideToast();
                } else if (event.data === YT.PlayerState.PAUSED) {
                    updatePlayPauseButtons(false);
                } else if (event.data === YT.PlayerState.ENDED) {
                    if (isAutoPlayEnabled && !hasFadedCurrentTrack) {
                        hasFadedCurrentTrack = true;
                        autoAdvanceWithFade();
                    }
                }
            }
        }

        // Tratamento de restrição de gravadora no YouTube:
        // NÃO PULA A MÚSICA! Em vez de pular, ativa o Áudio HD automaticamente sem interrupção!
        function onDeckError(event, deckName) {
            if (deckName !== activeDeck) return;
            const code = event ? event.data : null;
            console.warn("YouTube Player event error code:", code);
            
            if (code === 100 || code === 2) {
                showToast("⚠️ Vídeo não disponível no YouTube. Avançando para a próxima música...");
                setTimeout(() => {
                    autoAdvanceWithFade();
                }, 1200);
            } else if (code === 150 || code === 101 || code === 5) {
                showToast("⚠️ Vídeo bloqueado por direitos autorais. Avançando para a próxima música...");
                setTimeout(() => {
                    autoAdvanceWithFade();
                }, 1200);
            }
        }

        // ==========================================================
        // FILTROS DE GÊNEROS PARA AS PLAYLISTS SPOTIFY (111 PLAYLISTS)
        // ==========================================================
        let currentSpotifyGenreFilter = "all";

        function filterSpotifyPlaylistsByGenre(genreKey) {
            currentSpotifyGenreFilter = genreKey;
            document.querySelectorAll("#spotifyGenreFilterRow .sp-genre-chip").forEach(chip => {
                chip.classList.toggle("active", chip.id === `spChip_${genreKey}`);
            });

            if (!window.SPOTIFY_PLAYLISTS) return;

            const filterMap = {
                all: () => true,
                top: (id, p) => /top|hits|brasil|viral|tiktok|radar|semana|360|globais/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),
                sertanejo: (id, p) => /sertanejo|modao|sofrencia|churrasco|potencia|fazenda|bruto|vaquejada|piseiro|pisadinha|arrocha/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),
                funk: (id, p) => /funk|mandelao|ritmada|favela|fluxo|cria|150/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),
                rap: (id, p) => /rap|trap|drill|hip|poesia|rimas|flow/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),
                pagode: (id, p) => /pagode|samba|resenha|churrasquinho|tardezinha|parcas/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),
                eletronica: (id, p) => /eletronica|bass|desande|house|edm|club|vintage|alok/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),
                latino: (id, p) => /reggaeton|latino|cachengue|rkt|perreo|dembow|fuego/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),
                cumbia: (id, p) => /cumbia|villera|santafesina|chicha|sonidera|cuarteto|palmeras|damas|pibes|mattioli|gilda|fuego|marama|rombai|konga|luck/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "") + " " + (p.meta?.desc || "")),
                fronteira: (id, p) => /quarai|artigas|fronteira|miriam britos|sonido profesional|chacho ramos|mano lima|baitaca|joca martins|marenco|lucas sugo|valdez|charanga|gaucho/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "") + " " + (p.meta?.desc || "")),
                rock: (id, p) => /rock|pop|mpb|flashback|violao|axe|tchan|micareta/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || "")),
                treino: (id, p) => /treino|academia|sunset|pool|estrada|sitio|almoco|relax|lofi|chill|sextou|pre_balada|automotivo|carro|paredao/i.test(id + " " + (p.meta?.name || "") + " " + (p.meta?.genre || ""))
            };

            const testFn = filterMap[genreKey] || filterMap.all;
            let firstVisibleId = null;

            Object.keys(SPOTIFY_PLAYLISTS).forEach(plId => {
                const btn = document.getElementById(`spTab_${plId}`);
                const matches = testFn(plId, SPOTIFY_PLAYLISTS[plId]);
                if (btn) {
                    btn.style.display = matches ? "inline-flex" : "none";
                    if (matches && !firstVisibleId) firstVisibleId = plId;
                }
            });

            // Se a playlist atualmente ativa ficou escondida pelo filtro, seleciona a primeira visível
            const currentTab = document.getElementById(`spTab_${activeSpotifyPlaylist}`);
            if (currentTab && currentTab.style.display === "none" && firstVisibleId) {
                selectSpotifyPlaylist(firstVisibleId);
            }
        }

        // ==========================================================
        // MOTOR DE SINCRONIZAÇÃO DE BPM & BEATMATCH (MODAL & DJ ENGINE)
        // ==========================================================
        let isAutoBeatmatchEnabled = true;
        let currentPitchAdjustment = 0; // %

        function openBpmModal() {
            const modal = document.getElementById("bpmSyncModal");
            if (!modal) return;

            const curTrack = nowPlayingTrack || (DATA["Mega Funk & Ritmadas"] ? DATA["Mega Funk & Ritmadas"][0] : null);
            const nextTrack = getUpcomingTrack() || (DATA["Mega Funk & Ritmadas"] ? DATA["Mega Funk & Ritmadas"][1] : null);

            const curBpm = curTrack ? (curTrack.bpm || 130) : 130;
            const nextBpm = nextTrack ? (nextTrack.bpm || 130) : 130;

            const tCurrentTitle = document.getElementById("bpmCurrentTrackTitle");
            const tCurrentArtist = document.getElementById("bpmCurrentTrackArtist");
            const tCurrentVal = document.getElementById("bpmCurrentVal");

            const tNextTitle = document.getElementById("bpmNextTrackTitle");
            const tNextArtist = document.getElementById("bpmNextTrackArtist");
            const tNextVal = document.getElementById("bpmNextVal");

            const diffBadge = document.getElementById("bpmDiffBadge");
            const compatLabel = document.getElementById("bpmCompatLabel");
            const checkSync = document.getElementById("autoBpmSyncCheck");

            if (tCurrentTitle) tCurrentTitle.textContent = curTrack ? curTrack.title : "Nenhuma faixa ativa";
            if (tCurrentArtist) tCurrentArtist.textContent = curTrack ? (curTrack.artist || curTrack.category || "") : "-";
            if (tCurrentVal) tCurrentVal.textContent = `${curBpm} BPM`;

            if (tNextTitle) tNextTitle.textContent = nextTrack ? nextTrack.title : "Nenhuma próxima definida";
            if (tNextArtist) tNextArtist.textContent = nextTrack ? (nextTrack.artist || nextTrack.category || "") : "-";
            if (tNextVal) tNextVal.textContent = `${nextBpm} BPM`;

            const diff = nextBpm - curBpm;
            const diffPct = curBpm > 0 ? ((diff / curBpm) * 100).toFixed(1) : "0.0";

            if (diffBadge) {
                diffBadge.textContent = `${diff >= 0 ? "+" : ""}${diff} BPM (${diffPct}%)`;
                if (Math.abs(parseFloat(diffPct)) <= 6) {
                    diffBadge.style.background = "rgba(0, 230, 118, 0.15)";
                    diffBadge.style.borderColor = "rgba(0, 230, 118, 0.4)";
                    diffBadge.style.color = "#00e676";
                } else if (Math.abs(parseFloat(diffPct)) <= 12) {
                    diffBadge.style.background = "rgba(255, 170, 0, 0.15)";
                    diffBadge.style.borderColor = "rgba(255, 170, 0, 0.4)";
                    diffBadge.style.color = "#ffaa00";
                } else {
                    diffBadge.style.background = "rgba(255, 0, 85, 0.15)";
                    diffBadge.style.borderColor = "rgba(255, 0, 85, 0.4)";
                    diffBadge.style.color = "#ff0055";
                }
            }

            if (compatLabel) {
                if (Math.abs(parseFloat(diffPct)) <= 6) {
                    compatLabel.textContent = "🟢 Compatibilidade Perfeita (Mixagem 100% Harmônica)";
                    compatLabel.style.color = "#00e676";
                } else if (Math.abs(parseFloat(diffPct)) <= 12) {
                    compatLabel.textContent = "🟡 Boa Compatibilidade (Ajuste Suave no Crossfade)";
                    compatLabel.style.color = "#ffaa00";
                } else {
                    compatLabel.textContent = "🔴 Variação de Ritmo Maior (Keylock Automático Ativo)";
                    compatLabel.style.color = "#ff7777";
                }
            }

            if (checkSync) checkSync.checked = isAutoBeatmatchEnabled;
            updateBpmPitchUI();

            modal.style.display = "flex";
        }

        function closeBpmModal(event) {
            if (event && event.target && event.target !== event.currentTarget) return;
            const modal = document.getElementById("bpmSyncModal");
            if (modal) modal.style.display = "none";
        }

        function toggleAutoBpmSync(checked) {
            isAutoBeatmatchEnabled = checked;
            const barBtn = document.getElementById("barBpmSyncBtn");
            const statusBadge = document.getElementById("bpmSyncStatusBadge");
            if (barBtn) barBtn.classList.toggle("bpm-sync-active", isAutoBeatmatchEnabled);
            if (statusBadge) {
                statusBadge.textContent = isAutoBeatmatchEnabled ? "Auto Sync Ativo" : "Auto Sync Desativado";
                statusBadge.style.color = isAutoBeatmatchEnabled ? "var(--accent)" : "var(--text-dim)";
            }
            showToast(isAutoBeatmatchEnabled ? "⚡ Beatmatch Automático ATIVADO no Crossfade" : "Beatmatch Automático desativado");
        }

        function handleBpmPitchSlider(val) {
            currentPitchAdjustment = parseFloat(val) || 0;
            updateBpmPitchUI();
            applyPitchAdjustmentToAudio();
        }

        function setBpmPitchPreset(pct) {
            currentPitchAdjustment = pct;
            const slider = document.getElementById("bpmPitchSlider");
            if (slider) slider.value = pct;
            updateBpmPitchUI();
            applyPitchAdjustmentToAudio();
        }

        function updateBpmPitchUI() {
            const readout = document.getElementById("bpmPitchReadout");
            if (readout) {
                readout.textContent = `${currentPitchAdjustment >= 0 ? "+" : ""}${currentPitchAdjustment.toFixed(1)}% (${currentPitchAdjustment === 0 ? "Original" : "Pitch Ajustado"})`;
            }
            document.querySelectorAll(".btn-bpm-preset").forEach(btn => {
                if (btn.classList.contains("match")) return;
                const txt = btn.textContent;
                const matchVal = (currentPitchAdjustment === 0 && txt.includes("0%")) ||
                                 (currentPitchAdjustment === -5 && txt.includes("-5%")) ||
                                 (currentPitchAdjustment === -2 && txt.includes("-2%")) ||
                                 (currentPitchAdjustment === 2 && txt.includes("+2%")) ||
                                 (currentPitchAdjustment === 5 && txt.includes("+5%"));
                btn.classList.toggle("active", matchVal);
            });
        }

        function quickMatchBpm() {
            const curTrack = nowPlayingTrack;
            const nextTrack = getUpcomingTrack();
            if (!curTrack || !nextTrack) {
                showToast("⚡ Selecione uma faixa tocando para sincronizar!");
                return;
            }
            const curBpm = curTrack.bpm || 130;
            const nextBpm = nextTrack.bpm || 130;
            if (nextBpm === 0) return;
            const neededPct = ((curBpm - nextBpm) / nextBpm) * 100;
            const clamped = Math.max(-15, Math.min(15, neededPct));
            setBpmPitchPreset(parseFloat(clamped.toFixed(1)));
            showToast(`⚡ Próxima faixa sincronizada para ${curBpm} BPM!`);
        }

        function applyPitchAdjustmentToAudio() {
            const rate = currentPlaybackSpeed * (1.0 + (currentPitchAdjustment / 100));
            const clampedRate = Math.max(0.5, Math.min(2.0, rate));
            if (engineMode === "audio") {
                const curAudio = getActiveAudioDeck();
                if (curAudio) {
                    curAudio.preservesPitch = true;
                    curAudio.playbackRate = clampedRate;
                }
            } else {
                const p = getActivePlayer();
                if (p && typeof p.setPlaybackRate === "function") {
                    try { p.setPlaybackRate(clampedRate); } catch (e) {}
                }
            }
            updateLiveBpmPanel();
        }

        let liveBpmRampTimer = null;

        function updateLiveBpmPanel(overrideOriginalBpm = null, overrideCurrentBpm = null, overridePct = null, isRamping = false) {
            const curTrack = nowPlayingTrack;
            const origBpm = overrideOriginalBpm !== null ? overrideOriginalBpm : (curTrack && curTrack.bpm ? curTrack.bpm : 128);
            
            const effRate = currentPlaybackSpeed * (1.0 + (currentPitchAdjustment / 100));
            const currBpm = overrideCurrentBpm !== null ? overrideCurrentBpm : Math.round(origBpm * effRate);
            const diffPct = overridePct !== null ? overridePct : ((effRate - 1.0) * 100);

            const elPanel = document.getElementById("bpmLiveSyncPanel");
            const elOrig = document.getElementById("bpmLiveOriginalVal");
            const elCurr = document.getElementById("bpmLiveCurrentVal");
            const elDiff = document.getElementById("bpmLiveDiffChip");
            const elStatus = document.getElementById("bpmLiveStatusPill");
            const elArrowWrap = document.getElementById("bpmLiveArrowWrap");

            if (elOrig) elOrig.textContent = `${origBpm} BPM`;
            if (elCurr) elCurr.textContent = `${currBpm} BPM`;
            if (elDiff) {
                elDiff.textContent = `${effRate.toFixed(2)}x (${diffPct >= 0 ? "+" : ""}${diffPct.toFixed(1)}%)`;
            }

            const isShifted = Math.abs(diffPct) >= 0.8;

            if (elPanel) {
                elPanel.classList.toggle("is-pitch-shifted", isShifted && !isRamping);
                elPanel.classList.toggle("is-ramping", isRamping);
            }
            if (elCurr) {
                elCurr.classList.toggle("shifted", isShifted && !isRamping);
                elCurr.classList.toggle("ramping", isRamping);
            }
            if (elDiff) {
                elDiff.classList.toggle("shifted", isShifted && !isRamping);
                elDiff.classList.toggle("ramping", isRamping);
            }
            if (elArrowWrap) {
                elArrowWrap.classList.toggle("active", isShifted || isRamping);
            }
            if (elStatus) {
                elStatus.classList.toggle("shifted", isShifted && !isRamping);
                elStatus.classList.toggle("ramping", isRamping);
                if (isRamping) {
                    elStatus.textContent = "🔄 Fade Gradual";
                } else if (isShifted) {
                    elStatus.textContent = `⚡ Sincronizado (${diffPct >= 0 ? "+" : ""}${diffPct.toFixed(1)}%)`;
                } else {
                    elStatus.textContent = "Original (1.0x)";
                }
            }
        }

        function rampBpmToOriginal(targetAudio, startRate, endRate, originalBpm, durationMs = 4000) {
            if (!targetAudio) return;
            if (liveBpmRampTimer) {
                clearInterval(liveBpmRampTimer);
                liveBpmRampTimer = null;
            }

            const progressWrap = document.getElementById("bpmFadeProgressWrap");
            const progressBar = document.getElementById("bpmFadeProgressBar");
            const liveNum = document.getElementById("bpmFadeLiveNum");
            const caption = document.getElementById("bpmFadeCaption");

            if (progressWrap) progressWrap.style.display = "flex";
            if (progressBar) progressBar.style.width = "100%";
            if (caption) caption.textContent = "Restaurando BPM original em tempo real...";

            const stepInterval = 80;
            const totalSteps = Math.max(1, Math.round(durationMs / stepInterval));
            let step = 0;

            const startBpm = Math.round(originalBpm * startRate);
            if (liveNum) liveNum.textContent = `${startBpm} ➔ ${originalBpm} BPM`;

            updateLiveBpmPanel(originalBpm, startBpm, ((startRate - 1.0) * 100), true);

            liveBpmRampTimer = setInterval(() => {
                step++;
                const frac = step / totalSteps;
                // Curva de desaceleração suave (easeOutSin)
                const ease = Math.sin((frac * Math.PI) / 2);
                const curRate = startRate + (endRate - startRate) * ease;

                if (targetAudio) {
                    targetAudio.preservesPitch = true;
                    targetAudio.playbackRate = curRate;
                }

                const curBpm = Math.round(originalBpm * curRate);
                const curPct = (curRate - 1.0) * 100;
                const remainingPct = Math.max(0, 100 - (frac * 100));

                if (progressBar) progressBar.style.width = `${remainingPct}%`;
                if (liveNum) liveNum.textContent = `${curBpm} ➔ ${originalBpm} BPM`;

                // Atualiza o painel visual no player EM TEMPO REAL!
                updateLiveBpmPanel(originalBpm, curBpm, curPct, true);

                if (step >= totalSteps) {
                    clearInterval(liveBpmRampTimer);
                    liveBpmRampTimer = null;

                    if (targetAudio) {
                        targetAudio.preservesPitch = true;
                        targetAudio.playbackRate = endRate;
                    }
                    currentPitchAdjustment = 0;
                    const slider = document.getElementById("bpmPitchSlider");
                    if (slider) slider.value = 0;
                    updateBpmPitchUI();

                    if (progressBar) progressBar.style.width = "0%";
                    if (caption) caption.textContent = "✓ Ritmo original 100% restaurado!";

                    setTimeout(() => {
                        if (!liveBpmRampTimer && progressWrap) {
                            progressWrap.style.display = "none";
                        }
                        updateLiveBpmPanel();
                    }, 600);
                }
            }, stepInterval);
        }

        // ==========================================================
        // SISTEMA DE MODOS DJ INTELIGENTES (MATCH PERFEITO, PEAK TIME, SMART, SMOOTH)
        // ==========================================================
        let djPlayMode = "match"; // 'match', 'energy', 'shuffle', 'smooth'
        let currentLockedGenre = "Mega Funk & Ritmadas";

        function toggleDjActDropdown() {
            const menu = document.getElementById("djActDropdownMenu");
            const trigger = document.getElementById("btnDjActTrigger");
            if (!menu) return;
            const isShown = menu.style.display === "flex" || menu.style.display === "block";
            if (isShown) {
                menu.style.display = "none";
                return;
            }

            // Cálculo dinâmico de direção (Dropup inteligente se o espaço inferior for apertado)
            if (trigger) {
                const rect = trigger.getBoundingClientRect();
                const spaceBelow = window.innerHeight - rect.bottom - 75; // Reserva 75px da barra inferior
                const spaceAbove = rect.top - 60; // Reserva 60px do topo

                if (spaceBelow < 265 && spaceAbove > spaceBelow) {
                    // Abre para CIMA (Dropup)
                    menu.style.top = "auto";
                    menu.style.bottom = "calc(100% + 4px)";
                    menu.style.maxHeight = Math.min(320, spaceAbove - 10) + "px";
                } else {
                    // Abre para BAIXO (Dropdown)
                    menu.style.top = "calc(100% + 4px)";
                    menu.style.bottom = "auto";
                    menu.style.maxHeight = Math.min(280, spaceBelow - 10) + "px";
                }
            }

            menu.style.display = "flex";
        }

        // Fechar dropdown de Modo de Atuação ao clicar fora
        document.addEventListener("click", function(e) {
            const menu = document.getElementById("djActDropdownMenu");
            const trigger = document.getElementById("btnDjActTrigger");
            if (menu && (menu.style.display === "flex" || menu.style.display === "block")) {
                if (trigger && !trigger.contains(e.target) && !menu.contains(e.target)) {
                    menu.style.display = "none";
                }
            }
        });

        function selectDjActMode(mode) {
            setDjMode(mode);
            const menu = document.getElementById("djActDropdownMenu");
            if (menu) menu.style.display = "none";
        }

        function setDjMode(mode) {
            djPlayMode = mode;
            const shortLabels = {
                match: "🎯 Match Perfeito",
                energy: "⚡ Peak Time",
                shuffle: "🔀 Smart Shuffle",
                smooth: "🌊 Smooth Flow",
                club: "🔥 Balada & Club DJ",
                studio: "🎛️ Estúdio Pro & Mastering",
                drop: "⚡ Drop Hunter (Corte no Drop)"
            };
            const activeLabel = document.getElementById("djActModeActiveLabel");
            if (activeLabel) activeLabel.textContent = shortLabels[mode] || mode;

            // Atualiza o Badge de Confirmação do Modo Balada
            const clubBadge = document.getElementById("djClubActiveBadge");
            if (clubBadge) {
                clubBadge.style.display = (mode === "club") ? "flex" : "none";
            }
            // Atualiza o Badge de Confirmação do Modo Estúdio
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
                    const vc = document.getElementById("videoContainer");
                    if (vc) vc.classList.add("has-drop-hud");
                    if (typeof startDropHunterAnalyzer === "function") startDropHunterAnalyzer();
                } else {
                    dropHud.classList.remove("hud-visible");
                    dropHud.style.display = "none";
                    const vc = document.getElementById("videoContainer");
                    if (vc) vc.classList.remove("has-drop-hud");
                    if (typeof stopDropHunterAnalyzer === "function") stopDropHunterAnalyzer();
                }
            }
            if (mode !== "club") {
                hideDjClubHud();
            }
            if (mode === "studio") {
                initWebAudio();
                if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
                if (typeof selectStudioPreset === "function") selectStudioPreset("mastering");
                showToast("🎛️ MODO ESTÚDIO PRO ATIVO: Console de Mastering, Reverb & Compressor Habilitados");
            }

            document.querySelectorAll(".dj-act-menu-opt").forEach(opt => {
                opt.classList.remove("active");
            });
            const selOpt = document.getElementById(`actOpt_${mode}`);
            if (selOpt) selOpt.classList.add("active");

            const modeBtns = {
                match: document.getElementById("btnModeMatch"),
                energy: document.getElementById("btnModeEnergy"),
                shuffle: document.getElementById("btnModeShuffle"),
                smooth: document.getElementById("btnModeSmooth"),
                club: document.getElementById("btnModeClub")
            };
            Object.keys(modeBtns).forEach(k => {
                if (modeBtns[k]) modeBtns[k].classList.toggle("active", k === mode);
            });

            const modeLabels = {
                match: "🎯 Match Perfeito (Harmonia máxima, BPM ideal e descoberta inteligente)",
                energy: "⚡ Peak Time (Acelera BPM e eleva a energia da pista)",
                shuffle: "🔀 Smart Shuffle (Aleatório harmônico no mesmo gênero)",
                smooth: "🌊 Smooth Flow (Crossfade longo de 8s e transições ultra suaves)",
                club: "🔥 Balada & Club DJ (Drops explosivos, Bass Swap e FX sincronizados)"
            };

            // Ajusta o tempo de crossfade conforme o modo de atuação
            if (mode === "smooth") {
                crossfadeDuration = 8;
                crossfadeSeconds = 8;
            } else if (mode === "match") {
                crossfadeDuration = 6;
                crossfadeSeconds = 6;
            } else if (mode === "energy") {
                crossfadeDuration = 4;
                crossfadeSeconds = 4;
            } else if (mode === "club") {
                crossfadeDuration = 5;
                crossfadeSeconds = 5;
            } else {
                crossfadeDuration = 4;
                crossfadeSeconds = 4;
            }
            updateSettingsUI();

            // RECALCULA IMEDIATAMENTE A PRÓXIMA FAIXA CONFORME O MODO SELECIONADO!
            djModeNextTrack = null;
            const nextTrack = calculateDjModeNextTrack();

            // Atualiza Decks, Barra Inferior, Badges e Listas
            updateUpcomingTrackUI();
            updateTurntablesState();
            if (nowPlayingTrack) updateDjIdealHelper(nowPlayingTrack);
            renderAllActiveLists();

            if (nextTrack) {
                showToast(`Modo ${shortLabels[mode]}: Próxima faixa selecionada (${nextTrack.title.slice(0, 28)}...)`);
            } else {
                showToast(`Modo DJ: ${shortLabels[mode]}`);
            }
        }

        function setLockedGenre(genreName) {
            if (!genreName) return;
            currentLockedGenre = genreName;
            updateGenreLockUI();
        }

        function updateGenreLockUI() {
            const textEl = document.getElementById("djGenreLockText");
            if (textEl) {
                textEl.textContent = `Gênero Bloqueado: ${currentLockedGenre} (Seguindo lista)`;
            }
        }

        // ==========================================================
        // HISTÓRICO DE REPRODUÇÃO & SALVAR MÚSICAS DESCOBERTAS
        // ==========================================================
        let playbackHistory = [];

        async function recordTrackInHistory(track) {
            if (!track || !track.video_id) return;
            recordTrackInRecentHistory(track.video_id);
            try {
                const payload = {
                    track: {
                        video_id: track.video_id,
                        title: track.title,
                        artist: track.artist || "",
                        category: track.category || currentLockedGenre || "Geral",
                        bpm: track.bpm || 128,
                        played_at: new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
                        mode: djPlayMode,
                        source: activePlaybackSource || "Biblioteca"
                    }
                };
                const res = await fetch("/api/history/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                updateHistoryBadge(data.count || (playbackHistory.length + 1));
            } catch (e) {
                console.warn("Aviso ao registrar histórico:", e);
            }
        }

        function updateHistoryBadge(count) {
            const badge = document.getElementById("historyBadgeCount");
            if (badge) badge.textContent = count || 0;
            const modalBadge = document.getElementById("modalHistoryBadgeCount");
            if (modalBadge) modalBadge.textContent = `${count || 0} faixas`;
        }

        async function loadPlaybackHistory() {
            try {
                const res = await fetch("/api/history");
                const data = await res.json();
                playbackHistory = data.history || [];
                updateHistoryBadge(playbackHistory.length);
                return playbackHistory;
            } catch (e) {
                return [];
            }
        }

        async function openHistoryModal() {
            const modal = document.getElementById("historyModal");
            if (!modal) return;
            const curCount = (playbackHistory && playbackHistory.length) || 0;
            updateHistoryBadge(curCount);
            modal.style.display = "flex";
            modal.classList.add("open");
            await renderHistoryModal();
        }

        function closeHistoryModal(e) {
            if (e && e.target && e.target !== e.currentTarget && !e.target.classList.contains("eq-modal-overlay")) return;
            const modal = document.getElementById("historyModal");
            if (modal) {
                modal.style.display = "none";
                modal.classList.remove("open");
            }
        }

        window.openHistoryModal = openHistoryModal;
        window.closeHistoryModal = closeHistoryModal;
        window.saveHistoryTrackToLibrary = saveHistoryTrackToLibrary;
        window.saveHistoryTrackByIndex = saveHistoryTrackByIndex;
        window.playHistoryTrackByIndex = playHistoryTrackByIndex;
        window.clearPlaybackHistory = clearPlaybackHistory;
        window.setDjMode = setDjMode;
        window.toggleDjActDropdown = toggleDjActDropdown;
        window.selectDjActMode = selectDjActMode;
        window.toggleRepeatMode = toggleRepeatMode;
        window.updateRepeatButtonUI = updateRepeatButtonUI;

        // Fecha o dropdown do Modo de Atuação do DJ ao clicar fora
        document.addEventListener("click", (e) => {
            const box = document.getElementById("djActModeBox");
            const menu = document.getElementById("djActDropdownMenu");
            if (box && menu && !box.contains(e.target)) {
                menu.style.display = "none";
            }
        });

        function isTrackInLibrary(videoId) {
            if (!videoId || !window.DATA) return false;
            for (const cat of CATEGORIES) {
                if (DATA[cat] && DATA[cat].some(t => t.video_id === videoId)) return true;
            }
            return false;
        }

        async function renderHistoryModal() {
            const container = document.getElementById("historyModalItems");
            if (!container) return;
            container.innerHTML = `<div style="text-align: center; padding: 20px; color: var(--text-dim);">Carregando histórico...</div>`;

            const history = await loadPlaybackHistory();
            if (!history || history.length === 0) {
                container.innerHTML = `<div style="text-align: center; padding: 30px; color: var(--text-dim);">Nenhuma música tocada no histórico recente ainda.<br><span style="font-size: 11px;">Músicas tocadas nos modos DJ e sugestões aparecerão aqui para você salvar na biblioteca.</span></div>`;
                return;
            }

            let html = "";
            const totalHist = (history && history.length) || 0;
            updateHistoryBadge(totalHist);

            history.forEach((track, idx) => {
                const inLib = isTrackInLibrary(track.video_id);
                const bpmVal = track.bpm || 128;
                const timeVal = track.played_at || "";
                const modeBadge = track.mode === "match" ? "🎯 Match" :
                                  track.mode === "energy" ? "⚡ Peak Time" :
                                  track.mode === "shuffle" ? "🔀 Smart" : "🌊 Smooth";

                html += `
                    <div class="history-track-card" id="historyCard_${track.video_id}">
                        <div class="history-card-left">
                            <div class="history-thumb-box">
                                <img src="https://i.ytimg.com/vi/${track.video_id}/mqdefault.jpg" class="history-thumb" alt="Capa" onerror="this.src=window.DEFAULT_COVER_SVG">
                            </div>
                            <div class="history-info">
                                <div class="history-title" title="${escapeQuotes(track.title)}">${escapeQuotes(track.title)}</div>
                                <div class="history-sub">
                                    <span class="history-artist-text">${escapeQuotes(track.artist || track.category || "DJ Set")}</span>
                                    <span class="badge-bpm-chip">⚡ ${bpmVal} BPM</span>
                                    <span class="history-mode-chip">${modeBadge}</span>
                                    ${timeVal ? `<span class="history-time">${timeVal}</span>` : ""}
                                </div>
                            </div>
                        </div>
                        <div class="history-actions" id="histActions_${track.video_id}">
                            <button class="btn-history-play" onclick="playHistoryTrackByIndex(${idx})" title="Tocar esta faixa agora">▶</button>
                            ${inLib ? `
                                <div style="display: flex; gap: 5px; align-items: center;">
                                    <span class="history-saved-badge" title="Esta música já está na sua biblioteca">✓ Na Biblioteca</span>
                                    <button class="btn-move-card" onclick="openMovePlaylistModalByVideoId('${track.video_id}', '${escapeQuotes(track.title)}')" title="Mover para outra playlist">📂 Mover</button>
                                    <button class="btn-remove-lib-card" onclick="openConfirmRemoveModal(null, null, '${track.video_id}')" title="Remover da biblioteca">🗑️</button>
                                </div>
                            ` : `
                                <button class="btn-history-save" id="btnSaveHist_${track.video_id}" onclick="saveHistoryTrackByIndex(${idx})" title="Salvar permanentemente na sua Biblioteca">
                                    ⭐ Salvar na Biblioteca
                                </button>
                            `}
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function playHistoryTrackByIndex(idx) {
            const track = playbackHistory && playbackHistory[idx];
            if (!track || !track.video_id) return;
            playCustomTrack(track.video_id, track.title, track.artist || "", track.category || "", "Histórico", track.bpm || 128);
        }

        async function saveHistoryTrackByIndex(idx) {
            const track = playbackHistory && playbackHistory[idx];
            if (!track || !track.video_id) return;
            return saveHistoryTrackToLibrary(track.video_id, track.title, track.artist || "", track.category || "", track.bpm || 128);
        }

        async function saveHistoryTrackToLibrary(videoId, title, artist, category, bpm) {
            const btn = document.getElementById(`btnSaveHist_${videoId}`);
            if (btn) {
                btn.disabled = true;
                btn.textContent = "Salvando...";
            }
            try {
                let cat = category;
                if (!cat || cat === "Personalizada" || !CATEGORIES.includes(cat)) {
                    cat = mapTrackToLibraryCategory({ title, artist, category }, currentLockedGenre || "Reggaeton, Cachengue & Latino");
                }
                const res = await fetch("/api/library/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        video_id: videoId,
                        title: title,
                        artist: artist,
                        category: cat,
                        source: "Histórico DJ (Salva)",
                        bpm: bpm || 128
                    })
                });
                const data = await res.json();
                if (data.status === "ok" || data.success) {
                    if (!DATA[cat]) DATA[cat] = [];
                    if (!DATA[cat].some(t => t.video_id === videoId)) {
                        DATA[cat].unshift({
                            video_id: videoId,
                            title: title,
                            artist: artist,
                            category: cat,
                            source: "Histórico DJ (Salva)",
                            bpm: bpm || 128,
                            addedJustNow: true
                        });
                    }
                    lastAddedVideoId = videoId;
                    localStorage.setItem("pref_last_added_id", lastAddedVideoId);

                    updateLibraryCounters();
                    renderList();
                    renderAllActiveLists();

                    showToast(`⭐ "${title.slice(0, 32)}..." salva na sua biblioteca! Acesse na aba "${cat}".`, 5000);
                    const actionsBox = document.getElementById(`histActions_${videoId}`);
                    if (actionsBox) {
                        actionsBox.innerHTML = `
                            <button class="btn-history-play" onclick="playHistoryTrackByIndex(0)" title="Tocar esta faixa agora">▶</button>
                            <div style="display: flex; gap: 5px; align-items: center;">
                                <span class="history-saved-badge" title="Esta música já está na sua biblioteca">✓ Na Biblioteca</span>
                                <button class="btn-move-card" onclick="openMovePlaylistModalByVideoId('${videoId}', '${escapeQuotes(title)}')" title="Mover para outra playlist">📂 Mover</button>
                                <button class="btn-remove-lib-card" onclick="openConfirmRemoveModal(null, null, '${videoId}')" title="Remover da biblioteca">🗑️</button>
                            </div>
                        `;
                    } else if (btn) {
                        btn.outerHTML = `<span class="history-saved-badge">✓ Na Biblioteca</span>`;
                    }
                } else {
                    showToast("Erro ao salvar música na biblioteca.");
                    if (btn) {
                        btn.disabled = false;
                        btn.textContent = "⭐ Salvar na Biblioteca";
                    }
                }
            } catch (e) {
                showToast("Erro de rede ao salvar faixa.");
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = "⭐ Salvar na Biblioteca";
                }
            }
        }

        async function clearPlaybackHistory() {
            if (!confirm("Deseja realmente limpar todo o histórico recente de reprodução?")) return;
            try {
                await fetch("/api/history/clear", { method: "POST" });
                playbackHistory = [];
                updateHistoryBadge(0);
                renderHistoryModal();
                showToast("Histórico limpo!");
            } catch (e) {
                showToast("Erro ao limpar histórico.");
            }
        }

        // Atalho de teclado Escape para fechar qualquer modal aberto
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                closeEqualizerModal();
                closeStemsModal();
                closeSpotifyQueueModal();
                closeBpmModal();
                closeHistoryModal();
            }
        });

        // Inicialização de UI
        initTabs();
        initSpotifyTabs();
        setupTabsAutoScroll("tabsWrapper", "tabsScrollLeft", "tabsScrollRight");
        setupTabsAutoScroll("spotifyTabsWrapper", "spotifyTabsScrollLeft", "spotifyTabsScrollRight");
        setupTabsAutoScroll("suggestionsTabsWrapper", "suggScrollLeft", "suggScrollRight");
        setupListVerticalAutoScroll("trackList");
        setupListVerticalAutoScroll("spotifyTrackList");
        setupListVerticalAutoScroll("suggestionsList");
        setupListVerticalAutoScroll("queueList");
        selectCategoryToBrowse("Mega Funk & Ritmadas");
        updateVolumeUI();
        updateSettingsUI();
        loadPlaybackHistory();
        setDjMode(djPlayMode);
        updateGenreLockUI();

        // Configuração inicial do modo de engine (SEM AUTOPLAY INICIAL)
        setEngineMode(engineMode, false);
        if (!nowPlayingTrack && window.DATA) {
            const firstCat = CATEGORIES.find(c => DATA[c] && DATA[c].length > 0) || "Mega Funk & Ritmadas";
            if (DATA[firstCat] && DATA[firstCat][0]) {
                nowPlayingTrack = DATA[firstCat][0];
                activePlaybackSource = "Biblioteca";
                nowPlayingCategoryName = firstCat;
                nowPlayingQueue = DATA[firstCat];
                nowPlayingIndex = 0;
                currentLockedGenre = firstCat;
            }
        }
        if (nowPlayingTrack) {
            setDjMode(djPlayMode);
            updateTrackInfoUI(nowPlayingTrack);
            updateTurntablesState();
            renderAllActiveLists();
        }
        updateSpotifyNavBadge();

        // Desbloqueia Web Audio no primeiro clique do usuário em qualquer lugar da tela
        document.addEventListener("click", () => {
            initWebAudio();
            if (audioCtx && audioCtx.state === "suspended") {
                audioCtx.resume();
            }
        }, { once: true });

        // Exportações globais para inspeção e testes
        window.applyStemPreset = applyStemPreset;
        window.applyStemsToDsp = applyStemsToDsp;
        try {
            Object.defineProperty(window, 'crossfadeSeconds', { get: () => crossfadeSeconds, set: v => { crossfadeSeconds = v; }, configurable: true });
            Object.defineProperty(window, 'isTransitioning', { get: () => isTransitioning, set: v => isTransitioning = v, configurable: true });
            Object.defineProperty(window, 'crossfadeTimer', { get: () => crossfadeTimer, set: v => crossfadeTimer = v, configurable: true });
            Object.defineProperty(window, 'nowPlayingTrack', { get: () => nowPlayingTrack, set: v => nowPlayingTrack = v, configurable: true });
            Object.defineProperty(window, 'activeDeck', { get: () => activeDeck, set: v => activeDeck = v, configurable: true });
        } catch(e) {}
        window.applyTransitionCrossover = applyTransitionCrossover;
        window.triggerCrossfade = triggerCrossfade;
        window.manualTransition = manualTransition;
        window.getTrackIntroSkip = getTrackIntroSkip;
        window.recordTrackSilence = recordTrackSilence;
        window.toggleIntroSkip = toggleIntroSkip;
        window.openStemsModal = openStemsModal;
        window.closeStemsModal = closeStemsModal;
        window.initWebAudio = initWebAudio;
        window.detectGenreFx = detectGenreFx;
        window.playDjClubFx = playDjClubFx;
        window.synth808SubDrop = synth808SubDrop;
        window.synthHpfNoiseSweep = synthHpfNoiseSweep;
        window.synthDubEcho = synthDubEcho;
        window.showDjClubHud = showDjClubHud;
        window.updateDjClubHud = updateDjClubHud;
        window.hideDjClubHud = hideDjClubHud;
        window.DJ_GENRE_EFFECTS_CATALOG = DJ_GENRE_EFFECTS_CATALOG;
        window.djFxRotationIndex = djFxRotationIndex;

window.selectEqPreset = selectEqPreset;
window.onCustomEqChange = onCustomEqChange;
window.resetEqToFlat = resetEqToFlat;
window.setEqPreAmp = setEqPreAmp;
window.drawEqCurve = drawEqCurve;
window.openEqualizerModal = openEqualizerModal;
window.closeEqualizerModal = closeEqualizerModal;
window.updatePlayPauseButtons = updatePlayPauseButtons;
window.EQ_PRESETS = EQ_PRESETS;

window.initWebAudio = initWebAudio;
try {
    Object.defineProperty(window, 'audioCtx', {
        get: function() { return audioCtx; },
        set: function(val) { audioCtx = val; },
        configurable: true
    });
} catch(e) {
    window.audioCtx = audioCtx;
}
window.getDjFxDestination = getDjFxDestination;
window.updateDjFxVolume = updateDjFxVolume;
window.triggerMusicDucking = triggerMusicDucking;
window.testDjFx = function(type) {
    if (!audioCtx) initWebAudio();
    if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
    updateDjFxVolume();
    if (isMuted || masterVolume === 0) return;
    playDjClubFx({ type: type || "airhorn" }, 130, 4000, null, null);
};


// ==========================================================================
// SUÍTE DE ESTÚDIO PROFISSIONAL & MASTERING DSP CONSOLE [EXTENDED] (PRO AUDIO)
// ==========================================================================
let studioDspInitialized = false;
let studioBypass = false;
let studioMonoCheck = false;
let studioVuTimer = null;

let studioSettings = {
    preset: "mastering",
    // Módulo 1: Reverb
    reverbType: "hall",
    reverbPreDelay: 0.02,
    reverbDecay: 1.8,
    reverbMix: 22,
    // Módulo 2: Delay
    delayPreset: "1/4",
    delayTime: 0.24,
    delayHiCut: 3500,
    delayFeedback: 28,
    delayMix: 18,
    // Módulo 3: Compressor SSL Bus
    compThreshold: -14,
    compRatio: 4.0,
    compAttack: 0.005,
    compRelease: 0.15,
    compSidechainHpf: 80,
    // Módulo 4: Calor Valvulado & 3D Wide
    warmthColor: "tube",
    warmthDrive: 30,
    stereoWidth: 135,
    // Módulo 5: Aural Exciter & Air Band
    airFreq: 12000,
    airBoost: 4.0,
    airSparkle: 35,
    // Módulo 6: Sub-Bass 808 Pultec
    subFreq: 60,
    subBoost: 4.5,
    subRumbleCut: 30,
    // Módulo 7: De-Esser
    deEsserFreq: 6500,
    deEsserAmount: 30,
    // Módulo 8: Maximizer & Limiter
    maximizerDrive: 3.0,
    limiterCeiling: -0.1
};

const STUDIO_PRESETS = {
    mastering: {
        name: "Neve Warmth",
        reverbType: "hall", reverbPreDelay: 0.02, reverbDecay: 1.8, reverbMix: 20,
        delayPreset: "1/4", delayTime: 0.24, delayHiCut: 3500, delayFeedback: 25, delayMix: 14,
        compThreshold: -14, compRatio: 3.5, compAttack: 0.008, compRelease: 0.15, compSidechainHpf: 80,
        warmthColor: "tube", warmthDrive: 30, stereoWidth: 130,
        airFreq: 12000, airBoost: 3.5, airSparkle: 30,
        subFreq: 60, subBoost: 3.5, subRumbleCut: 30,
        deEsserFreq: 6500, deEsserAmount: 25,
        maximizerDrive: 2.5, limiterCeiling: -0.1
    },
    hall: {
        name: "Concert Arena",
        reverbType: "cathedral", reverbPreDelay: 0.035, reverbDecay: 3.2, reverbMix: 42,
        delayPreset: "1/4", delayTime: 0.24, delayHiCut: 4500, delayFeedback: 38, delayMix: 25,
        compThreshold: -12, compRatio: 2.5, compAttack: 0.012, compRelease: 0.22, compSidechainHpf: 0,
        warmthColor: "tube", warmthDrive: 20, stereoWidth: 165,
        airFreq: 10000, airBoost: 4.0, airSparkle: 25,
        subFreq: 60, subBoost: 2.0, subRumbleCut: 25,
        deEsserFreq: 6500, deEsserAmount: 20,
        maximizerDrive: 2.0, limiterCeiling: -0.1
    },
    club: {
        name: "SSL Club Master",
        reverbType: "club", reverbPreDelay: 0.01, reverbDecay: 1.2, reverbMix: 15,
        delayPreset: "1/8", delayTime: 0.12, delayHiCut: 3000, delayFeedback: 22, delayMix: 14,
        compThreshold: -18, compRatio: 5.0, compAttack: 0.003, compRelease: 0.09, compSidechainHpf: 140,
        warmthColor: "germanium", warmthDrive: 45, stereoWidth: 140,
        airFreq: 12000, airBoost: 5.0, airSparkle: 45,
        subFreq: 60, subBoost: 6.5, subRumbleCut: 30,
        deEsserFreq: 6500, deEsserAmount: 35,
        maximizerDrive: 4.5, limiterCeiling: -0.1
    },
    vocal: {
        name: "Vocal Clarity & Air",
        reverbType: "plate", reverbPreDelay: 0.025, reverbDecay: 1.6, reverbMix: 28,
        delayPreset: "1/4", delayTime: 0.24, delayHiCut: 4000, delayFeedback: 22, delayMix: 18,
        compThreshold: -15, compRatio: 3.0, compAttack: 0.005, compRelease: 0.18, compSidechainHpf: 140,
        warmthColor: "tube", warmthDrive: 25, stereoWidth: 115,
        airFreq: 12000, airBoost: 6.5, airSparkle: 55,
        subFreq: 80, subBoost: 1.5, subRumbleCut: 35,
        deEsserFreq: 6500, deEsserAmount: 60,
        maximizerDrive: 3.0, limiterCeiling: -0.1
    },
    lofi: {
        name: "Lo-Fi Tape",
        reverbType: "room", reverbPreDelay: 0.03, reverbDecay: 1.0, reverbMix: 22,
        delayPreset: "1/8d", delayTime: 0.18, delayHiCut: 2200, delayFeedback: 45, delayMix: 28,
        compThreshold: -16, compRatio: 4.0, compAttack: 0.002, compRelease: 0.12, compSidechainHpf: 0,
        warmthColor: "tape", warmthDrive: 70, stereoWidth: 85,
        airFreq: 8000, airBoost: 0.0, airSparkle: 10,
        subFreq: 80, subBoost: 3.0, subRumbleCut: 0,
        deEsserFreq: 5500, deEsserAmount: 40,
        maximizerDrive: 1.5, limiterCeiling: -0.5
    },
    subpunch: {
        name: "Sub-Bass 808",
        reverbType: "club", reverbPreDelay: 0.01, reverbDecay: 0.8, reverbMix: 10,
        delayPreset: "1/8", delayTime: 0.12, delayHiCut: 2800, delayFeedback: 15, delayMix: 10,
        compThreshold: -16, compRatio: 4.5, compAttack: 0.004, compRelease: 0.08, compSidechainHpf: 140,
        warmthColor: "germanium", warmthDrive: 40, stereoWidth: 130,
        airFreq: 12000, airBoost: 3.0, airSparkle: 30,
        subFreq: 45, subBoost: 8.5, subRumbleCut: 25,
        deEsserFreq: 6500, deEsserAmount: 25,
        maximizerDrive: 5.0, limiterCeiling: -0.1
    },
    crystal: {
        name: "Modern Pop/EDM",
        reverbType: "hall", reverbPreDelay: 0.02, reverbDecay: 2.0, reverbMix: 24,
        delayPreset: "1/4", delayTime: 0.24, delayHiCut: 5000, delayFeedback: 30, delayMix: 18,
        compThreshold: -16, compRatio: 4.0, compAttack: 0.004, compRelease: 0.12, compSidechainHpf: 80,
        warmthColor: "tube", warmthDrive: 30, stereoWidth: 155,
        airFreq: 16000, airBoost: 7.5, airSparkle: 60,
        subFreq: 60, subBoost: 5.0, subRumbleCut: 30,
        deEsserFreq: 7500, deEsserAmount: 45,
        maximizerDrive: 4.0, limiterCeiling: -0.1
    },
    loudness: {
        name: "Loudness War (+6dB)",
        reverbType: "room", reverbPreDelay: 0.01, reverbDecay: 0.9, reverbMix: 12,
        delayPreset: "1/8", delayTime: 0.12, delayHiCut: 3500, delayFeedback: 18, delayMix: 10,
        compThreshold: -20, compRatio: 6.0, compAttack: 0.002, compRelease: 0.08, compSidechainHpf: 140,
        warmthColor: "tape", warmthDrive: 35, stereoWidth: 120,
        airFreq: 12000, airBoost: 4.0, airSparkle: 35,
        subFreq: 60, subBoost: 4.0, subRumbleCut: 30,
        deEsserFreq: 6500, deEsserAmount: 40,
        maximizerDrive: 6.5, limiterCeiling: -0.1
    },
    acoustic: {
        name: "Acoustic Live",
        reverbType: "room", reverbPreDelay: 0.02, reverbDecay: 1.4, reverbMix: 22,
        delayPreset: "1/4", delayTime: 0.24, delayHiCut: 3800, delayFeedback: 15, delayMix: 12,
        compThreshold: -10, compRatio: 2.0, compAttack: 0.015, compRelease: 0.22, compSidechainHpf: 80,
        warmthColor: "tube", warmthDrive: 15, stereoWidth: 110,
        airFreq: 10000, airBoost: 2.5, airSparkle: 20,
        subFreq: 80, subBoost: 1.5, subRumbleCut: 25,
        deEsserFreq: 6500, deEsserAmount: 20,
        maximizerDrive: 1.5, limiterCeiling: -0.5
    },
    flat: {
        name: "Flat Reference",
        reverbType: "hall", reverbPreDelay: 0.0, reverbDecay: 1.0, reverbMix: 0,
        delayPreset: "1/4", delayTime: 0.24, delayHiCut: 4000, delayFeedback: 0, delayMix: 0,
        compThreshold: 0, compRatio: 1.5, compAttack: 0.01, compRelease: 0.2, compSidechainHpf: 0,
        warmthColor: "tube", warmthDrive: 0, stereoWidth: 100,
        airFreq: 12000, airBoost: 0, airSparkle: 0,
        subFreq: 60, subBoost: 0, subRumbleCut: 0,
        deEsserFreq: 6500, deEsserAmount: 0,
        maximizerDrive: 0, limiterCeiling: -0.1
    }
};

// Nós de Áudio da Console de Estúdio
let studioInputNode = null;
let studioDryGainNode = null;
let studioWetGainNode = null;
let studioMasterMixerNode = null;
let studioMonoGainL = null;
let studioMonoGainR = null;
let studioMonoMerger = null;

// Reverb & Delay
let studioReverbPreDelayNode = null;
let studioReverbNode = null;
let studioReverbWetNode = null;
let studioDelayNode = null;
let studioDelayHiCutFilter = null;
let studioDelayFeedbackNode = null;
let studioDelayWetNode = null;

// Racks de Processamento Dinâmico e Harmônico
let studioRumbleFilter = null;
let studioBassBoostFilter = null;
let studioDeEsserFilter = null;
let studioAirFilter = null;
let studioWarmthNode = null;
let studioCompNode = null;
let studioSplitterNode = null;
let studioMergerNode = null;
let studioDelayLeft = null;
let studioDelayRight = null;
let studioMaximizerGain = null;
let studioLimiterNode = null;

// Analisadores e Visualizadores
let studioAnalyserL = null;
let studioAnalyserR = null;
let studioSpectrumAnalyser = null;

// Gerador de Curvas de Saturação Analógica Avançadas
function makeStudioWarmthCurve(driveAmount, colorType = "tube") {
    const n_samples = 44100;
    const curve = new Float32Array(n_samples);
    const drive = driveAmount / 100;
    if (drive === 0) {
        for (let i = 0; i < n_samples; ++i) curve[i] = (i * 2) / n_samples - 1;
        return curve;
    }

    if (colorType === "tape") {
        // Saturação arredondada de fita magnética com compressão natural
        const k = drive * 3.5;
        for (let i = 0; i < n_samples; ++i) {
            const x = (i * 2) / n_samples - 1;
            curve[i] = Math.tanh(x * (1 + k)) / (Math.tanh(1 + k) || 1);
        }
    } else if (colorType === "germanium") {
        // Transistor germânio com harmônicos pares e corte assimétrico
        const k = drive * 4.0;
        for (let i = 0; i < n_samples; ++i) {
            const x = (i * 2) / n_samples - 1;
            if (x >= 0) {
                curve[i] = (Math.PI / 2) * Math.atan(x * (1 + k)) / 1.5;
            } else {
                curve[i] = x / (1 + Math.abs(x * k * 0.5));
            }
        }
    } else {
        // Válvula 6L6 clássica suave (Tube Warmth)
        const k = drive * 2.8;
        const deg = Math.PI / 180;
        for (let i = 0; i < n_samples; ++i) {
            const x = (i * 2) / n_samples - 1;
            curve[i] = ((3 + k) * x * 20 * deg) / (Math.PI + k * Math.abs(x));
        }
    }
    return curve;
}

// Gerador procedural de Resposta de Impulso para múltiplos ambientes de sala
function createStudioImpulseBuffer(ctx, duration = 2.2, decay = 2.5, type = "hall") {
    if (!ctx) return null;
    try {
        const rate = ctx.sampleRate;
        const length = Math.max(1, Math.round(rate * Math.max(0.2, duration)));
        const impulse = ctx.createBuffer(2, length, rate);
        const left = impulse.getChannelData(0);
        const right = impulse.getChannelData(1);

        for (let i = 0; i < length; i++) {
            const t = i / length;
            let env = Math.exp(-t * decay);

            if (type === "cathedral") {
                // Cauda longa e densa com reflexões ricas
                env *= 1.0 + 0.15 * Math.sin(t * 40);
            } else if (type === "spring") {
                // Ressonância metálica saltitante
                env *= 0.8 + 0.3 * Math.sin(t * 120 * Math.PI);
            } else if (type === "plate") {
                // Difusão brilhante rápida
                env = Math.pow(1 - t, decay * 0.7);
            }

            left[i] = (Math.random() * 2 - 1) * env;
            right[i] = (Math.random() * 2 - 1) * env;
        }
        return impulse;
    } catch (e) {
        return null;
    }
}

function initStudioDsp() {
    if (studioDspInitialized || !audioCtx) return;
    try {
        studioInputNode = audioCtx.createGain();
        studioDryGainNode = audioCtx.createGain();
        studioWetGainNode = audioCtx.createGain();
        studioMasterMixerNode = audioCtx.createGain();

        // Matriz de Mono Check
        studioMonoGainL = audioCtx.createGain();
        studioMonoGainR = audioCtx.createGain();
        studioMonoMerger = audioCtx.createChannelMerger(2);

        // 1. MÓDULO SUB-BASS & RUMBLE FILTER (PULTEC)
        studioRumbleFilter = audioCtx.createBiquadFilter();
        studioRumbleFilter.type = "highpass";
        studioRumbleFilter.frequency.value = studioSettings.subRumbleCut || 30;

        studioBassBoostFilter = audioCtx.createBiquadFilter();
        studioBassBoostFilter.type = "lowshelf";
        studioBassBoostFilter.frequency.value = studioSettings.subFreq || 60;
        studioBassBoostFilter.gain.value = studioSettings.subBoost || 4.5;

        // 2. MÓDULO DE-ESSER (DYNAMIC NOTCH)
        studioDeEsserFilter = audioCtx.createBiquadFilter();
        studioDeEsserFilter.type = "peaking";
        studioDeEsserFilter.frequency.value = studioSettings.deEsserFreq || 6500;
        studioDeEsserFilter.Q.value = 2.5;
        const deEssGainDb = -((studioSettings.deEsserAmount || 0) / 100) * 8.0;
        studioDeEsserFilter.gain.value = deEssGainDb;

        // 3. MÓDULO AURAL EXCITER & AIR BAND 12kHz+
        studioAirFilter = audioCtx.createBiquadFilter();
        studioAirFilter.type = "highshelf";
        studioAirFilter.frequency.value = studioSettings.airFreq || 12000;
        studioAirFilter.gain.value = studioSettings.airBoost || 4.0;

        // 4. MÓDULO CALOR ANALÓGICO VALVULADO (WAVESHAPER)
        studioWarmthNode = audioCtx.createWaveShaper();
        studioWarmthNode.curve = makeStudioWarmthCurve(studioSettings.warmthDrive, studioSettings.warmthColor);
        studioWarmthNode.oversample = "2x";

        // 5. MÓDULO COMPRESSOR SSL BUS GLUE
        studioCompNode = audioCtx.createDynamicsCompressor();
        studioCompNode.threshold.value = studioSettings.compThreshold;
        studioCompNode.ratio.value = studioSettings.compRatio;
        studioCompNode.attack.value = studioSettings.compAttack;
        studioCompNode.release.value = studioSettings.compRelease;
        studioCompNode.knee.value = 6.0;

        // 6. MÓDULO ESPACIALIZADOR ESTÉREO 3D (HAAS WIDENER)
        studioSplitterNode = audioCtx.createChannelSplitter(2);
        studioMergerNode = audioCtx.createChannelMerger(2);
        studioDelayLeft = audioCtx.createDelay();
        studioDelayRight = audioCtx.createDelay();
        studioDelayLeft.delayTime.value = 0.0;
        studioDelayRight.delayTime.value = 0.008;

        // 7. MÓDULO MASTER MAXIMIZER & BRICKWALL LIMITER
        studioMaximizerGain = audioCtx.createGain();
        const maxGainLinear = Math.pow(10, (studioSettings.maximizerDrive || 3.0) / 20);
        studioMaximizerGain.gain.value = maxGainLinear;

        studioLimiterNode = audioCtx.createDynamicsCompressor();
        studioLimiterNode.threshold.value = studioSettings.limiterCeiling || -0.1;
        studioLimiterNode.ratio.value = 20.0;
        studioLimiterNode.attack.value = 0.001;
        studioLimiterNode.release.value = 0.04;
        studioLimiterNode.knee.value = 0.0;

        // 8. MÓDULO REVERB DE ESTÚDIO CONVOLUCIONAL (SEND PARALELO)
        studioReverbPreDelayNode = audioCtx.createDelay();
        studioReverbPreDelayNode.delayTime.value = studioSettings.reverbPreDelay || 0.02;
        studioReverbNode = audioCtx.createConvolver();
        const revBuf = createStudioImpulseBuffer(audioCtx, studioSettings.reverbDecay, 2.5, studioSettings.reverbType);
        if (revBuf) studioReverbNode.buffer = revBuf;
        studioReverbWetNode = audioCtx.createGain();
        studioReverbWetNode.gain.value = studioSettings.reverbMix / 100;

        // 9. MÓDULO DELAY ANALÓGICO PING-PONG & TAPE (SEND PARALELO)
        studioDelayNode = audioCtx.createDelay();
        studioDelayNode.delayTime.value = studioSettings.delayTime;
        studioDelayHiCutFilter = audioCtx.createBiquadFilter();
        studioDelayHiCutFilter.type = "lowpass";
        studioDelayHiCutFilter.frequency.value = studioSettings.delayHiCut || 3500;
        studioDelayFeedbackNode = audioCtx.createGain();
        studioDelayFeedbackNode.gain.value = studioSettings.delayFeedback / 100;
        studioDelayWetNode = audioCtx.createGain();
        studioDelayWetNode.gain.value = studioSettings.delayMix / 100;

        // ================= CONEXÕES DO GRAFO DE ÁUDIO =================
        // Delay Send: Input -> Delay -> HiCut -> Feedback Loop + Send to Mixer
        studioInputNode.connect(studioDelayNode);
        studioDelayNode.connect(studioDelayHiCutFilter);
        studioDelayHiCutFilter.connect(studioDelayFeedbackNode);
        studioDelayFeedbackNode.connect(studioDelayNode);
        studioDelayHiCutFilter.connect(studioDelayWetNode);
        studioDelayWetNode.connect(studioMasterMixerNode);

        // Reverb Send: Input -> PreDelay -> Reverb -> ReverbWet -> Mixer
        studioInputNode.connect(studioReverbPreDelayNode);
        studioReverbPreDelayNode.connect(studioReverbNode);
        studioReverbNode.connect(studioReverbWetNode);
        studioReverbWetNode.connect(studioMasterMixerNode);

        // Rota Principal Serial Processada:
        // Input -> RumbleCut -> SubBass -> DeEsser -> AirBand -> Warmth -> SSL Comp -> Haas 3D -> Maximizer -> Limiter -> WetGain -> Mixer
        studioInputNode.connect(studioRumbleFilter);
        studioRumbleFilter.connect(studioBassBoostFilter);
        studioBassBoostFilter.connect(studioDeEsserFilter);
        studioDeEsserFilter.connect(studioAirFilter);
        studioAirFilter.connect(studioWarmthNode);
        studioWarmthNode.connect(studioCompNode);

        studioCompNode.connect(studioSplitterNode);
        studioSplitterNode.connect(studioDelayLeft, 0);
        studioSplitterNode.connect(studioDelayRight, 1);
        studioDelayLeft.connect(studioMergerNode, 0, 0);
        studioDelayRight.connect(studioMergerNode, 0, 1);

        studioMergerNode.connect(studioMaximizerGain);
        studioMaximizerGain.connect(studioLimiterNode);
        studioLimiterNode.connect(studioWetGainNode);
        studioWetGainNode.connect(studioMasterMixerNode);

        // Rota Dry (Sinal Direto para Bypass A/B)
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

        // Analisador FFT de Espectro Real-Time
        studioSpectrumAnalyser = audioCtx.createAnalyser();
        studioSpectrumAnalyser.fftSize = 512;
        studioSpectrumAnalyser.smoothingTimeConstant = 0.82;
        studioMasterMixerNode.connect(studioSpectrumAnalyser);

        // Inserir no Grafo Master se os filtros de EQ existirem
        if (eqFilters && eqFilters.length > 0) {
            const lastFilter = eqFilters[eqFilters.length - 1];
            try {
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

    // DSP Ativo
    if (studioDryGainNode) studioDryGainNode.gain.setValueAtTime(0.0, now);
    if (studioWetGainNode) studioWetGainNode.gain.setValueAtTime(1.0, now);

    // 1. Reverb
    if (studioReverbPreDelayNode) {
        studioReverbPreDelayNode.delayTime.setValueAtTime(studioSettings.reverbPreDelay || 0.02, now);
    }
    if (studioReverbWetNode) {
        studioReverbWetNode.gain.setValueAtTime(studioSettings.reverbMix / 100, now);
    }

    // 2. Delay
    if (studioDelayNode) {
        studioDelayNode.delayTime.setValueAtTime(studioSettings.delayTime, now);
    }
    if (studioDelayHiCutFilter) {
        studioDelayHiCutFilter.frequency.setValueAtTime(studioSettings.delayHiCut || 3500, now);
    }
    if (studioDelayFeedbackNode) {
        studioDelayFeedbackNode.gain.setValueAtTime(studioSettings.delayFeedback / 100, now);
    }
    if (studioDelayWetNode) {
        studioDelayWetNode.gain.setValueAtTime(studioSettings.delayMix / 100, now);
    }

    // 3. SSL Bus Compressor
    if (studioCompNode) {
        studioCompNode.threshold.setValueAtTime(studioSettings.compThreshold, now);
        studioCompNode.ratio.setValueAtTime(studioSettings.compRatio, now);
        studioCompNode.attack.setValueAtTime(studioSettings.compAttack, now);
        studioCompNode.release.setValueAtTime(studioSettings.compRelease, now);
    }

    // 4. Calor Valvulado & Saturação
    if (studioWarmthNode) {
        studioWarmthNode.curve = makeStudioWarmthCurve(studioSettings.warmthDrive, studioSettings.warmthColor);
    }

    // 5. Haas Stereo 3D
    if (studioDelayRight) {
        const offset = Math.max(0, (studioSettings.stereoWidth - 100) / 100) * 0.016;
        studioDelayRight.delayTime.setValueAtTime(offset, now);
    }

    // 6. Air Band & Exciter
    if (studioAirFilter) {
        studioAirFilter.frequency.setValueAtTime(studioSettings.airFreq || 12000, now);
        const sparkleBonus = (studioSettings.airSparkle || 0) * 0.03;
        studioAirFilter.gain.setValueAtTime((studioSettings.airBoost || 0) + sparkleBonus, now);
    }

    // 7. Sub-Bass & Rumble Filter
    if (studioBassBoostFilter) {
        studioBassBoostFilter.frequency.setValueAtTime(studioSettings.subFreq || 60, now);
        studioBassBoostFilter.gain.setValueAtTime(studioSettings.subBoost || 0, now);
    }
    if (studioRumbleFilter) {
        const rCut = studioSettings.subRumbleCut || 0;
        studioRumbleFilter.frequency.setValueAtTime(rCut > 0 ? rCut : 10, now);
    }

    // 8. De-Esser Dynamic Tamer
    if (studioDeEsserFilter) {
        studioDeEsserFilter.frequency.setValueAtTime(studioSettings.deEsserFreq || 6500, now);
        const reductionDb = -((studioSettings.deEsserAmount || 0) / 100) * 8.0;
        studioDeEsserFilter.gain.setValueAtTime(reductionDb, now);
    }

    // 9. Maximizer & Brickwall Limiter
    if (studioMaximizerGain) {
        const linGain = Math.pow(10, (studioSettings.maximizerDrive || 0) / 20);
        studioMaximizerGain.gain.setValueAtTime(linGain, now);
    }
    if (studioLimiterNode) {
        studioLimiterNode.threshold.setValueAtTime(studioSettings.limiterCeiling || -0.1, now);
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
        updateStudioUiElements();
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

function toggleStudioMonoCheck() {
    studioMonoCheck = !studioMonoCheck;
    const btn = document.getElementById("btnStudioMono");
    const dot = document.getElementById("studioMonoDot");
    const label = document.getElementById("studioMonoLabel");
    if (btn) btn.classList.toggle("active", studioMonoCheck);
    if (dot) dot.classList.toggle("active", studioMonoCheck);
    if (label) label.textContent = studioMonoCheck ? "MONO ATIVO" : "STEREO";

    if (studioDelayRight) {
        // No modo mono, cancela qualquer defasagem estéreo
        studioDelayRight.delayTime.setValueAtTime(studioMonoCheck ? 0.0 : Math.max(0, (studioSettings.stereoWidth - 100) / 100) * 0.016, audioCtx ? audioCtx.currentTime : 0);
    }
}

function resetStudioFlat() {
    selectStudioPreset("flat");
}

function selectStudioPreset(key) {
    const p = STUDIO_PRESETS[key];
    if (!p) return;
    studioSettings = { ...studioSettings, ...p, preset: key };

    document.querySelectorAll(".studio-preset-chip").forEach(c => c.classList.remove("active"));
    const activeChip = document.getElementById(`stPreset_${key}`);
    if (activeChip) activeChip.classList.add("active");

    updateStudioUiElements();

    if (audioCtx && studioReverbNode) {
        const buf = createStudioImpulseBuffer(audioCtx, studioSettings.reverbDecay, 2.5, studioSettings.reverbType);
        if (buf) studioReverbNode.buffer = buf;
    }

    applyStudioDspParams();
}

function updateStudioUiElements() {
    // 1. Reverb
    const sPre = document.getElementById("sliderStudioReverbPreDelay");
    if (sPre) sPre.value = studioSettings.reverbPreDelay;
    const vPre = document.getElementById("valStudioReverbPreDelay");
    if (vPre) vPre.textContent = Math.round((studioSettings.reverbPreDelay || 0) * 1000) + "ms";

    const sDecay = document.getElementById("sliderStudioReverbDecay");
    if (sDecay) sDecay.value = studioSettings.reverbDecay;
    const vDecay = document.getElementById("valStudioReverbDecay");
    if (vDecay) vDecay.textContent = studioSettings.reverbDecay + "s";

    const sRevMix = document.getElementById("sliderStudioReverbMix");
    if (sRevMix) sRevMix.value = studioSettings.reverbMix;
    const vRevMix = document.getElementById("valStudioReverbMix");
    if (vRevMix) vRevMix.textContent = studioSettings.reverbMix + "%";

    const revBadge = document.getElementById("reverbTypeBadge");
    if (revBadge) revBadge.textContent = studioSettings.reverbType.toUpperCase();

    // 2. Delay
    const sHiCut = document.getElementById("sliderStudioDelayHiCut");
    if (sHiCut) sHiCut.value = studioSettings.delayHiCut || 3500;
    const vHiCut = document.getElementById("valStudioDelayHiCut");
    if (vHiCut) vHiCut.textContent = (studioSettings.delayHiCut || 3500) + " Hz";

    const sFeed = document.getElementById("sliderStudioDelayFeedback");
    if (sFeed) sFeed.value = studioSettings.delayFeedback;
    const vFeed = document.getElementById("valStudioDelayFeedback");
    if (vFeed) vFeed.textContent = studioSettings.delayFeedback + "%";

    const sDelMix = document.getElementById("sliderStudioDelayMix");
    if (sDelMix) sDelMix.value = studioSettings.delayMix;
    const vDelMix = document.getElementById("valStudioDelayMix");
    if (vDelMix) vDelMix.textContent = studioSettings.delayMix + "%";

    // 3. Compressor
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

    const vHpf = document.getElementById("valStudioCompHpf");
    if (vHpf) vHpf.textContent = studioSettings.compSidechainHpf ? studioSettings.compSidechainHpf + " Hz" : "Off";

    // 4. Warmth & 3D Wide
    const sWarmth = document.getElementById("sliderStudioWarmth");
    if (sWarmth) sWarmth.value = studioSettings.warmthDrive;
    const vWarmth = document.getElementById("valStudioWarmth");
    if (vWarmth) vWarmth.textContent = studioSettings.warmthDrive + "%";

    const sWidth = document.getElementById("sliderStudioWidth");
    if (sWidth) sWidth.value = studioSettings.stereoWidth;
    const vWidth = document.getElementById("valStudioWidth");
    if (vWidth) vWidth.textContent = studioSettings.stereoWidth + "%";

    // 5. Air Band
    const sAirB = document.getElementById("sliderStudioAirBoost");
    if (sAirB) sAirB.value = studioSettings.airBoost;
    const vAirB = document.getElementById("valStudioAirBoost");
    if (vAirB) vAirB.textContent = "+" + (studioSettings.airBoost || 0).toFixed(1) + " dB";

    const sAirS = document.getElementById("sliderStudioAirSparkle");
    if (sAirS) sAirS.value = studioSettings.airSparkle;
    const vAirS = document.getElementById("valStudioAirSparkle");
    if (vAirS) vAirS.textContent = (studioSettings.airSparkle || 0) + "%";

    // 6. Sub-Bass
    const sSubB = document.getElementById("sliderStudioSubBoost");
    if (sSubB) sSubB.value = studioSettings.subBoost;
    const vSubB = document.getElementById("valStudioSubBoost");
    if (vSubB) vSubB.textContent = "+" + (studioSettings.subBoost || 0).toFixed(1) + " dB";

    const vSubR = document.getElementById("valStudioSubRumble");
    if (vSubR) vSubR.textContent = studioSettings.subRumbleCut ? studioSettings.subRumbleCut + " Hz" : "Off";

    // 7. De-Esser
    const sDeEss = document.getElementById("sliderStudioDeEss");
    if (sDeEss) sDeEss.value = studioSettings.deEsserAmount;
    const vDeEss = document.getElementById("valStudioDeEss");
    if (vDeEss) {
        const dbRed = ((studioSettings.deEsserAmount || 0) / 100 * 8.0).toFixed(1);
        vDeEss.textContent = `${studioSettings.deEsserAmount || 0}% (-${dbRed} dB)`;
    }

    // 8. Maximizer
    const sMax = document.getElementById("sliderStudioMaximizer");
    if (sMax) sMax.value = studioSettings.maximizerDrive;
    const vMax = document.getElementById("valStudioMaximizer");
    if (vMax) vMax.textContent = "+" + (studioSettings.maximizerDrive || 0).toFixed(1) + " dB";
}

function setStudioReverbType(type) {
    studioSettings.reverbType = type;
    document.querySelectorAll(".btn-rev-type").forEach(b => b.classList.remove("active"));
    const btn = document.getElementById(`btnRev_${type}`);
    if (btn) btn.classList.add("active");
    const revBadge = document.getElementById("reverbTypeBadge");
    if (revBadge) revBadge.textContent = type.toUpperCase();

    const decayMap = { hall: 2.2, plate: 1.6, club: 1.2, room: 0.9, cathedral: 3.5, spring: 1.8 };
    studioSettings.reverbDecay = decayMap[type] || 1.8;
    updateStudioUiElements();

    if (audioCtx && studioReverbNode) {
        const buf = createStudioImpulseBuffer(audioCtx, studioSettings.reverbDecay, 2.5, type);
        if (buf) studioReverbNode.buffer = buf;
    }
    applyStudioDspParams();
}

function setStudioDelayPreset(timeSec, label) {
    studioSettings.delayTime = timeSec;
    studioSettings.delayPreset = label;
    document.querySelectorAll(".btn-del-time").forEach(b => b.classList.remove("active"));
    if (typeof event !== "undefined" && event && event.target) {
        event.target.classList.add("active");
    }
    updateStudioUiElements();
    applyStudioDspParams();
}

function setStudioCompHpf(freq, label) {
    studioSettings.compSidechainHpf = freq;
    document.querySelectorAll(".btn-comp-hpf").forEach(b => b.classList.remove("active"));
    if (typeof event !== "undefined" && event && event.target) {
        event.target.classList.add("active");
    }
    updateStudioUiElements();
    applyStudioDspParams();
}

function setStudioWarmthColor(color) {
    studioSettings.warmthColor = color;
    document.querySelectorAll(".btn-warmth-color").forEach(b => b.classList.remove("active"));
    const btn = document.getElementById(`btnWarmth_${color}`);
    if (btn) btn.classList.add("active");
    applyStudioDspParams();
}

function setStudioAirFreq(freq, label) {
    studioSettings.airFreq = freq;
    document.querySelectorAll(".btn-air-freq").forEach(b => b.classList.remove("active"));
    if (typeof event !== "undefined" && event && event.target) {
        event.target.classList.add("active");
    }
    applyStudioDspParams();
}

function setStudioSubFreq(freq, label) {
    studioSettings.subFreq = freq;
    document.querySelectorAll(".btn-sub-freq").forEach(b => b.classList.remove("active"));
    if (typeof event !== "undefined" && event && event.target) {
        event.target.classList.add("active");
    }
    applyStudioDspParams();
}

function setStudioRumbleCut(freq, label) {
    studioSettings.subRumbleCut = freq;
    document.querySelectorAll(".btn-rumble-cut").forEach(b => b.classList.remove("active"));
    if (typeof event !== "undefined" && event && event.target) {
        event.target.classList.add("active");
    }
    updateStudioUiElements();
    applyStudioDspParams();
}

function setStudioDeEssFreq(freq, label) {
    studioSettings.deEsserFreq = freq;
    document.querySelectorAll(".btn-deess-freq").forEach(b => b.classList.remove("active"));
    if (typeof event !== "undefined" && event && event.target) {
        event.target.classList.add("active");
    }
    applyStudioDspParams();
}

function setStudioLimiterCeiling(ceil, label) {
    studioSettings.limiterCeiling = ceil;
    document.querySelectorAll(".btn-limiter-ceiling").forEach(b => b.classList.remove("active"));
    if (typeof event !== "undefined" && event && event.target) {
        event.target.classList.add("active");
    }
    applyStudioDspParams();
}

function onStudioParamChange(param, val) {
    const num = parseFloat(val);
    studioSettings[param] = num;
    updateStudioUiElements();

    if ((param === "reverbDecay" || param === "reverbType") && audioCtx && studioReverbNode) {
        const buf = createStudioImpulseBuffer(audioCtx, studioSettings.reverbDecay, 2.5, studioSettings.reverbType);
        if (buf) studioReverbNode.buffer = buf;
    }
    applyStudioDspParams();
}

// Loop de Animação dos Medidores VU & Analisador de Espectro FFT
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
    const lufsFill = document.getElementById("studioLufsFill");
    const lufsVal = document.getElementById("studioLufsVal");
    const specCanvas = document.getElementById("studioSpectrumCanvas");
    const specCtx = specCanvas ? specCanvas.getContext("2d") : null;

    const dataL = new Uint8Array(128);
    const dataR = new Uint8Array(128);
    const freqData = new Uint8Array(256);

    function update() {
        const modal = document.getElementById("studioModal");
        if (!modal || modal.style.display === "none") return;

        let pctL = 10, pctR = 10;
        let dbL = -48, dbR = -48;
        let estLufs = -18;

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
            const avgRms = (rmsL + rmsR) / 2;

            dbL = rmsL > 1e-4 ? Math.round(20 * Math.log10(rmsL)) : -48;
            dbR = rmsR > 1e-4 ? Math.round(20 * Math.log10(rmsR)) : -48;
            estLufs = avgRms > 1e-4 ? Math.round(20 * Math.log10(avgRms) - 0.7) : -36;

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

        // Medidor de Loudness Percebido (LUFS Estimado)
        if (lufsFill && lufsVal) {
            const lufsPct = Math.max(0, Math.min(100, ((estLufs + 36) / 30) * 100));
            lufsFill.style.width = lufsPct + "%";
            lufsVal.textContent = estLufs > -36 ? estLufs + " LUFS" : "-∞ LUFS";
        }

        // Analisador de Espectro FFT em Tempo Real
        if (specCtx && studioSpectrumAnalyser && audioCtx && audioCtx.state === "running") {
            studioSpectrumAnalyser.getByteFrequencyData(freqData);
            const w = specCanvas.width;
            const h = specCanvas.height;
            specCtx.clearRect(0, 0, w, h);

            // Grade de fundo sutil
            specCtx.strokeStyle = "rgba(255, 255, 255, 0.04)";
            specCtx.lineWidth = 1;
            for (let y = 15; y < h; y += 15) {
                specCtx.beginPath();
                specCtx.moveTo(0, y);
                specCtx.lineTo(w, y);
                specCtx.stroke();
            }

            // Gradiente dinâmico do espectro
            const grad = specCtx.createLinearGradient(0, 0, w, 0);
            grad.addColorStop(0.00, "#a855f7"); // Sub
            grad.addColorStop(0.18, "#38bdf8"); // Bass
            grad.addColorStop(0.40, "#34d399"); // Mid
            grad.addColorStop(0.65, "#fbbf24"); // High-Mid
            grad.addColorStop(0.85, "#f97316"); // Presence
            grad.addColorStop(1.00, "#00f2fe"); // Air

            specCtx.beginPath();
            specCtx.moveTo(0, h);
            const barCount = 120;
            const step = w / barCount;

            for (let i = 0; i < barCount; i++) {
                // Mapeamento logarítmico para resposta auditiva humana natural
                const logIndex = Math.floor(Math.pow(i / barCount, 1.8) * (freqData.length - 1));
                const val = freqData[logIndex] || 0;
                const barHeight = (val / 255) * (h - 6);
                const x = i * step;
                const y = h - barHeight;

                if (i === 0) specCtx.lineTo(x, y);
                else specCtx.lineTo(x, y);
            }
            specCtx.lineTo(w, h);
            specCtx.closePath();

            // Área preenchida com transparência
            specCtx.fillStyle = "rgba(168, 85, 247, 0.12)";
            specCtx.fill();

            // Linha neon do topo
            specCtx.strokeStyle = grad;
            specCtx.lineWidth = 2.2;
            specCtx.shadowColor = "#00f2fe";
            specCtx.shadowBlur = 6;
            specCtx.stroke();
            specCtx.shadowBlur = 0;
        }

        studioVuTimer = requestAnimationFrame(update);
    }

    studioVuTimer = requestAnimationFrame(update);
}

// Exportações Globais
window.openStudioModal = openStudioModal;
window.closeStudioModal = closeStudioModal;
window.toggleStudioBypass = toggleStudioBypass;
window.toggleStudioMonoCheck = toggleStudioMonoCheck;
window.resetStudioFlat = resetStudioFlat;
window.selectStudioPreset = selectStudioPreset;
window.setStudioReverbType = setStudioReverbType;
window.setStudioDelayPreset = setStudioDelayPreset;
window.setStudioCompHpf = setStudioCompHpf;
window.setStudioWarmthColor = setStudioWarmthColor;
window.setStudioAirFreq = setStudioAirFreq;
window.setStudioSubFreq = setStudioSubFreq;
window.setStudioRumbleCut = setStudioRumbleCut;
window.setStudioDeEssFreq = setStudioDeEssFreq;
window.setStudioLimiterCeiling = setStudioLimiterCeiling;
window.onStudioParamChange = onStudioParamChange;
window.initStudioDsp = initStudioDsp;
window.applyStudioDspParams = applyStudioDspParams;
window.createStudioImpulseBuffer = createStudioImpulseBuffer;
window.studioSettings = studioSettings;

window.initStemsDsp = initStemsDsp;
window.startStemsMeters = startStemsMeters;
window.applyStemsToDsp = applyStemsToDsp;
window.applyStemPreset = applyStemPreset;
window.onStemSliderChange = onStemSliderChange;
window.toggleStemMute = toggleStemMute;
window.toggleStemSolo = toggleStemSolo;
window.openStemsModal = openStemsModal;
window.closeStemsModal = closeStemsModal;

window.setStemGenreProfile = setStemGenreProfile;
window.detectStemGenreKey = detectStemGenreKey;
window.GENRE_STEM_PROFILES = GENRE_STEM_PROFILES;
