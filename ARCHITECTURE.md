# Arquitetura — Sistema de Presença

Sistema de registro de presença por QR Code, com painel ao vivo (fotos flutuantes dos presentes) e placar de pontuação. Pensado para eventos recorrentes de uma comunidade (ex.: Escola Sabatina).

## Visão geral

- **Front-end**: SvelteKit (Svelte 5, runes) + Tailwind CSS 4, build estático (`adapter-static`, fallback SPA, `ssr = false`). Em `front/`.
- **Back-end**: Django 6 + Django Ninja (API REST) + Django Channels/Daphne (WebSocket). Em `back/`. Gerenciado com `uv` (`back/pyproject.toml`, `back/uv.lock`), Python ≥ 3.12.
- **Banco**: SQLite (`db.sqlite3` na raiz do repositório, montado no container).
- **Proxy**: Caddy roteia `/api/*`, `/ws*`, `/media/*` para o back e serve o build estático do front. Config em `docker/Caddyfile`.
- **Deploy**: Docker Compose (`docker-compose-dev.yml`, `docker-compose-prod.yml`, `docker-compose-test.yml`).
- **Protótipos**: `prototypes/` guarda HTML/CSS/JS puros de cada tela (ver `prototypes/README.md`). A `CONSTITUTION.md` exige que protótipo e tela nunca divirjam.

## Fluxo principal (check-in por QR Code)

1. Administrador abre a página inicial (`front/src/routes/+page.svelte`), digita o nome do evento (padrão "Escola Sabatina") e aperta Enter.
2. O front abre um WebSocket em `/ws` (`front/src/lib/websocket/socket.ts`) e envia `{type: "joinEvent", event: <nome>}`.
3. O `Consumer` (`back/presenca/consumer.py`) busca o `Event` pelo nome exato, adiciona a conexão ao grupo do evento (`Event.as_websocket_group_name()`), registra a conexão no `CodeTimerRegistry` (`back/presenca/code_timer.py`) e envia `{type: "newCode", code: <uuid>, expiresAt: <ISO 8601>}` com o código corrente do evento (`CodeController.get_current_code`, que reutiliza o último código com idade menor que a rotação ou cria um novo).
4. O `CodeTimerRegistry` mantém **uma thread por evento** que gera um código novo a cada `Code.rotation_seconds()` e o difunde ao grupo. Primeiro ouvinte do grupo inicia a thread; o último a encerra. O intervalo de rotação vem da tabela `Config` (key `CODE_ROTATION_SECONDS`, editável no admin em runtime; seed de 60s na migração 0014, linha recriada automaticamente se apagada). Cada código vale pela rotação + 20s de folga (`Code.validity_seconds()`), para não invalidar quem escaneou perto da troca. **Várias pessoas podem escanear o mesmo código** — ele não é consumido no scan. O `expiresAt` enviado ao painel é `Code.rotates_at()` (fim da rotação), não o fim da validade: a folga fica invisível.
5. O front embute o código no QR Code (`QrCode.svelte`), apontando para `<origem atual>/checkin/<code>`, e o re-renderiza a cada `newCode`. Um anel SVG ao redor do QR drena até `expiresAt`.
6. A pessoa escaneia e abre `/checkin/[code]`. O front chama `GET /api/checkin/pending/<code>`, que valida o código (expirado → 400, inexistente → 404) e retorna `{id, name}` dos membros que ainda não fizeram check-in hoje no evento do código (`Member.didnt_checkin_today`).
7. A pessoa seleciona seu nome e o front chama `POST /api/checkin/<code>/<member_id>`. O back:
   - valida que o código ainda está na janela de validade;
   - se o membro já tem check-in hoje nesse evento, devolve os pontos do check-in existente sem criar nada nem notificar o painel (`CheckinController.checkin`);
   - senão cria o `CheckIn` (`CheckIn.create_idempotent`) com horário `timezone.now()`;
   - emite `{type: "memberCheckin", member: {name, photo, birthday}}` para o grupo do evento;
   - calcula pontos por horário via `TimeScoreRules.get_points_for_time_in_event` (0 se o evento não tem regra ou o horário está fora de todas as faixas) e retorna ao cliente.
