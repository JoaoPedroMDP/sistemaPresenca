# Protótipos — Sistema de Presença

HTML, CSS e JavaScript puros. Sem build, sem dependências, sem servidor:
abra qualquer arquivo no navegador ou carregue a pasta no Pinacoteca.
Cada arquivo é uma tela isolada, fiel ao app — sem menus ou controles extras.

## Telas

| Arquivo | Rota no app | O que é |
|---|---|---|
| `01-painel.html` | `/` | Painel do telão: nome do evento, QR Code, fotos flutuantes, placar |
| `02-checkin-scan.html` | `/checkin/[code]` | Check-in aberto pelo scan do QR |
| `03-checkin-erro.html` | `/checkin/[code]` (erro) | Código expirado (400) ou inexistente (404) |
| `04-login.html` | `/login` | Login por usuário e senha |
| `05-perfil.html` | `/me` | Perfil, foto com recorte, histórico e pontos |
| `06-dispositivo-lista.html` | `/checkin/device/[code]` | **Novo** — grade de membros pendentes com busca; na primeira visita, ativa o aparelho |
| `07-dispositivo-confirmacao.html` | `/checkin/device/[code]` (estado de confirmação) | **Novo** — confirma identidade e registra presença; no app é um estado da mesma rota, não uma rota à parte |

As telas se ligam entre si igual ao app: o login leva ao perfil, a ativação
leva à lista, a lista leva à confirmação. Não há tela de digitar código nem
senha — o aparelho é liberado escaneando o QR Code gerado no admin.

A ativação não é uma tela à parte: é o estado inicial da lista, visível só na
primeira visita. `06-dispositivo-lista.html?code=abc` mostra o "Ativando este
dispositivo…" antes da grade; `?erro=usado` (ou `?erro=invalido`) mostra a
falha. Sem parâmetro, a lista abre direto — é o que o aparelho já ativado vê.
Nenhuma tela do protótipo exige credencial para ser aberta.

## Arquivos compartilhados

- `assets/styles.css` — tokens de cor e componentes espelhando as classes
  Tailwind usadas no app (indigo-900, emerald-500, Readex Pro, Courier Prime).
- `assets/app.js` — componente de membro, dados falsos, QR Code desenhado à
  mão e o motor do Phloating.
- `assets/*.png` — logos e chapéu de festa copiados de `front/src/lib/assets/`.

## Componente de membro

`memberHTML(member, { size, showName })` em `assets/app.js` é a única marcação
de um membro em todo o protótipo: foto (ou o placeholder `profileAzul.png`,
como no `PhotoSelector`), nome completo e, na semana do aniversário, chapéu de
festa com confete. O Phloating e a lista do tablet usam a mesma função, só com
tamanhos diferentes — quem nasce aniversariante ganha os mesmos perks nos dois
lugares.

Na implementação isso vira um componente Svelte (`Member.svelte`), consumido
pelo `Phloating.svelte` e pela tela do tablet.

## Fluxo do modo tablet

```
admin gera código  ──QR──►  lista de pendentes (ativa na 1ª visita)
                                   ▲                  │ toque no nome
                                   └──── 3s ──── confirmação
```

1. No admin, o responsável cria um `Device` para o evento. A tela de edição
   mostra o QR Code de ativação.
2. O tablet escaneia e cai em `/checkin/device/<code>`. O código é resgatado
   uma única vez: não serve para liberar um segundo aparelho. Enquanto isso a
   própria lista mostra "Ativando este dispositivo…".
3. O código fica no `localStorage` e vai no path de toda chamada do aparelho.
   Reabrir o app cai direto na lista, sem pedir nada.
4. O tablet passa de mão em mão. Cada pessoa acha seu nome (busca ou rolagem),
   toca, confirma pela foto e vê os pontos ganhos.
5. Depois de 3 segundos a tela volta sozinha para a lista, pronta para a
   próxima pessoa. Quem já marcou some da lista.

Não existe botão de encerrar: o aparelho fica liberado até o código expirar ou
ser revogado no admin.

## Notas de segurança para a implementação

Estas decisões estão desenhadas no protótipo e já implementadas no app
(`Device`, `DeviceController`, `presenca/api/device.py`, `DeviceAdmin` e a
rota `/checkin/device/[code]`); o protótipo só encena o fluxo.

- **Nada de "tablet" nas rotas.** Hoje o uso é um tablet passando de mão em
  mão, mas o conceito é "dispositivo liberado". Rotas sob
  `/api/checkin/device/<code_str>/...` (router próprio), espelhando o check-in
  por QR (`/api/checkin/<code_str>/<m_id>`): o código vai no path e é a
  credencial.
  - `POST /api/checkin/device/<code_str>/activate` — resgata o código (uso
    único) e devolve o evento;
  - `GET  /api/checkin/device/<code_str>/pending` — lista de pendentes;
  - `POST /api/checkin/device/<code_str>/<m_id>` — registra a presença.

  O `device_router` é montado antes do `checkin_router` em `core/urls.py`,
  para `/checkin/device/...` não cair na rota genérica `{code_str}/{m_id}`.
- **Uso único.** Cada código libera um aparelho e é queimado no resgate. Um
  vazamento do código depois disso não libera mais ninguém, e o admin sabe
  quantos aparelhos existem: um por código emitido.
- **Modelagem: tabela própria.** Misturar com o `Code` confunde duas coisas
  diferentes — o `Code` é um segredo efêmero compartilhado por vários scans e
  rotacionado por thread. O aparelho é um `Device`: `code`, `event`, `label`,
  `activated_at` (nulo até o resgate, preenchido por UPDATE condicional, então
  o segundo resgate falha) e `revoked_at` (corta um tablet perdido sem mexer
  nos outros). Validação em `DeviceController`, separada do `CodeController`.
- **Admin.** Na tela de edição do `Device` (`DeviceAdmin`), renderizar o QR
  apontando para `/checkin/device/<code>` — é assim que o código chega ao
  aparelho sem ninguém digitar nada. Só mostrar o QR enquanto o código não foi
  resgatado.
- **Validade: 1 mês.** `Device.VALIDITY_DAYS = 30` a partir da criação; depois disso o aparelho volta a pedir um QR novo. Também pode ser
  revogado no admin a qualquer momento — como não há botão de encerrar no
  aparelho, a revogação é o único corte imediato.
- **Força bruta.** O código é um `uuid4`, então não dá para adivinhar; ainda
  assim vale limitar tentativas em `/device/...` para não virar oráculo.
- **Sem QR rotativo no check-in do dispositivo.** A proteção deixa de ser a
  expiração do código e passa a ser inteiramente a posse do código do aparelho.
