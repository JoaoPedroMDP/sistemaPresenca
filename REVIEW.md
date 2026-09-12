# Revisão — Sistema de Presença

Análise feita sobre a branch `device` (commit `b8959b8`). Suíte de testes do back
executada localmente: 54 testes passando. `svelte-check` do front: 19 erros e
2 avisos, todos anteriores a esta revisão (lista em B5).

Prioridade: **Alta** = bug que afeta o uso real ou segurança; **Média** = defeito
com contorno ou dívida que vai custar em breve; **Baixa** = limpeza.

## Alta

### A1. `Member.didnt_checkin_today` exclui membro errado (`exclude` com relação multi-valorada)

`back/presenca/models.py`, `didnt_checkin_today`. O `exclude(checkins__event=event, checkins__date__range=...)` gera dois `EXISTS` independentes: um para "tem check-in nesse evento em qualquer data" e outro para "tem check-in hoje em qualquer evento". Um membro que marcou presença ontem no evento A e hoje no evento B some da lista de pendentes de A. Reproduzido com teste local (falha). Com um único evento em uso o bug não aparece, mas o sistema já aceita vários eventos.

Correção: filtrar os ids em uma subquery e excluir por `id__in`, ou usar `~Q(...)` sobre um `filter` de `CheckIn`:

```python
today_ids = CheckIn.objects.filter(event=event, date__range=(start, end)).values("member_id")
return cls.objects.exclude(id__in=today_ids).order_by("name")
```

### A2. Histórico e pontos do membro dependem de `Event.start`/`end` (rebaixado para Média)

Afeta só eventos criados sem ajustar as datas: o "Escola Sabatina" da migração 0007 e os de `populate_db`. Verificar no admin de produção.

`CheckinController.get_member_checkins_for_event` filtra `date__range=(event.start, event.end)`. Os dois campos recebem `timezone.now()` na criação (`Event`, migração 0010) e nada os atualiza. Para o "Escola Sabatina" criado pela migração 0007, `start == end`, então `/api/checkin/history` e `/api/score/per-event` devolvem vazio para todo mundo até alguém editar o evento no admin. O placar público (`get_scoreboard_for_event`) não usa esse filtro, o que faz o perfil e o placar discordarem.

Correção: decidir o significado de `start`/`end` (temporada? recorte do placar?) e aplicá-lo nos dois lugares, ou remover o filtro do histórico.

### A3. Reconexão do WebSocket invertida — **corrigido**

`front/src/lib/websocket/socket.ts`, `onclose`: só agenda `createSocket` quando `event.code === 1000` (fechamento normal). Qualquer queda real (rede, restart do Daphne) loga "Reconectando em 3s..." e nunca reconecta. O painel fica com o último QR até alguém recarregar a página, e o código exibido expira em 80s. Trocar a condição para reconectar nos fechamentos anormais e não reconectar no 1000.

### A4. Janela em que o QR exibido já está inválido

Novo ouvinte recebe `CodeController.get_current_code`, que reutiliza um código com idade até `rotation_seconds` (60s). A thread do `CodeTimerRegistry`, recém-criada, só rotaciona após um intervalo completo. Um código reaproveitado com 50s de idade é substituído aos 110s, mas deixa de validar aos 80s: por até 30s o QR na tela devolve "Este código expirou". Acontece toda vez que o último painel sai e um novo entra dentro da janela de rotação. Correções possíveis: a thread calcular o primeiro `wait` a partir de `code.rotates_at()`, ou `get_current_code` criar um código novo sempre que uma thread nova nasce.

### A5. Nome de evento inexistente ou inválido derruba o consumer — **corrigido**

`back/presenca/consumer.py`, `receive_json`: `Event.objects.get(name=...)` sem tratamento de `DoesNotExist`. O front aceita qualquer texto no input; um nome errado fecha o socket com exceção no log e o painel fica em "Aguardando código..." sem feedback. Nomes com acento ou pontuação passam no `get` mas falham no `group_add` (Channels só aceita `[a-zA-Z0-9\-_.]`), e o cliente também não é avisado. Responder uma mensagem de erro no socket e usar `slugify` (com `unidecode`) em `as_websocket_group_name`.

