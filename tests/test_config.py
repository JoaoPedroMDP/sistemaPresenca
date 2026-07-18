from __future__ import annotations

import pytest

from presenca.models import Code, Config


@pytest.mark.parametrize(
    ("type_", "raw", "expected"),
    [
        (Config.Type.STRING, "hello", "hello"),
        (Config.Type.INTEGER, "42", 42),
        (Config.Type.FLOAT, "3.5", 3.5),
        (Config.Type.BOOLEAN, "true", True),
        (Config.Type.BOOLEAN, "false", False),
    ],
)
def test_coerce_converts_value_to_configured_type(db, type_, raw, expected):
    config = Config.objects.create(key="X", value=raw, type=type_)

    assert config.coerce() == expected
    assert type(config.coerce()) is type(expected)


def test_get_value_returns_default_when_key_missing(db):
    assert Config.get_value("NAO_EXISTE", default=7) == 7


def test_code_rotation_recreates_deleted_config_row(db):
    Config.objects.filter(key=Code.ROTATION_CONFIG_KEY).delete()

    assert Code.rotation_seconds() == 60
    assert Config.objects.filter(key=Code.ROTATION_CONFIG_KEY).exists()


def test_code_rotation_reads_config_override(db):
    # Migração 0014 já seeda essa key
    Config.objects.update_or_create(
        key=Code.ROTATION_CONFIG_KEY,
        defaults={"value": "120", "type": Config.Type.INTEGER},
    )

    assert Code.rotation_seconds() == 120
    assert Code.validity_seconds() == 120 + Code.VALIDITY_GRACE_SECONDS
