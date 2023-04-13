class RequestError (Exception):
    """Ошибка подключения."""

    pass


class ConnectError(ConnectionError):
    """Ошибка соединения."""

    pass
