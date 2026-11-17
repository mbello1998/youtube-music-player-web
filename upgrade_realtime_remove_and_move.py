# -*- coding: utf-8 -*-
"""
upgrade_realtime_remove_and_move.py
Aprimora os fluxos de Remover e Mover para atualização 100% em tempo real com modal in-app e persistência imediata.
"""

import re
from pathlib import Path

SERVER_PATH = Path("server.py")
TEMPLATE_PATH = Path("player_template.html")
CSS_PATH = Path("assets/css/player.css")
JS_PATH = Path("assets/js/player.js")

# =========================================================================
# 1. ATUALIZAR SERVER.PY
# =========================================================================
with open(SERVER_PATH, "r", encoding="utf-8") as f:
    server_code = f.read()

old_server_remove = """            if self.path == "/api/library/remove":
                video_id = data.get("video_id")
                category = data.get("category")
                if not video_id:
                    self.send_json({"error": "video_id required"}, status=400)
                    return

                lib = []
                if LIBRARY_FILE.exists():
                    try:
                        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                            lib = json.load(f)
                    except Exception:
                        lib = []

                initial_len = len(lib)
                if category:
                    lib = [t for t in lib if not (t.get("video_id") == video_id and t.get("category") == category)]
                else:
                    lib = [t for t in lib if t.get("video_id") != video_id]

                removed_count = initial_len - len(lib)
                try:
                    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
                        json.dump(lib, f, ensure_ascii=False, indent=2)
                except Exception as err:
                    print("Erro ao salvar complete_library.json na remoção:", err)

                self.send_json({
                    "success": True,
                    "removed_count": removed_count,
                    "video_id": video_id,
                    "count": len(lib)
                })
                return"""

new_server_remove = """            if self.path == "/api/library/remove":
                video_id = data.get("video_id")
                category = data.get("category")
                if not video_id:
                    self.send_json({"error": "video_id required"}, status=400)
                    return

                lib = []
                if LIBRARY_FILE.exists():
                    try:
                        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                            lib = json.load(f)
                    except Exception:
                        lib = []

                initial_len = len(lib)
                # Remove incondicionalmente por video_id para garantir que nunca falhe por divergência de categoria
                lib = [t for t in lib if t.get("video_id") != video_id]
                removed_count = initial_len - len(lib)

                try:
                    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
                        json.dump(lib, f, ensure_ascii=False, indent=2)
                except Exception as err:
                    print("Erro ao salvar complete_library.json na remoção:", err)

                # Rebuild assíncrono para manter player.html sempre atualizado em disco
                try:
                    import subprocess
                    subprocess.Popen(["python", "build_full_player.py"], shell=False)
                except Exception as b_err:
                    print("Aviso ao rebuildar player.html:", b_err)

                self.send_json({
                    "success": True,
                    "removed_count": removed_count,
                    "video_id": video_id,
                    "count": len(lib)
                })
                return"""

old_server_move = """            if self.path == "/api/library/move":
                video_id = data.get("video_id")
                new_category = data.get("new_category")
                old_category = data.get("old_category")
                if not video_id or not new_category:
                    self.send_json({"error": "video_id and new_category required"}, status=400)
                    return

                lib = []
                if LIBRARY_FILE.exists():
                    try:
                        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                            lib = json.load(f)
                    except Exception:
                        lib = []

                moved = False
                for t in lib:
                    if t.get("video_id") == video_id:
                        if not old_category or t.get("category") == old_category:
                            t["category"] = new_category
                            moved = True
                            break

                if moved:
                    try:
                        with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
                            json.dump(lib, f, ensure_ascii=False, indent=2)
                    except Exception as err:
                        print("Erro ao salvar complete_library.json na mudança de categoria:", err)

                self.send_json({
                    "success": moved,
                    "video_id": video_id,
                    "new_category": new_category,
                    "count": len(lib)
                })
                return"""

