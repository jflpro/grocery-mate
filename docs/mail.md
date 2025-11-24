# 📬 Mail Stack – Mailcow & Mailgun

```mermaid
flowchart TB
  %% ===========================
  %% STACK MAIL – MAILCOW & MAILGUN
  %% ===========================

  MAILCLIENT[Benutzer<br/>Mail-Client (z.B. Outlook, Handy)]

  subgraph MAILCOW_NET[Docker Netzwerk: mailcowdockerized_mailcow-network]
    MC_NGINX[mailcow-nginx<br/>HTTPS 80/443<br/>Weiterleitung auf Mail-Dienste]
    MC_STACK[Mailcow Stack<br/>Postfix, Dovecot, Rspamd, MariaDB, Redis, SOGo…<br/>Standardports: 25,465,587,110,143,993,995]
  end

  subgraph EXTERN[Externe Dienste]
    DNS[DNS Provider<br/>MX / SPF / DKIM für mail.gro-mate.tech]
    MAILGUN[Mailgun<br/>Transaktionale E-Mails via API/SMTP]
  end

  MAILCLIENT -->|SMTP/IMAP/POP3<br/>25,465,587,110,143,993,995| MC_NGINX
  MC_NGINX --> MC_STACK
  MC_STACK -->|Ausgehende Mails| MAILGUN

  DNS -. MX / SPF / DKIM .- MAILCOW_NET
```
