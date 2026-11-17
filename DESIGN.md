# Instagram → YouTube Playlist — Design

## Intent
Pegar as músicas que o usuário salvou no Instagram (posts/reels salvos) e organizá-las numa playlist do YouTube, para ele poder ouvir fora do Instagram. Uso pessoal, roda local no PC do usuário, usando as contas já logadas no Chrome.

## Goals
- Listar os posts/reels salvos na conta do Instagram do usuário.
- Para cada um, descobrir o nome da música (e artista, quando possível).
  - Quando o Instagram já expõe o nome da faixa de áudio (reels com áudio da biblioteca do Instagram), usar isso.
  - Quando não expõe (áudio original/sem atribuição), identificar por reconhecimento de áudio (fingerprint, como o Shazam faz).
- Buscar cada música no YouTube e adicionar o melhor resultado a uma playlist do YouTube do usuário.
- Rodar de novo no futuro sem duplicar o que já foi processado.

## Non-goals
- Não é um app contínuo monitorando novos salvos em tempo real (pode rodar quando o usuário quiser, mas não fica de pé 24/7).
- Não garante 100% de acerto na identificação — reconhecimento de áudio e busca no YouTube têm margem de erro; o script reporta o que não conseguiu identificar/casar em vez de inventar.
- Não lida com milhares de itens salvos de uma vez por conta dos limites de cota da API do YouTube (ver Constraints).

## Anti-goals (seria falha mesmo funcionando)
- Vazar/expor as credenciais ou sessão do Instagram/Google do usuário.
- Disparar um bloqueio/checkpoint na conta do Instagram do usuário por excesso de requisições.

## Constraints
- **Cota da API do YouTube**: `search.list` custa 100 unidades, cota diária grátis é 10.000 unidades — isso limitaria a ~100 músicas/dia se cada busca fosse pela API oficial. Mitigação: usar `yt-dlp` (busca `ytsearch1:`) para achar o vídeo no YouTube (sem custo de cota), e usar a API oficial do Google só pra criar a playlist e inserir os itens (operação de escrita, mais barata e é a única parte que realmente precisa de OAuth).
- **Instagram não tem API pública para "salvos"**: usar `instaloader`, que sabe listar e baixar a coleção de salvos (`:saved`) de uma conta autenticada.
- **Autenticação sem login programático**: em vez de instaloader fazer login (risco de checkpoint/2FA), vamos reaproveitar o cookie de sessão já ativo do Instagram no Chrome do usuário (ele já está logado). Isso evita um login automatizado "suspeito" do ponto de vista do Instagram.
- **OAuth do YouTube**: precisa de um client OAuth (projeto no Google Cloud Console, API do YouTube Data v3 habilitada). É configuração única; depois disso o token fica salvo e reutilizável.

## Approaches (decidido na conversa)
Foram consideradas: (A) tudo via automação de navegador, (B) pipeline em script Python com yt-dlp + instaloader + shazamio + YouTube Data API, (C) híbrido. O usuário escolheu B pela confiabilidade e por poder rodar de novo depois.

## Pipeline (como vai funcionar)
1. **Extrair sessão do Instagram**: ler o cookie `sessionid` do Instagram direto do seu Chrome (via o mecanismo de leitura de cookies do navegador) e montar uma sessão do `instaloader` com ele — sem pedir usuário/senha.
   - Se a extração automática falhar (o Chrome às vezes cifra cookies de um jeito que bloqueia isso), o fallback é você exportar um `cookies.txt` com uma extensão do Chrome tipo "Get cookies.txt LOCALLY" (1 clique) e me passar o arquivo.
2. **Listar os salvos**: `instaloader` baixa a lista de posts/reels da sua coleção de salvos (metadados + vídeo), com uma pausa entre pedidos pra não levantar suspeita de bot.
3. **Achar o nome da música** (tenta todos os modos antes de desistir, na ordem — pedido explícito do usuário: "tenta usar tudo que é modo"):
   1. Metadados do próprio post (quando o reel usa áudio da biblioteca do Instagram, vem o nome da faixa e do artista).
   2. Se não tiver, extrai o áudio do vídeo com `ffmpeg` e identifica com `shazamio` (biblioteca gratuita que consulta o mesmo tipo de serviço do Shazam).
   3. Se o fingerprint não bater, tenta uma busca textual (Google/YouTube Music) usando a legenda do post e as hashtags como pista, pra ver se dá pra inferir o nome da faixa a partir do texto.
   4. Se nem isso achar, a música entra numa lista de "não identificadas" no final, pra você decidir manualmente.
4. **Achar no YouTube**: pesquisa "nome da música + artista" usando `yt-dlp` (`ytsearch1:`), sem gastar cota da API.
5. **Playlist no YouTube**: login único via navegador (OAuth, já logado na sua conta Google), cria a playlist (ou usa uma que você já tenha) e insere cada vídeo achado.
6. **Controle de duplicado**: guarda localmente (arquivo `processed.json`) quais posts do Instagram já foram processados, pra poder rodar de novo só pegando os salvos novos.
7. **Relatório final**: quantas músicas foram adicionadas, quais não foram identificadas, quais não foram achadas no YouTube.

## Decisões tomadas (o usuário pode corrigir)
- Nome da playlist nova: "Músicas do Instagram" — a confirmar, ou usar uma playlist já existente.
- Config do OAuth do Google Cloud (criar projeto, habilitar API, gerar credencial "Desktop app"): proposta é pilotar isso pelo Chrome do usuário (automação de navegador), já que ele topa — a confirmar.
- Stack: Python (já tem no PC: Python 3.15, `yt-dlp`, `ffmpeg`). Será instalado via pip: `instaloader`, `shazamio`, `google-api-python-client`, `google-auth-oauthlib`.
- Tudo roda localmente, nada sobe pra servidor nenhum.

## O que fica a cargo de quem for construir
- Tratamento de erros, formato exato dos logs/relatório.
- Lógica de rate-limit/retry do instaloader e do shazamio.
- Estrutura dos arquivos do projeto.
