from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("presenca", "0012_remove_code_used_remove_code_used_by"),
    ]

    operations = [
        migrations.RenameModel(old_name="Configs", new_name="Config"),
        migrations.AddField(
            model_name="config",
            name="type",
            field=models.CharField(
                choices=[
                    ("str", "Texto"),
                    ("int", "Inteiro"),
                    ("float", "Decimal"),
                    ("bool", "Booleano"),
                ],
                default="str",
                max_length=10,
            ),
        ),
    ]
