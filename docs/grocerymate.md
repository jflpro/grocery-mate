# 🍏 GroceryMate – WebApp Stack

```mermaid
flowchart TB
  %% ===========================
  %% STACK GROCERYMATE – WEBAPP
  %% ===========================

  USER[Benutzer<br/>Webbrowser]

  subgraph GM_NET[Docker Netzwerk: grocery-mate_devnet]
    subgraph NPM[Nginx Proxy Manager]
      NPM_SVC[Nginx Proxy Manager<br/>Ports Host: 80,81,443<br/>Reverse Proxy + SSL/TLS]
    end

    subgraph FRONTEND[Frontend – Vue 3 + Tailwind]
      FE[grocery_frontend<br/>Container-Port: 80<br/>Nginx Static SPA]
    end

    subgraph BACKEND[Backend – FastAPI]
      BE[grocery_backend<br/>Gunicorn/Uvicorn<br/>Container-Port: 8000<br/>REST API]
    end

    subgraph DB[Persistente Daten – PostgreSQL & pgAdmin]
      PG[grocery_postgres<br/>PostgreSQL 16<br/>Port: 5432<br/>Volume: grocery-mate_postgres_data]
      PGA[pgAdmin<br/>Port Container: 80<br/>Host: 8082/tcp<br/>Volume: grocery-mate_pgadmin_data]
    end

    subgraph IDP[Identity – Keycloak]
      KC[Keycloak<br/>quay.io/keycloak/keycloak:latest<br/>Port: 8080 (Container)<br/>Volumes: keycloak_*]
    end
  end

  USER -->|HTTPS 443<br/>gro-mate.tech / www.gro-mate.tech| NPM_SVC
  USER -->|HTTPS 443<br/>api.gro-mate.tech| NPM_SVC
  USER -->|HTTPS 443<br/>id.gro-mate.tech| NPM_SVC
  USER -->|HTTPS 443<br/>pg.gro-mate.tech| NPM_SVC

  NPM_SVC -->|HTTP 80<br/>Host → Container 80| FE
  NPM_SVC -->|HTTP 80<br/>Host → Container 8000| BE
  NPM_SVC -->|HTTPS id.gro-mate.tech 443<br/>→ Keycloak 8080| KC
  NPM_SVC -->|HTTPS pg.gro-mate.tech 443<br/>→ pgAdmin 80| PGA

  BE -->|PostgreSQL 5432| PG
  PGA -->|PostgreSQL 5432| PG
```