### A6. Erros não tratados viram 500 — **corrigido**

- `GET /api/checkin/already/{event_name}`: `Event.objects.get` sem `try`.
- `GET /api/checkin/history` e `GET /api/score/per-event`: `Member.objects.get(user=request.user)` sem `try` (usuário sem membro, caso já previsto em `/member/me`).
- `POST /api/member/photo`: `request.FILES.get("photo")` pode ser `None` e vai direto para `member.photo.save`. Sem validação de tipo nem tamanho do arquivo.

### A7. Segurança de configuração e credenciais

- `SECRET_KEY` hardcoded em `core/settings.py`; `CSRF_TRUSTED_ORIGINS` com IPs fixos. Mover ambos para `.env` via `decouple`.
- `MemberController.get_or_create` (usado por `import_checkins`) cria `User` com senha literal `default_password`.
- `set_default_passwords` e a migração 0006 definem senhas derivadas de nome + data de nascimento, informação pública dentro da comunidade. Trocar por senha aleatória com fluxo de redefinição, ou marcar `set_unusable_password()`.
- `GET /api/auth/logout` muda estado via GET (sem CSRF). Passar para `POST`.
- Não há rate limiting em `/api/checkin/pending/{code}`, `/api/checkin/device/...` nem no login. O próprio `prototypes/README.md` lista isso como pendência.

## Média

### M1. `ws://` fixo no front

`socket.ts` monta `ws://${window.location.host}/ws`. Em HTTPS o navegador bloqueia. Usar `location.protocol === 'https:' ? 'wss' : 'ws'`.

### M2. Contrato `login` e `score/event` devolvem erro com HTTP 200

`POST /api/auth/login` retorna `{"error_code": 401, ...}` com status 200; `GET /api/score/event/{nome}` retorna `{"success": false}` com 200. O resto da API usa `JsonResponse(..., status=N)`. O front compensa lendo `data.error`. Padronizar para status HTTP real.

### M3. Corrida no check-in do mesmo membro no mesmo segundo

`CheckinController.checkin` faz `filter(...).first()` e depois `create`. Duas requisições simultâneas (toque duplo no tablet, dois scans) passam pelo `first()` vazio e criam dois `CheckIn` com timestamps diferentes; `unique_together (member, date, event)` não impede porque a data-hora difere. O painel recebe dois `memberCheckin` (o front deduplica por nome, o que mascara o problema) e o placar conta em dobro. Trocar `unique_together` para (member, event, dia) via campo `date` separado ou `UniqueConstraint` com expressão, e tratar a `IntegrityError` no controller.

### M4. Tabela `Code` cresce sem limite

Um `Code` por minuto por evento, enquanto houver painel aberto; nada apaga. Em um ano de uso semanal são milhares de linhas inúteis. Adicionar limpeza (command ou na própria thread: apagar códigos com `created_at` anterior à validade).

### M5. Cache de membro no front é opaco e quebra com erro

`memberStore.getMember`: quando `callMe` falha, chama `goToLogin()` e continua para `Member.fromJson(undefined)`, que lança `TypeError`. Além disso, `types/api.ts` tipa `User.username`, mas a API devolve `email` (`MeUserResponse`); `/me` renderiza `member.user?.username` como `undefined`.

### M6. Datas de aniversário com off-by-one

`dateUtils.isBirthWeek` faz `new Date("2000-01-02")` (interpretado como UTC meia-noite) e compara com `getDate()` local. Em `America/Sao_Paulo` isso vira 1º de janeiro; na fronteira do mês a semana do aniversário some (`getMonth()` diferente). `formatDateInUTC` contorna para exibição, mas o chapéu/confete usa a versão errada. Comparar componentes de data em UTC ou construir a data com `new Date(y, m - 1, d)`.

### M7. Verificação de autenticação no layout `(auth)` não bloqueia nada

`routes/(auth)/+layout.svelte`: `checkedAuth = true` é setado logo após disparar `getLoggedFromServer()` sem `await`. A tela "Verificando autenticação..." praticamente nunca aparece e a página filha renderiza antes da resposta. Após `logout` não há redirecionamento.

### M8. Logs e mídia em caminhos que o Docker não persiste

