from . import create_app
from app.general import config, logger_config

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(config.PORT),
        log_config=logger_config.dict_config
    )