8. Na tela do celular, após o sucesso, o front mostra a animação de pontos e redireciona em 3s para uma URL externa de quiz (hardcoded em `routes/checkin/[code]/+page.svelte`).
9. No painel, o evento `memberCheckin` adiciona a foto/nome do membro ao componente `Phloating` (fotos flutuando pela tela; quem está na semana do aniversário ganha chapéu de festa e confete). Ao conectar, o painel repopula o `Phloating` com `GET /api/checkin/already/<evento>` e carrega o placar com `GET /api/score/event/<evento>` (exibe top 4). O placar **não** é atualizado a cada check-in, só na entrada.

## Fluxo do modo dispositivo (check-in sem QR rotativo)

Um aparelho liberado (hoje, um tablet que passa de mão em mão) marca presença
sem que cada pessoa escaneie nada. O que impede alguém de abrir a mesma URL no
próprio celular é a posse do código do dispositivo.

1. No admin (`DeviceAdmin`), cria-se um `Device` para o evento. A tela de edição mostra o QR Code de ativação (gerado no servidor com a lib `qrcode`, SVG), apontando para `<SITE_URL>/checkin/device/<code>` (a `Config` `SITE_URL` define o host; padrão `http://localhost:5173`; a linha não é seedada por migração — precisa ser criada no admin).
2. O aparelho lê o QR e abre `/checkin/device/[code]`. Na primeira visita o front chama `POST /api/checkin/device/<code>/activate`, que resgata o código **uma única vez** (`Device.activate()` faz um UPDATE condicional em `activated_at`). Um segundo aparelho recebe 409.
3. O código fica no `localStorage` (`storage/deviceStorage.ts`, key `device`, com `expiresAt` igual ao do servidor) e passa a ir no path de toda chamada do aparelho. Reabrir a URL não reativa nada: a lista abre direto. Se o código salvo for diferente do da URL (QR novo lido no mesmo tablet), o front tenta ativar o novo.
4. `GET /api/checkin/device/<code>/pending` devolve os membros que ainda não marcaram hoje, com foto e aniversário. A pessoa acha o próprio nome, confirma pela foto e o front chama `POST /api/checkin/device/<code>/<member_id>`.
5. Daí para frente o fluxo é o mesmo do QR: `CheckinController.checkin` cria o `CheckIn`, difunde `memberCheckin` no WebSocket e devolve os pontos. Depois de 3s a tela volta sozinha para a lista.
6. O código vale `Device.VALIDITY_DAYS` (30 dias) a partir da criação e pode ser cortado a qualquer momento pela ação "Revogar acesso" no admin — não há botão de encerrar no aparelho.

O `Code` (QR rotativo) e o `Device` são tabelas separadas de propósito: o primeiro é um segredo efêmero compartilhado por vários scans, o segundo é a credencial durável de um aparelho.

## Back-end (`back/`)

Camadas: **api** (rotas Ninja) → **controllers** (regra de negócio) → **models** (com métodos de domínio). Não há camada de repositories (foi removida).

### Models (`presenca/models.py`)

