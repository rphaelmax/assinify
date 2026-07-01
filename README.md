# Assinify — CRUD das Models (feat/crud-models)

Esta branch implementa o CRUD completo das principais Models do projeto, seguindo a arquitetura em camadas com Controllers, Services, Models e Repositories, conforme o material disponibilizado pelo professor Gleison (Projeto de Software).

---

## O que foi implementado

### Models

Todas herdam de `db.Model` e possuem os métodos `salvar()`, `atualizar()`, `deletar()`, `listar_todos()`, `buscar_por_id()` e `to_dict()`.

| Model | Tabela | Campos |
|---|---|---|
| `Usuario` | `usuarios` | id, nome, email, senha, telefone, data_cadastro |
| `Categoria` | `categorias` | id, nome_categoria, descricao |
| `Assinatura` | `assinaturas` | id, nome_servico, valor_mensal, data_renovacao, status, tipo_plano, id_usuario, id_categoria |

### Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| POST | `/usuarios` | Criar usuário |
| GET | `/usuarios` | Listar usuários |
| GET | `/usuarios/<id>` | Buscar usuário por ID |
| PUT | `/usuarios/<id>` | Atualizar usuário |
| DELETE | `/usuarios/<id>` | Deletar usuário |
| POST | `/categorias` | Criar categoria |
| GET | `/categorias` | Listar categorias |
| GET | `/categorias/<id>` | Buscar categoria por ID |
| PUT | `/categorias/<id>` | Atualizar categoria |
| DELETE | `/categorias/<id>` | Deletar categoria |
| POST | `/assinaturas` | Criar assinatura |
| GET | `/assinaturas` | Listar assinaturas |
| GET | `/assinaturas/<id>` | Buscar assinatura por ID |
| PUT | `/assinaturas/<id>` | Atualizar assinatura |
| DELETE | `/assinaturas/<id>` | Deletar assinatura |

### Services

Organizados por caso de uso, um arquivo por operação, dentro de subpastas por Model:

```
services/
├── usuario/
│   ├── criar_usuario_service.py
│   ├── listar_usuarios_service.py
│   ├── buscar_usuario_service.py
│   ├── atualizar_usuario_service.py
│   └── deletar_usuario_service.py
├── categoria/
│   └── (mesma estrutura)
└── assinatura/
    └── (mesma estrutura)
```

### Frontend (provisório)

O frontend desta entrega é provisório e tem como objetivo demonstrar o funcionamento completo do CRUD via interface, conforme exigido pela atividade. As telas serão redesenhadas nas próximas entregas com autenticação real e navegação definitiva.

| Página | Funcionalidades |
|---|---|
| `dashboard.html` | Listar, criar, editar e excluir assinaturas |
| `categorias.html` | Listar, criar, editar e excluir categorias |
| `usuarios.html` | Listar, criar, editar e excluir usuários |

> O seletor de usuário no dashboard é provisório e será substituído por autenticação via login nas próximas entregas.

---

## Como executar

### Pré-requisitos

- Python 3.10+
- MySQL 8.0+ (via XAMPP)
- Extensão Live Server no VSCode (para o frontend)

### 1. Criar o banco de dados

Abra o phpMyAdmin (`http://localhost/phpmyadmin`), vá em **SQL** e execute o conteúdo do arquivo:

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

A API estará disponível em: `http://localhost:5000`

### 3. Rodar o frontend

Abra a pasta `frontend/pages/` com o Live Server do VSCode e acesse `dashboard.html`.

> Certifique-se de que a API está rodando antes de abrir o frontend.

---

## Estrutura da branch

```
assinify/
├── frontend/
│   ├── css/style.css
│   ├── js/
│   │   ├── dashboard.js
│   │   ├── categorias.js
│   │   └── usuarios.js
│   └── pages/
│       ├── dashboard.html
│       ├── categorias.html
│       └── usuarios.html
└── backend/
    ├── app.py
    ├── requirements.txt
    ├── database/
    │   └── create_database.sql
    └── app/
        ├── __init__.py
        ├── extensions.py
        ├── routes.py
        ├── controllers/
        │   ├── usuario_controller.py
        │   ├── categoria_controller.py
        │   └── assinatura_controller.py
        ├── models/
        │   ├── usuario.py
        │   ├── categoria.py
        │   └── assinatura.py
        ├── repositories/
        └── services/
            ├── usuario/
            ├── categoria/
            └── assinatura/
```
