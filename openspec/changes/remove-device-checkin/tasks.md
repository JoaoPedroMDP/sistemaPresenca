## 1. Back-end

- [x] 1.1 Remover o mount do `device_router` e o comentário de ordem em `back/core/urls.py`, e verificar que `/api/docs` sobe sem as três rotas `/api/checkin/device/...`
- [x] 1.2 Apagar `back/presenca/api/device.py` e `back/presenca/controllers/device_controller.py`, e verificar com `grep -rn "device" back/ --include="*.py"` que só sobram `models.py`, `admin.py` e `errors.py`
- [x] 1.3 Remover `DeviceAdmin`, o `admin.site.register(Device, ...)` e os imports de `qrcode` em `back/presenca/admin.py`, e verificar que o admin abre em `/admin/` sem a entrada "Dispositivo"
- [x] 1.4 Remover `class Device` de `back/presenca/models.py` e as quatro exceções (`ExpiredDeviceError`, `DeviceRevokedError`, `DeviceAlreadyActivatedError`, `DeviceNotActivatedError`) de `back/presenca/errors.py`, e verificar que `uv run python manage.py check` passa
- [x] 1.5 Apagar `tests/test_device.py`, `tests/test_device_concurrency.py`, `tests/test_admin_device_qr.py` e `tests/test_admin_device_revoke.py`, e remover as fixtures `device` e `active_device` de `tests/conftest.py`
- [x] 1.6 Rodar `cd back && uv run python -m pytest ../tests` e verificar que a suíte passa (com o `xfail` de `didnt_checkin_today` intacto)

## 2. Front-end

- [x] 2.1 Apagar o diretório `front/src/routes/checkin/device/`, `front/src/lib/api/deviceApi.svelte.ts` e `front/src/lib/storage/deviceStorage.ts`, mantendo `Member.svelte`, `dateUtils.ts` e `storage/index.ts`, que são compartilhados
- [x] 2.2 Rodar `cd front && bun run check` e verificar que o `svelte-check` segue sem erros nem avisos

## 3. Protótipos

- [x] 3.1 Apagar `prototypes/06-dispositivo-lista.html` e `prototypes/07-dispositivo-confirmacao.html`
- [x] 3.2 Remover as linhas das duas telas da tabela do `prototypes/README.md` e os trechos que descrevem o fluxo do dispositivo, o `Device`/`DeviceAdmin` e as rotas `/api/checkin/device/...`
- [x] 3.3 Remover o bloco "Credencial do dispositivo" e as chaves `DEVICE_CODE_KEY`/`device_event` de `prototypes/assets/app.js`, e verificar com `grep -rn "device\|dispositivo" prototypes/` que nada sobra

## 4. Documentação

- [x] 4.1 Remover a seção "Fluxo do modo dispositivo" do `ARCHITECTURE.md`, a linha `Device` da tabela de models, a menção a `device.py`, `device_controller.py`, `deviceApi`, `deviceStorage`, à rota `/checkin/device/[code]` e à `Config` `SITE_URL`, e ajustar a linha de cobertura de testes
- [x] 4.2 Verificar com `grep -rn -i "device\|dispositivo" ARCHITECTURE.md` que só restam ausências esperadas, e confirmar que `REVIEW.md` (registro datado) e `CHANGELOG.md` (gerado pelo commitizen) não foram tocados

## 5. Dependência

- [x] 5.1 Rodar `cd back && uv remove qrcode` e verificar que `pyproject.toml` e `uv.lock` foram atualizados pelo comando, sem edição manual

## 6. Migration (requer aprovação explícita — Constituição, regra 2)

- [x] 6.1 Apagar `back/presenca/migrations/0016_alter_device_code.py` e confirmar com `git status` que era arquivo não rastreado, portanto nunca aplicado em produção — o arquivo já não existia na árvore quando a implementação começou; `git status` confirma que nada foi removido do versionado, a última migration versionada é a `0015_device`
- [ ] 6.2 Com aprovação do desenvolvedor, criar `back/presenca/migrations/0016_delete_device.py` com `DeleteModel("Device")` e `dependencies = [("presenca", "0015_device")]`
- [ ] 6.3 Verificar com `uv run python manage.py makemigrations --check --dry-run` que não sobra diferença de schema, e com `uv run python manage.py migrate` em banco recriado do zero que o grafo aplica limpo

## 7. Deploy

- [ ] 7.1 Confirmar com o responsável que nenhum tablet em campo ainda depende do modo dispositivo e que os aparelhos voltaram ao fluxo de QR rotativo
- [ ] 7.2 Copiar o `db.sqlite3` de produção para fora do servidor antes de subir as imagens, e verificar que o arquivo copiado abre e lista as tabelas
- [ ] 7.3 Subir back e front juntos (`sendimage.py back front` e `loadimage.py back front`) e verificar nos logs do container que a `0016_delete_device` foi aplicada e que o check-in por QR rotativo marca presença normalmente