| Model | Papel |
|---|---|
| `Member` | Membro da comunidade. Liga-se opcionalmente a um `User` do Django. Tem foto (`FileField`, `images/members/`) e aniversário. `to_checkin()` é o payload usado no WebSocket e nas listas públicas. |
| `Event` | Evento recorrente (ex.: "Escola Sabatina"). Nome único; vira nome de grupo WebSocket (`lower()` + espaços → `_`). Tem `start`/`end` (default `timezone.now`), usados só para recortar o histórico do membro. |
| `Code` | Código UUID de acesso ao check-in, por evento. Rotacionado por thread (`code_timer.py`); válido por rotação + 20s; compartilhável entre vários scans. Guardado por `RETENTION_DAYS` (365); `Code.purge_old()` apaga os mais antigos e roda toda vez que uma thread de rotação nasce. |
| `Device` | Aparelho liberado para marcar presença sem QR rotativo. Código UUID por evento, resgatado uma única vez (`activated_at`), válido por `VALIDITY_DAYS` (30) e cortável (`revoked_at`). É a credencial que vai no path das rotas `/api/checkin/device/...`. |
| `CheckIn` | Presença de um membro em (evento, data-hora). `unique_together (member, date, event)` + criação idempotente por timestamp exato. A idempotência **por dia** fica em `CheckinController.checkin`, dentro de `transaction.atomic()`; com `transaction_mode: IMMEDIATE` no SQLite, dois check-ins simultâneos do mesmo membro são serializados e geram um único registro. |
| `Scoreboard` / `Score` | Quadro de pontuação e pontos acumulados por membro. **Não são usados pela API**: o placar e os pontos por evento são calculados on-the-fly a partir dos `CheckIn` + `TimeScoreRules`. Só `populate_db` cria um `Scoreboard`; `ScoreboardController.add_points` não tem chamador. |
| `TimeScoreRules` | Faixas de horário → pontos por evento (ex.: chegou até 9h = 100 pts). Fonte da pontuação do placar. Comparação feita em horário local (`America/Sao_Paulo`). Sem validação de sobreposição; em caso de faixas sobrepostas vale a primeira encontrada. |
| `Config` | Variáveis de ambiente em runtime, editáveis no admin. Chave/valor + tipo (`str`/`int`/`float`/`bool`); `coerce()` converte o valor para o tipo da linha, `get_value(key, default)` busca já coagido. Keys em uso: `CODE_ROTATION_SECONDS` (seed na 0014) e `SITE_URL` (sem seed). |

Todos herdam de `Base` (`created_at`/`updated_at`).

`presenca/model_schemas.py` contém schemas Ninja (`MemberSchema`, `CodeSchema` etc.) que **não são importados por nenhuma rota**; os schemas em uso vivem dentro dos próprios módulos de API (`MeResponse`, `LoginSchema`).

### API (`presenca/api/`, montada em `core/urls.py` sob `/api/`)

Convenções: rotas públicas (sem `auth`) para o fluxo de check-in; `SessionAuth` para o que depende do membro logado. Erros são sempre `JsonResponse({"error_code": N, "error": "..."}, status=N)` com o status HTTP real.

- `auth.py` — `/api/auth/`: `POST login` (username é normalizado para minúsculas; campos vazios → 400, credenciais inválidas → 401), `GET logout`, `GET logged`. Autenticação por sessão (`SessionAuth`, cookie `sessionid`).
- `checkin.py` — `/api/checkin/`: `GET pending/{code}` (valida código + lista pendentes), `POST {code}/{member_id}` (efetiva check-in), `GET history` (histórico do membro logado, até 6 por evento, recortado por `Event.start`/`end`), `GET already/{event}` (quem já marcou hoje — usado para repopular o painel ao conectar; evento inexistente → 404).
- `device.py` — `/api/checkin/device/`: `POST {code}/activate` (resgate único), `GET {code}/pending`, `POST {code}/{member_id}`. Router montado **antes** do `checkin_router` em `core/urls.py`, para `/checkin/device/...` não cair na rota genérica `{code}/{member_id}`. Erros de credencial (não ativado, revogado, expirado) → 401; código já resgatado → 409.
- `member.py` — `/api/member/`: `GET me`, `POST photo` (upload multipart no campo `photo`; exige `content_type` `image/*` e até 5 MB (`PHOTO_MAX_BYTES`), senão 400; apaga a foto anterior e salva com nome `<slug>_profile_<timestamp>`). Usuário logado sem `Member` → 404 nas duas rotas, igual a `history` e `per-event`.
- `score.py` — `/api/score/`: `GET per-event` (pontuação do membro logado por evento), `GET event/{nome}` (placar público do evento: `{success, data: [{name, score}]}` ordenado desc; evento inexistente → 404).

Documentação OpenAPI gerada pelo Ninja em `/api/docs`.

### Controllers (`presenca/controllers/`)

