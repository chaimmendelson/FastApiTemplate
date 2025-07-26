from .swagger import router as swagger_router
from .exception import handlers as exception_handlers

handlers = exception_handlers
routers = [swagger_router]