from django.db import migrations


def seed_config(apps, schema_editor):
    Config = apps.get_model("presenca", "Config")
    Config.objects.get_or_create(
        key="CODE_ROTATION_SECONDS",
        defaults={"value": str(60), "type": "int"},
    )


class Migration(migrations.Migration):

    dependencies = [
        ("presenca", "0013_rename_configs_config_add_type"),
    ]

    operations = [
        migrations.RunPython(seed_config, migrations.RunPython.noop),
    ]