`LOGGING.file` grava em `BASE_DIR/presenca.log` (`/app/presenca.log`), mas o compose monta `./back/logs:/app/logs`, que nada usa. `STORAGES.default.location = "media/"` é relativo ao cwd e `MEDIA_ROOT = BASE_DIR / 'media'` é absoluto; hoje coincidem porque o `WORKDIR` é `/app`, mas basta o comando mudar de diretório para divergir. Apontar o log para `logs/` e usar `MEDIA_ROOT` no `STORAGES`.

### M9. Imagem de produção do back carrega dependências de dev

`pyproject.toml` lista `pytest`, `pytest-django`, `ipdb` e `django-extensions` como dependências principais. Mover para `[dependency-groups] dev` e usar `uv sync --no-dev` no `Dockerfile.back`. O `readme = "README.md"` aponta para arquivo inexistente.

### M10. Fluxo de deploy manual e frágil

- `sendimage.py` rebuilda com `--no-cache`, salva `docker save -o back.tar.gz` (não é gzip, só o nome) e faz `scp` para `root@presenca`; `loadimage.py` faz `docker compose down back` sem `-f`, dependendo de um `compose.yml` que está no `.gitignore`.
- `docker-compose-*.yml` montam `./db.sqlite3` como arquivo; se não existir, o Docker cria um diretório e o Django falha.
- `caddy:latest` sem pin. Portas 80/443 publicadas sem site block.
- Nenhum `healthcheck`; `depends_on` só espera o container subir, não o Daphne ouvir.
- Não há CI: testes só rodam manualmente.

### M11. Placar do painel não atualiza ao vivo

`routes/+page.svelte` carrega `/api/score/event/<nome>` uma vez, na entrada. Cada `memberCheckin` muda a pontuação, mas o placar exibido só muda ao recarregar. Recarregar o placar no `handle()` do `MemberCheckinEvent` ou mandar o placar no próprio evento.

### M12. Página de check-in por QR

`routes/checkin/[code]/+page.svelte`:
- `checkin()` seta erro quando `member` é nulo mas segue e faz `POST /api/checkin/<code>/null`.
- Usa `fetch` direto em vez de `callFetch`/`checkinApi`, sem tratar rede fora.
- URL do quiz externo hardcoded no componente; deveria vir do evento (campo no `Event` ou `Config`).
- `pointsEarned` começa em `10`, keyframe `fadeOut` não existe, função `teste()` sem uso, tipo `Member` importado mas a rota devolve `{id, name}`.

### M13. Dedup no front e id do `Phloating` por nome

`checkinStore.addMember` e o `Phloating` usam `name` como id. Dois membros homônimos: o segundo nunca aparece no painel. Usar `member.id` no payload de `to_checkin()` e nos stores.

## Baixa

### B1. Código morto e dependências sem uso

- `presenca/model_schemas.py` (nenhum import; `CodeSchema.used` referencia campo removido na 0012).
- `Scoreboard`, `Score`, `ScoreboardController`, `CHECKIN_BOARD`: sem chamador fora de `populate_db`. Ou passam a ser a fonte do placar (com atualização no check-in) ou saem.
- `codeStore.useCode`, `authStore.isLogged`, `Consumer.send_json` (override que só chama `super`).
- `front/package.json`: `@skeletonlabs/skeleton`, `@skeletonlabs/skeleton-svelte` e `qrcode` não são importados em `src/`.
- `Caddyfile`: handle `/cdn/*` → unpkg sem uso.
- `app.html`: carrega Google Font "Funnel Sans" não usada; `.font-courier` referencia "Courier Prime", que nunca é carregada; `lang="en"` em app em português.
- Rota `/teste` vai para o build de produção (e passa `birthday: '2026-05-15'` onde o tipo pede `boolean`).

### B2. Documentação defasada (corrigido em `ARCHITECTURE.md` nesta revisão)

O `ARCHITECTURE.md` ainda citava `SABBATH_CLASS_EVENT`/`checkin_sabbath` e o `.get()` que lançava `DoesNotExist`, ambos removidos nos commits `b92f969` e `24f9205`. `prototypes/README.md` ainda descreve o `Device` como "Code com modo de dispositivo" em "Admin" e menciona a rota `/checkin/device/[code]/confirmar`, que não existe no app (a confirmação é estado da mesma rota).