- `checkin_controller.py` — orquestra check-in: dentro de uma transação verifica check-in existente no dia e cria o `CheckIn`; após o commit notifica o WebSocket e calcula pontos. Constante `CHECKIN_BOARD = "Presença"` (não usada). O evento vem sempre do `Code` ou do `Device`; não há mais evento fixo.
- `code_controller.py` — código corrente, rotação e validação (lança `ExpiredCodeError` se fora da janela).
- `device_controller.py` — ativação (uso único) e validação do aparelho: lança `DeviceAlreadyActivatedError`, `DeviceNotActivatedError`, `DeviceRevokedError` ou `ExpiredDeviceError`.
- `ws_controller.py` — envia mensagens ao channel layer: `send_current_code_for_event`, `rotate_code_for_event`, `send_member_checkin_for_event`.
- `score_controller.py` — soma pontos por evento e monta o placar a partir dos `CheckIn` (sem cache, N consultas a `TimeScoreRules` por check-in).
- `scoreboard_controller.py` — grava em `Scoreboard`/`Score`; sem chamador.
- `event_controller.py`, `member_controller.py`, `user_controller.py` — get-or-create usados pelo `import_checkins`. `MemberController.get_or_create` cria um `User` com senha fixa `default_password` para membros novos.

Exceções de domínio em `presenca/errors.py`; constantes de horário (`DAY_START`, `DAY_END`) em `presenca/constants.py`.

### WebSocket

- ASGI: `core/asgi.py` (`ProtocolTypeRouter` http + websocket com `AuthMiddlewareStack`).
- Rota: `/ws` (`presenca/routing.py`) → `Consumer` (`presenca/consumer.py`), síncrono (`JsonWebsocketConsumer`, roda em threadpool).
- Channel layer: `InMemoryChannelLayer` (funciona com processo único do Daphne; não escala horizontalmente).
- Mensagens servidor→cliente: `newCode` (`{code, expiresAt}`), `memberCheckin` (`{member: {name, photo, birthday}}`) e `error` (`{message}`, resposta a um `joinEvent` de evento inexistente ou a um tipo de mensagem desconhecido; o painel fecha o socket e volta ao input mostrando a mensagem). Cliente→servidor: `joinEvent` (`{event: <nome>}`). Não há autenticação no WebSocket: qualquer cliente pode entrar em qualquer grupo.
- Nomes de grupo do Channels só aceitam `[a-zA-Z0-9\-_.]` e até 100 chars; `Event.as_websocket_group_name` passa o nome por `unidecode`, minúsculas e troca o resto por `_` ("Reunião: Louvor" → `reuniao_louvor`).

### Comandos de gerenciamento (`presenca/management/commands/`)

- `populate_db [--test]` — cria `Scoreboard` e `Event` "Escola Sabatina" e as 4 faixas de `TimeScoreRules` (100/70/50/0 pts); com `--test`, cria membros de exemplo.
- `export_checkins` — grava `checkins.csv` no diretório corrente com `(evento, membro, data ISO)`.
- `import_checkins <csv>` — lê o CSV, faz get-or-create de evento e membro (criando `User` com senha padrão) e chama `CheckinController.checkin` para cada linha (isso também dispara `memberCheckin` no WebSocket).
- `set_default_passwords` — para usuários com `password=''`, define `<primeiro nome sem acento><ddmmaaaa do aniversário ou último nome>`. A função `fix_passwords` é também importada e executada pela migração 0006.

### Migrações com dados (seed)

- `0006` — normaliza usernames e chama `fix_passwords` (import de um management command dentro da migração).
- `0007` — cria o `Event` "Escola Sabatina" e o associa a todos os `CheckIn` existentes.
- `0014` — seeda `Config` `CODE_ROTATION_SECONDS = 60`.

### Configuração (`core/settings.py`)

