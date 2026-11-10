# Instalação

Esta página descreve a execução local em **Windows 11** e **Ubuntu/Linux** e a implantação do backend em Docker.

## Pré-requisitos

- Python 3.11;
- Node.js 18 ou superior para o frontend;
- Docker com suporte a Compose para produção;
- Git.

## Desenvolvimento local

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Linux:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o `.env` com `Copy-Item .env.example .env` no Windows ou `cp .env.example .env` no Linux. O perfil padrão de `manage.py` é `src.gestao_risco.settings.development`: usa SQLite persistente em `dev.sqlite3` e não precisa de servidor de banco.

Prepare o banco e inicie o backend:

```bash
python manage.py migrate
python manage.py runserver
```

As migrations versionadas criam as tabelas e carregam dados de referência. Execute `makemigrations` apenas quando modelos forem alterados. Para dados fictícios de demonstração, `python manage.py seed_apresentacao` limpa os dados existentes de usuários e riscos antes de recriá-los; use somente em banco local descartável.

Para iniciar o frontend, em outro terminal:

```bash
cd src/frontend
npm install
npm run dev
```

## Testes

O perfil `src.gestao_risco.settings.test`, usado pelo pytest, usa SQLite em memória e não persiste dados:

```bash
python -m pytest
```

## Produção com DB2

No servidor, mantenha o `.env` fora do repositório e configure `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `DB_DATABASE`, `DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD` e `DB_SCHEMA`. O perfil `src.gestao_risco.settings.production` exige essas configurações e conecta ao DB2 existente.

O Docker Compose não cria serviço de banco. No diretório do projeto no servidor:

```bash
docker compose build
docker compose run --rm web python manage.py migrate --noinput
docker compose run --rm web python manage.py collectstatic --noinput
docker compose up -d
```

O pipeline de CI executa os testes em container com SQLite em memória. Em pushes para `main`, o job de deploy usa um runner self-hosted; configure a variável de repositório `DEPLOY_PATH` com o caminho do checkout no servidor.