new_server_move = """            if self.path == "/api/library/move":
                video_id = data.get("video_id")
                new_category = data.get("new_category")
                old_category = data.get("old_category")
                if not video_id or not new_category:
                    self.send_json({"error": "video_id and new_category required"}, status=400)
                    return

                lib = []
                if LIBRARY_FILE.exists():
                    try:
                        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                            lib = json.load(f)
                    except Exception:
                        lib = []

                moved = False
                # 1. Tenta correspondência exata ou por old_category
                for t in lib:
                    if t.get("video_id") == video_id:
                        if not old_category or str(t.get("category")).strip() == str(old_category).strip():
                            t["category"] = new_category
                            moved = True
                            break

                # 2. Fallback: encontra qualquer entrada com video_id e atualiza a categoria
                if not moved:
                    for t in lib:
                        if t.get("video_id") == video_id:
                            t["category"] = new_category
                            moved = True
                            break

                if moved:
                    try:
                        with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
                            json.dump(lib, f, ensure_ascii=False, indent=2)
                    except Exception as err:
                        print("Erro ao salvar complete_library.json na mudança de categoria:", err)

                    try:
                        import subprocess
                        subprocess.Popen(["python", "build_full_player.py"], shell=False)
                    except Exception as b_err:
                        print("Aviso ao rebuildar player.html:", b_err)

                self.send_json({
                    "success": moved,
                    "video_id": video_id,
                    "new_category": new_category,
                    "count": len(lib)
                })
                return"""

if old_server_remove in server_code:
    server_code = server_code.replace(old_server_remove, new_server_remove)
    print("✓ server.py: endpoint /api/library/remove atualizado com robustez e auto-rebuild!")
else:
    print("! old_server_remove não encontrado exato em server.py!")

if old_server_move in server_code:
    server_code = server_code.replace(old_server_move, new_server_move)
    print("✓ server.py: endpoint /api/library/move atualizado com robustez e auto-rebuild!")
else:
    print("! old_server_move não encontrado exato em server.py!")

with open(SERVER_PATH, "w", encoding="utf-8") as f:
    f.write(server_code)

# =========================================================================
# 2. ATUALIZAR PLAYER_TEMPLATE.HTML (MODAL DE CONFIRMAÇÃO IN-APP E CACHEBUSTER)
# =========================================================================
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

# Modal in-app de confirmação de exclusão
confirm_modal_html = """
    <!-- MODAL DE CONFIRMAÇÃO DE REMOÇÃO DA BIBLIOTECA -->
    <div class="eq-modal-overlay" id="confirmRemoveModal" onclick="closeConfirmRemoveModal(event)">
        <div class="eq-modal-card remove-modal-card" onclick="event.stopPropagation()">
            <div class="eq-modal-header">
                <div class="eq-modal-title">
                    <span style="color: #ff3366;">🗑️ Remover da Biblioteca</span>
                </div>
                <button class="eq-close-btn" onclick="closeConfirmRemoveModal()" title="Fechar" aria-label="Fechar"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></button>
            </div>
            <div class="remove-modal-body">
                <p class="remove-modal-prompt">Tem certeza que deseja remover esta música da sua biblioteca?</p>
                <div class="remove-track-preview-box">
                    <div class="remove-track-thumb-wrap">
                        <img id="removeModalThumb" src="" class="remove-track-thumb" alt="Capa" onerror="this.src=window.DEFAULT_COVER_SVG">
                    </div>
                    <div class="remove-track-info">
                        <div class="remove-modal-title-text" id="removeModalTrackTitle">Título da Música</div>
                        <div class="remove-modal-artist-text" id="removeModalTrackArtist">Artista</div>
                        <div class="remove-modal-cat-text">Playlist: <span id="removeModalCurrentCat" style="color: var(--accent);">Gênero</span></div>
                    </div>
                </div>
            </div>
            <div class="queue-modal-footer remove-modal-footer">
                <button type="button" class="btn-modal-cancel-remove" onclick="closeConfirmRemoveModal()">Cancelar</button>
                <button type="button" class="btn-modal-confirm-remove" id="btnConfirmDeleteTrack" onclick="executeRemoveLibraryTrack()">🗑️ Sim, Remover</button>
            </div>
        </div>
    </div>
"""

if 'id="confirmRemoveModal"' not in template:
    target_place = '</div>\n    </div>\n\n</body>'
    replace_place = '</div>\n    </div>\n' + confirm_modal_html + '\n</body>'
    if target_place in template:
        template = template.replace(target_place, replace_place)
        print("✓ Modal #confirmRemoveModal adicionado a player_template.html!")
    else:
        template = template.replace('</body>', confirm_modal_html + '\n</body>')
        print("✓ Modal #confirmRemoveModal adicionado antes de </body>!")

# Cachebuster v=20261116_12
template = re.sub(r'assets/css/player\.css\?v=[^\"]+', 'assets/css/player.css?v=20261116_12', template)
template = re.sub(r'assets/js/player\.js\?v=[^\"]+', 'assets/js/player.js?v=20261116_12', template)

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(template)

