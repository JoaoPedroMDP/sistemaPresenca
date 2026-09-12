class ExpiredCodeError(Exception):
    pass


class ExpiredDeviceError(Exception):
    """Código do aparelho passou da validade."""
    pass


class DeviceRevokedError(Exception):
    """Aparelho cortado no admin."""
    pass


class DeviceAlreadyActivatedError(Exception):
    """Código já resgatado por outro aparelho."""
    pass


class DeviceNotActivatedError(Exception):
    """Código ainda não resgatado por nenhum aparelho."""
    pass
