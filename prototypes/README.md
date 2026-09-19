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

As telas se ligam entre si igual ao app: o scan do QR leva ao check-in e o
login leva ao perfil. Nenhuma tela do protótipo exige credencial para ser
aberta.

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
festa.

Na implementação isso vira um componente Svelte (`Member.svelte`), consumido
pelo `Phloating.svelte`.
