from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [("dynamics", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Fuel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.TextField(unique=True)),
                ("short_name", models.TextField(unique=True)),
                ("color", models.TextField(unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="currency",
            options={"ordering": ["name"], "verbose_name_plural": "currency"},
        ),
    ]
