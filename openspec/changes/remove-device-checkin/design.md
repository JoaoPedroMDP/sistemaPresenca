## Context

Ver `proposal.md` — Why. O que importa aqui é o estado das migrations e do
deploy.

A `0015_device` (commit `b8959b8`) saiu nas tags 1.1.0 e 1.1.1, então a tabela
`presenca_device` existe em produção. A `0016_alter_device_code.py` — que encurta
o código para 6 caracteres e reseta `activated_at` — nunca foi versionada:
existe apenas como arquivo não rastreado na árvore local do desenvolvedor.

Produção roda em SQLite (`/app/data/db.sqlite3`, montado no host) com um único
container de back; não há registry nem pipeline: `sendimage.py` builda e envia as
imagens de back e front, `loadimage.py` recria os serviços no servidor. O
`back_entrypoint.sh` roda `migrate` na subida.

O ambiente de desenvolvimento é descartável e não entra em nenhuma decisão
abaixo.

## Goals / Non-Goals

**Goals**

- Tirar a tabela `presenca_device` do banco de produção por migration, sem passo
  manual no servidor.
- Deixar o histórico de migrations coerente: nenhuma operação em produção sobre
  uma tabela que será dropada em seguida.

**Non-Goals**

- Preservar códigos de dispositivo, ativações ou revogações. São credenciais
  operacionais, não histórico de presença.
- Migrar os aparelhos em campo automaticamente. A volta ao QR rotativo é
  operacional e acontece antes do deploy.
- Mexer no fluxo de `Code` (QR rotativo), em `CheckinController.checkin` ou em
  `Member.didnt_checkin_today`.

## Decisions

### Descartar a `0016_alter_device_code` em vez de commitá-la

A alternativa seria versionar a 0016 como está e criar uma `0017_delete_device`.
Isso faria produção executar o `RunPython shorten_codes` — sorteando códigos
novos e zerando `activated_at` de cada linha — para dropar a tabela na operação
seguinte. Trabalho inútil sobre dados condenados, e um `RunPython` a mais no
histórico permanente.

Como a 0016 nunca foi commitada, ela pode ser apagada e o número reaproveitado:
entra uma `0016_delete_device` com `DeleteModel("Device")`, dependendo de
`0015_device`. Produção sai da 0015 direto para a remoção.

Constituição, regra 2: essa migration só é criada com aprovação explícita do
desenvolvedor.

### Rollback é `migrate presenca 0015` + backup, não a migration reversa

`DeleteModel` é reversível no grafo — o `migrate` para trás recria a tabela a
partir do estado da 0015. Mas ela volta **vazia**, e com a coluna `code` no
tamanho antigo (UUID), já que a 0016 que a encurtava foi descartada. Nenhum
código de dispositivo é recuperado.

Recuperar de verdade exige o `db.sqlite3` de antes do deploy. Como a remoção do
model e das rotas acompanha a migration no mesmo par de imagens, um rollback
real é voltar as imagens anteriores **e** restaurar o banco — não é um
`migrate` isolado. Por isso o backup do arquivo antes de subir é passo de
tarefa, não recomendação.

### Back e front sobem no mesmo deploy

Não existe janela de incompatibilidade a proteger: `loadimage.py` recria os dois
serviços e o front é estático servido pelo Caddy. Uma remoção só do back deixaria
a rota `/checkin/device/[code]` no ar chamando API morta; uma remoção só do front
deixaria a superfície de API aberta, que é parte do motivo da mudança. As duas
metades andam juntas.

## Risks / Trade-offs

- **Tablet em uso no culto seguinte ao deploy para de funcionar sem aviso** (o
  front responde 404 genérico, não uma mensagem de fim de vida) → conferir antes
  do deploy que nenhum aparelho depende do modo dispositivo e devolvê-lo ao
  fluxo de QR rotativo.
- **Perda irreversível dos registros de ativação/revogação** → backup do
  `db.sqlite3` antes do `migrate`; os check-ins em si não estão em risco, pois
  `CheckIn` não referencia `Device`.
- **`Config` `SITE_URL` fica órfã** (só o QR do `DeviceAdmin` a lia) → a linha é
  inofensiva; não vale uma migration de limpeza. Fica registrada na remoção da
  menção do `ARCHITECTURE.md`.
- **Rotas antigas passam a cair no `checkin_router`** depois que o
  `device_router` sai da frente → `POST /api/checkin/device/<code>/activate` não
  casa com `{code_str}/{m_id}` (`activate` não é `int`) e responde 404. Sem
  efeito colateral, mas o comentário de ordem em `core/urls.py` perde sentido e
  sai junto.

## Migration Plan

1. Remover código, testes, front, protótipos e docs (a tabela continua no banco;
   nada mais a lê).
2. Apagar `back/presenca/migrations/0016_alter_device_code.py` (não rastreado).
3. Com aprovação, criar `0016_delete_device` (`DeleteModel("Device")`,
   `dependencies = [("presenca", "0015_device")]`) e conferir com
   `makemigrations --check` que não sobra diferença de schema.
4. `uv remove qrcode` (regra 5: nunca editar o lock à mão).
5. Backup do `db.sqlite3` de produção antes de subir as imagens novas.
6. Deploy com `sendimage.py back front` + `loadimage.py back front`; o
   `back_entrypoint.sh` aplica a migration na subida.
