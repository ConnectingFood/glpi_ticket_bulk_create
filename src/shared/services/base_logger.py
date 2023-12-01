import logging

class BaseLogger:

    @classmethod
    def set_logger(cls, format_string: str = None, name="base_log", level=logging.DEBUG):
        
        if format_string is None:
            format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"

        logger = logging.getLogger(name)
        logger.setLevel(level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    @classmethod
    def get_logger(cls, name="base_log"):
        if not logging.getLogger(name).handlers:
            cls.set_logger(name=name)
        
        return logging.getLogger(name)