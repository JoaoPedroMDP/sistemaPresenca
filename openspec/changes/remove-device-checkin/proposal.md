## Why

O modo dispositivo (check-in por aparelho liberado, sem QR rotativo) não será
mais o caminho do projeto. Enquanto o código continuar de pé ele custa
manutenção e mantém aberta uma superfície sem proteção contra força bruta
(`REVIEW.md`, A6: nenhum rate limiting em `/api/checkin/device/...`, com código
de 6 caracteres alfanuméricos). O check-in por QR rotativo (`Code`) segue sendo
o único fluxo de presença.

## What Changes

- **BREAKING** As rotas `POST /api/checkin/device/{code}/activate`,
  `GET /api/checkin/device/{code}/pending` e
  `POST /api/checkin/device/{code}/{member_id}` deixam de existir. Aparelhos com
  código salvo no `localStorage` passam a receber 404 na próxima chamada, sem
  aviso prévio no app.
- **BREAKING** O model `Device` e a tabela `presenca_device` são removidos. A
  migration de remoção é destrutiva: em produção a tabela é dropada com os
  códigos, ativações e revogações que existirem.
- A rota do front `/checkin/device/[code]` sai, junto de `deviceApi.svelte.ts` e
  `deviceStorage.ts`.
- O `DeviceAdmin` sai do admin, e com ele o QR Code de ativação — único uso da
  dependência `qrcode` no back, que também é removida.
- Os protótipos `06-dispositivo-lista.html` e `07-dispositivo-confirmacao.html`
  saem, junto das referências no `prototypes/README.md` e no bloco "Credencial
  do dispositivo" de `prototypes/assets/app.js` (Constituição, regra 4:
  protótipos nunca divergem das telas).
- Os check-ins já gravados por aparelho **permanecem**: `CheckIn` não tem
  vínculo com `Device`, guarda apenas membro, evento e data-hora.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. O projeto ainda não tem inventário de specs (`openspec list --specs`
não devolve nada) e o modo dispositivo nunca foi especificado, então não há
requisito existente para marcar como REMOVED. A mudança altera comportamento
observável, mas não há spec a alterar: `skip_specs: true` no `.openspec.yaml`.

## Impact

**Back** — `presenca/api/device.py` e `presenca/controllers/device_controller.py`
(arquivos inteiros); `class Device` em `presenca/models.py`; `DeviceAdmin`,
registro e imports de `qrcode` em `presenca/admin.py`; as quatro exceções de
dispositivo em `presenca/errors.py`; o mount do `device_router` em
`core/urls.py` e o comentário sobre a ordem antes do `checkin_router`; a
dependência `qrcode` em `back/pyproject.toml`.

**Migration** — a `0015_device` está aplicada em produção (saiu nas tags 1.1.0 e
1.1.1), então a tabela precisa ser dropada por migration. A
`0016_alter_device_code.py` nunca foi versionada (existe só na árvore local) e é
descartada; no lugar entra uma `0016_delete_device` com `DeleteModel`,
dependendo da `0015_device`. Constituição, regra 2: criar essa migration exige
aprovação explícita do desenvolvedor.

**Front** — `routes/checkin/device/[code]/+page.svelte`,
`lib/api/deviceApi.svelte.ts` e `lib/storage/deviceStorage.ts`. `Member.svelte`,
`dateUtils.ts` e `storage/index.ts` são compartilhados com outras telas e ficam
como estão.

**Testes** — `tests/test_device.py`, `tests/test_device_concurrency.py`,
`tests/test_admin_device_qr.py`, `tests/test_admin_device_revoke.py` e as
fixtures `device`/`active_device` em `tests/conftest.py`.

**Docs** — seção "Fluxo do modo dispositivo" do `ARCHITECTURE.md`, mais as
linhas de `Device`, `SITE_URL`, `device.py`, `device_controller.py`,
`deviceApi`, `deviceStorage`, rota do front e cobertura de testes. O `REVIEW.md`
é registro datado de uma revisão e não é reescrito. O `CHANGELOG.md` é gerado
pelo commitizen e nunca editado à mão.

**Operacional** — qualquer tablet ainda em uso precisa voltar ao fluxo de QR
rotativo antes do deploy. A `Config` `SITE_URL` perde o único consumidor; a
linha pode ficar no banco sem efeito.
