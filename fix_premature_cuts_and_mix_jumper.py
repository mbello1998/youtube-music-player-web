# -*- coding: utf-8 -*-
"""
fix_premature_cuts_and_mix_jumper.py
1. Corrige o corte precoce: garante que o refrão toque por inteiro (75s a 90s)
   - Janela padrão aumentada de 45s para 75s (expansível até 95s em alta energia)
   - Proteção do refrão: nenhuma queda de energia encerra antes de pelo menos 65s de drop!
2. Corrige o Mix Jumper para mixes longos:
   - Elimina o travamento, estalos e paradas bruscas com Quick Fader Duck & Seeked Resume
   - Evita que a música "volte": flag isJumpingMix blindando contra saltos duplos ou resets
   - Tempo mínimo de 90s para cada segmento do mix antes de avançar para o próximo refrão
"""

from pathlib import Path
import re
import subprocess
import sys

BASE_DIR = Path(r"C:\Users\Mbello\Desktop\ig-to-youtube-playlist\.claude\worktrees\instagram-youtube-playlist")
TEMPLATE_PATH = BASE_DIR / "player_template.html"
JS_PATH = BASE_DIR / "assets" / "js" / "player.js"

print("--- 1. Atualizando assets/js/player.js ---")
with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# Substitui o bloco do Drop Hunter pelo novo algoritmo com proteção de refrão (75s - 95s) e Mix Jumper suave
old_engine_pattern = r'// =+ *\r?\n *// DROP HUNTER & WAVE ANALYSIS ENGINE[\s\S]*?function smartCutToNextDrop\(\) \{[\s\S]*?autoAdvanceWithFade\(\);\s*\}'

new_engine_code = """// ==========================================================================
        // DROP HUNTER & WAVE ANALYSIS ENGINE (REFRÃO COMPLETO 75s-95s & SALTO SUAVE)
        // ==========================================================================
        let dropHunterTimer = null;
        let dropActiveSeconds = 0;
        let dropTargetSeconds = 75; // Janela ideal de festa: 75s a 95s (toca o refrão completo!)
        let dropHunterThreshold = 60; // % de energia para considerar Drop Ativo
        let isAutoDropEnabled = true; // Modo 100% automático (pula intro e corta no drop da próxima)
        let consecutiveLowEnergyCount = 0;
        let mixSegmentCount = 0;
        let maxMixSegmentsBeforeNext = 3; // Em mixes longos, curte até 3 saltos de refrão antes de trocar de faixa
        let isJumpingMix = false; // Flag de proteção contra interrupções/conflitos durante o salto no mix

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
            dropTargetSeconds = isTrackLongMix(nowPlayingTrack) ? 90 : 75;
            consecutiveLowEnergyCount = 0;
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
            const hud = document.getElementById("djDropHunterHud");
            if (hud) hud.classList.remove("hud-visible");
        }

        function toggleAutoDropMode() {
            isAutoDropEnabled = !isAutoDropEnabled;
            const btn = document.getElementById("btnAutoDropToggle");
            if (btn) {
                btn.classList.toggle("active", isAutoDropEnabled);
                btn.textContent = isAutoDropEnabled ? "🤖 Auto: ON" : "⏸️ Auto: OFF";
            }
            showToast(isAutoDropEnabled ? "🤖 Auto DJ LIGADO: Toca o refrão completo (75s-90s) e corta suave!" : "⏸️ Auto DJ em pausa: Você controla os cortes!");
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
                    footerText.innerHTML = `💡 <strong>Refrão Completo Protegido:</strong> Toca o refrão inteiro (75s a 95s) antes de virar para a próxima!`;
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

            // JANELA DE REFRÃO COMPLETO (75s A 95s)
            if (energy >= dropHunterThreshold) {
                // DROP ATIVO!
                dropActiveSeconds += 0.1;
                consecutiveLowEnergyCount = 0;

                // Se a energia está estourando no ápice (>= 75%), estende a janela até 95s para curtir mais
                if (energy >= 75) {
                    const maxAllowed = isLongMix ? 110 : 95;
                    dropTargetSeconds = Math.min(maxAllowed, dropTargetSeconds + 0.05);
                }

                if (statusPill) {
                    statusPill.className = "drop-status-pill drop-active";
                    statusPill.innerHTML = "💥 DROP ATIVO! (PISTA FERVENTE)";
                }
            } else if (energy >= 42) {
                // Buildup / Subindo Energia
                dropActiveSeconds += 0.08;
                if (statusPill) {
                    statusPill.className = "drop-status-pill buildup";
                    statusPill.innerHTML = "⚡ Subindo Energia (Buildup)";
                }
            } else {
                // Queda de energia momentânea (Vocal, respiro ou breakdown)
                // PROTEÇÃO ANTI-CORTE PRECOCE:
                // NUNCA encurta a janela se a faixa tocou menos de 65 segundos de drop!
                if (dropActiveSeconds >= 65) {
                    consecutiveLowEnergyCount++;
                    // Exige pelo menos 3.5 segundos contínuos de energia baixa pós-refrão para considerar corte
                    if (consecutiveLowEnergyCount >= 35) {
                        const minFloor = isLongMix ? 85 : 70;
                        dropTargetSeconds = Math.max(minFloor, Math.round(dropActiveSeconds));
                    }
                }
                if (statusPill) {
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

            // DISPARO DO CORTE AUTOMÁTICO DE FESTA (SÓ APÓS O REFRÃO COMPLETO!)
            if (isAutoDropEnabled && dropActiveSeconds >= dropTargetSeconds && !isTransitioning && !isJumpingMix) {
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
                statusPill.innerHTML = `🔀 SALTO SUAVE (${mixSegmentCount}/${maxMixSegmentsBeforeNext + 1})`;
            }

            showToast(`🔀 Mix Jumper: Pulei suave para o próximo refrão do mix! (${mixSegmentCount + 1}/${maxMixSegmentsBeforeNext + 1})`);

            if (engineMode === "audio") {
                const curAudio = getActiveAudioDeck();
                const activeGain = (activeDeck === "A") ? deckGainA : deckGainB;

                if (curAudio && activeGain && audioCtx) {
                    const now = audioCtx.currentTime;
                    // 1. Duck suave de volume (sem estalo e sem parar a música)
                    activeGain.gain.cancelScheduledValues(now);
                    activeGain.gain.setValueAtTime(activeGain.gain.value, now);
                    activeGain.gain.linearRampToValueAtTime(0.02, now + 0.15);

                    setTimeout(() => {
                        const dur = curAudio.duration || 1800;
                        const nextTime = Math.min(dur - 40, (curAudio.currentTime || 0) + 80);

                        const onSeekedDone = () => {
                            curAudio.removeEventListener("seeked", onSeekedDone);
                            curAudio.play().then(() => {
                                if (activeGain && audioCtx) {
                                    const resumeNow = audioCtx.currentTime;
                                    activeGain.gain.cancelScheduledValues(resumeNow);
                                    activeGain.gain.setValueAtTime(0.02, resumeNow);
                                    activeGain.gain.linearRampToValueAtTime(1.0, resumeNow + 0.25);
                                }
                            }).catch(() => {});
                            setTimeout(() => { isJumpingMix = false; }, 400);
                        };

                        curAudio.addEventListener("seeked", onSeekedDone, { once: true });
                        curAudio.currentTime = nextTime;

                        // Fallback seguro caso seeked não dispare no tempo
                        setTimeout(() => {
                            if (isJumpingMix) onSeekedDone();
                        }, 700);
                    }, 160);
                } else if (curAudio) {
                    const dur = curAudio.duration || 1800;
                    curAudio.currentTime = Math.min(dur - 40, (curAudio.currentTime || 0) + 80);
                    curAudio.play().catch(() => {});
                    setTimeout(() => { isJumpingMix = false; }, 600);
                }
            } else {
                const activeP = getActivePlayer();
                if (activeP && typeof activeP.seekTo === "function") {
                    const dur = (typeof activeP.getDuration === "function") ? (activeP.getDuration() || 1800) : 1800;
                    const cur = (typeof activeP.getCurrentTime === "function") ? (activeP.getCurrentTime() || 0) : 0;
                    const nextTime = Math.min(dur - 40, cur + 80);
                    activeP.seekTo(nextTime, true);
                }
                setTimeout(() => { isJumpingMix = false; }, 800);
            }
        }

        // Corte no Drop da próxima música (com transição profissional)
        function smartCutToNextDrop() {
            mixSegmentCount = 0;
            dropActiveSeconds = 0;
            dropTargetSeconds = 75;
            consecutiveLowEnergyCount = 0;
            isJumpingMix = false;

            const statusPill = document.getElementById("dropStatusPill");
            if (statusPill) {
                statusPill.className = "drop-status-pill cutting";
                statusPill.innerHTML = "✂️ CORTE NO DROP! VIRANDO...";
            }
            showToast("✂️ Corte no Drop: Virando no ápice direto pro Drop da próxima!");
            autoAdvanceWithFade();
        }"""

