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

## 2. Código de recuperação de senha (`CodigoRecuperacao`)

### Finalidade

O sistema de recuperação de senha permite que um usuário que não se recorda de sua senha solicite um código temporário por e-mail para realizar a redefinição.

Esse mecanismo permite recuperar o acesso à conta sem precisar da intervenção direta de um administrador.

### Como funciona

O processo utiliza o modelo `CodigoRecuperacao`, localizado em `src/usuarios/models.py`, cuja tabela correspondente no banco de dados é `codigos_recuperacao`.

A tabela armazena as seguintes informações:

| Campo | Finalidade |
|---|---|
| E-mail | Identifica o endereço associado à solicitação de recuperação. |
| Código | Armazena o código de seis dígitos enviado ao usuário. |
| Data e hora de criação | Permite verificar quando o código foi gerado e controlar seu prazo de validade. |

A tabela é criada pela migration `src/usuarios/migrations/0002_codigorecuperacao.py`.

### Etapas da recuperação

O fluxo é conduzido pelas rotas e respectivas views implementadas em `src/usuarios/views.py`:

1. **Solicitação:** o usuário informa seu e-mail para iniciar a recuperação.
2. **Geração:** a aplicação gera um código de seis dígitos e registra as informações na tabela `codigos_recuperacao`.
3. **Envio:** o código é enviado ao usuário por e-mail.
4. **Validação:** o usuário informa o código recebido, e a aplicação verifica se ele corresponde ao registro armazenado e se ainda está dentro do prazo de validade.
5. **Redefinição:** após a validação, o usuário pode cadastrar uma nova senha.
6. **Remoção:** o código é removido após sua utilização ou quando a aplicação identifica que ele expirou.

### Prazo de validade

O código possui validade de **um minuto**, contado a partir do horário de criação. Após esse período, ele não deve mais ser aceito pela aplicação.

### Cuidados de segurança

Existem alguns pontos importantes relacionados à implementação atual:

- O código é armazenado diretamente como texto no banco de dados, sem utilização de hash.
- A geração utiliza `random.randint`, que não é o método mais adequado para gerar códigos destinados à autenticação.
- É recomendável utilizar um gerador criptograficamente seguro, como `secrets`, do Python.
- Também é recomendável armazenar o código como hash e implementar um limite de tentativas de validação.

Essas melhorias ajudam a reduzir o risco de utilização indevida dos códigos de recuperação.

### Onde está implementado?

| Arquivo ou configuração | Responsabilidade |
|---|---|
| `src/usuarios/models.py` | Define o modelo `CodigoRecuperacao`. |
| `src/usuarios/migrations/0002_codigorecuperacao.py` | Cria a tabela de recuperação no banco de dados. |
| `src/usuarios/views.py` | Implementa o envio, a validação e a redefinição de senha. |
| `codigos_recuperacao` | Armazena os códigos temporários e seus dados associados. |

**Em resumo:** o código de recuperação permite que o próprio usuário redefina sua senha por meio de um código temporário enviado ao e-mail cadastrado.

**Mudar o método de recuperação de conta posteriormente exigirá alterações no modelo, na tabela e nas views**, 
mas a finalidade do componente permanecerá a mesma: permitir que o usuário recupere o acesso à sua conta de forma segura.
**Procurar achar um método de fazer isso sem a necessidade de uma tabela no banco de dados** é uma melhoria que pode ser considerada, mas atualmente a tabela `codigos_recuperacao` é necessária para armazenar os códigos temporários e controlar seu prazo de validade.

**Recomendação encontrada:** Usar um token assinado do Django em vez de um código numérico. Evita guardar o token no banco, mas muda o fluxo para validar um token/link e exige definir o prazo de validade.

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
