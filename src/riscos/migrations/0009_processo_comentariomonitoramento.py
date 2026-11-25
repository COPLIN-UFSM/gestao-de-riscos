import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riscos", "0008_alter_historicoplano_options"),
        ("usuarios", "0012_remove_codigorecuperacao"),
    ]

    operations = [
        migrations.CreateModel(
            name="Processo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ativo", models.BooleanField(db_column="ativo", default=True)),
                ("nome", models.CharField(db_column="nome", max_length=255, unique=True)),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("Operacional", "Operacional"),
                            ("Estratégico", "Estratégico"),
                            ("Integridade", "Integridade"),
                            ("Imagem", "Imagem"),
                            ("Financeiro", "Financeiro"),
                        ],
                        db_column="categoria",
                        max_length=50,
                    ),
                ),
                (
                    "macroprocesso",
                    models.ForeignKey(
                        db_column="id_macroprocesso",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="processos",
                        to="riscos.macroprocesso",
                    ),
                ),
                (
                    "unidades",
                    models.ManyToManyField(
                        blank=True,
                        db_table="riscos_processos",
                        related_name="processos",
                        to="usuarios.setor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Processo",
                "verbose_name_plural": "Processos",
                "db_table": "processos",
                "ordering": ["nome"],
            },
        ),
        migrations.AddField(
            model_name="risco",
            name="processo",
            field=models.ForeignKey(
                blank=True,
                db_column="id_processo",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="riscos",
                to="riscos.processo",
            ),
        ),
        migrations.CreateModel(
            name="ComentarioMonitoramento",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("comentario", models.TextField(db_column="comentario")),
                (
                    "data_hora",
                    models.DateTimeField(auto_now_add=True, db_column="data_hora"),
                ),
                (
                    "monitoramento",
                    models.ForeignKey(
                        db_column="id_monitoramento",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comentarios",
                        to="riscos.monitoramento",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        db_column="id_usuario",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="comentarios_monitoramento",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Comentário de Monitoramento",
                "verbose_name_plural": "Comentários de Monitoramento",
                "db_table": "comentarios_monitoramento",
                "ordering": ["data_hora", "id"],
            },
        ),
    ]
