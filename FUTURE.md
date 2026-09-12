# Ideias para depois

Coisas que valem a pena mas não são para agora. Contexto suficiente para
retomar sem reler a conversa.

## Deploy automatizado (registry + GitHub Actions)

Hoje o deploy é manual e funciona: `sendimage.py` builda, faz `docker save`
e `scp` para o servidor; `loadimage.py` faz `docker load` e recria o serviço.
Sem domínio e sem CI, por decisão.

Quando fizer sentido trocar:

- **Registry**: GitHub Container Registry (`ghcr.io`), gratuito para
  repositório público. Imagens taggeadas com a versão do `commitizen`
  (`sistemapresenca-back:1.0.2`) em vez de `latest`, o que dá rollback
  (`APP_VERSION` no `.env` já existe para isso).
- **Workflow** (`.github/workflows/`): em todo push roda `pytest` e
  `bun run check`; na tag criada pelo `cz bump` builda as duas imagens e faz
  push. Pré-requisito: zerar os erros do `svelte-check` (REVIEW.md, B5), senão
  o check não pode ser bloqueante.
- **Servidor**: `docker compose -f docker-compose-prod.yml pull && up -d`.
  Os dois scripts Python somem. `pull_policy: never` sai do compose de prod.
- **Segredos**: o token do registry no servidor (`docker login ghcr.io`) e o
  `GITHUB_TOKEN` padrão no workflow bastam.

Ordem: registry primeiro (já elimina o `scp`), Actions depois.
