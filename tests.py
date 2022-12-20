import logging
import logging.config
import time
import unittest
from unittest import mock

from titi_client import HttpHandler, LogWorker


class TitiClient(unittest.TestCase):
    def create_logger(self, **kwargs):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        hdlr = HttpHandler(**kwargs)
        hdlr.setLevel(logging.DEBUG)
        logger.addHandler(hdlr)

        hdlr.worker.client.post = mock.MagicMock(name="post")
        return logger, hdlr

    def test_simple(self):
        log_msg = "Let test"
        logger, hdlr = self.create_logger()

        logger.info(log_msg)

        time.sleep(1)

        self.assertEqual(hdlr.worker.client.post.called, True)
        passed_json = hdlr.worker.client.post.mock_calls[0].kwargs["json"]
        self.assertEqual(log_msg, passed_json["message"])
        self.assertEqual("INFO", passed_json["level_name"])

    def test_with_identifier_name_and_project(self):
        log_msg = "Let test"
        proj_name = "Titi client"
        identifier = "zero"
        name = "tests"
        logger, hdlr = self.create_logger(
            project_name=proj_name, name=name, identifier=identifier
        )

        logger.info(log_msg)

        time.sleep(1)

        self.assertEqual(hdlr.worker.client.post.called, True)
        passed_json = hdlr.worker.client.post.mock_calls[0].kwargs["json"]
        # print(passed_json)
        self.assertEqual(log_msg, passed_json["message"])
        self.assertEqual("INFO", passed_json["level_name"])
        self.assertEqual(proj_name, passed_json["project_name"])
        self.assertEqual(identifier, passed_json["identifier"])
        self.assertEqual(name, passed_json["name"])

    def test_logging_dict(self):
        log_msg = "Let test"
        proj_name = "Titi client"
        identifier = "zero"
        name = "tests"

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
                name: {
                    "level": "DEBUG",
                    "class": "titi_client.HttpHandler",
                    "project_name": proj_name,
                    "identifier": identifier,
                },
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                },
            },
            "loggers": {
                "": {
                    "handlers": [name],
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

        logging.config.dictConfig(LOGGING_DICT)
        logger = logging.getLogger()
        for hdlr in logger.handlers:
            if isinstance(hdlr, HttpHandler):
                break
        hdlr.worker.client.post = mock.MagicMock(name="post")

        logger.info(log_msg)

        time.sleep(1)

        self.assertEqual(hdlr.worker.client.post.called, True)
        passed_json = hdlr.worker.client.post.mock_calls[0].kwargs["json"]
        # print(passed_json)
        self.assertEqual(log_msg, passed_json["message"])
        self.assertEqual("INFO", passed_json["level_name"])
        self.assertEqual(proj_name, passed_json["project_name"])
        self.assertEqual(identifier, passed_json["identifier"])
        self.assertEqual(name, passed_json["name"])

    def test_logging_dict_and_level_is_respected(self):
        log_msg = "Let test"
        proj_name = "Titi client"
        identifier = "zero"
        name = "tests"

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
                name: {
                    "level": "INFO",
                    "class": "titi_client.HttpHandler",
                    "project_name": proj_name,
                    "identifier": identifier,
                },
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                },
            },
            "loggers": {
                "": {
                    "handlers": [name],
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

        logging.config.dictConfig(LOGGING_DICT)
        logger = logging.getLogger()
        for hdlr in logger.handlers:
            if isinstance(hdlr, HttpHandler):
                break
        hdlr.worker.client.post = mock.MagicMock(name="post")

        logger.debug(log_msg)

        time.sleep(1)

        self.assertEqual(hdlr.worker.client.post.called, False)

    def test_server_url(self):
        log_msg = "Let test"
        LogWorker.base_url = None
        LogWorker.client = None
        LogWorker.log_endpoint = None
        logger, hdlr = self.create_logger(
            base_url="https://titi.synkio.se/", log_endpoint="/newapi/logs/"
        )

        logger.info(log_msg)

        time.sleep(1)

        self.assertEqual(hdlr.worker.client.post.called, True)
        used_url = hdlr.worker.client.post.mock_calls[0].args[0]
        self.assertEqual(used_url, "https://titi.synkio.se/newapi/logs/")


unittest.main()
