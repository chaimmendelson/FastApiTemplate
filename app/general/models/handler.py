from typing import Callable, Type, Awaitable, Union
from pydantic import BaseModel

from fastapi import Request, HTTPException
from fastapi.exceptions import ValidationException, WebSocketException
from fastapi.responses import JSONResponse

exception_type = Union[Exception, HTTPException, ValidationException, WebSocketException]

class ExceptionHandlerConfig(BaseModel):
    exception_class: exception_type
    handler: Callable[[Request, exception_type], Awaitable[JSONResponse]]
