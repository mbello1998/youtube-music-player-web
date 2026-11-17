import json
from pathlib import Path

with open("playlist_categories.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

CATEGORY_ORDER = [
    "Eletrônica",
    "Sertanejo & Forró",
    "Funk & Mega Funk",
    "Trap & Rap",
    "Reggaeton & Latino",
    "Rock & Pop",
    "Outros"
]

CATEGORY_ICONS = {
    "Eletrônica": "⚡",
    "Sertanejo & Forró": "🤠",
    "Funk & Mega Funk": "🔊",
    "Trap & Rap": "🎤",
    "Reggaeton & Latino": "🌴",
    "Rock & Pop": "🎸",
    "Outros": "🎧",
}

# Agrupar por categoria
grouped = {}
for cat in CATEGORY_ORDER:
    grouped[cat] = [t for t in catalog if t.get("category") == cat and t.get("video_id")]

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Músicas do Instagram - Player por Categorias</title>
    <style>
        :root {{
            --bg: #0f0f13;
            --surface: #1a1a24;
            --primary: #ff0050;
            --accent: #00f2fe;
            --text: #ffffff;
            --text-dim: #a0a0b0;
            --border: #2a2a3a;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background: var(--bg); color: var(--text); padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 25px; }}
        .header h1 {{ font-size: 26px; font-weight: 800; background: linear-gradient(45deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }}
        .header p {{ color: var(--text-dim); font-size: 14px; }}
        .tabs {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 25px; }}
        .tab-btn {{ background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 10px 18px; border-radius: 20px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; display: flex; align-items: center; gap: 8px; }}
        .tab-btn:hover {{ background: #252535; border-color: var(--accent); }}
        .tab-btn.active {{ background: linear-gradient(135deg, #ff0055, #ff5500); border-color: transparent; box-shadow: 0 4px 15px rgba(255, 0, 85, 0.4); }}
        .count-badge {{ background: rgba(255, 255, 255, 0.2); font-size: 11px; padding: 2px 7px; border-radius: 10px; }}
        .main-container {{ display: flex; flex-direction: column; gap: 20px; max-width: 1200px; margin: 0 auto; }}
        @media (min-width: 900px) {{
            .main-container {{ flex-direction: row; }}
            .player-pane {{ flex: 1.2; position: sticky; top: 20px; height: fit-content; }}
            .list-pane {{ flex: 1; max-height: 80vh; overflow-y: auto; padding-right: 10px; }}
        }}
        .player-wrapper {{ background: var(--surface); border-radius: 16px; overflow: hidden; border: 1px solid var(--border); padding: 16px; }}
        .video-container {{ position: relative; width: 100%; padding-bottom: 56.25%; border-radius: 12px; overflow: hidden; background: #000; }}
        .video-container iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; }}
        .current-track-info {{ margin-top: 15px; }}
        .current-track-title {{ font-size: 17px; font-weight: 700; }}
        .current-track-artist {{ color: var(--text-dim); font-size: 14px; margin-top: 4px; }}
        .category-actions {{ display: flex; gap: 10px; margin-top: 15px; }}
        .btn-action {{ flex: 1; padding: 10px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; text-decoration: none; text-align: center; font-size: 13px; transition: opacity 0.2s; }}
        .btn-queue {{ background: #2a2a3e; color: #fff; }}
        .btn-yt {{ background: #cc0000; color: #fff; }}
        .btn-action:hover {{ opacity: 0.9; }}
        .track-list {{ display: flex; flex-direction: column; gap: 8px; }}
        .track-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.2s; }}
        .track-card:hover {{ background: #222232; border-color: rgba(255, 255, 255, 0.2); transform: translateX(3px); }}
        .track-card.active {{ border-color: var(--accent); background: rgba(0, 242, 254, 0.08); }}
        .track-meta {{ display: flex; flex-direction: column; gap: 3px; max-width: 80%; }}
        .track-card-title {{ font-size: 14px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .track-card-artist {{ font-size: 12px; color: var(--text-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .play-indicator {{ color: var(--accent); font-size: 18px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Músicas do Instagram</h1>
        <p>Catálogo completo organizado por categorias (Zero dependência da API)</p>
    </div>

    <div class="tabs" id="tabsContainer"></div>

    <div class="main-container">
        <div class="player-pane">
            <div class="player-wrapper">
                <div class="video-container">
                    <iframe id="ytPlayer" src="" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                </div>
                <div class="current-track-info">
                    <div class="current-track-title" id="trackTitle">Selecione uma música</div>
                    <div class="current-track-artist" id="trackArtist">---</div>
                </div>
                <div class="category-actions">
                    <a id="btnQueue" href="#" target="_blank" class="btn-action btn-queue">▶ Tocar Bloco no YouTube</a>
                    <a id="btnYt" href="#" target="_blank" class="btn-action btn-yt">Abrir no YouTube</a>
                </div>
            </div>
        </div>

        <div class="list-pane">
            <div class="track-list" id="trackList"></div>
        </div>
    </div>

    <script>
        const DATA = {json.dumps(grouped, ensure_ascii=False)};
        const ICONS = {json.dumps(CATEGORY_ICONS, ensure_ascii=False)};
        const CATEGORIES = {json.dumps(CATEGORY_ORDER, ensure_ascii=False)};

        let currentCategory = CATEGORIES[0];
        let currentVideoId = null;

        function initTabs() {{
            const tabsContainer = document.getElementById("tabsContainer");
            tabsContainer.innerHTML = "";
            CATEGORIES.forEach(cat => {{
                const list = DATA[cat] || [];
                if (list.length === 0) return;
                const btn = document.createElement("button");
                btn.className = `tab-btn ${{cat === currentCategory ? "active" : ""}}`;
                btn.innerHTML = `<span>${{ICONS[cat] || "🎵"}} ${{cat}}</span><span class="count-badge">${{list.length}}</span>`;
                btn.onclick = () => selectCategory(cat);
                tabsContainer.appendChild(btn);
            }});
        }}

        function selectCategory(cat) {{
            currentCategory = cat;
            initTabs();
            renderList();
            updateQueueButton();
            const list = DATA[cat] || [];
            if (list.length > 0) {{
                playTrack(list[0]);
            }}
        }}

        function renderList() {{
            const listContainer = document.getElementById("trackList");
            listContainer.innerHTML = "";
            const tracks = DATA[currentCategory] || [];

            tracks.forEach((t, index) => {{
                const card = document.createElement("div");
                card.className = `track-card ${{t.video_id === currentVideoId ? "active" : ""}}`;
                card.onclick = () => playTrack(t);

                card.innerHTML = `
                    <div class="track-meta">
                        <div class="track-card-title">${{index + 1}}. ${{t.title}}</div>
                        <div class="track-card-artist">${{t.artist}}</div>
                    </div>
                    <div class="play-indicator">▶</div>
                `;
                listContainer.appendChild(card);
            }});
        }}

        function playTrack(track) {{
            currentVideoId = track.video_id;
            document.getElementById("ytPlayer").src = `https://www.youtube.com/embed/${{track.video_id}}?autoplay=1`;
            document.getElementById("trackTitle").textContent = track.title;
            document.getElementById("trackArtist").textContent = track.artist;
            document.getElementById("btnYt").href = `https://www.youtube.com/watch?v=${{track.video_id}}`;
            renderList();
        }}

        function updateQueueButton() {{
            const tracks = DATA[currentCategory] || [];
            if (tracks.length === 0) return;
            const ids = tracks.map(t => t.video_id).filter(Boolean).slice(0, 50).join(",");
            document.getElementById("btnQueue").href = `https://www.youtube.com/watch_videos?video_ids=${{ids}}`;
        }}

        // Inicializar
        initTabs();
        selectCategory("Eletrônica");
    </script>
</body>
</html>
"""

with open("player.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("player.html gerado com sucesso!")
