# Desenvolvimento local — Gestão de Risco UFSM

Este guia explica como executar o backend e o frontend localmente, sem conectar ao DB2 de produção. Em desenvolvimento,
o Django usa SQLite persistente; os testes usam um SQLite em memória.

## 1. Pré-requisitos

- Python 3.11;
- Node.js 18 ou superior e npm;
- Git.

Docker não é necessário para desenvolvimento local. O `docker-compose.yml` está configurado para produção e espera
conectar ao DB2 existente.

## 2. Preparar o backend

Execute os comandos na raiz do repositório, onde está o `manage.py`.

Crie e ative um ambiente virtual.

```bash
conda env create -f environment.yml
conda activate riscos
```

Crie o `.env` a partir do exemplo.

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

No Linux:

```bash
cp .env.example .env
```

Para desenvolvimento local, não é preciso preencher as variáveis `DB_*`: elas só são usadas pelo perfil de produção. Se
`SECRET_KEY` estiver vazia, o perfil local usa uma chave de desenvolvimento. Não use essa chave em produção.

## 3. Criar e popular o banco local

Com o ambiente virtual ativado, na raiz do repositório:

```bash
python manage.py migrate
```

O `manage.py` seleciona `src.gestao_risco.settings.development` por padrão. Esse perfil cria/usa o arquivo `dev.sqlite3`
na raiz. As migrations versionadas criam as tabelas e carregam os dados de referência do PDI e das unidades da UFSM. Não
é necessário iniciar um container de banco nem executar `makemigrations` para preparar o banco.

Opcionalmente, crie dados fictícios para testar a interface:

```bash
python manage.py seed_apresentacao
```

**Atenção:** esse comando apaga os usuários e riscos existentes no banco selecionado antes de inserir os dados de
demonstração. Use-o somente no banco local. A conta administrativa criada pelo seed é:

```text
SIAPE: 202512603
Senha: 12345678
```

## 4. Iniciar o backend

Em um terminal, na raiz do repositório:

```bash
python manage.py runserver
```

A API e o painel administrativo ficam disponíveis em `http://localhost:8000/` e `http://localhost:8000/admin/`. Para
recuperação de senha local, os emails são impressos no terminal do backend.

Se estiver configurando uma IDE, selecione `src.gestao_risco.settings.development` como `DJANGO_SETTINGS_MODULE`.

## 5. Iniciar o frontend

Em outro terminal:

```bash
cd src/frontend
npm install  # apenas para instalar pacotes, uma vez; depois use `npm ci` para instalar as versões travadas
npm ci  # apenas para instalar as versões travadas no package-lock.json
npm run dev
```

Abra `http://localhost:5173/`. O Vite encaminha automaticamente as chamadas `/api` para o backend em
`http://localhost:8000/`; mantenha os dois servidores em execução.

## 6. Executar os testes

Na raiz do repositório, com as dependências Python instaladas:

```bash
python -m pytest
```

O pytest seleciona `src.gestao_risco.settings.test` por meio de `pytest.ini`. Esse perfil usa SQLite em memória, recria
o banco para os testes e não altera `dev.sqlite3` nem conecta ao DB2.

Outras verificações do backend:

```bash
python manage.py check
python -m ruff check .
```

## 7. Endpoints principais

### Usuários

- Login: `POST /api/usuarios/login/`
- Registro: `POST /api/usuarios/registro/`
- Unidades/departamentos: `GET /api/usuarios/setores/`
- Perfil: `PATCH /api/usuarios/me/`
- Recuperação de senha: `/api/usuarios/recuperar-senha/enviar/`, `/validar/` e `/redefinir/`

### Gestão de riscos

- Desafios, objetivos e macroprocessos: `/api/riscos/desafios/`, `/api/riscos/objetivos/` e
  `/api/riscos/macroprocessos/`
- Planos de risco: `/api/riscos/planos/` (detalhes usam UUID)
- Histórico: `/api/riscos/planos/{uuid}/historico/`
- Ações: `/api/riscos/acoes/`
- Monitoramentos: `/api/riscos/monitoramentos/`

## 8. Produção

O perfil de produção é `src.gestao_risco.settings.production` e exige credenciais DB2 e configurações próprias no `.env`
do servidor. Não use o perfil de produção nem execute `docker compose up` para o fluxo local descrito acima.
