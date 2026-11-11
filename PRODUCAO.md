# Produção

Esse arquivo explica como colocar a aplicação em produção, na primeira vez que ela precisar ser configurada.

## Uma vez por servidor

Crie um action runner e execute-o no servidor de produção. Instruções na documentação do GitHub
Actions: https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners

Instale Docker Engine com o plugin Docker Compose e Nginx. Libere no firewall somente as portas
80 e 443 para acesso externo; as portas 8005 (API) e 3000 (frontend) ficam restritas ao próprio
servidor.

## Uma vez por repositório/aplicação

Clone o repositório:

```bash
git clone git@github.com:COPLIN-UFSM/gestao-de-riscos.git
cd gestao-de-riscos
cp .env.example .env
chmod 600 .env
```

Preencha `.env` com as credenciais DB2 e demais valores de produção. Use uma chave `SECRET_KEY`
forte e configure `ALLOWED_HOSTS` com o domínio público, sem protocolo ou caminho, por exemplo:

```dotenv
ALLOWED_HOSTS=app.exemplo.ufsm.br
```

Configure o DNS do domínio para apontar para o servidor. O `docker compose` sobe o backend Django
em `127.0.0.1:8005` e o frontend React em `127.0.0.1:3000`; o Nginx, instalado no host, encaminha
as requisições para esses serviços.

Crie `/etc/nginx/sites-available/gestao-de-riscos` com o conteúdo abaixo, substituindo
`app.exemplo.ufsm.br` pelo domínio real:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name app.exemplo.ufsm.br;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    location /api/ {
        proxy_pass http://127.0.0.1:8005;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8005;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:8005;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
    }
}
```

Habilite e valide o site:

```bash
sudo ln -s /etc/nginx/sites-available/gestao-de-riscos /etc/nginx/sites-enabled/gestao-de-riscos
sudo nginx -t
sudo systemctl reload nginx
```

Com o DNS já apontado para o servidor, configure HTTPS com Certbot (o plugin ajusta o site do
Nginx para usar o certificado e redirecionar HTTP para HTTPS):

```bash
sudo certbot --nginx -d app.exemplo.ufsm.br
sudo certbot renew --dry-run
```

O workflow de deploy faz `docker compose build`, aplica migrations, coleta os arquivos estáticos e
executa `docker compose up -d`; assim, novas versões do frontend e do backend são publicadas juntas.
