<div align="center">

<h1>Assinify</h1>

<p><strong>Seu agente inteligente de assinaturas, integrado com IA.</strong></p>

<p>
  <img src="https://img.shields.io/badge/PHP-8.2+-777BB4?style=for-the-badge&logo=php&logoColor=white" />
  <img src="https://img.shields.io/badge/Laravel-Framework-FF2D20?style=for-the-badge&logo=laravel&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Python-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/IA-Agente_Inteligente-8A2BE2?style=for-the-badge&logo=openai&logoColor=white" />
</p>

</div>

---

## Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Agente de IA](#-agente-de-ia)
- [Funcionalidades](#-funcionalidades)
- [Stack Tecnológica](#-stack-tecnológica)
- [Arquitetura](#-arquitetura)
- [Como Executar](#-como-executar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Equipe](#-equipe)

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

O agente é exposto como um microsserviço independente via Flask, consumido pelo backend Laravel através de chamadas HTTP internas.

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
- **PHP 8.2+** — Linguagem principal do servidor
- **Laravel** — Framework MVC para estruturação da aplicação, rotas, autenticação e ORM
- **Python 3.10+** — Linguagem do microsserviço de IA
- **Flask** — Microsserviço que expõe o agente de IA como API REST, consumido pelo Laravel

### Banco de Dados
- **MySQL** — Armazenamento relacional de usuários, assinaturas e histórico de pagamentos

---

## Arquitetura

O projeto segue o padrão **MVC (Model-View-Controller)** provido pelo Laravel:

```
Frontend (HTML/CSS/JS)
        │
        ▼
  Laravel Router
        │
        ▼
   Controllers  ──►  Models (Eloquent ORM)  ──►  MySQL
        │
        ▼
  Flask AI Service  ──►  Agente de IA (LLM)
        │
        ▼
  Insights / Recomendações / Chat
```

O Laravel atua como orquestrador principal, delegando ao microsserviço Flask todas as operações que envolvem inteligência artificial.

---

## Como Executar

### Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas:

- [PHP](https://www.php.net/) 8.2 ou superior
- [Composer](https://getcomposer.org/)
- [MySQL](https://www.mysql.com/) 8.0+
- [Node.js](https://nodejs.org/) (para assets frontend, opcional)

### Passo a Passo

**1. Clone o repositório**
```bash
git clone https://github.com/rphaelmax/assinify.git
cd assinify
```

**2. Instale as dependências PHP**
```bash
composer install
```

**3. Configure o ambiente**
```bash
cp .env.example .env
php artisan key:generate
```

**4. Configure o banco de dados**

Edite o arquivo `.env` com suas credenciais MySQL:
```env
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=assinify
DB_USERNAME=seu_usuario
DB_PASSWORD=sua_senha
```

**5. Execute as migrations**
```bash
php artisan migrate
```

**6. (Opcional) Popule o banco com dados de exemplo**
```bash
php artisan db:seed
```

**7. Inicie o servidor de desenvolvimento**
```bash
php artisan serve
```

Acesse a aplicação em: [http://localhost:8000](http://localhost:8000)

---

## 📁 Estrutura do Projeto

```
assinify/
├── app/                         # Aplicação Laravel
│   ├── Http/
│   │   ├── Controllers/         # Lógica de negócio
│   │   └── Middleware/          # Autenticação e filtros
│   └── Models/                  # Modelos Eloquent
├── database/
│   ├── migrations/              # Estrutura do banco de dados
│   └── seeders/                 # Dados de exemplo
├── public/
│   ├── css/                     # Estilos CSS
│   └── js/                      # Scripts JavaScript
├── resources/
│   └── views/                   # Templates HTML (Blade)
├── routes/
│   └── web.php                  # Definição de rotas
├── ai-agent/                    # Microsserviço Flask (Agente de IA)
│   ├── app.py                   # Ponto de entrada da API Flask
│   ├── agent/                   # Lógica do agente de IA
│   │   ├── analyzer.py          # Análise de perfil e padrões
│   │   └── recommender.py       # Motor de recomendações
│   └── requirements.txt         # Dependências Python
└── .env.example                 # Exemplo de configuração
```

---

## Equipe

Desenvolvido como projeto de conclusão de curso no colégio COTEMIG:

| Nome | GitHub |
|---|---|
| **Juan Marco Costa Xavier** | [@JuanMxavieer](https://github.com/JuanMxavieer) |
| **Raphael Max Alves Jacomo** | [@rphaelmax](https://github.com/rphaelmax) |
| **Juan Leonel** | [@JuanLeonel27](https://github.com/JuanLeonel27) |
| **João Marcelo** | — |
| **Arthur de Paiva** | — |

---
