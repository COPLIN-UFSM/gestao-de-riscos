
from django.db import migrations


def obter_colunas_usuario_setores(schema_editor):
    conexao = schema_editor.connection

    with conexao.cursor() as cursor:
        if conexao.vendor == "postgresql":
            cursor.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'usuario_setores'
                """
            )
            return {row[0] for row in cursor.fetchall()}

        # Db2: consulta o catálogo nativo do banco.
        cursor.execute(
            "SELECT CURRENT SCHEMA FROM SYSIBM.SYSDUMMY1"
        )
        schema = cursor.fetchone()[0].strip().upper()

        cursor.execute(
            """
            SELECT COLNAME
            FROM SYSCAT.COLUMNS
            WHERE TABSCHEMA = %s
              AND TABNAME = %s
            """,
            [schema, "USUARIO_SETORES"],
        )

        return {row[0].lower() for row in cursor.fetchall()}


def renomear_coluna_legada_usuario_setores(apps, schema_editor):
    conexao = schema_editor.connection
    colunas = obter_colunas_usuario_setores(schema_editor)

    if "unidadeorganizacional_id" in colunas and "setor_id" not in colunas:
        if conexao.vendor == "postgresql":
            tabela = '"usuario_setores"'
            coluna_antiga = '"unidadeorganizacional_id"'
            coluna_nova = '"setor_id"'
        else:
            tabela = '"USUARIO_SETORES"'
            coluna_antiga = '"UNIDADEORGANIZACIONAL_ID"'
            coluna_nova = '"SETOR_ID"'

        with conexao.cursor() as cursor:
            cursor.execute(
                f"ALTER TABLE {tabela} "
                f"RENAME COLUMN {coluna_antiga} TO {coluna_nova}"
            )


def desfazer_renomeacao_coluna_legada_usuario_setores(apps, schema_editor):
    conexao = schema_editor.connection
    colunas = obter_colunas_usuario_setores(schema_editor)

    if "setor_id" in colunas and "unidadeorganizacional_id" not in colunas:
        if conexao.vendor == "postgresql":
            tabela = '"usuario_setores"'
            coluna_antiga = '"setor_id"'
            coluna_nova = '"unidadeorganizacional_id"'
        else:
            tabela = '"USUARIO_SETORES"'
            coluna_antiga = '"SETOR_ID"'
            coluna_nova = '"UNIDADEORGANIZACIONAL_ID"'

        with conexao.cursor() as cursor:
            cursor.execute(
                f"ALTER TABLE {tabela} "
                f"RENAME COLUMN {coluna_antiga} TO {coluna_nova}"
            )


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0007_alter_setor_options_alter_usuario_setores"),
    ]

    operations = [
        migrations.RunPython(
            renomear_coluna_legada_usuario_setores,
            reverse_code=desfazer_renomeacao_coluna_legada_usuario_setores,
        ),
    ]
