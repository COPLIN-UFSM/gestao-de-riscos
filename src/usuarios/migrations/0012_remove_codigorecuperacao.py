from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0011_add_sem_equipe_desde"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CodigoRecuperacao",
        ),
    ]
