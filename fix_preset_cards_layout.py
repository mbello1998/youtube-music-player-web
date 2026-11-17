import re
import os

print("Aplicando correção no layout dos Presets Acústicos do Equalizador...")

# -------------------------------------------------------------
# 1. ATUALIZAR player_template.html COM A ESTRUTURA .eq-preset-info
# -------------------------------------------------------------
with open("player_template.html", "r", encoding="utf-8") as f:
    template_html = f.read()

# Atualizar canvas para height="60"
template_html = template_html.replace(
    '<canvas id="eqCurveCanvas" width="680" height="75" class="eq-curve-canvas"></canvas>',
    '<canvas id="eqCurveCanvas" width="680" height="60" class="eq-curve-canvas"></canvas>'
)

# Atualizar o bloco dos 14 presets com <div class="eq-preset-info">
old_presets_block_pattern = r'<div class="eq-presets-grid-scroll">.*?</div>\s*<!-- Equalizador Gráfico'
new_presets_block = '''<div class="eq-presets-grid-scroll">
                <div class="eq-preset-card" id="eqCard_padrao" onclick="selectEqPreset('padrao')">
                    <span class="eq-preset-icon">🎵</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Padrão (Flat)</span>
                        <span class="eq-preset-desc">Original de estúdio</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_grave" onclick="selectEqPreset('grave')">
                    <span class="eq-preset-icon">💥</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Mega Bass / 808</span>
                        <span class="eq-preset-desc">Subwoofer & batidas</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_funk" onclick="selectEqPreset('funk')">
                    <span class="eq-preset-icon">🔥</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Funk & Mandelão</span>
                        <span class="eq-preset-desc">Punch no kick & caixa</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_balada" onclick="selectEqPreset('balada')">
                    <span class="eq-preset-icon">⚡</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Balada / Club</span>
                        <span class="eq-preset-desc">Curva em V com pressão</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_eletronica" onclick="selectEqPreset('eletronica')">
                    <span class="eq-preset-icon">🌀</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">House & Desande</span>
                        <span class="eq-preset-desc">Sub firme & agudo limpo</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_cumbia" onclick="selectEqPreset('cumbia')">
                    <span class="eq-preset-icon">🎺</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Cumbia & Charanga</span>
                        <span class="eq-preset-desc">Médios quentes & chimbais</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_gaucho" onclick="selectEqPreset('gaucho')">
                    <span class="eq-preset-icon">🤠</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Gaúcho & Vanera</span>
                        <span class="eq-preset-desc">Bombo & acordeom brilhante</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_trap" onclick="selectEqPreset('trap')">
                    <span class="eq-preset-icon">🎤</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Trap & 808 Slide</span>
                        <span class="eq-preset-desc">Subwoofer & voz seca</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_voz" onclick="selectEqPreset('voz')">
                    <span class="eq-preset-icon">🎙️</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Vocal Cristalino</span>
                        <span class="eq-preset-desc">Voz em destaque & clareza</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_fone" onclick="selectEqPreset('fone')">
                    <span class="eq-preset-icon">🎧</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Fone de Ouvido</span>
                        <span class="eq-preset-desc">Curva Harman estéreo</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_sala" onclick="selectEqPreset('sala')">
                    <span class="eq-preset-icon">🏛️</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Sala / Espacial</span>
                        <span class="eq-preset-desc">Palco sonoro amplo</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_rock" onclick="selectEqPreset('rock')">
                    <span class="eq-preset-icon">🎸</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Rock & Guitarras</span>
                        <span class="eq-preset-desc">Médios para cordas & ataque</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_acustico" onclick="selectEqPreset('acustico')">
                    <span class="eq-preset-icon">🪕</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Acústico & Cordas</span>
                        <span class="eq-preset-desc">Timbre quente natural</span>
                    </div>
                </div>
                <div class="eq-preset-card" id="eqCard_claridade" onclick="selectEqPreset('claridade')">
                    <span class="eq-preset-icon">✨</span>
                    <div class="eq-preset-info">
                        <span class="eq-preset-name">Máxima Definição</span>
                        <span class="eq-preset-desc">Air & agudos estendidos</span>
                    </div>
                </div>
            </div>

            <!-- Equalizador Gráfico'''

template_html, count_p = re.subn(old_presets_block_pattern, new_presets_block, template_html, flags=re.DOTALL)
print(f"player_template.html: Presets atualizados com .eq-preset-info ({count_p} ocorrência)")

with open("player_template.html", "w", encoding="utf-8") as f:
    f.write(template_html)


# -------------------------------------------------------------
# 2. ATUALIZAR assets/css/player.css COM CSS ANTI-COLAPSO & CARD ROW
# -------------------------------------------------------------
with open("assets/css/player.css", "r", encoding="utf-8") as f:
    css = f.read()

