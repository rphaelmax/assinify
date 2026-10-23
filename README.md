# Assinify

## RESUMO DAS 10 NOVAS FUNCIONALIDADES

Em relação à versão anterior:

1. **Periodicidade das assinaturas**: além de mensal, agora há assinaturas semanais e anuais. Os valores são anualizados (semanal × 52, mensal × 12, anual × 1) e os totais mensais são normalizados por esse fator.
2. **Próxima renovação automática**: calculada a partir da data cadastrada e da periodicidade, respeitando meses curtos, 29/fev e o intervalo de 7 dias das semanais. A data cadastrada nunca precisa ser atualizada à mão.
3. **Busca, filtros, ordenação e paginação**: a listagem de assinaturas aceita busca por nome, filtros (categoria, status, pagamento e periodicidade), ordenação e paginação.
4. **Histórico de alterações**: cada assinatura registra campo alterado, valor antigo → novo e data (`GET /assinaturas/<id>/historico`).
5. **Exportação em CSV**: respeita os filtros ativos e gera UTF-8 com BOM, abrindo direto no Excel (`GET /assinaturas/exportar`).
6. **Gráficos no dashboard**: gasto por categoria e por método de pagamento (Chart.js), além de gasto mensal e anual, média por assinatura e categoria mais cara.
7. **Notificações e calendário de renovações**: alertas de vencimentos nos próximos 7 dias e calendário mensal, independentes da paginação da lista.
8. **Perfil e troca de senha**: nova página `perfil.html` para editar nome, e-mail e senha.
9. **Medidor de força de senha**: exibido no cadastro e na troca de senha, com a API recusando senhas muito fracas.
10. **Tema claro/escuro/automático e PWA**: o tema segue o sistema ou é definido manualmente, e o app pode ser instalado no celular e no desktop.

