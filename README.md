# titi-client

Client for Titi LogServer


### Simple Usage

```python
import logging
from titi_client import HttpHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

hdlr = HttpHandler(base_url='http://127.0.0.1')
hdlr.setLevel(logging.DEBUG)
logger.addHandler(hdlr)
```


### Usage with custom arguments

```python
import logging
from titi_client import HttpHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

hdlr = HttpHandler(base_url="http://localhost:8000",
        log_endpoint="/api/logs/",
        project_name=None,
        name=None,
        identifier=None
        )
hdlr.setLevel(logging.DEBUG)
logger.addHandler(hdlr)
```


### Usage with logging dict (Django example)

```python
PROJECT_NAME = 'proj_name'
IDENTIFIER = 'server X'

LOGGING_DICT = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s - %(pathname)s",
                    "datefmt": "%d/%b/%Y %H:%M:%S",
                },
            },
            "handlers": {
                'name': {
                    "level": "INFO",
                    "class": "titi_client.HttpHandler",
                    "project_name": PROJECT_NAME,
                    "identifier": IDENTIFIER,
                },
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                },
            },
            "loggers": {
                "": {
                    "handlers": ['name'],
                    "level": "INFO",
                    "propagate": True,
                },
                "scraper": {
                    "handlers": [
                        "console",
                    ],
                    "level": "DEBUG",
                    "propagate": True,
                },
            },
        }
```