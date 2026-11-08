<div align="center">

<h1>Assinify</h1>

<p><strong>Seu gerenciador inteligente de assinaturas, com um assistente de IA que cuida delas com você.</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-API_REST-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" />
  <img src="https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/Google_Gemini-IA-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" />
</p>

</div>

---

## Sobre o projeto

O **Assinify** reúne em um só painel todas as assinaturas e serviços recorrentes de uma pessoa: streaming, música, software, cursos, jogos, armazenamento e o que mais ela pagar todo mês, toda semana ou todo ano.

**Público-alvo:** pessoas que assinam vários serviços digitais e perdem o controle de quanto gastam, de quando cada cobrança chega e de quais assinaturas ainda valem a pena.

**Problema que resolve:** assinaturas são cobradas em datas, moedas e periodicidades diferentes, algumas começam com teste gratuito, outras são divididas com amigos ou familiares, e os preços sobem sem aviso. Sem um lugar único para acompanhar isso, o gasto real fica invisível. O Assinify calcula o gasto mensal e anual, avisa das renovações, projeta os próximos 12 meses, registra reajustes de preço e usa IA para sugerir economia.

> O Assinify **não processa pagamentos** e **não coleta CPF, telefone nem dados de cartão**. Os valores são os que o próprio usuário informa.

---

## Casos de uso implementados

### As 20 funcionalidades principais

| # | Funcionalidade | Descrição |
|---|---|---|
| 1 | **Periodicidade** | Assinaturas semanais, mensais ou anuais. Os valores são anualizados (semanal × 52, mensal × 12, anual × 1) para que os totais sejam comparáveis. |
| 2 | **Próxima renovação automática** | Calculada a partir da data cadastrada e da periodicidade, respeitando meses curtos, 29/fev e o intervalo de 7 dias das semanais. A data nunca precisa ser atualizada à mão. |
| 3 | **Busca, filtros, ordenação e paginação** | Busca por nome; filtros por categoria, status, pagamento e periodicidade; ordenação e paginação. |
| 4 | **Histórico de alterações** | Cada mudança registra o campo, o valor antigo, o novo e a data. |
| 5 | **Exportação em CSV** | Respeita os filtros ativos, em UTF-8 com BOM (abre direto no Excel). |
| 6 | **Dashboard com indicadores e gráficos** | Gasto mensal e anual, média por assinatura, categoria mais cara, gráficos por categoria e por forma de pagamento (Chart.js). |
| 7 | **Notificações e calendário de renovações** | Alertas dos vencimentos dos próximos 7 dias, lista de próximas renovações e calendário mensal. |
| 8 | **Perfil e troca de senha** | Edição de nome, e-mail, moeda base e senha. |
| 9 | **Medidor de força de senha** | No cadastro e na troca de senha; a API também recusa senhas muito fracas. |
| 10 | **Tema claro, escuro ou automático** | Segue o sistema ou é escolhido manualmente. |
| 11 | **Assistente de IA conversacional** | Chat em linguagem natural que consulta, cria, altera, pausa e cancela assinaturas por meio de ferramentas (function calling). A exclusão só acontece após confirmação em botão. |
| 12 | **Análise proativa com IA** | Cartão no dashboard com até 3 insights (alertas de renovação, peso do gasto, sobreposição de serviços), gerados sem o usuário perguntar. |
| 13 | **Recomendação de planos mais baratos** | A IA pesquisa preços atuais na web (Google Search) e sugere plano anual, família, estudante ou combos, com fontes e a economia estimada. |
| 14 | **Multi-moeda com câmbio automático** | 10 moedas (BRL, USD, EUR, GBP, CAD, AUD, JPY, CHF, ARS, MXN). Cada assinatura tem a própria moeda e os totais são convertidos para a moeda base do usuário. |
| 15 | **Assinaturas divididas** | Informe quantas pessoas dividem o plano; o gasto do usuário passa a ser só a parte dele. |
| 16 | **Teste gratuito** | Informe quando o teste termina: o sistema não conta gasto durante o teste, avisa o fim e só considera a primeira cobrança depois dele. |
| 17 | **Pausar e cancelar** | Três status (ativa, pausada, cancelada). Cancelar registra a data e calcula quanto o usuário já economizou. |
| 18 | **Estatísticas avançadas** | Página própria com projeção de caixa dos próximos 12 meses, ranking das maiores assinaturas, concentração do gasto, perfil por faixa de valor, periodicidade e pagamento, canceladas e pausadas. |
| 19 | **Foto de perfil** | Upload validado, recortado em quadrado, reduzido e regravado como JPEG (remove metadados como GPS). |
| 20 | **Detecção de reajustes de preço** | A partir do histórico, mostra quais serviços aumentaram ou reduziram de preço e a variação percentual. |

