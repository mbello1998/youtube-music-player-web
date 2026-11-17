import re
from pathlib import Path

JS_PATH = Path("assets/js/player.js")
TEMPLATE_PATH = Path("player_template.html")
CSS_PATH = Path("assets/css/player.css")

with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# 1. Substituir cleanTrackTitleForBar por versão robusta que remove qualquer resquício de feat, tags entre colchetes, emojis, etc.
clean_pattern = r"function cleanTrackTitleForBar\(rawTitle, rawArtist\) \{[\s\S]*?return clean;\s*\}"
clean_replacement = """function cleanTrackTitleForBar(rawTitle, rawArtist) {
            if (!rawTitle) return "";
            let clean = String(rawTitle).trim();

            // 1. Remove bracketed / parenthesized content completely: [ ... ], ( ... ), { ... }
            clean = clean.replace(/[\\(\\[\\{][^\\)\\]\\}]*[\\)\\]\\}]/gi, " ");

            // 2. Remove feat / ft / featuring / part: e.g. 'feat. ...', 'ft ...', 'part. ...'
            clean = clean.replace(/\\b(?:feat\\.?|ft\\.?|featuring|part\\.?|participação)\\b.*$/gi, "");
            clean = clean.replace(/\\s*(?:feat\\.?|ft\\.?|featuring|part\\.?)\\s+[^\\-\\–\\—\\|]+[\\-\\–\\—]\\s*/gi, " - ");

            // 3. Remove common promo words and delimiters
            clean = clean.replace(/\\b(?:video\\s*oficial|clipe?\\s*oficial|official\\s*music\\s*video|official\\s*video|lyric\\s*video|audio\\s*oficial|official\\s*audio|en\\s*vivo|ao\\s*vivo|hd|4k)\\b/gi, "");

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
            clean = clean.replace(/[\\u{1F300}-\\u{1F9FF}\\u{2600}-\\u{27BF}\\u{1F1E0}-\\u{1F1FF}\\u{1F600}-\\u{1F64F}\\u{1F680}-\\u{1F6FF}•*~–—]/gu, " ");

            // 7. Collapse spaces and trim
            clean = clean.replace(/\\s+/g, " ").trim();

            // 8. Clamp to 28 characters
            if (clean.length > 28) {
                clean = clean.slice(0, 27).trim() + "…";
            }
            return clean;
        }"""

if re.search(clean_pattern, js):
    js = re.sub(clean_pattern, lambda m: clean_replacement, js, count=1)
    print("✓ cleanTrackTitleForBar atualizado via regex!")
else:
    print("! clean_pattern não encontrado!")

# 2. Corrigir optCard.id para remover encodeURIComponent e usar caracteres alfanuméricos seguros
js = js.replace(
    'optCard.id = `moveOptCat_${encodeURIComponent(cat)}`;',
    'optCard.id = `moveOptCat_${cat.replace(/[^a-zA-Z0-9]/g, "_")}`;'
)
js = js.replace(
    'const selectedEl = document.getElementById(`moveOptCat_${encodeURIComponent(catName)}`);',
    'const selectedEl = document.getElementById(`moveOptCat_${catName.replace(/[^a-zA-Z0-9]/g, "_")}`);'
)
print("✓ IDs do modal de mover corrigidos para alfanumérico seguro!")

# 3. Compactar tag no barStatusText para nunca espremer o título da próxima música
old_bar_next = '<span class="status-badge-next">⏭️ A Seguir (${tagLabel}):</span>'
new_bar_next = '<span class="status-badge-next" title="Próxima Faixa (${tagLabel})">⏭️ A Seguir:</span>'
if old_bar_next in js:
    js = js.replace(old_bar_next, new_bar_next)
    print("✓ Status bar 'A Seguir' compactado para preservar espaço!")

# 4. Corrigir Histórico de Reprodução:
# a) openHistoryModal deve atualizar contador imediatamente antes do fetch
old_open_hist = """        async function openHistoryModal() {
            const modal = document.getElementById("historyModal");
            if (!modal) return;
            modal.style.display = "flex";
            modal.classList.add("open");
            await renderHistoryModal();
        }"""

new_open_hist = """        async function openHistoryModal() {
            const modal = document.getElementById("historyModal");
            if (!modal) return;
            const curCount = (playbackHistory && playbackHistory.length) || 0;
            updateHistoryBadge(curCount);
            modal.style.display = "flex";
            modal.classList.add("open");
            await renderHistoryModal();
        }"""

if old_open_hist in js:
    js = js.replace(old_open_hist, new_open_hist)
    print("✓ openHistoryModal atualizado com atualização antecipada de contadores!")

