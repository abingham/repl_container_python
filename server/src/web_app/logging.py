"""Configuration of the logging system.
"""


def logging_config(level):
    """Configure the logging system.

    This mostly exists to ensure that aiohttp logging out will be available. It
    configures logging to both `STDOUT` and to a rotating file.

    Args:
        level: A `logging` level at which all logging will be configured.
    """

    # modifed from the sanic default config
    return {
        'disable_existing_loggers': False,
        'formatters': {
            'access': {
                'class': 'logging.Formatter',
                'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
                'format': '%(asctime)s - '
                '(%(name)s)[%(levelname)s][%(host)s]: '
                '%(request)s %(message)s %(status)d '
                '%(byte)d'},
            'generic': {
                'class': 'logging.Formatter',
                'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
                'format': '%(asctime)s [%(process)d] '
                '[%(levelname)s] %(message)s'}},
        'handlers': {
            'access_console': {
                'class': 'logging.StreamHandler',
                'formatter': 'access',
                'stream': 'ext://sys.stdout'},
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
                'stream': 'ext://sys.stdout'},
            'error_console': {
                'class': 'logging.StreamHandler',
                'formatter': 'generic',
                'stream': 'ext://sys.stderr'}},
        'loggers': {
            'sanic.access': {
                'handlers': ['access_console'],
                'level': level,
                'propagate': True,
                'qualname': 'sanic.access'},
            'sanic.error': {
                'handlers': ['error_console'],
                'level': level,
                'propagate': True,
                'qualname': 'sanic.error'}},
        'root': {
            'handlers': ['console'],
            'level': level},
        'version': 1}
