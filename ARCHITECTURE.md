# Arquitetura — Sistema de Presença

Sistema de registro de presença por QR Code, com painel ao vivo (fotos flutuantes dos presentes) e placar de pontuação. Pensado para eventos recorrentes de uma comunidade (ex.: Escola Sabatina).

## Visão geral

- **Front-end**: SvelteKit (Svelte 5, runes) + Tailwind CSS 4, build estático (`adapter-static`, fallback SPA). Em `front/`.
- **Back-end**: Django 6 + Django Ninja (API REST) + Django Channels/Daphne (WebSocket). Em `back/`.
- **Banco**: SQLite.
- **Proxy**: Caddy roteia `/api/*`, `/ws*`, `/media/*` para o back e serve o build estático do front. Config em `docker/Caddyfile`.
- **Deploy**: Docker Compose (`docker-compose-dev.yml`, `docker-compose-prod.yml`, `docker-compose-test.yml`).

## Fluxo principal (check-in por QR Code)

1. Administrador abre a página inicial (`front/src/routes/+page.svelte`), digita o nome do evento e aperta Enter.
2. O front abre um WebSocket em `/ws` (`front/src/lib/websocket/socket.ts`) e envia `{type: "joinEvent", event: <nome>}`.
3. O `Consumer` (`back/presenca/consumer.py`) adiciona a conexão ao grupo do evento (`Event.as_websocket_group_name()`), registra a conexão no `CodeTimerRegistry` (`back/presenca/code_timer.py`) e envia `{type: "newCode", code: <uuid>, expiresAt: <ISO 8601>}` com o código corrente do evento.
4. O `CodeTimerRegistry` mantém **uma thread por evento** que gera um código novo a cada `Code.rotation_seconds()` e o difunde ao grupo. Primeiro ouvinte do grupo inicia a thread; o último a encerra. O intervalo de rotação vem da tabela `Config` (key `CODE_ROTATION_SECONDS`, editável no admin em runtime; seed de 60s na migração 0014, linha recriada automaticamente se apagada). Cada código vale pela rotação + 20s de folga (`Code.validity_seconds()`), para não invalidar quem escaneou perto da troca. **Várias pessoas podem escanear o mesmo código** — ele não é consumido no scan.
5. O front embute o código no QR Code (`QrCode.svelte`), apontando para a rota `/checkin/<code>`, e o re-renderiza a cada `newCode`.
6. A pessoa escaneia e abre `/checkin/[code]`. O front chama `GET /api/checkin/pending/<code>`, que valida o código (expirado/inexistente retorna erro pedindo novo scan) e retorna a lista de membros que ainda não fizeram check-in hoje (`Member.didnt_checkin_today`).
7. A pessoa seleciona seu nome e o front chama `POST /api/checkin/<code>/<member_id>`. O back:
   - valida que o código ainda está na janela de validade;
   - cria o `CheckIn` de forma idempotente (`CheckIn.create_idempotent`) com horário `timezone.now()`;
   - emite `{type: "memberCheckin", member: {...}}` para o grupo do evento;
   - calcula pontos por horário via `TimeScoreRules.get_points_for_time_in_event` e retorna ao cliente.
8. No painel, o evento `memberCheckin` adiciona a foto/nome do membro ao componente `Phloating` (fotos flutuando pela tela; quem está na semana do aniversário ganha chapéu de festa e confete). O placar (`GET /api/score/event/<nome>`) é exibido ao lado do QR Code.

## Back-end (`back/`)

Camadas: **api** (rotas Ninja) → **controllers** (regra de negócio) → **models** (com métodos de domínio). Não há camada de repositories (foi removida).

### Models (`presenca/models.py`)

| Model | Papel |
|---|---|
| `Member` | Membro da comunidade. Liga-se opcionalmente a um `User` do Django. Tem foto e aniversário. |
| `Event` | Evento recorrente (ex.: "Escola Sabatina"). Nome único; vira nome de grupo WebSocket. |
| `Code` | Código UUID de acesso ao check-in, por evento. Rotacionado a cada 30s por thread (`code_timer.py`); válido por 60s; compartilhável entre vários scans. |
| `CheckIn` | Presença de um membro em (evento, data). `unique_together (member, date, event)` + criação idempotente. |
| `Scoreboard` / `Score` | Quadro de pontuação e pontos por membro. |
| `TimeScoreRules` | Faixas de horário → pontos por evento (ex.: chegou até 9h = 100 pts). Fonte da pontuação do placar. |
| `Config` | Variáveis de ambiente em runtime, editáveis no admin. Chave/valor + tipo (`str`/`int`/`float`/`bool`); `coerce()` converte o valor para o tipo da linha, `get_value(key, default)` busca já coagido. |

Todos herdam de `Base` (`created_at`/`updated_at`).

### API (`presenca/api/`, montada em `core/urls.py` sob `/api/`)