if re.search(old_engine_pattern, js):
    js = re.sub(old_engine_pattern, new_engine_code, js, count=1)
    print("✓ Motor Drop Hunter atualizado com proteção de refrão (75s-95s) e Mix Jumper suave!")
else:
    print("! old_engine_pattern não casou, buscando manualmente...")
    pos_s = js.find("// DROP HUNTER & WAVE ANALYSIS ENGINE")
    pos_e = js.find("autoAdvanceWithFade();\n        }", pos_s)
    if pos_s != -1 and pos_e != -1:
        end_idx = pos_e + len("autoAdvanceWithFade();\n        }")
        js = js[:pos_s] + new_engine_code + js[end_idx:]
        print("✓ Motor Drop Hunter atualizado via corte manual!")

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)

print("\n--- 2. Atualizando player_template.html ---")
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

# Atualizar o valor inicial da label da Janela Dinâmica no template para 01:15s (75s)
template = template.replace('00:00 / 00:45s', '00:00 / 01:15s')
template = template.replace('JANELA DINÂMICA (VARIÁVEL)', 'JANELA DO REFRÃO (VARIÁVEL)')
template = template.replace('Pula a intro sozinho, toca o drop no ápice e já salta para a próxima direto no drop!', 'Refrão Completo Protegido: Toca o refrão inteiro (75s a 95s) antes de virar para a próxima!')

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(template)
print("✓ player_template.html atualizado!")

print("\n--- 3. Executando build_full_player.py ---")
res = subprocess.run([sys.executable, str(BASE_DIR / "build_full_player.py")], capture_output=True, text=True, cwd=str(BASE_DIR))
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
print(f"Build Exit code: {res.returncode}")
