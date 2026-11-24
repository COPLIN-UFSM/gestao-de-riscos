# Desenvolvimento

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

Para enviar e-mails de recuperação de senha, configure `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` no `.env` com uma
conta SMTP válida. O exemplo usa Gmail, que exige uma senha de app; não use a senha normal da conta. O remetente padrão
usa esse mesmo endereço autenticado. `DEFAULT_FROM_EMAIL` pode ser definido para um alias autorizado pelo provedor.
O backend padrão é SMTP. Para testar o fluxo manualmente sem credenciais, defina temporariamente
`EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` no `.env`: o link será impresso no terminal do backend
para abrir no navegador. Isso não entrega e-mail; para testar o recebimento no Gmail é necessário configurar credenciais
SMTP válidas. Em desenvolvimento, `PASSWORD_RESET_URL` aponta para `http://localhost:5173/recuperar-senha`; ajuste-o
se o frontend estiver rodando em outro endereço. O link expira em uma hora.

## 3. Criar e popular o banco local

Com o ambiente virtual ativado, na raiz do repositório:

```bash
python manage.py migrate
```

O `manage.py` seleciona `src.gestao_risco.settings.development` por padrão. Esse perfil cria/usa o arquivo `dev.sqlite3`
na raiz. As migrations versionadas criam as tabelas e carregam os dados de referência do PDI e das unidades da UFSM. Não
é necessário iniciar um container de banco nem executar `makemigrations` para preparar o banco.

```bash
python manage.py importar_unidades_ufsm
```

Importa as unidades da UFSM do CSV versionado. Esse comando é idempotente: se o banco já tiver unidades, ele atualiza
os registros existentes e cria os novos.

```bash
python manage.py importar_pdi
```
Importa os desafios, objetivos e macroprocessos do PDI a partir dos CSVs versionados. 
Esse comando é idempotente: se o banco já tiver registros, ele atualiza os existentes e cria os novos.


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
recuperação de senha, o backend envia o e-mail pelo SMTP configurado no `.env`.

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