Variáveis via `python-decouple` (`back/.env`, exemplo em `back/.env.example`): `DJANGO_DEBUG` (default `False`), `DJANGO_DB_NAME` (default `back/db.sqlite3`), `ALLOWED_HOSTS` (default `localhost,127.0.0.1,testserver`). SQLite com `transaction_mode: IMMEDIATE` (todo `atomic()` abre com `BEGIN IMMEDIATE`) e banco de teste em arquivo no diretório temporário do sistema (em memória o SQLite não espera lock de tabela, o que inviabiliza testes de concorrência). Timezone `America/Sao_Paulo`, idioma `pt-br`, `USE_TZ = True`. Logger `presenca` em nível DEBUG para console e arquivo `back/logs/presenca.log` (`LOG_DIR`, criado no import do settings e montado pelo compose). Mídia em `MEDIA_ROOT = BASE_DIR / 'media'`, mesmo caminho usado no `STORAGES`. `CSRF_TRUSTED_ORIGINS` hardcoded (localhost, um IP de rede local e um IP público). `SECRET_KEY` hardcoded.

## Front-end (`front/`)

SvelteKit em modo SPA estático (`+layout.ts`: `ssr = false`, `prerender = false`). Alias `$events` → `src/lib/websocket/events`. Build com `bun` (`bun.lock`). A versão exibida no rodapé (`__APP_VERSION__`) é lida de `cz.json` pelo `vite.config.ts`.

Em desenvolvimento, o Vite (`bun run dev`, porta 3000) faz proxy de `/api`, `/media` e `/ws` para `localhost:8000` (Django rodando fora do Docker). `VITE_ALLOWED_HOSTS` libera hosts extras no dev server.

### Rotas (`src/routes/`)

- `/` — painel do administrador: input do nome do evento → conecta WebSocket → mostra QR Code + `Phloating` (fotos flutuantes) + placar (top 4). Não exige login.
- `/checkin/[code]` — página aberta pelo scan: seleciona membro em um `<select>`, marca presença, mostra pontos ganhos e redireciona para um quiz externo após 3s. `+error.svelte` cobre erros de rota.
- `/checkin/device/[code]` — modo dispositivo: ativa o aparelho na primeira visita e depois mostra a grade de membros pendentes com busca; ao tocar num nome, confirma pela foto, registra a presença e volta sozinho em 3s.
- `/login` — login por usuário e senha; redireciona para `/me`.
- `/(auth)/me` — perfil do membro logado: foto com recorte (`PhotoSelector`), aniversário, histórico de check-ins e pontos por evento. O layout `(auth)` espera `authStore.getLoggedFromServer()` antes de renderizar a página; sem sessão redireciona para `/login`. "Sair" faz logout e também vai para `/login`.
- `/teste` — página de desenvolvimento que enche o `Phloating` com fotos falsas (`debug=true`). Vai para o build de produção.

### Estrutura de `src/lib/`

- `api/` — wrappers de fetch por domínio (`authApi`, `checkinApi`, `deviceApi`, `memberApi`, `scoreApi`) sobre `callFetch` em `index.svelte.ts`. Cada wrapper devolve `ApiResponse {success, message, data}`. `callFetch` redireciona para `/login` em 401 quando `ensureLogin` (padrão `true`); rotas públicas passam `ensureLogin: false`. CSRF: `getCsrfToken()` lê o cookie `csrftoken` e só o upload de foto o envia (no corpo multipart).
- `stores/` — estado global com runes (`$state`): `codeStore` (código atual do QR + `expiresAt`), `socketStore` (último erro vindo do WebSocket), `checkinStore` (membros presentes, deduplicados por nome, + padrão observer que alimenta o `Phloating`), `authStore` (login/logout/`isLogged`/`getLoggedFromServer`), `memberStore` (membro logado, com cache em localStorage).
- `websocket/` — `socket.ts` (singleton `socket.current`, conexão via `ws://` ou `wss://` conforme o protocolo da página, join, reconexão em queda) e `events/` (padrão builder: payload cru → `NewCodeEvent` | `MemberCheckinEvent` | `ErrorEvent`, cada um com seu `handle()` que atualiza o store correspondente).
- `components/` — `QrCode.svelte` (QR via `@svelte-put/qr` com logo, anel de contagem), `Member.svelte` (marcação única de um membro: foto com placeholder, nome e, na semana do aniversário, chapéu e confete), `Phloating.svelte` (animação física das fotos: velocidade, desaceleração, colisão com bordas medindo o tamanho real do nó; renderiza cada item com `Member`), `PhotoSelector.svelte` (seleção, recorte circular com drag/pinch/scroll em canvas e upload JPEG 400×400).
- `inputs/` — `Button.svelte` e `Text.svelte`, wrappers Tailwind sem tipagem de props.
- `storage/` — persistência em localStorage com envelope `{version, expiresAt, data}` (`index.ts`): `authStorage` (key `auth`, TTL 5 min), `memberStorage` (key `member`, TTL 5 min), `deviceStorage` (key `device`, TTL igual à validade do `Device`). Versão diferente ou expirado → volta ao default.
- `dateUtils.ts` — `formatDateInUTC` e `isBirthWeek` (aniversário a até 5 dias de hoje, cruzando mês e ano; lê `AAAA-MM-DD` como data local).
- `types/api.ts` — `MemberI`/`Member`/`User` (`{id, email}`, espelho de `MeUserResponse`).