# b) renderHistoryModal deve garantir atualização de modalHistoryBadgeCount e fornecer botões Mover/Remover
old_render_hist = """            let html = "";
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
                        <div class="history-actions">
                            <button class="btn-history-play" onclick="playHistoryTrackByIndex(${idx})" title="Tocar esta faixa agora">▶</button>
                            ${inLib ? `
                                <span class="history-saved-badge">✓ Na Biblioteca</span>
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
        }"""

new_render_hist = """            let html = "";
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
                                    <button class="btn-remove-lib-card" onclick="removeLibraryTrackPrompt('${track.video_id}', '${escapeQuotes(track.title)}')" title="Remover da biblioteca">🗑️</button>
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
        }"""

if old_render_hist in js:
    js = js.replace(old_render_hist, new_render_hist)
    print("✓ renderHistoryModal atualizado com ações completas e sincronização de contadores!")

# c) saveHistoryTrackToLibrary: atualizar UI com ações Mover/Remover após salvar
old_save_hist = """                    showToast(`⭐ "${title.slice(0, 32)}..." salva na sua biblioteca! Acesse na aba "${cat}".`, 5000);
                    if (btn) {
                        btn.outerHTML = `<span class="history-saved-badge">✓ Salvo na Biblioteca</span>`;
                    }"""

new_save_hist = """                    showToast(`⭐ "${title.slice(0, 32)}..." salva na sua biblioteca! Acesse na aba "${cat}".`, 5000);
                    const actionsBox = document.getElementById(`histActions_${videoId}`);
                    if (actionsBox) {
                        actionsBox.innerHTML = `
                            <button class="btn-history-play" onclick="playHistoryTrackByIndex(0)" title="Tocar esta faixa agora">▶</button>
                            <div style="display: flex; gap: 5px; align-items: center;">
                                <span class="history-saved-badge" title="Esta música já está na sua biblioteca">✓ Na Biblioteca</span>
                                <button class="btn-move-card" onclick="openMovePlaylistModalByVideoId('${videoId}', '${escapeQuotes(title)}')" title="Mover para outra playlist">📂 Mover</button>
                                <button class="btn-remove-lib-card" onclick="removeLibraryTrackPrompt('${videoId}', '${escapeQuotes(title)}')" title="Remover da biblioteca">🗑️</button>
                            </div>
                        `;
                    } else if (btn) {
                        btn.outerHTML = `<span class="history-saved-badge">✓ Na Biblioteca</span>`;
                    }"""

if old_save_hist in js:
    js = js.replace(old_save_hist, new_save_hist)
    print("✓ saveHistoryTrackToLibrary atualizado com botões dinâmicos de Mover/Remover!")

# 5. startDropHunterAnalyzer deve checar estritamente djPlayMode === 'drop'
old_start_drop = """        function startDropHunterAnalyzer() {
            if (dropHunterTimer) clearInterval(dropHunterTimer);"""

new_start_drop = """        function startDropHunterAnalyzer() {
            if (djPlayMode !== "drop") {
                stopDropHunterAnalyzer();
                return;
            }
            if (dropHunterTimer) clearInterval(dropHunterTimer);"""

if old_start_drop in js:
    js = js.replace(old_start_drop, new_start_drop)
    print("✓ startDropHunterAnalyzer protegido com verificação estrita de modo!")

# Salvar assets/js/player.js
with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)
print("✓ assets/js/player.js salvo com sucesso!")

# 6. Atualizar player_template.html com cachebuster v=20261116_11
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

template = re.sub(r'assets/css/player\.css\?v=[^\"]+', 'assets/css/player.css?v=20261116_11', template)
template = re.sub(r'assets/js/player\.js\?v=[^\"]+', 'assets/js/player.js?v=20261116_11', template)

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(template)
print("✓ player_template.html atualizado com cachebuster v=20261116_11!")

# 7. Atualizar assets/css/player.css para garantir que .dj-drop-glass-panel não corte texto do rodapé
with open(CSS_PATH, "r", encoding="utf-8") as f:
    css = f.read()

old_glass_panel = """.dj-drop-glass-panel {
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
}"""

new_glass_panel = """.dj-drop-glass-panel {
    width: 100% !important;
    max-width: 100% !important;
    max-height: 100% !important;
    overflow-y: auto !important;
    background: rgba(10, 13, 26, 0.97) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(255, 170, 0, 0.6) !important;
    border-radius: 10px !important;
    padding: 6px 10px !important;
    box-shadow: 0 8px 26px rgba(0, 0, 0, 0.95), 0 0 20px rgba(255, 170, 0, 0.25) !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    box-sizing: border-box !important;
}"""

if old_glass_panel in css:
    css = css.replace(old_glass_panel, new_glass_panel)
    print("✓ .dj-drop-glass-panel otimizado para não cortar texto do rodapé!")

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)
print("✓ assets/css/player.css salvo com sucesso!")
