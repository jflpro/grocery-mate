# 🏗️ Infrastructure – Hetzner & Docker

```mermaid
flowchart TB
  %% ===========================
  %% INFRA – HETZNER & NETZWERKE
  %% ===========================

  USER[Benutzer<br/>Webbrowser]
  MAILCLIENT[Benutzer<br/>Mail-Client (z.B. Outlook, Handy)]

  subgraph INFRA[Infrastruktur – Hetzner vServer]
    OS[Ubuntu 24.04.3 LTS<br/>2 vCPU, 4 GB RAM, ~38 GB SSD]
    DOCKER[Docker Engine 29.0.1<br/>Docker Compose v2.40.3]
    UFW[UFW Firewall<br/>Eingehend: 22,80,81,443,8082,8000,…<br/>Mail: 25,465,587,110,143,993,995]
    OS --> DOCKER
    OS --> UFW
  end

  subgraph GM_NET[Docker Netzwerk: grocery-mate_devnet]
  end

  subgraph MAILCOW_NET[Docker Netzwerk: mailcowdockerized_mailcow-network]
  end

  subgraph EXTERN[Externe Dienste]
    DNS[DNS Provider<br/>A/AAAA/CNAME + MX/SPF/DKIM]
  end

  DOCKER --> GM_NET
  DOCKER --> MAILCOW_NET

  DNS -. Domainauflösung .- USER
  DNS -. MX / SPF / DKIM .- MAILCOW_NET
```
