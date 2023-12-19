"""Core APIRoute clases, can inherit from these modified APIRoutes for specific added functionality"""
import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute


class BaseAPIRoute(APIRoute):
    """Log inbound HTTP Request data"""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            # FastAPI has no global request context, using env vars to store
            req_body = await request.body()

            logging.info(
                f"{request.method} Request; URL={request.base_url}; headers={request.headers}; body={req_body}"
            )

            response = await original_route_handler(request)

            return response

        return custom_route_handler
