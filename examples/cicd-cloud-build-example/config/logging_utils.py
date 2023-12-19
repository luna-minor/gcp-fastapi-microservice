"""Helpers for setting up logging in local and deployed envs"""
import importlib
import json
import logging
import os
import sys
from contextvars import ContextVar
from typing import Optional

from fastapi import Request

# FastAPI does not have a global context with the Request object like Flask,
# using ContextVar to create one
request_context_var: ContextVar[Optional[Request]] = ContextVar(
    "request_context_var", default=None
)


async def set_request_context(request: Request):
    """Set global request context var"""
    request_context_var.set(request)
    return


class GCPLogFormatter(logging.Formatter):
    """GCP log formatter, for use in deployed GCP envs.
    Writes json logs matching GCP's Structured Logging payload format.
    docs: https://cloud.google.com/logging/docs/structured-logging
    """

    def format(self, record: logging.LogRecord):
        log_fields = {
            "message": super().format(record),
            "severity": record.levelname,
            "timestamp": {
                "seconds": int(record.created),
                "nanos": record.msecs * 1000000,
            },
        }

        # If a fastapi Request object is defined in the above ContextVar,
        # fetch and add extra info, else write json log
        http_request_context: Request = request_context_var.get()
        if not http_request_context:
            return json.dumps(log_fields)

        trace_header = http_request_context.headers.get("X-Cloud-Trace-Context")
        cloud_tasks_header = http_request_context.headers.get(
            "X-CloudTasks-TaskName"
        ) or http_request_context.headers.get("X-AppEngine-TaskName")

        # Add Cloud Trace (fetches GCP Project from env vars set in deployed gcp_env)
        gcp_project = os.environ.get("GCP_PROJECT")
        if trace_header:
            if "/" in trace_header:
                trace, span_id = trace_header.split("/")
                log_fields["logging.googleapis.com/trace"] = (
                    "projects/{gcp_project}/traces/{trace}" if gcp_project else trace
                )
                log_fields["logging.googleapis.com/spanId"] = span_id
            else:
                log_fields["logging.googleapis.com/trace"] = trace_header

        # Add Cloud Task
        if cloud_tasks_header:
            log_fields["cloud_task_id"] = cloud_tasks_header

        return json.dumps(log_fields)


def init_logging(level: str, gcp_logging: bool) -> None:
    """Helper fucntion to initialize loggers, for both local and deployed envs"""

    # Logging defaults
    log_format = "%(levelname)s:%(name)s:%(message)s"
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(log_format))
    handlers = [stream_handler]

    # If GCP logging format desired, specify custom Formatter
    if gcp_logging:
        gcp_formatter = GCPLogFormatter(log_format)
        stream_handler.setFormatter(gcp_formatter)

    # Else if the "rich" python package is installed, use rich log handler for prettier logs
    elif importlib.util.find_spec("rich"):
        # pylint: disable-next=import-outside-toplevel
        from rich.logging import RichHandler

        handlers = [RichHandler(rich_tracebacks=True)]
        log_format = "%(module)s:%(message)s"

    # Setup logging
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers,
    )
    return
