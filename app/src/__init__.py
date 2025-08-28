from fastapi import FastAPI

async_background_tasks = []

def update_app(app: FastAPI) -> FastAPI:

    return app