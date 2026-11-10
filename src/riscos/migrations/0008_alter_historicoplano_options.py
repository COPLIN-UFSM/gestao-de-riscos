from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('riscos', '0007_add_progresso_historico'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicoplano',
            options={'ordering': ['-data_hora', '-id'], 'verbose_name': 'Histórico do Plano', 'verbose_name_plural': 'Históricos dos Planos'},
        ),
    ]
