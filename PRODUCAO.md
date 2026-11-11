# Produção

Esse arquivo explica como colocar a aplicação em produção, na primeira vez que ela precisar ser configurada.

## Uma vez por servidor

No servidor de produção, crie um action runner e execute-o. Instruções na documentação do GitHub
Actions: https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners

O servidor de produção também deve estar rodando um Docker Engine.

## Uma vez por repositório/aplicação

Clone o repositório:

```bash
git clone git@github.com:COPLIN-UFSM/gestao-de-riscos.git
cd gestao-de-riscos
cp .env.example .env
chmod 600 .env
```

Preencha `.env` com as credenciais DB2 e demais valores de produção. O arquivo `.env.example` possui os campos que
precisam ser preenchidos.

Use uma chave `SECRET_KEY` forte (comprida) e configure `ALLOWED_HOSTS` com o domínio público do servidor, por exemplo:

```dotenv
ALLOWED_HOSTS=proplan.ufsm.br
```

O `docker compose` sobe o backend Django em `127.0.0.1:8005` e o frontend React em `127.0.0.1:3000`. A aplicação fica
publicada sob o caminho `/gestao-de-riscos`; o Nginx, instalado no host, encaminha as requisições para esses serviços.

### Nginx

No bloco `server` HTTPS já existente para `proplan.ufsm.br`, adicione as seguintes `location`. Não crie outro bloco
para o mesmo domínio; assim, o restante do site continua sendo servido normalmente.

```nginx
location = /gestao-de-riscos {
    return 301 /gestao-de-riscos/;
}

location ^~ /gestao-de-riscos/api/ {
    proxy_pass http://127.0.0.1:8005/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location ^~ /gestao-de-riscos/admin/ {
    proxy_pass http://127.0.0.1:8005/admin/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location ^~ /gestao-de-riscos/static/ {
    proxy_pass http://127.0.0.1:8005/static/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location ^~ /gestao-de-riscos/ {
    proxy_pass http://127.0.0.1:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

O caminho `/gestao-de-riscos/` serve o frontend; a API, o admin do Django e os arquivos estáticos também ficam sob esse
prefixo. O Nginx remove o prefixo ao encaminhar as requisições, e `FORCE_SCRIPT_NAME` faz o Django gerar URLs com ele.
As demais rotas do domínio continuam disponíveis para o ProPlan.

Valide e recarregue o Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Se o domínio ainda não tiver HTTPS configurado, configure um certificado antes de testar a URL:

```bash
sudo certbot --nginx -d proplan.ufsm.br
sudo certbot renew --dry-run
```

O workflow de deploy faz `docker compose build`, aplica migrations, coleta os arquivos estáticos e
executa `docker compose up -d`; assim, novas versões do frontend e do backend são publicadas juntas.