### Casos de uso de base

**Conta e acesso**
- Cadastro com aceite dos Termos de Uso e da Política de Privacidade (versão e data do aceite ficam registradas) e login com JWT (expira em 8 horas).
- Duas roles: `user` e `admin`. Todo cadastro público nasce como `user`.
- Um **admin padrão** é criado no primeiro startup (dados no `.env`) e é protegido: não pode ser excluído, ter o e-mail alterado nem ser rebaixado, e outros admins não podem editá-lo.
- Admins listam, editam, promovem, rebaixam e excluem usuários. Ninguém altera a própria role nem exclui a própria conta.

**Categorias**
- CRUD de categorias, sempre restrito ao dono: cada usuário vê e edita só as suas, sem exceção para admin.
- Ao se cadastrar, o usuário recebe 8 categorias iniciais (Entretenimento, Música, Software, Educação, Jogos, Armazenamento, Produtividade e Outros), que podem ser editadas ou excluídas.
- Uma categoria que possui assinaturas não pode ser excluída.

**Assinaturas**
- CRUD com nome do serviço, valor, moeda, periodicidade, data de renovação, status, plano, forma de pagamento (cartão de crédito, cartão de débito, PIX, boleto, débito automático, transferência ou outro), número de pessoas, categoria, fim do teste e data de cancelamento.
- Logos dos serviços exibidos via [Logo.dev](https://logo.dev).

---

## Tecnologias

| Camada | Tecnologias |
|---|---|
| **Frontend** | HTML5, CSS3 e JavaScript puros (sem framework e sem build), Chart.js 4, fontes Sora e Inter |
| **Backend** | Python 3.10+, Flask (API REST que devolve apenas JSON), Flask-SQLAlchemy (ORM), Flask-CORS, PyJWT, Werkzeug (hash de senha), Pillow, python-dotenv |
| **Banco de dados** | MySQL 8 (via XAMPP) |
| **IA** | Google Gemini API (chat com ferramentas, saída em JSON e busca na web) |
| **Serviços externos** | open.er-api.com (cotações de câmbio) e Logo.dev (logos) |

---

## Arquitetura

O projeto tem **arquitetura cliente-servidor**: o frontend é um conjunto de arquivos estáticos servido em um servidor próprio, e a API Flask roda em outro. Eles conversam só por requisições HTTP (`fetch()`) com JSON. Não há renderização de HTML no servidor (nenhum Jinja2 ou template).

```
┌─────────────────────────────┐        fetch() + JSON         ┌──────────────────────────────┐
│  FRONTEND (servidor 1)      │  ───────────────────────────► │  API FLASK (servidor 2)      │
│  HTML + CSS + JavaScript    │  ◄───────────────────────────  │  http://localhost:5000       │
│  http://localhost:5500      │     Authorization: Bearer      │                              │
└─────────────────────────────┘                                └──────────────┬───────────────┘
                                                                              │
                              Controllers ──► Services ──► Repositories ──► Models (SQLAlchemy) ──► MySQL
                                                  │
                                                  └──► Gemini API · open.er-api.com
```

### Organização da API em camadas

| Camada | Pasta | Responsabilidade |
|---|---|---|
| **Controllers** | `app/controllers/` | Um Blueprint por recurso. Recebem a requisição HTTP, extraem os dados, acionam o caso de uso e devolvem a resposta. Não têm regra de negócio. |
| **Services** | `app/services/` | **Um Service por caso de uso**, agrupados por domínio (`auth/`, `usuario/`, `categoria/`, `assinatura/`, `agente/`). É aqui que ficam as regras de negócio, as validações e a checagem de posse dos dados. |
| **Repositories** | `app/repositories/` | Consultas que vão além do CRUD básico: filtros, busca, ordenação, paginação, contagens, agregações de gasto e junções do histórico. Não conhecem HTTP nem regras de negócio. |
| **Models** | `app/models/` | Entidades SQLAlchemy mapeadas para as tabelas, com o CRUD convencional (`salvar`, `atualizar`, `deletar`, `buscar_por_id`) e cálculos simples do domínio (valor anualizado, próxima renovação). |

Fluxo típico de uma leitura com filtros (`GET /assinaturas`):

```
AssinaturaController.listar ─► ListarAssinaturasService ─► AssinaturaRepository.listar_filtradas ─► Assinatura (model) ─► MySQL
```

Peças de apoio: `middlewares/` (decorators `@token_requerido` e `@admin_requerido`), `security/` (hash de senha e JWT), `exceptions.py` (erros de negócio com status HTTP), `validacao.py` (validações de entrada), `renovacao.py` (datas de renovação), `cambio.py` e `moedas.py` (conversão de moedas), `gemini.py` (cliente da IA) e `armazenamento.py` (fotos de perfil).

### Modelo de dados

| Model | Tabela | Campos principais |
|---|---|---|
| `Usuario` | `usuarios` | id_usuario, nome, email, senha_hash, role, data_cadastro, foto_perfil, moeda_base, termos_aceitos_em, termos_versao |
| `Categoria` | `categorias` | id_categoria, nome_categoria, descricao, id_usuario |
| `Assinatura` | `assinaturas` | id_assinatura, nome_servico, valor_mensal, moeda, num_pessoas, periodicidade, data_renovacao, status, data_cancelamento, teste_ate, tipo_plano, metodo_pagamento, id_usuario, id_categoria |
| `HistoricoAssinatura` | `historico_assinaturas` | id, id_assinatura, campo, valor_antigo, valor_novo, data_alteracao, id_usuario |
| `TaxaCambio` | `taxas_cambio` | moeda, taxa_por_usd, atualizada_em |

O campo `valor_mensal` guarda o preço cobrado **por período**: numa assinatura anual de R$ 600 ele vale `600`. O gasto do usuário é calculado como `preço ÷ pessoas × fator anual`, convertido para a moeda base. Assinaturas em teste gratuito, pausadas e canceladas não entram nos totais de gasto.

### Estrutura do projeto

```
assinify/
├── README.md
├── frontend/
│   ├── pages/                      # login, registro, termos, dashboard, estatisticas,
│   │                               # categorias, usuarios, perfil
│   ├── js/                         # api.js, auth.js, dashboard.js, estatisticas.js, agente.js,
│   │                               # calendario.js, categorias.js, usuarios.js, perfil.js,
│   │                               # forca-senha.js, tema.js, ui.js, auth-preview.js
│   ├── css/                        # style.css, estatisticas.css, agente.css
│   └── icons/
└── backend/
    ├── app.py                      # ponto de entrada da API
    ├── requirements.txt
    ├── .env.example
    ├── database/create_database.sql
    └── app/
        ├── __init__.py             # app factory, handlers de erro, migração leve, admin inicial
        ├── config.py               # configuração via .env
        ├── extensions.py
        ├── exceptions.py
        ├── validacao.py
        ├── renovacao.py
        ├── cambio.py
        ├── moedas.py
        ├── gemini.py
        ├── armazenamento.py
        ├── security/               # senha.py (hash) e token.py (JWT)
        ├── middlewares/            # auth_middleware.py
        ├── controllers/            # auth, usuario, categoria, assinatura, agente, upload
        ├── models/                 # usuario, categoria, assinatura, historico_assinatura, taxa_cambio
        ├── repositories/           # usuario, categoria, assinatura, historico
        └── services/
            ├── auth/               # registrar, autenticar, atualizar_perfil, alterar_senha,
            │                       # atualizar_foto, remover_foto
            ├── usuario/            # listar, buscar, atualizar, deletar, promover
            ├── categoria/          # criar, listar, buscar, atualizar, deletar
            ├── assinatura/         # criar, listar, buscar, atualizar, deletar, historico,
            │                       # exportar, estatisticas, visao_geral, renovacoes
            └── agente/             # conversar, gerar_insights, recomendar_planos,
                                    # ferramentas, cache
```

### Telas

| Página | Descrição |
|---|---|
| `login.html` e `registro.html` | Entrada e cadastro, em layout de dois painéis. O cadastro exige o aceite dos termos. |
| `termos.html` | Termos de Uso e Política de Privacidade. |
| `dashboard.html` | Painel principal: resumo de gastos, análise da IA, lista de assinaturas com filtros, renovações, gráficos, calendário e o assistente de IA. |
| `estatisticas.html` | Estatísticas avançadas, projeção de 12 meses e reajustes de preço. |
| `categorias.html` | CRUD das categorias do usuário. |
| `perfil.html` | Nome, e-mail, moeda base, foto e senha. |
| `usuarios.html` | Gestão de usuários, restrita a admin. |

`js/api.js` centraliza o `fetch` autenticado (injeta o header `Authorization` e redireciona para o login se o token faltar ou expirar) e a proteção das páginas (`protegerPagina()`, `exigirAdmin()`).

---

## Como executar

### Pré-requisitos

- Python 3.10 ou superior
- MySQL 8.0+ (via XAMPP)
- Extensão Live Server no VSCode, ou o próprio Python, para servir o frontend
- (Opcional) uma chave da API do Gemini, obtida no [Google AI Studio](https://aistudio.google.com/apikey), para habilitar os recursos de IA

### 1. Clone o repositório

```bash
git clone https://github.com/rphaelmax/assinify.git
cd assinify
```

### 2. Crie o banco de dados

Inicie o MySQL no XAMPP, abra o phpMyAdmin (`http://localhost/phpmyadmin`), vá em **SQL** e execute o conteúdo de `backend/database/create_database.sql`. As tabelas também são criadas automaticamente quando a API sobe.

### 3. Configure e rode o backend (servidor 1)

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
| `ADMIN_SENHA` | Senha inicial do admin padrão (padrão: `admin123`). **Troque.** |
| `GEMINI_API_KEY` | Chave da API do Gemini. Sem ela, os recursos de IA respondem 503 e o resto do sistema funciona normalmente. |
| `GEMINI_MODEL` | Modelo principal da IA. |
| `GEMINI_MODEL_FALLBACK` | Modelo reserva, usado se o principal estiver indisponível ou sem cota. |

### 4. Rode o frontend (servidor 2)

Abra a **raiz do projeto** no VSCode, clique com o botão direito em `frontend/pages/login.html` e escolha **Open with Live Server**. A raiz do servidor precisa conter a pasta `frontend/`, porque as páginas carregam `../js` e `../css`.

Alternativa sem VSCode:

```bash
cd frontend
python -m http.server 5500          # acesse http://localhost:5500/pages/login.html
```

O endereço da API fica na constante `API` em `frontend/js/api.js` (padrão `http://localhost:5000`). Deixe a API rodando antes de abrir o frontend e crie sua conta pelo cadastro. Para entrar como administrador, use o e-mail e a senha definidos em `ADMIN_EMAIL` e `ADMIN_SENHA`.

---

## API

Todas as rotas, exceto cadastro e login (e as fotos em `/uploads`), exigem `Authorization: Bearer <token>`. Erros retornam `{"erro": "mensagem"}`.

**Autenticação e perfil**

| Método | Rota | Descrição |
|---|---|---|
| POST | `/auth/registrar` | Cria conta (`nome`, `email`, `senha`, `aceitou_termos`), sempre com `role='user'` |
| POST | `/auth/login` | Retorna `{token, usuario}` |
| GET | `/auth/me` | Usuário autenticado |
| PUT | `/auth/perfil` | Atualiza nome, e-mail e moeda base |
| PATCH | `/auth/senha` | Troca a senha (`senha_atual`, `nova_senha`) |
| POST, DELETE | `/auth/foto` | Envia (campo `foto`) ou remove a foto de perfil |
| GET | `/uploads/avatars/<nome>` | Entrega a foto de perfil (pública, nome com token aleatório) |

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

A listagem e as estatísticas mostram sempre as assinaturas do próprio usuário. Os endpoints por id também aceitam admin.

| Método | Rota | Descrição |
|---|---|---|
| GET | `/assinaturas` | Lista com busca, filtros, ordenação e paginação |
| POST | `/assinaturas` | Cria assinatura |
| GET | `/assinaturas/estatisticas` | Totais, médias e quebra por categoria e por forma de pagamento |
| GET | `/assinaturas/estatisticas/detalhadas` | Projeção de 12 meses, rankings, concentração, canceladas, pausadas e reajustes |
| GET | `/assinaturas/proximas` | Assinaturas ativas ordenadas pela próxima renovação (`limite`, padrão 50) |
| GET | `/assinaturas/calendario` | Renovações de um mês (`ano`, `mes`; padrão: mês atual) |
| GET | `/assinaturas/exportar` | CSV com os mesmos filtros da listagem |
| GET, PUT, DELETE | `/assinaturas/<id>` | Detalhe, edição e exclusão |
| GET | `/assinaturas/<id>/historico` | Histórico de alterações |

Parâmetros de `GET /assinaturas`: `busca`, `id_categoria`, `status`, `metodo_pagamento`, `periodicidade`, `ordenar_por` (`nome_servico`, `valor_mensal`, `data_renovacao` ou `status`), `ordem` (`asc` ou `desc`), `page` e `limit` (máx. 100). Sem `page` e `limit` a resposta é uma lista simples; com eles, vem `{assinaturas, paginacao}`.

Valores aceitos:
- `periodicidade`: `semanal`, `mensal`, `anual`
- `status`: `ativa`, `pausada`, `cancelada`
- `metodo_pagamento`: `cartao_credito`, `cartao_debito`, `pix`, `boleto`, `debito_automatico`, `transferencia`, `outro`
- `moeda`: `BRL`, `USD`, `EUR`, `GBP`, `CAD`, `AUD`, `JPY`, `CHF`, `ARS`, `MXN`

**Agente de IA**

| Método | Rota | Descrição |
|---|---|---|
| POST | `/agente` | Conversa com o assistente (`mensagem`, `historico`). Ele pode consultar, criar, atualizar e preparar a exclusão de assinaturas. |
| GET | `/agente/insights` | Análise proativa do perfil de gastos (`?atualizar=1` ignora o cache) |
| POST | `/agente/planos` | Pesquisa planos mais baratos na web (`id_assinatura` opcional) |

O assistente só enxerga e altera as assinaturas do usuário autenticado: as ferramentas dele reutilizam os mesmos Services da API, então passam pelas mesmas validações e regras de acesso. As análises e as pesquisas de planos ficam em cache por 30 minutos para poupar a cota da IA.

---

## Segurança e privacidade

- Senhas guardadas com hash (Werkzeug), nunca em texto puro.
- Sessão por JWT com validade de 8 horas; as regras de acesso são aplicadas nos Services, não só escondidas na interface.
- Entradas validadas no servidor, ordenação restrita a colunas permitidas e texto escapado no frontend contra XSS.
- Os **Termos de Uso e a Política de Privacidade** (`frontend/pages/termos.html`) são exibidos no cadastro. O aceite é obrigatório e a data, a hora e a versão ficam registradas na conta do usuário.
- A página dos termos informa quais dados vão para o Google Gemini (assinaturas e, no chat, o nome do usuário), nunca o e-mail, a senha ou a foto.

---

## Licença

Este projeto é licenciado sob a GNU General Public License v3.0 (GPL-3.0). Você é livre para usar, estudar, modificar e distribuir este software, desde que qualquer trabalho derivado seja distribuído sob os mesmos termos. Para mais detalhes, consulte o arquivo `LICENSE`.

---

## Equipe

Desenvolvido como projeto de conclusão do curso técnico em Informática no colégio COTEMIG:

| Nome | GitHub |
|---|---|
| **Juan Marco Costa Xavier** | [@JuanMxavieer](https://github.com/JuanMxavieer) |
| **Raphael Max Alves Jacomo** | [@rphaelmax](https://github.com/rphaelmax) |
| **Juan Leonel Monteiro** | [@JuanLeonel27](https://github.com/JuanLeonel27) |
| **João Marcelo Augusto Moreira** | [@joaomarceloaugusto](https://github.com/joaomarceloaugusto) |
| **Arthur de Paiva** | — |
