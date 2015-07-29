'''
Logging config for pyaurora.

.. moduleauthor:: paul sorenson
'''


logconfig = {
    'version': 1,

    'loggers': {
        'aurora': {
            'level': 'INFO',
            'handlers': ['file', 'console'],
        },
    },

    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'aurora.log',
            'maxBytes': 1024*1024,
            'backupCount': 1,
            'formatter': 'default',
        },

        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'level': 'INFO',
            'formatter': 'default',
        }
    },

    'formatters': {
        'default': {
            'datefmt': '%y-%m-%d %H:%M:%S',
            'format': '{asctime} {levelname:8s} {message}',
            'style': '{',

        }
    },

}