# =========================================================================
# 3. ATUALIZAR ASSETS/CSS/PLAYER.CSS
# =========================================================================
with open(CSS_PATH, "r", encoding="utf-8") as f:
    css = f.read()

remove_modal_css = """
/* ==========================================================================
   MODAL DE CONFIRMAÇÃO DE REMOÇÃO DA BIBLIOTECA
   ========================================================================== */
.remove-modal-card {
    max-width: 480px !important;
    border: 1px solid rgba(255, 51, 102, 0.45) !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.9), 0 0 25px rgba(255, 51, 102, 0.25) !important;
}

.remove-modal-prompt {
    font-size: 13.5px !important;
    color: #e2e8f0 !important;
    margin-bottom: 14px !important;
    line-height: 1.4 !important;
}

.remove-track-preview-box {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    background: rgba(255, 51, 102, 0.08) !important;
    border: 1px solid rgba(255, 51, 102, 0.25) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}

.remove-track-thumb-wrap {
    width: 48px !important;
    height: 48px !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    flex-shrink: 0 !important;
}

.remove-track-thumb {
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
}

.remove-track-info {
    flex: 1 !important;
    min-width: 0 !important;
}

.remove-modal-title-text {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #fff !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

.remove-modal-artist-text {
    font-size: 11.5px !important;
    color: var(--text-dim) !important;
}

.remove-modal-cat-text {
    font-size: 11px !important;
    color: #a0aec0 !important;
    margin-top: 2px !important;
}

.remove-modal-footer {
    display: flex !important;
    justify-content: flex-end !important;
    gap: 10px !important;
    margin-top: 18px !important;
}

.btn-modal-cancel-remove {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: var(--text) !important;
    padding: 8px 18px !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
}

.btn-modal-cancel-remove:hover {
    background: rgba(255, 255, 255, 0.16) !important;
}

.btn-modal-confirm-remove {
    background: linear-gradient(135deg, #ff0055, #ff3366) !important;
    border: none !important;
    color: #fff !important;
    padding: 8px 20px !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    cursor: pointer !important;
    box-shadow: 0 4px 14px rgba(255, 0, 85, 0.4) !important;
    transition: all 0.2s !important;
}

.btn-modal-confirm-remove:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(255, 0, 85, 0.6) !important;
}

/* Transições fluidas em tempo real ao remover e mover */
.track-card.anim-removing {
    opacity: 0 !important;
    transform: translateX(45px) scale(0.96) !important;
    transition: all 0.32s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.track-card.anim-moving {
    opacity: 0 !important;
    transform: translateX(-45px) scale(0.96) !important;
    transition: all 0.32s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
"""

if '.remove-modal-card' not in css:
    css += remove_modal_css
    print("✓ CSS para modal de remoção e animações em tempo real adicionado!")

with open(CSS_PATH, "w", encoding="utf-8") as f:
    f.write(css)

# =========================================================================
# 4. ATUALIZAR ASSETS/JS/PLAYER.JS (RESOLVEDOR FLEXÍVEL & ATUALIZAÇÃO REAL-TIME)
# =========================================================================
with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# Substituir o bloco de mover e remover pelo motor atualizado
old_move_remove_block_pattern = r"// GERENCIADOR DE PLAYLISTS & BIBLIOTECA[\s\S]*?window\.removeLibraryTrackPrompt = removeLibraryTrackPrompt;"

new_move_remove_block = """// ==========================================================================
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
        window.executeRemoveLibraryTrack = executeRemoveLibraryTrack;"""

if re.search(old_move_remove_block_pattern, js):
    js = re.sub(old_move_remove_block_pattern, lambda m: new_move_remove_block, js, count=1)
    print("✓ assets/js/player.js: Bloco de mover e remover atualizado com animação em tempo real e resolvedor universal!")
else:
    print("! old_move_remove_block_pattern não encontrado!")

# Atualizar chamadas nos cards do histórico para usar as novas funções com segurança
js = js.replace(
    "onclick=\"removeLibraryTrackPrompt('${track.video_id}', '${escapeQuotes(track.title)}')\"",
    "onclick=\"openConfirmRemoveModal(null, null, '${track.video_id}')\""
)
js = js.replace(
    "onclick=\"removeLibraryTrackPrompt('${videoId}', '${escapeQuotes(title)}')\"",
    "onclick=\"openConfirmRemoveModal(null, null, '${videoId}')\""
)

with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)
print("✓ assets/js/player.js salvo com sucesso!")
