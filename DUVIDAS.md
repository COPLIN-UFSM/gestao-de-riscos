# Documentação dos componentes de usuários e histórico de riscos

Este documento descreve três componentes da aplicação: o gerenciador de usuários, o código de recuperação de senha e o histórico dos planos. O objetivo é esclarecer a finalidade de cada um, como funcionam e quais arquivos e tabelas estão envolvidos.

---

## 1. Gerenciador de usuários (`GerenciadorUsuario`)

### Finalidade

O `GerenciadorUsuario` é responsável por centralizar a criação e a configuração de usuários da aplicação. Ele garante que os usuários sejam cadastrados seguindo as regras de autenticação definidas pelo sistema.

### Como funciona

O modelo `Usuario`, localizado em `src/usuarios/models.py`, utiliza um sistema próprio de autenticação, configurado pela propriedade `AUTH_USER_MODEL` no Django.

Diferentemente da configuração padrão, que normalmente utiliza o campo `username` para identificar o usuário, a aplicação utiliza o **SIAPE**:

- `USERNAME_FIELD = 'siape'`: define o SIAPE como identificador utilizado na autenticação.
- `GerenciadorUsuario`: concentra as operações de criação de usuários.

O gerenciador possui dois métodos principais:

**`create_user()`**

Responsável pela criação de usuários comuns. Seu funcionamento envolve:

1. Validar o SIAPE informado.
2. Definir a senha utilizando `set_password()`.
3. Salvar o usuário no banco de dados.

O método `set_password()` transforma a senha em um hash antes de armazená-la. Portanto, a senha não fica gravada em texto puro no banco de dados.

**`create_superuser()`**

Responsável pela criação de usuários administradores. Ele reaproveita o processo de criação de `create_user()` e exige que o usuário tenha as permissões de equipe (`is_staff`) e superusuário (`is_superuser`) habilitadas.

### Integração com a API

Durante o cadastro de usuários pela API, o `RegistroUsuarioSerializer` utiliza o gerenciador para criar o novo usuário. Dessa maneira, o cadastro pela API segue as mesmas regras de validação e armazenamento de senha.

### Onde está implementado?

| Arquivo ou configuração | Responsabilidade |
|---|---|
| `src/usuarios/models.py` | Define o modelo `Usuario` e o `GerenciadorUsuario`. |
| `AUTH_USER_MODEL` | Informa ao Django qual modelo de usuário deve ser utilizado. |
| `RegistroUsuarioSerializer` | Integra o processo de criação de usuários à API. |

**Em resumo:** o gerenciador garante que a criação de usuários aconteça de maneira padronizada, com validação do SIAPE e armazenamento seguro das senhas.

**O gerenciador não é uma tabela do banco de dados**, mas sim uma classe que organiza a lógica de criação e configuração dos usuários.

---

## 2. Recuperação de senha por link temporário

### Finalidade

O usuário solicita um link no endereço de e-mail associado à conta e usa esse link para definir uma nova senha, sem precisar da intervenção de um administrador.

### Como funciona

O servidor usa o `PasswordResetTokenGenerator` do Django para gerar um token assinado usando os dados atuais do usuário. O token não é salvo em uma tabela, expira após uma hora e fica inválido após a troca da senha. A migration `0012_remove_codigorecuperacao.py` remove a tabela antiga de códigos.

### Etapas da recuperação

O fluxo é conduzido pelas rotas e respectivas views implementadas em `src/usuarios/views.py`:

1. **Solicitação:** o usuário informa o e-mail cadastrado.
2. **Envio:** se o endereço corresponder a uma conta, o sistema envia um link com o identificador do usuário e o token.
3. **Redefinição:** o frontend envia o token e a nova senha à API, que verifica a validade e aplica os validadores de senha do Django.
4. **Invalidação:** após a troca, o token deixa de ser válido e os tokens de login existentes são revogados.

### Cuidados de segurança

- A resposta da solicitação é igual para endereços cadastrados e não cadastrados, para reduzir enumeração de contas.
- A solicitação é limitada por IP; o segredo do Django e o token temporário assinado protegem o fluxo.
- Em produção, `PASSWORD_RESET_URL` deve apontar para a tela pública HTTPS do frontend.
- SMTP deve estar configurado para que a mensagem chegue ao destinatário; falhas de envio ficam registradas nos logs do servidor.

### Onde está implementado?

| Arquivo ou configuração | Responsabilidade |
|---|---|
| `src/usuarios/views.py` | Envio do link, validação do token e redefinição de senha. |
| `src/usuarios/urls.py` | Rotas de solicitação e redefinição. |
| `PASSWORD_RESET_URL` | URL pública do frontend incluída no e-mail. |

**Em resumo:** a recuperação não armazena códigos ou tokens em tabelas; a posse do link enviado ao e-mail cadastrado autoriza a redefinição durante o prazo de validade.

---

## 3. Histórico dos planos (`HistoricoPlano`)

### Finalidade

O histórico dos planos permite registrar acontecimentos e alterações relacionados aos riscos cadastrados na aplicação.

Sua função é manter um registro das atividades realizadas, possibilitando consultar o que aconteceu com determinado risco ao longo do tempo e identificar os eventos registrados.

### Como funciona

A funcionalidade é implementada pelo modelo `HistoricoPlano`, localizado em `src/riscos/models.py`.

Os registros são armazenados na tabela `historico_planos`, criada pela migration:

`src/riscos/migrations/0007_add_progresso_historico.py`

Apesar do nome `HistoricoPlano`, é importante observar que o modelo não armazena uma cópia completa dos campos de um plano de ação.

Na realidade, cada registro está relacionado a um risco e armazena informações sobre um evento ocorrido.

As principais informações registradas são:

| Informação | Finalidade |
|---|---|
| Risco relacionado | Identifica a qual risco o evento pertence. |
| Nome do usuário | Identifica o usuário associado à operação registrada. |
| Data e hora | Indica quando o evento aconteceu. |
| Descrição do evento | Apresenta o que foi realizado ou alterado. |

### Quais operações geram registros?

As views de `src/riscos/views.py` criam registros no histórico quando ocorrem determinadas operações:

1. **Atualização de um risco:** registra alterações realizadas nos dados de um risco.
2. **Criação de um plano de ação:** registra a inclusão de um novo plano relacionado ao risco.
3. **Atualização de um plano de ação:** registra alterações realizadas em um plano existente.
4. **Registro de monitoramento:** registra eventos relacionados ao acompanhamento do risco.
5. **Duplicação de um risco:** registra a operação de duplicação.

### Consulta do histórico

O histórico pode ser consultado por meio da rota de histórico do risco.

Essa consulta permite visualizar os eventos associados ao risco, incluindo quem realizou a operação, quando ela aconteceu e qual ação foi registrada.

### Onde está implementado?

| Arquivo ou configuração | Responsabilidade |
|---|---|
| `src/riscos/models.py` | Define o modelo `HistoricoPlano`. |
| `src/riscos/migrations/0007_add_progresso_historico.py` | Cria a tabela de histórico. |
| `src/riscos/views.py` | Registra os eventos e disponibiliza a consulta do histórico. |
| `historico_planos` | Armazena os registros dos eventos relacionados aos riscos. |

**Em resumo:** o histórico funciona como um registro de auditoria das atividades realizadas nos riscos e em seus planos de ação, permitindo acompanhar as operações ao longo do tempo.
**Atualmente está ligado diretamente ao risco**, ou seja, cada risco tem o seu HistóricoPlanos, assim como cada risco tem o seu Monitoramento e o seu PlanosAção.
