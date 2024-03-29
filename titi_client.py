import logging
import re
from datetime import datetime
from queue import Queue
from threading import Thread

import requests
from traceback_with_variables import format_exc

logger = logging.getLogger()


class LogWorker(Thread):
    logger = logging.getLogger()

    def __init__(self, base_url, log_endpoint):
        super().__init__()
        self.daemon = True
        self.queue = Queue(maxsize=0)
        self.client = requests.Session()
        self.base_url = base_url
        self.log_endpoint = log_endpoint

    def run(self) -> None:
        while True:
            event = self.queue.get()
            self.queue.task_done()
            for i in range(3):
                try:
                    self.client.post(
                        f"{self.base_url}{self.log_endpoint}",
                        json=event,
                    )
                    break
                except Exception as e:
                    logger.error(format_exc(e))


class HttpHandler(logging.Handler):
    rgx_for_blocking = []

    def __init__(
        self,
        base_url="http://localhost:8000",
        log_endpoint="/api/logs/",
        project_name=None,
        name=None,
        identifier=None,
        use_instance_name=False,
        **kwargs,
    ):
        super().__init__(*[], **kwargs)

        # customization
        self.use_instance_name = use_instance_name
        self.project_name = project_name
        self.name = name
        self.identifier = identifier
        self.base_url = base_url
        if self.base_url.endswith("/"):
            self.base_url = base_url[:-1]
        self.log_endpoint = log_endpoint

        r = re.search(r"\/([a-zA-z:\d\.]+)", base_url)
        self.domain = r.group(1)
        self.rgx_full_log_url = re.compile(
            f'{self.base_url}(\:\d+)? "POST {self.log_endpoint}'  # noqa: W605
        )
        self.rgx_start_log_url = re.compile(
            f"Starting new HTTP connection \(\d+\): {self.domain}"  # noqa: W605
        )
        self.rgx_reset_log_url = re.compile(
            f"Resetting dropped connection: {self.domain}"
        )

        self.rgx_for_blocking.append(self.rgx_full_log_url)
        self.rgx_for_blocking.append(self.rgx_reset_log_url)
        self.rgx_for_blocking.append(self.rgx_start_log_url)

        self.worker = LogWorker(self.base_url, self.log_endpoint)
        self.worker.start()

    def emit(self, record: logging.LogRecord):
        try:
            message = record.getMessage()
            if record.name.startswith("urllib3"):
                for rgx in self.rgx_for_blocking:
                    if rgx.search(message):
                        return

            data = {
                "level": record.levelname,
                "name": self.get_record_name(record),
                "message": message,
                "lineno": record.lineno,
                "pathname": record.pathname,
                "project": self.project_name,
                "identifier": self.get_identifier(record),
                "timestamp": record.created,
                "datetime": str(datetime.fromtimestamp(record.created)),
                "thread_id": record.thread,
                "thread_name": record.threadName,
                "process_id": record.process,
                "process_name": record.processName,
            }
            self.worker.queue.put(data, block=False)
        except Exception as e:
            logger.error(format_exc(e))

    def get_identifier(self, record: logging.LogRecord):
        return self.identifier

    def get_record_name(self, record: logging.LogRecord):
        if self.use_instance_name:
            return self.name
        else:
            return record.name