## Infra e deploy

- **Dev (Docker)**: `docker-compose-dev.yml` builda back (`docker/Dockerfile.back`: imagem `uv:alpine`, `uv sync --frozen --no-dev`; o build arg `INSTALL_DEV=true`, usado só pelo compose de teste, inclui o grupo `dev` com `pytest`/`ipdb`; entrypoint roda `collectstatic`, `migrate` e `daphne`) e front (`docker/Dockerfile.front`: `bun run build` e um container `alpine` que copia o build para o volume `front_build/` e fica em `tail -f`). Caddy expõe `:3000` (front + proxy de `/api`, `/ws`, `/media`; também um proxy `/cdn/*` → unpkg.com, sem uso no front atual) e `:8000` (admin do Django + `/static/`). Portas 80/443 são publicadas mas não têm site block no Caddyfile.
- **Prod**: `docker-compose-prod.yml` usa as imagens `sistemapresenca-back:latest` e `sistemapresenca-front:latest` com `pull_policy: never`; mesmo Caddy. Não há registry: `sendimage.py [back] [front]` builda com o compose de dev, faz `docker save` e envia por `scp` para `root@presenca:/images/`; no servidor, `loadimage.py [back] [front]` faz `docker load` e recria o serviço.
- **Testes**: `docker-compose-test.yml` roda `pytest -q ../tests` dentro do container do back, com banco em `/tmp`. Localmente: `cd back && uv run python -m pytest ../tests`. Config em `pytest.ini` (raiz) + `conftest.py` (adiciona `back/` ao `sys.path`). Fixtures em `tests/conftest.py` (`user`, `member`, `event` com regra única de 50 pts, `code`, `expired_code`, `device`, `active_device`). Cobertura atual: API de check-in (inclusive `history` e `already`), `per-event`, consumer WebSocket (`joinEvent`, erros), device (controller, API e admin), código/rotação/timer, `Config`, `member/me` e upload de foto, pontuação e `didnt_checkin_today`. Não há testes das rotas de auth, dos management commands nem do front.
- **Versionamento**: `commitizen` (`cz.json`, semver, tag = versão, `CHANGELOG.md` gerado no bump). `.env` na raiz só carrega `APP_VERSION` para o compose. A versão do front vem de `cz.json` em build time.
- O front é buildado para `front_build/` e servido como arquivos estáticos pelo Caddy — não há servidor Node em produção.
- O `db.sqlite3` da raiz é montado como arquivo nos containers; se não existir, o Docker cria um diretório com esse nome e o Django falha ao abrir o banco.

## Pontos de atenção

- `SECRET_KEY` está hardcoded em `settings.py`; `CSRF_TRUSTED_ORIGINS` também.
- Channel layer em memória: exige um único processo de back. As threads de rotação de código (`code_timer.py`) e o `CodeTimerRegistry` (dict em memória) também assumem processo único.
- O WebSocket não exige autenticação e o painel `/` é público: qualquer pessoa na rede vê o QR e o placar.
- `Event.start`/`end` recebem `timezone.now()` na criação e nunca são atualizados automaticamente; como o histórico do membro (`/api/checkin/history`, `/api/score/per-event`) filtra por esse intervalo, eventos criados sem ajuste manual mostram histórico vazio.
- A lista de pontos a corrigir está em `REVIEW.md`.