- `auth.py` — `/api/auth/`: `login`, `logout`, `logged`. Autenticação por sessão (`SessionAuth`).
- `checkin.py` — `/api/checkin/`: `pending/{code}` (valida código + lista pendentes), `POST {code}/{member_id}` (efetiva check-in), `history` (histórico do membro logado), `already/{event}` (quem já marcou hoje — usado para repopular o painel ao conectar).
- `member.py` — `/api/member/`: `me`, `POST photo` (upload de foto de perfil).
- `score.py` — `/api/score/`: `per-event` (pontuação do membro logado), `event/{nome}` (placar público do evento).

### Controllers (`presenca/controllers/`)

- `checkin_controller.py` — orquestra check-in: cria `CheckIn`, notifica WebSocket, calcula pontos. Constantes `CHECKIN_BOARD = "Presença"` e `SABBATH_CLASS_EVENT = "Escola Sabatina"` (o check-in via QR Code é hardcoded para esse evento em `checkin_sabbath`).
- `code_controller.py` — código corrente, rotação e validação (lança `ExpiredCodeError` se fora da janela).
- `ws_controller.py` — envia mensagens ao channel layer: `send_current_code_for_event`, `rotate_code_for_event`, `send_member_checkin_for_event`.
- `score_controller.py` / `scoreboard_controller.py` — pontuação por evento e quadros.
- `event_controller.py`, `member_controller.py`, `user_controller.py` — get-or-create e utilitários.

### WebSocket

- ASGI: `core/asgi.py` (`ProtocolTypeRouter` http + websocket com `AuthMiddlewareStack`).
- Rota: `/ws` (`presenca/routing.py`) → `Consumer` (`presenca/consumer.py`).
- Channel layer: `InMemoryChannelLayer` (funciona com processo único do Daphne; não escala horizontalmente).
- Mensagens servidor→cliente: `newCode` (novo código para o QR) e `memberCheckin` (membro fez presença). Cliente→servidor: `joinEvent`.

### Comandos de gerenciamento (`presenca/management/commands/`)

`populate_db`, `export_checkins`, `import_checkins`, `set_default_passwords`.

### Configuração (`core/settings.py`)

Variáveis via `python-decouple` (`.env`): `DJANGO_DEBUG`, `DJANGO_DB_NAME`, `ALLOWED_HOSTS`. Timezone `America/Sao_Paulo`, idioma `pt-br`. Logs em console e `presenca.log`. Mídia em `media/`.

## Front-end (`front/`)

SvelteKit em modo SPA estático. Alias `$events` → `src/lib/websocket/events`.

### Rotas (`src/routes/`)

- `/` — painel do administrador: input do nome do evento → conecta WebSocket → mostra QR Code + `Phloating` (fotos flutuantes) + placar (top 4).
- `/checkin/[code]` — página aberta pelo scan: seleciona membro, marca presença, mostra pontos ganhos e redireciona para um quiz externo após 3s.
- `/login` — login.
- `/(auth)/me` — perfil do membro logado (layout `(auth)` exige sessão).

### Estrutura de `src/lib/`

- `api/` — wrappers de fetch por domínio (`authApi`, `checkinApi`, `memberApi`, `scoreApi`) sobre `callFetch` em `index.svelte.ts` (trata 401 redirecionando para login; CSRF via cookie `csrftoken`).
- `stores/` — estado global com runes (`$state`): `codeStore` (código atual do QR), `checkinStore` (membros presentes + padrão observer que alimenta o `Phloating`), `authStore`, `memberStore`.
- `websocket/` — `socket.ts` (conexão, reconexão, join) e `events/` (padrão builder: payload cru → `NewCodeEvent` | `MemberCheckinEvent`, cada um com seu `handle()` que atualiza o store correspondente).
- `components/` — `QrCode.svelte`, `Phloating.svelte` (animação física das fotos: velocidade, desaceleração, colisão com bordas; confete e chapéu para aniversariantes), `PhotoSelector.svelte`.
- `storage/` — persistência em localStorage (auth, member).

## Infra e deploy

- **Dev**: `docker-compose-dev.yml` builda back (uv + Daphne) e front; Caddy expõe `:3000` (front + proxy de `/api` e `/ws`) e `:8000` (admin/estáticos do Django).
- **Prod**: `docker-compose-prod.yml` usa imagens pré-buildadas (`pull_policy: never`); mesmo Caddy.
- **Testes**: `docker-compose-test.yml` roda `pytest` dentro do container do back. Config em `pytest.ini` (raiz) + `conftest.py` (adiciona `back/` ao `sys.path`). Testes em `tests/`.
- O front é buildado para `front_build/` e servido como arquivos estáticos pelo Caddy — não há servidor Node em produção.

## Pontos de atenção

- `SECRET_KEY` está hardcoded em `settings.py`.
- Channel layer em memória: exige um único processo de back. As threads de rotação de código (`code_timer.py`) também assumem processo único.
- Evento do check-in via QR é fixo em "Escola Sabatina" (`CheckinController.checkin_sabbath`), embora o painel aceite qualquer nome de evento.
- `TimeScoreRules.get_points_for_time_in_event` usa `.get()` — check-in fora de qualquer faixa de horário lança `DoesNotExist`.
