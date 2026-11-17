# Instagram → YouTube Playlist

Pega as músicas que você salvou no Instagram e organiza numa playlist do YouTube. Veja `DESIGN.md` para o design completo.

## Instalação

```bash
pip install -r requirements.txt
```

(`yt-dlp` e `ffmpeg` já precisam estar instalados na máquina — eles não estão no `requirements.txt` porque já são pré-requisitos.)

## Configuração única

### 1. Credencial do YouTube (Google Cloud)

1. Crie um projeto em https://console.cloud.google.com/ (ou use um existente).
2. Ative a "YouTube Data API v3" nesse projeto.
3. Crie uma credencial OAuth do tipo "Desktop app".
4. Baixe o JSON gerado e salve como `client_secret.json` na raiz deste projeto.

Isso pode ser feito manualmente no navegador, ou pedindo pro Claude pilotar essas telas pelo Chrome que você já tem aberto (ver `DESIGN.md`).

Na primeira execução (`python -m igtoyt.main`), uma aba do navegador vai abrir pedindo pra você autorizar o acesso à sua conta do YouTube. Depois disso, o token fica salvo em `token.json` e não pede de novo.

### 2. Sessão do Instagram

O script tenta ler automaticamente o cookie de sessão do Instagram direto do seu Chrome (com o Chrome **fechado**, não só minimizado). Em versões recentes do Chrome no Windows isso pode falhar por conta de uma proteção do próprio navegador (App-Bound Encryption) — nesse caso, o script avisa e você precisa:

1. Instalar uma extensão do Chrome como "Get cookies.txt LOCALLY".
2. Estar logado em instagram.com no Chrome.
3. Exportar os cookies de instagram.com como `cookies.txt` e salvar na raiz deste projeto.

Com o arquivo presente, o script usa ele automaticamente como alternativa.

## Como rodar

```bash
python -m igtoyt.main
```

Ao final, imprime um resumo:

```
Adicionadas: N
Adicionadas por palpite (confira): N
Fotos ignoradas: N
Não identificadas: N
Não encontradas no YouTube: N
```

Rodar de novo só processa os posts salvos que ainda não tinham sido vistos (controle em `processed.json`).
