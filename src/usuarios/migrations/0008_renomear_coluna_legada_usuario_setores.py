
from django.db import migrations


def obter_colunas_usuario_setores(schema_editor):
    with schema_editor.connection.cursor() as cursor:
        tabela = next(
            (
                nome
                for nome in schema_editor.connection.introspection.table_names(cursor)
                if nome.lower() == "usuario_setores"
            ),
            None,
        )
        if tabela is None:
            return None, {}

        colunas = {
            coluna.name.lower(): coluna.name
            for coluna in schema_editor.connection.introspection.get_table_description(
                cursor, tabela
            )
        }
    return tabela, colunas


def renomear_coluna_legada_usuario_setores(apps, schema_editor):
    tabela, colunas = obter_colunas_usuario_setores(schema_editor)
    if tabela is None:
        return

    coluna_antiga = colunas.get("unidadeorganizacional_id")
    if coluna_antiga and "setor_id" not in colunas:
        schema_editor.execute(
            f"ALTER TABLE {schema_editor.quote_name(tabela)} "
            f"RENAME COLUMN {schema_editor.quote_name(coluna_antiga)} "
            f"TO {schema_editor.quote_name('setor_id')}"
        )


def desfazer_renomeacao_coluna_legada_usuario_setores(apps, schema_editor):
    tabela, colunas = obter_colunas_usuario_setores(schema_editor)
    if tabela is None:
        return

    coluna_antiga = colunas.get("setor_id")
    if coluna_antiga and "unidadeorganizacional_id" not in colunas:
        schema_editor.execute(
            f"ALTER TABLE {schema_editor.quote_name(tabela)} "
            f"RENAME COLUMN {schema_editor.quote_name(coluna_antiga)} "
            f"TO {schema_editor.quote_name('unidadeorganizacional_id')}"
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
