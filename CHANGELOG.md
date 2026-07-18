## 1.0.1 (2026-07-18)

### Fix

- Agora novos eventos sem regras de pontuação atreladas não travam na hora do checkin
- Agora commitizen sempre cria annotated tags

## 1.0.0 (2026-07-18)

### Feat

- Agora o QRcode dura um tempo e várias pessoas podem escanear o mesmo
- Scoreboard ao lado do QRcode
- Estilização
- Agora mostra aniversário e nao created_at no admin de membros

### Fix

- Dados de teste removidos, versao atualziada
- Ao buscar checkins hoje, não levava em conta o fuso horário change: Agora a largura e altura dos nós flutuantes é dinâmica fix: Por algum motivo, de vez em quando o front travava depois de certo numero de checkins, alegando ids duplicados. Embora cada nó tenha como id o nome do membro, que não tem duplicatas, fiz uma verificação de duplicidade no checkin, pra evitar esse problema. Suspeito que pode ser algum tipo de envio duplicado de mensagem no websocket
- Falhar na busca de membro na API nao redirecionava para o login
- Rota de checkin deve vir por ultimo para nao sobrescrever outras rotas com menos variaveis no path change: Mais chamadas de api no front com padrão call... add: Feature de aniversariante no front fix: Botão e input de texto estavam formatados erroneamente add: Página de teste
- Tipagem errada nos consumers wip: Chapeu de aniversario nos aniversariantes wip: Buscar lista de quem já fez checkin quando troca o qrcode de computador
- Logout no front nao funcionava caso a rota de logout /desse erro. Agora independente do retorno ele reseta o auth change: Ao enviar nova imagem de perfil, apaga a antiga. Nome da imagem agora tem o timestamp que foi adicionada
- arquivo de log nao podia ser criado
- Na hora de fazer a comparação com o horário definido nas regras, não considerava o timezone
- Bug na hora de mostrar a data de aniversário fix: Bug na versão do código add: Agora o checkin tem evento associado change: Campo used agora é a data de quando o código foi usado change: Agora quando o trigger de login é ativado no fornt, ele checa diretamente no backend se o usuario está logado, melhorando o estado de autenticação add: Funções para exportar e importar checkins
- Apenas restart não reiniciava o container com a nova imagem
- Faltou atualizar o dockercomposeprod
- Rotas estaticas devem ser declaradas antes das dinamicas fix:  Biblioteca própria para svelte para gerar qrcode
- typo
- Problema com CDN
- Url errada
- Faltou definir o volume

### Refactor

- removidos repositories