# Substituir bloco do equalizador modal
old_css_pro_pattern = r'\.eq-modal-card\.eq-modal-pro\s*\{.*?\.eq-bars-row-10\s*\.eq-slider-vertical\s*\{.*?\}'
new_css_pro = '''.eq-modal-card.eq-modal-pro {
            max-width: 760px !important;
            max-height: 94vh !important;
            overflow-y: auto !important;
            padding: 16px 20px !important;
            scrollbar-width: thin !important;
            scrollbar-color: rgba(0, 242, 254, 0.3) rgba(0, 0, 0, 0.2) !important;
            gap: 10px !important;
        }
        .eq-modal-card.eq-modal-pro > * {
            flex-shrink: 0 !important;
        }
        .eq-modal-card.eq-modal-pro::-webkit-scrollbar {
            width: 6px;
        }
        .eq-modal-card.eq-modal-pro::-webkit-scrollbar-thumb {
            background: rgba(0, 242, 254, 0.3);
            border-radius: 4px;
        }
        .eq-badge-mode {
            font-size: 9.5px;
            font-weight: 800;
            background: linear-gradient(135deg, #00f2fe, #ff0055);
            color: #fff;
            padding: 2px 7px;
            border-radius: 4px;
            letter-spacing: 0.5px;
            margin-left: 6px;
        }
        .btn-eq-reset {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #cbd5e1;
            font-size: 11px;
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        .btn-eq-reset:hover {
            background: rgba(0, 242, 254, 0.15);
            border-color: var(--accent);
            color: var(--accent);
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
        }
        .eq-curve-container {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(0, 242, 254, 0.25);
            border-radius: 10px;
            padding: 6px 12px 8px 12px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);
            flex-shrink: 0 !important;
        }
        .eq-curve-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .eq-curve-title {
            font-size: 11px;
            font-weight: 700;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .eq-curve-tag {
            font-size: 10.5px;
            font-weight: 800;
            color: #00f2fe;
            background: rgba(0, 242, 254, 0.12);
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid rgba(0, 242, 254, 0.3);
        }
        .eq-curve-canvas {
            width: 100%;
            height: 60px;
            border-radius: 6px;
            background: #070913;
            display: block;
        }
        .eq-section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1px;
            flex-shrink: 0 !important;
        }
        .eq-section-hint {
            font-size: 10.5px;
            color: var(--text-dim);
        }
        .eq-presets-grid-scroll {
            display: grid !important;
            grid-template-columns: repeat(auto-fill, minmax(155px, 1fr)) !important;
            gap: 7px !important;
            max-height: 138px !important;
            min-height: 125px !important;
            overflow-y: auto !important;
            padding-right: 4px !important;
            flex-shrink: 0 !important;
            scrollbar-width: thin !important;
            scrollbar-color: rgba(0, 242, 254, 0.35) rgba(0, 0, 0, 0.2) !important;
        }
        .eq-presets-grid-scroll::-webkit-scrollbar {
            width: 5px;
        }
        .eq-presets-grid-scroll::-webkit-scrollbar-thumb {
            background: rgba(0, 242, 254, 0.35);
            border-radius: 4px;
        }
        .eq-preset-card {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            padding: 5px 9px !important;
            cursor: pointer !important;
            text-align: left !important;
            transition: all 0.18s ease !important;
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 8px !important;
            height: 38px !important;
            min-height: 38px !important;
            box-sizing: border-box !important;
            overflow: hidden !important;
            flex-shrink: 0 !important;
        }
        .eq-preset-card:hover {
            background: var(--surface-hover) !important;
            border-color: rgba(0, 242, 254, 0.45) !important;
            transform: translateY(-1px) !important;
        }
        .eq-preset-card.active {
            background: rgba(0, 242, 254, 0.15) !important;
            border-color: var(--accent) !important;
            box-shadow: 0 0 12px rgba(0, 242, 254, 0.3) !important;
        }
        .eq-preset-icon {
            font-size: 17px !important;
            flex-shrink: 0 !important;
            line-height: 1 !important;
        }
        .eq-preset-info {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            min-width: 0 !important;
            overflow: hidden !important;
            line-height: 1.15 !important;
        }
        .eq-preset-name {
            font-size: 11px !important;
            font-weight: 700 !important;
            color: #fff !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        .eq-preset-desc {
            font-size: 9px !important;
            color: var(--text-dim) !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        .eq-preamp-wrap {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 3px 10px;
            border-radius: 6px;
        }
        .preamp-slider {
            width: 85px;
            cursor: pointer;
            accent-color: var(--accent);
            height: 5px;
        }
        .preamp-val {
            font-size: 11px;
            font-weight: 800;
            color: var(--accent);
            min-width: 44px;
            text-align: right;
        }
        .eq-bars-row-10 {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0, 0, 0, 0.4);
            padding: 8px 6px;
            border-radius: 10px;
            border: 1px solid var(--border);
            gap: 4px;
            flex-shrink: 0 !important;
        }
        .eq-bars-row-10 .eq-bar-col {
            flex: 1;
            min-width: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
        }
        .eq-bars-row-10 .eq-slider-vertical {
            -webkit-appearance: slider-vertical;
            writing-mode: bt-lr;
            width: 12px;
            height: 72px;
            cursor: pointer;
            accent-color: var(--accent);
        }'''

css, count_c = re.subn(old_css_pro_pattern, new_css_pro, css, flags=re.DOTALL)
print(f"assets/css/player.css: Regras CSS Pro atualizadas ({count_c} ocorrência)")

with open("assets/css/player.css", "w", encoding="utf-8") as f:
    f.write(css)

print("Arquivos atualizados com sucesso!")
