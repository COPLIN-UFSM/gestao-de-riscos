# Produção

Esse arquivo explica como colocar a aplicação em produção, na primeira vez que ela precisar ser configurada.

## Uma vez por servidor

Crie um action runner e execute-o no servidor de produção. Instruções na documentação do GitHub
Actions: https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners

## Uma vez por repositório/aplicação

Clone o repositório:

```bash
git clone git@github.com:COPLIN-UFSM/gestao-de-riscos.git
cd gestao-de-riscos
cp .env.example .env
chmod 600 .env
```

Coloque as credenciais de acesso ao banco de dados e outra variáveis em `.env`.