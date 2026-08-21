# Assinify — Autenticação e frontend integrado

Sistema de gerenciamento inteligente de assinaturas, projeto de graduação da COTEMIG. Esta branch implementa autenticação completa (JWT), autorização por papel (`user`/`admin`) com controle de posse sobre os próprios dados, e o frontend de produção integrado a esse fluxo — substituindo o CRUD acadêmico e o frontend provisório das entregas anteriores.

---

## Arquitetura

Monolito modular em camadas (`controllers/` → `services/` → `models/`/`repositories/`), com elementos pontuais de Clean Architecture e Hexagonal aplicados onde resolvem um problema real do projeto — sem abstrações decorativas. Detalhes das decisões arquiteturais estão registrados na conversa que gerou esta branch.

### Controllers

As Controllers são implementadas como classes (`AuthController`, `UsuarioController`, `CategoriaController` e `AssinaturaController`). Elas recebem a requisição HTTP, extraem os dados, delegam o caso de uso ao Service e retornam a resposta HTTP. As regras de negócio ficam nos Services.

### Services

Cada caso de uso possui seu próprio Service em forma de classe, por exemplo `CriarAssinaturaService`, `AtualizarAssinaturaService` e `DeletarCategoriaService`.

### Models

| Model | Tabela | Campos |
|---|---|---|
| `Usuario` | `usuarios` | id, nome, email, senha_hash, role (`user`/`admin`), data_cadastro |
| `Categoria` | `categorias` | id, nome_categoria, descricao |
| `Assinatura` | `assinaturas` | id, nome_servico, valor_mensal, data_renovacao, status, tipo_plano, metodo_pagamento, id_usuario, id_categoria |

> `telefone` foi removido do escopo do projeto. Assinify não coleta CPF nem telefone, e não processa pagamentos.

### Rotas da API

| Método | Rota | Acesso |
|---|---|---|
| POST | `/auth/registrar` | Público — cadastro (sempre cria com `role='user'`) |
| POST | `/auth/login` | Público — retorna JWT |
| GET | `/auth/me` | Autenticado |
| GET | `/usuarios` | Admin |
| GET, PUT | `/usuarios/<id>` | Admin ou o próprio usuário |
| DELETE | `/usuarios/<id>` | Admin |
| PATCH | `/usuarios/<id>/role` | Admin — promove/rebaixa outro usuário |
| GET, POST | `/categorias` | Autenticado — cada usuário vê/cria só as próprias categorias |
| PUT, DELETE | `/categorias/<id>` | Autenticado — apenas o dono da categoria |
| GET, POST | `/assinaturas` | Autenticado — cada um vê/cria só as próprias; admin vê todas |
| GET, PUT, DELETE | `/assinaturas/<id>` | Admin ou dono da assinatura |

Admin de bootstrap criado automaticamente no primeiro startup (configurável em `.env`): `admin@assinify.com` / `admin123`.

### Backend

```
backend/app/
├── config.py            → configuração via .env
├── exceptions.py        → hierarquia de erros (ValidationError, UnauthorizedError, ForbiddenError, NotFoundError)
├── security/            → hash de senha (werkzeug) e geração/validação de JWT (PyJWT)
├── middlewares/         → @token_requerido, @admin_requerido
├── repositories/        → consultas específicas que não são CRUD convencional
├── controllers/         → um Blueprint por feature (auth, usuario, categoria, assinatura)
└── services/            → um arquivo por caso de uso, em subpastas por domínio
```

### Frontend (produção)

Sem frontend provisório — todas as telas usam o design system definitivo (Sora + Inter, `#2563EB`) e estão integradas à autenticação real via JWT.

| Página | Descrição |
|---|---|
| `login.html` | Entrada — layout split-panel com preview do dashboard |
| `registro.html` | Cadastro público |
| `dashboard.html` | Assinaturas do usuário logado (gasto mensal, próximas renovações, CRUD e método de pagamento) |
| `categorias.html` | Categorias do usuário autenticado — CRUD das próprias categorias, incluindo as categorias iniciais |
| `usuarios.html` | Gestão de usuários — restrita a admin (promover/rebaixar role, editar, excluir) |

`js/api.js` centraliza o `fetch` autenticado (injeta o header `Authorization`, redireciona para o login em token ausente/expirado) e a proteção de página (`protegerPagina()`, `exigirAdmin()`).

---


## Funcionalidades Implementadas

As 10 funcionalidades iniciais entregues nesta etapa foram definidas como casos de uso completos, com fluxo **Interface → API Flask → Controller → Service → Model/Repository → Banco de Dados**:

1. Cadastrar usuário
2. Realizar login
3. Cadastrar assinatura
4. Listar assinaturas
5. Atualizar assinatura
6. Excluir assinatura
7. Cadastrar categoria
8. Listar categorias
9. Atualizar categoria
10. Excluir categoria

Cada caso de uso possui um Service próprio. As Controllers são classes responsáveis pelo fluxo HTTP, enquanto as Models concentram o CRUD convencional. O Repository de usuários fica reservado para consultas específicas, como busca por e-mail e verificação da existência de administrador.

Novas contas recebem automaticamente categorias iniciais inspiradas em gerenciadores de assinaturas como o Wallos (Entretenimento, Música, Software, Educação, Jogos, Armazenamento, Produtividade e Outros), mas o usuário pode editar ou excluir essas categorias. Cada assinatura também permite informar o método de pagamento (cartão de crédito, cartão de débito, PIX, boleto, débito automático, transferência ou outro).

## Como executar

### Pré-requisitos

- Python 3.10+
- MySQL 8.0+ (via XAMPP)
- Extensão Live Server no VSCode (para o frontend)

### 1. Criar o banco de dados

> **Se você já tinha o banco de uma entrega anterior**, dê `DROP DATABASE assinify;` antes — o schema de `usuarios` mudou (sem `telefone`, com `role`, `senha` virou `senha_hash`) e o script usa `create table if not exists`, então não migra uma tabela já existente.

Abra o phpMyAdmin (`http://localhost/phpmyadmin`), vá em **SQL** e execute:

```
backend/database/create_database.sql
```

### 2. Configurar e rodar o backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask run
```

Copie `.env.example` para `.env` e ajuste se necessário (já vem com um valor padrão de desenvolvimento). A API sobe em `http://localhost:5000`.

### 3. Rodar o frontend

Abra a pasta `frontend/pages/` com o Live Server do VSCode e acesse `login.html` (crie uma conta pelo próprio cadastro).

> Certifique-se de que a API está rodando antes de abrir o frontend.

---

## Estrutura da branch

```
assinify/
├── frontend/
│   ├── css/style.css
│   ├── js/
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── dashboard.js
│   │   ├── categorias.js
│   │   └── usuarios.js
│   └── pages/
│       ├── login.html
│       ├── registro.html
│       ├── dashboard.html
│       ├── categorias.html
│       └── usuarios.html
└── backend/
    ├── app.py
    ├── requirements.txt
    ├── .env.example
    ├── database/
    │   └── create_database.sql
    └── app/
        ├── __init__.py
        ├── config.py
        ├── extensions.py
        ├── exceptions.py
        ├── security/
        ├── middlewares/
        ├── controllers/
        │   ├── auth_controller.py
        │   ├── usuario_controller.py
        │   ├── categoria_controller.py
        │   └── assinatura_controller.py
        ├── models/
        │   ├── usuario.py
        │   ├── categoria.py
        │   └── assinatura.py
        ├── repositories/
        │   └── usuario_repository.py
        └── services/
            ├── auth/
            ├── usuario/
            ├── categoria/
            └── assinatura/
```
