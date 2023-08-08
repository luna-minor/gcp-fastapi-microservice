"""Core APIRoute clases, can inherit from these modified APIRoutes for specific added functionality"""

import logging
from typing import Callable

from fastapi.routing import APIRoute
from fastapi import Response, Request

       
class LoggingRoute(APIRoute):
    """Log inbound HTTP Request data"""
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            req_body = await request.body()

            logging.info("{} Request; URL={}; headers={}; body={}".format(
                request.method, request.base_url, request.headers, req_body
                )
            )

            response = await original_route_handler(request)
            
            return response
            
        return custom_route_handler