### B3. Logging

Todas as rotas logam `INICIO`/`FIM` em `INFO` com f-strings avaliadas mesmo com nível desligado. Baixar para `DEBUG` ou substituir por um middleware de request log. Logger `presenca` em `DEBUG` também em produção (`settings.py`).

### B4. Admin

- `MemberAdmin.ordering = ("name","birthday")` ok, mas `list_display` não mostra se tem foto.
- `CodeAdmin` lista uma tabela que só cresce (ver M4) sem filtro por evento nem data.
- `Event` e `Scoreboard` registrados sem `ModelAdmin` (sem busca/filtros).
- `TimeScoreRules` sem validação de `start_time <= end_time` nem de sobreposição entre faixas do mesmo evento.

### B5. Front — tipagem e pequenos defeitos

`bun run check` (svelte-check) hoje falha com 19 erros. Agrupados:
- `ApiResponse.data` é `object`: todo consumidor acessa `.members`, `.data`, indexa por string (`+page.svelte`, `checkin/[code]/+page.svelte`, `(auth)/me/+page.svelte`). Tipar `ApiResponse<T>` com generic.
- `bind:this={phloating}` tipado como `PhloatingHandlers` não bate com o tipo do componente Svelte 5 (`+page.svelte`, `teste/+page.svelte`). Usar `ReturnType<typeof Phloating>` ou exportar o tipo do próprio componente.
- `scoreboard = $state([])` infere `never[]` (`entry.name`, `entry.score`).
- `memberStorage.ts` importa `memberI` (o tipo se chama `MemberI`).
- `__APP_VERSION__` sem declaração global (`app.d.ts`); `vite.config.ts` sem `@types/node`.
- `+error.svelte`: `page.error` possivelmente `null`.
- `PhotoSelector.svelte`: `canvas` não declarado com `$state` (aviso `non_reactive_update`); `role="img"` em `<canvas>`.


- `inputs/Button.svelte` e `inputs/Text.svelte` sem tipo nas props; `Button` monta `icon-[{icon}]` dinamicamente, o que o Tailwind 4 não gera.
- `routes/+page.svelte`: `scoreboard = $state([])` sem tipo, `response.error` não existe em `ApiResponse`, `$inspect(scoreboard)` esquecido.
- `Phloating.svelte.d.ts` ao lado do `.svelte` para exportar `PhloatingHandlers`; o tipo pode sair de `components/types.ts`.
- `Member.svelte` recalcula `Math.random()` do confete a cada render.
- `routes/checkin/device/[code]`: `activationError` é reaproveitado para erros de `loadPending`, mostrando "Não foi possível ativar este dispositivo" para um 401 de revogação; `doneToday` começa em 0 a cada recarga em vez de vir do servidor.
- `authStorage`/`memberStorage` com TTL de 5 min duplicam o que a sessão do Django já controla.

### B6. Testes ausentes

Sem cobertura para: rotas de auth, `import_checkins`/`export_checkins`, ação `revoke` do admin, concorrência da ativação de `Device`, e o caso do A1. Nenhum teste de front. `pytest.ini` sem `--reuse-db`/`-p no:cacheprovider`, e o `.gitignore` da raiz não ignora `.pytest_cache`.

### B7. Migração importa management command

`0006_member_photo_alter_score_unique_together.py` importa `fix_passwords` de `presenca.management.commands.set_default_passwords`. Renomear ou apagar o command quebra a migração. Copiar a lógica para dentro da migração (ou remover, já que a 0006 já rodou em produção e um `RunPython.noop` de ida basta em bancos novos — decisão que exige aprovação, conforme `CONSTITUTION.md`).

## Ordem sugerida

1. A1, A3, A5, A6 — pequenos, isolados, testáveis.
2. A4 e M4 juntos (mexem na thread e no ciclo de vida do `Code`).
3. A2 e M11 (semântica de `Event.start`/`end` e placar ao vivo).
4. A7 e M8/M9/M10 (configuração, imagem e deploy).
5. M3 exige migração: planejar com o desenvolvedor antes.
6. Limpezas B1–B7.
