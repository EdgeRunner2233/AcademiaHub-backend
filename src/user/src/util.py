def get_logger():
    _logger = None

    def _get_singleton():
        nonlocal _logger
        if _logger is None:
            import logging
            import logging.config
            from pathlib import Path

            ini_path = Path(__file__).absolute().parent.parent / "logging.ini"
            logging.config.fileConfig(ini_path.as_posix())
            _logger = logging.getLogger("infoLogger")
        return _logger

    return _get_singleton()


logger = get_logger()
