<div align="center">

<h1>Assinify</h1>

<p><strong>Seu agente inteligente de assinaturas, integrado com IA.</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Framework-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/IA-Agente_Inteligente-8A2BE2?style=for-the-badge&logo=openai&logoColor=white" />
</p>

</div>

---

## Sobre o Projeto

O **Assinify** é um agente inteligente de gerenciamento de assinaturas digitais. Com ele, usuários podem centralizar e monitorar todos os seus serviços recorrentes — como plataformas de streaming, aplicativos e assinaturas digitais — em um único painel.

Mais do que um simples gerenciador, o Assinify conta com um **agente de IA** capaz de analisar o perfil de consumo do usuário, identificar padrões de gasto e agir proativamente para sugerir economia, detectar cobranças redundantes e recomendar planos mais adequados ao uso real.

---

## Agente de IA

O coração do Assinify é seu agente inteligente, construído sobre uma API de LLM e servido via **Flask (Python)**. Ele opera de forma autônoma sobre os dados do usuário para:

| Capacidade | Descrição |
|---|---|
| **Análise de Perfil** | Avalia o histórico de assinaturas e identifica padrões de uso e gasto ao longo do tempo |
| **Detecção de Desperdício** | Identifica assinaturas subutilizadas ou redundantes que podem ser canceladas |
| **Recomendação de Planos** | Sugere planos mais baratos ou promoções disponíveis com base no perfil do usuário |
| **Previsão de Gastos** | Projeta o gasto futuro com assinaturas com base no comportamento atual |
| **Interface Conversacional** | Permite ao usuário interagir com o agente em linguagem natural para tirar dúvidas e receber insights financeiros |

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **Cadastro de Assinaturas** | Registre todos os seus serviços recorrentes com detalhes como valor, ciclo de cobrança e categoria |
| **Controle de Gastos** | Acompanhe em tempo real quanto você gasta mensalmente com assinaturas |
| **Histórico de Pagamentos** | Visualize o histórico completo de cobranças por serviço |
| **Notificações de Vencimento** | Receba alertas antes das datas de renovação para evitar cobranças indesejadas |
| **Sugestões de Economia** | Receba recomendações de planos mais baratos, promoções e descontos disponíveis |
| **Dashboard Financeiro** | Painel visual com resumo dos seus gastos, gráficos e indicadores financeiros |

---

## Stacks

### Frontend
- **HTML5** — Estrutura semântica das páginas
- **CSS3** — Estilização e responsividade
- **JavaScript** — Interatividade e requisições dinâmicas

### Backend
- **Python 3.10+** — Linguagem principal do servidor
- **Flask** — Framework principal da aplicação: rotas, autenticação, lógica de negócio e agente de IA
- **SQLAlchemy** — ORM para interação com o banco de dados
- **Flask-Login** — Gerenciamento de sessões e autenticação de usuários

### Banco de Dados
- **MySQL** — Armazenamento relacional de usuários, assinaturas e histórico de pagamentos

---

## Arquitetura

O projeto segue o padrão **MVC (Model-View-Controller)** implementado com Flask e seus blueprints:

```
Frontend (HTML/CSS/JS)
        │
        ▼
  Flask Router (Blueprints)
        │
        ▼
   Controllers  ──►  Models (SQLAlchemy ORM)  ──►  MySQL
        │
        ▼
  Agente de IA (LLM)
        │
        ▼
  Insights / Recomendações / Chat
```

O Flask atua como orquestrador único da aplicação, unificando o backend principal e o agente de IA em um mesmo serviço Python.

---

## Como Executar

### Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas:

- [Python](https://www.python.org/) 3.10 ou superior
- [pip](https://pip.pypa.io/)
- [MySQL](https://www.mysql.com/) 8.0+

### Passo a Passo

**1. Clone o repositório**
```bash
git clone https://github.com/rphaelmax/assinify.git
cd assinify
```

**2. Crie e ative um ambiente virtual**
```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Instale as dependências Python**
```bash
pip install -r requirements.txt
```

**4. Configure o ambiente**
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta

DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=assinify
DB_USERNAME=seu_usuario
DB_PASSWORD=sua_senha
```

**5. Crie o banco de dados e execute as migrations**
```bash
flask db upgrade
```

**6. (Opcional) Popule o banco com dados de exemplo**
```bash
flask seed
```

**7. Inicie o servidor de desenvolvimento**
```bash
flask run
```

Acesse a aplicação em: [http://localhost:5000](http://localhost:5000)

---

## Estrutura do Projeto

```
assinify/
├── app/
│   ├── __init__.py              # Factory da aplicação Flask
│   ├── models/                  # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── subscription.py
│   │   └── payment.py
│   ├── controllers/             # Blueprints e lógica de negócio
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   └── subscriptions.py
│   ├── agent/                   # Agente de IA (LLM)
│   │   ├── analyzer.py          # Análise de perfil e padrões
│   │   └── recommender.py       # Motor de recomendações
│   ├── static/
│   │   ├── css/                 # Estilos CSS
│   │   └── js/                  # Scripts JavaScript
│   └── templates/               # Templates HTML (Jinja2)
├── migrations/                  # Migrations do banco de dados (Flask-Migrate)
├── app.py                       # Ponto de entrada da aplicação
├── requirements.txt             # Dependências Python
└── .env.example                 # Exemplo de configuração
```

---

## Licença

Este projeto é licenciado sob a GNU General Public License v3.0 (GPL-3.0).
Isso significa que você é livre para usar, estudar, modificar e distribuir este software, desde que qualquer trabalho derivado seja distribuído sob os mesmos termos desta licença. Para mais detalhes, consulte o arquivo LICENSE.

---

## Equipe

Desenvolvido como projeto de conclusão de curso no colégio COTEMIG:

| Nome | GitHub |
|---|---|
| **Juan Marco Costa Xavier** | [@JuanMxavieer](https://github.com/JuanMxavieer) |
| **Raphael Max Alves Jacomo** | [@rphaelmax](https://github.com/rphaelmax) |
| **Juan Leonel Monteiro** | [@JuanLeonel27](https://github.com/JuanLeonel27) |
| **João Marcelo Augusto Moreira** | [@joaomarceloaugusto](https://github.com/joaomarceloaugusto) |
| **Arthur de Paiva** | — |

---
