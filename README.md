# Desafio de MVP para Plataforma de Gerenciamento de Pedidos usando Microserviços e Microfrontends

Plataforma construída internamente com backend de microserviço (FastAPI + Python) e microfrontends  (React + Webpack Module Federation).

---

## Arquitetura 

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend — Federação de Módulos Webpack                    │
│                                                             │
│  ┌──────────────────┐  ┌───────────────────┐                │
│  │  Shell / Host    │  │   Pedidos MFE     │                │
│  │  (porta 3000)    │  │   (porta 3001)    │                │
│  │  routing, auth   │  │   listar/filtar/  │                │
│  │  layout, context │  │   criar pedidos   │                │
│  └─────────┬────────┘  └────────┬──────────┘                │
└────────────┼────────────────────┼──────────────────────────-┘
             │                    │  (Federação de Módulos)
             ▼                    ▼
┌──────────────────────────────────────────────────────────────┐
│  API Gateway — Nginx (port 8080)                             │
│  /api/orders/*  →  orders-service                            │ 
│  /api/users/*   →  users-service                             │
└──────┬──────────────────────┬────────────────────────────────┘ 
       │                      │
       ▼                      ▼
┌─────────────────┐  ┌─────────────────┐
│  Service Pedidos│  │  Serviço Usuário│
│  FastAPI :8001  │  │  FastAPI :8002  │
│  CRUD orders    │  │  Auth / JWT     │
│  status history │  │  user mgmt      │
└────────┬────────┘  └────────┬────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐
│  orders_db      │  │  users_db       │   │  Redis          │
│  PostgreSQL     │  │  PostgreSQL     │   │  cache/session  │
│  :5432          │  │  :5433          │   │  :6379          │
└─────────────────┘  └─────────────────┘   └─────────────────┘
```

---

Cada microserviço tem sua próprio banco de dados. Serviços nunca compartilha conexão ou esquema do banco de dados.

## Estrutura do Projeto

```
order-management-mvp/
├── services/
│   ├── orders-service/  # FastAPI — CRUD do pedido +  histórico da situação
│   │   ├── app/
│   │   │   ├── api/endpoints/   # orders.py roteador
│   │   │   ├── core/            # config.py
│   │   │   ├── db/              # session.py
│   │   │   ├── models/          # SQLAlchemy:Pedido,OrderItem,OrderStatusHistory
│   │   │   ├── schemas/         # Esquemas Pydantic I/O 
│   │   │   ├── services/        # order_service.py (lógica de negócio)
│   │   │   └── tests/           # test_orders.py (testes unitários)
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── users-service/           # FastAPI — Gerenciamento do Usuário + JWT auth
│       ├── app/
│       │   ├── api/endpoints/   # auth.py, users.py routers
│       │   ├── core/            # config.py, security.py
│       │   ├── db/              # session.py
│       │   ├── models/          # SQLAlchemy — User
│       │   ├── schemas/         # Pydantic I/O schemas
│       │   ├── services/        # user_service.py
│       │   └── tests/           # test_users.py (testes unitários)
│       ├── Dockerfile
│       └── requirements.txt
│
├── frontend/
│   ├── shell-app/               # Host MFE — Roteamento, auth context, layout
│   │   ├── src/
│   │   │   ├── App.jsx
│   │   │   ├── contexts/AuthContext.jsx
│   │   │   └── components/     # Layout.jsx, LoginPage.jsx
│   │   ├── webpack.config.js   # ModuleFederationPlugin (host)
│   │   └── Dockerfile
│   │
│   └── orders-mfe/              # Orders MFE — exposed remote
│       ├── src/
│       │   ├── OrdersApp.jsx    # exposed entry point
│       │   ├── components/     # OrdersListPage, OrderDetailPage, OrderCreatePage
│       │   ├── hooks/          # useOrders.js
│       │   └── services/       # ordersApi.js
│       ├── webpack.config.js   # ModuleFederationPlugin (remote)
│       └── Dockerfile
│
├── nginx/
│   └── nginx.conf               # Rotealmento da API gateway
│
├── .github/
│   └── workflows/
│       ├── orders-service-ci.yml
│       ├── users-service-ci.yml
│       └── frontend-ci.yml
│
└── docker-compose.yml           # Full stack — single command startup
```

---
## Executando a pilha

### Pré-requisitos

- Docker ≥ 24 e Docker Compose v2
- Portas 8080, 8001, 8002, 5432, 5433, 6379 disponível no host

### Em modo de produção via docker

```bash
git clone <repository-url>
cd order-management-mvp

docker compose up --build
```

O commando docker compose inicia: `orders-db`, `users-db`, `redis`, `orders-service`, `users-service`, `shell-app`, `orders-mfe`, `api-gateway`.


### Parar a pilha

```bash
docker-compose down           # Parar containers, manter os volumes de dados
docker-compose down -v        # Parar e and deletar todos volumes de dados
```


### Executando no modo de desenvolvimento

####  MicroFrontEnd de Pedidos
```bash
cd frontend/orders-mfe && npm run start
```

#### MicroFrontEnd de Host
```bash
cd frontend/shell-app && npm run start 
```

####  Microserviço de Pedidos
```bash
cd services/orders-service && source ./venv/bin/activate &&  uvicorn app.main:app --host "0.0.0.0" --port 8002 --reload
```
#### Mcroserviço de Usuários/Auth
```bash 
cd services/users-service && source ./venv/bin/activate && uvicorn app.main:app --host "0.0.0.0" --port 8001 --reload
```


---
## Testes

### Executando testes localmente

#### Serviço de Pedidos

```bash
cd services/orders-service
pip install -r requirements.txt
pytest app/tests/ -v
```

#### Serviço do Usuários

```bash
cd services/users-service
pip install -r requirements.txt
pytest app/tests/ -v
```

Os testes usam Banco de dados em memória SQLite  — nenhum PostgreSQL externo requerido para executar a suíte de teste.

---

## Referência API

### Serviço da API de Pedidos (porta 8001)

| Método | Caminho                           | Descrição                    |
|--------|-------------------------------|--------------------------------|
| GET    | /api/v1/orders                | Listar pedidos(filter, paginate) |
| POST   | /api/v1/orders                | Criar novo pediod              |
| GET    | /api/v1/orders/{id}           | Recuperar Pedido + Histórico     |
| PATCH  | /api/v1/orders/{id}/status    | Atualizar situação do pedido            |
| DELETE | /api/v1/orders/{id}           | Excluir pedido                |
| GET    | /health                       | Verificar saúde do endpoint                 |

Situações/Estados do Pedido: `pending` → `confirmed` → `processing` → `shipped` → `delivered` / `cancelled`

### Serviço da API de Usuários (porta 8002)

| Método | Caminho                           | Descrição                    |
|--------|-------------------------|---------------------------|
| POST   | /api/v1/auth/register   | Registrar novo usuário        |
| POST   | /api/v1/auth/login      | Autenticar, pegar JWT     |
| GET    | /api/v1/users           | Listar usuários                |
| POST   | /api/v1/users           | Criar usuário (admin)       |
| GET    | /api/v1/users/{id}      | Recuperar usuário user por ID            |
| PATCH  | /api/v1/users/{id}      | Atualizar usuário               |
| DELETE | /api/v1/users/{id}      | Excluir usuário               |
| GET    | /health                 | Verificar saúde               |

Papéis do Usuário: `admin`, `operator`, `viewer`

---

## Endpoints

### Endpoints local em Instância da AWS via Docker
|  Serviço da URL         |                                       |
|-----------------|------------------------------------------|
|  UI  Platform    | http://ec2-35-170-191-147.compute-1.amazonaws.com:8080                    |
|docs da API dos Pedidos  | http://ec2-35-170-191-147.compute-1.amazonaws.com:8001/docs               |
| docs da API dos Usuários   | http://ec2-35-170-191-147.compute-1.amazonaws.com:8002/docs               |
| Serviço de Pedidos  | http://ec2-35-170-191-147.compute-1.amazonaws.com:8001/health             |
| Serviço de Usuários  | http://ec2-35-170-191-147.compute-1.amazonaws.com:8002/health             |



### Endpoints local em Instância da AWS

|  Serviço da URL         |                                       |
|-----------------|------------------------------------------|
|  Microfrontend de Pedidos    | http://35.170.191.147:3000                    |
|   Microfrontend de Usuários    | http://35.170.191.147:3001                    |
|  Microserviço API de Pedidos  | http://35.170.191.147:8001                    |
|    Microserviço API de Usuários   | http://35.170.191.147:8002                    |
| Docs da API de Pedidos  | http://35.170.191.147:8001/docs               |
| Docs da API de Usuários   | http://35.170.191.147:8002/docs               |
| Saúde do Microserviço de Pedidos  | http://35.170.191.147:8001/health             |
| Saúde do Microserviço de Usuários | http://35.170.191.147:8002/health             |


### Endpoints local

| Serviço da URL         |                                       |
|-----------------|------------------------------------------|
|  Microfrontend de Pedidos    | http://localhost:3000                    |
|   Microfrontend de Usuários    | http://localhost:3001                    |
|  Microserviço API de Pedidos  | http://localhost:8001                    |
|    Microserviço API de Usuários   | http://localhost:8002                    |
| Docs da API de Pedidos  | http://localhost:8001/docs               |
| Docs da API de Usuários   | http://localhost:8002/docs               |
| Saúde do Microserviço de Pedidos  | http://localhost:8001/health             |
| Saúde do Microserviço de Usuários | http://localhost:8002/health  

---

## Pipeline Github Actions

Três fluxos de trabalho do Github Actions são disparados quando os arquivos no serviço relevante muda


| Workflow                    | Trigger path                | Jobs                          |
|-----------------------------|-----------------------------|-------------------------------|
| `orders-service-ci.yml`     | `services/orders-service/**`| test → lint (ruff) → docker build |
| `users-service-ci.yml`      | `services/users-service/**` | test → lint (ruff) → docker build |
| `frontend-ci.yml`           | `frontend/**`               | build shell-app, build orders-mfe, verify remoteEntry.js |

Os gatilhos com escopo de caminho significam que uma ação push que afeta apenas o serviço de pedidos não executa o serviço de usuários nem o pipeline de front-end — cada serviço possui sua própria CI independente.

---


## Decisões Técnicas

### Backend
O FastAPI foi escolhido em detrimento do Django REST Framework ou do Flask por oferecer suporte nativo a operações assíncronas, geração automática de documentação OpenAPI e integração de primeira classe com o Pydantic — reduzindo significativamente o código repetitivo em um contexto de microsserviços, onde cada serviço precisa de contratos bem definidos em seus limites.

**Banco de dados por serviço** é o padrão central de isolamento de dados. `orders-db` e `users-db` são instâncias separadas do PostgreSQL executadas em contêineres distintos. Nenhum serviço acessa o banco de dados de outro diretamente; a comunicação entre serviços ocorre somente por meio de APIs HTTP. Isso permite que cada serviço evolua seu esquema de forma independente.

**SQLAlchemy + Alembic** para ORM e migrações. Os diretórios de migração do Alembic são criados em cada serviço; neste MVP, as tabelas são criadas via `metadata.create_all` na inicialização para simplificar, com o Alembic pronto para ser ativado para gerenciamento de migrações em produção.

**O Redis** está incluído como uma camada não relacional complementar. Neste MVP, ele está provisionado e configurado; na próxima iteração, será usado para armazenamento de sessões distribuídas (serviço de usuários), chaves de idempotência na criação de pedidos e como uma camada de cache para dados de produtos/catálogo consultados com frequência.

**Autenticação baseada em JWT** no serviço de usuários. Os tokens contêm `sub` (ID do usuário), `email` e `role`. Neste MVP, o serviço de pedidos ainda não valida os tokens (ele confia no gateway); uma etapa de reforço de segurança em produção adicionaria um middleware de verificação de JWT em cada serviço subsequente.


### Frontend

O **Webpack Module Federation** (integrado ao Webpack 5) foi escolhido como mecanismo de composição do MFE. Ele permite que cada MFE seja construído, implantado e versionado independentemente, compartilhando instâncias singleton do React e do React Router em tempo de execução — evitando problemas de duplicação de peso de pacote e isolamento de contexto que surgem com abordagens ingênuas de iframe ou web-component.


**Padrão Shell/Host**: o aplicativo shell é responsável pelo roteamento, pelo contexto de autenticação (`AuthContext`) e pelo layout. Ele carrega o MFE de Pedidos em tempo de execução por meio de uma importação dinâmica de `import("ordersMfe/OrdersApp")`. O shell expõe `token` e `user` por meio do React Context, permitindo que MFEs remotos consumam o estado de autenticação sem precisar reimplementar a lógica de login.

**Roteamento SPA dentro de cada MFE**: O React Router v6 é usado dentro do MFE de Pedidos com `<Routes>` aninhadas. O shell passa `/*` para o remoto, então o MFE controla suas próprias sub-rotas (`/orders`, `/orders/new`, `/orders/:id`).

**Separação da camada de API**: cada MFE possui sua própria pasta `services/` com chamadas de API tipadas. A URL do gateway (`http://localhost:8080`) é o único ponto de entrada — os MFEs nunca chamam as portas dos microsserviços diretamente.