**Também incluído:** logos dos serviços via [logo.dev](https://logo.dev), proteção do admin padrão (não pode ser excluído, ter o e-mail alterado nem ser rebaixado), bloqueio de exclusão de categorias que possuem assinaturas e novos módulos no backend (`validacao.py` e `renovacao.py`).

## Funcionalidades completas

**Conta e acesso**
- Cadastro e login com JWT (expira em 8h), perfil (nome e e-mail) e troca de senha.
- Medidor de força de senha no cadastro e na troca de senha. A API recusa senhas muito fracas (mínimo de 6 caracteres).
- Duas roles: `user` e `admin`. Todo cadastro público nasce como `user`.
- Um **admin padrão** é criado no primeiro startup (dados no `.env`) e é protegido: não pode ser excluído, ter o e-mail alterado nem ser rebaixado.
- Admins gerenciam usuários (editar, promover/rebaixar, excluir). Ninguém altera a própria role nem exclui a própria conta.

**Categorias**
- Cada usuário vê e edita só as suas. Ao se cadastrar, recebe 8 categorias iniciais inspiradas em gerenciadores como o Wallos (Entretenimento, Música, Software, Educação, Jogos, Armazenamento, Produtividade e Outros), que podem ser editadas ou excluídas.
- Uma categoria com assinaturas não pode ser excluída.

**Assinaturas**
- CRUD com nome do serviço, valor, **periodicidade** (semanal, mensal ou anual), data de renovação, status (ativa/cancelada), plano, método de pagamento (cartão de crédito, cartão de débito, PIX, boleto, débito automático, transferência ou outro) e categoria.
- Busca por nome, filtros (categoria, status, pagamento, periodicidade), ordenação e paginação.
- **Próxima renovação calculada automaticamente** a partir da data cadastrada e da periodicidade: mensal respeita meses curtos, anual respeita 29/fev e semanal soma 7 dias. A data cadastrada nunca precisa ser atualizada à mão.
- **Histórico de alterações** por assinatura (campo, valor antigo → novo, data).
- **Exportação em CSV** respeitando os filtros ativos (UTF-8 com BOM, abre direto no Excel).
- Valores **anualizados**: semanal × 52, mensal × 12, anual × 1. Os totais mensais são sempre normalizados por esse fator.

**Dashboard**
- Gasto mensal e anual, média por assinatura e categoria mais cara.
- Gráficos (Chart.js): gasto por categoria e por método de pagamento.
- Próximas renovações, notificações de vencimentos nos próximos 7 dias e calendário mensal de renovações. Os três independem da paginação da lista.
- Logos dos serviços via [logo.dev](https://logo.dev).
- Tema claro, escuro ou automático (segue o sistema).
- PWA: manifest e service worker, instalável no celular e no desktop.

## Arquitetura

Monolito modular em camadas (`controllers/` → `services/` → `models/` e `repositories/`), com elementos pontuais de Clean Architecture e Hexagonal aplicados onde resolvem um problema real do projeto, sem abstrações decorativas. Backend em Flask + SQLAlchemy + MySQL; frontend em HTML, CSS e JavaScript puros, sem framework nem build.

### Controllers

Classes (`AuthController`, `UsuarioController`, `CategoriaController` e `AssinaturaController`) que recebem a requisição HTTP, extraem os dados, delegam o caso de uso ao Service e devolvem a resposta. Não têm regra de negócio.

### Services

Um Service por caso de uso, em forma de classe (`CriarAssinaturaService`, `AtualizarAssinaturaService`, `DeletarCategoriaService`…), agrupados em subpastas por domínio. É aqui que ficam as regras de negócio e as checagens de posse dos dados.

### Models e Repositories

As Models concentram o CRUD convencional. O Repository de usuários fica reservado para consultas específicas, como busca por e-mail e verificação da existência de administrador.

| Model | Tabela | Campos |
|---|---|---|
| `Usuario` | `usuarios` | id_usuario, nome, email, senha_hash, role (`user`/`admin`), data_cadastro |
| `Categoria` | `categorias` | id_categoria, nome_categoria, descricao, id_usuario |
| `Assinatura` | `assinaturas` | id_assinatura, nome_servico, valor_mensal, periodicidade, data_renovacao, status, tipo_plano, metodo_pagamento, id_usuario, id_categoria |
| `HistoricoAssinatura` | `historico_assinaturas` | id, id_assinatura, campo, valor_antigo, valor_novo, data_alteracao, id_usuario |

O campo `valor_mensal` guarda o valor cobrado **por período**. Para uma assinatura anual de R$ 600 ele vale `600`, e `valor_anualizado` na resposta traz o total do ano.

### Estrutura do projeto

```
assinify/
├── README.md
├── frontend/
│   ├── pages/                  # login, registro, dashboard, categorias, usuarios, perfil
│   ├── js/                     # api.js, auth.js, dashboard.js, calendario.js, categorias.js,
│   │                           # usuarios.js, perfil.js, forca-senha.js, tema.js, auth-preview.js
│   ├── css/style.css
│   ├── icons/
│   ├── manifest.json
│   └── sw.js                   # service worker (PWA)
└── backend/
    ├── app.py                  # ponto de entrada
    ├── requirements.txt
    ├── .env.example
    ├── database/create_database.sql
    └── app/
        ├── __init__.py         # app factory, handlers de erro, migração leve, admin inicial
        ├── config.py           # configuração via .env
        ├── extensions.py
        ├── exceptions.py       # ValidationError, UnauthorizedError, ForbiddenError, NotFoundError
        ├── validacao.py        # validações de entrada reutilizáveis
        ├── renovacao.py        # cálculo de próxima renovação e calendário
        ├── security/           # hash de senha (werkzeug) e JWT (PyJWT)
        ├── middlewares/        # @token_requerido, @admin_requerido
        ├── controllers/        # um Blueprint por feature (auth, usuario, categoria, assinatura)
        ├── models/
        ├── repositories/
        └── services/           # auth/, usuario/, categoria/, assinatura/
```

### Frontend

Todas as telas usam o design system definitivo (Sora + Inter, `#2563EB`) e estão integradas à autenticação real via JWT.

| Página | Descrição |
|---|---|
| `login.html` | Entrada, em layout split-panel com preview do dashboard |
| `registro.html` | Cadastro público |
| `dashboard.html` | Assinaturas do usuário logado: gastos, gráficos, renovações, notificações, calendário e CRUD |
| `categorias.html` | CRUD das categorias do usuário autenticado |
| `usuarios.html` | Gestão de usuários, restrita a admin |
| `perfil.html` | Edição de nome, e-mail e senha |

`js/api.js` centraliza o `fetch` autenticado (injeta o header `Authorization` e redireciona para o login se o token faltar ou expirar) e a proteção de página (`protegerPagina()`, `exigirAdmin()`).

---

## Como executar

### Pré-requisitos

- Python 3.10+
- MySQL 8.0+ (via XAMPP)
- Extensão Live Server no VSCode (para o frontend)

### 1. Criar o banco de dados

Abra o phpMyAdmin (`http://localhost/phpmyadmin`), vá em **SQL** e execute o conteúdo de:

```
backend/database/create_database.sql
```

As tabelas também são criadas automaticamente quando a API sobe. O script garante que o banco `assinify` exista.

### 2. Configurar e rodar o backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate               # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env              # Linux/macOS: cp .env.example .env
flask run
```

A API sobe em `http://localhost:5000`. Também funciona com `python app.py`.

Variáveis do `.env`:

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave de assinatura dos JWT. **Troque por um valor longo e aleatório.** |
| `DATABASE_URL` | Padrão do XAMPP: `mysql+pymysql://root:@localhost/assinify` |
| `ADMIN_EMAIL` | E-mail do admin padrão (padrão: `admin@assinify.com`) |
| `ADMIN_SENHA` | Senha inicial do admin padrão (padrão: `admin123`) |

O admin é criado automaticamente no primeiro startup, caso ainda não exista nenhum.

### 3. Rodar o frontend

Abra a **raiz do projeto** no VSCode, clique com o botão direito em `frontend/pages/login.html` e escolha **Open with Live Server**. A raiz do servidor precisa conter a pasta `frontend/`, porque as páginas carregam `../js` e `../css`. Depois crie uma conta pelo próprio cadastro.

Alternativa sem VSCode:

```bash
cd frontend
python -m http.server 5500          # acesse http://localhost:5500/pages/login.html
```

O endereço da API fica na constante `API` em `frontend/js/api.js` (padrão `http://localhost:5000`). Certifique-se de que a API está rodando antes de abrir o frontend.

---

## API

Todas as rotas, exceto registro e login, exigem `Authorization: Bearer <token>`. Erros retornam `{"erro": "mensagem"}`.

**Autenticação**

| Método | Rota | Descrição |
|---|---|---|
| POST | `/auth/registrar` | Cria conta (`nome`, `email`, `senha`), sempre com `role='user'` |
| POST | `/auth/login` | Retorna `{token, usuario}` |
| GET | `/auth/me` | Usuário autenticado |
| PUT | `/auth/perfil` | Atualiza nome e e-mail |
| PATCH | `/auth/senha` | Troca a senha (`senha_atual`, `nova_senha`) |

**Usuários**

| Método | Rota | Acesso |
|---|---|---|
| GET | `/usuarios` | Admin |
| GET, PUT | `/usuarios/<id>` | Admin ou o próprio usuário |
| DELETE | `/usuarios/<id>` | Admin |
| PATCH | `/usuarios/<id>/role` | Admin (`{"role": "user"}` ou `{"role": "admin"}`) |

**Categorias** (sempre as do usuário autenticado, sem exceção para admin)

`GET /categorias`, `POST /categorias`, `GET | PUT | DELETE /categorias/<id>`

**Assinaturas**

A listagem e as estatísticas mostram sempre as assinaturas do próprio usuário. Os endpoints por id (`/assinaturas/<id>` e `/assinaturas/<id>/historico`) também aceitam admin.

| Método | Rota | Descrição |
|---|---|---|
| GET | `/assinaturas` | Lista com busca, filtros, ordenação e paginação (parâmetros abaixo) |
| POST | `/assinaturas` | Cria assinatura |
| GET | `/assinaturas/estatisticas` | Totais, médias e quebra por categoria e por método de pagamento |
| GET | `/assinaturas/proximas` | Assinaturas ativas ordenadas pela próxima renovação (`limite`, padrão 50) |
| GET | `/assinaturas/calendario` | Renovações de um mês (`ano`, `mes`; padrão: mês atual) |
| GET | `/assinaturas/exportar` | CSV com os mesmos filtros da listagem |
| GET, PUT, DELETE | `/assinaturas/<id>` | Detalhe, edição e exclusão |
| GET | `/assinaturas/<id>/historico` | Histórico de alterações |

Parâmetros de `GET /assinaturas`: `busca`, `id_categoria`, `status`, `metodo_pagamento`, `periodicidade`, `ordenar_por` (`nome_servico`, `valor_mensal`, `data_renovacao` ou `status`), `ordem` (`asc` ou `desc`), `page` e `limit` (máx. 100). Sem `page` e `limit` a resposta é uma lista simples. Com eles, vem `{assinaturas, paginacao}`.

Valores aceitos:
- `periodicidade`: `semanal`, `mensal`, `anual`
- `status`: `ativa`, `cancelada`
- `metodo_pagamento`: `cartao_credito`, `cartao_debito`, `pix`, `boleto`, `debito_automatico`, `transferencia`, `outro`