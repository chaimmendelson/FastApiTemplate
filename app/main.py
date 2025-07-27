from app import create_app
from app.general import basicSettings, logger_config

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(basicSettings.PORT),
        log_config=logger_config.dict_config,
        reload=bool(basicSettings.DEV_MODE),
        reload_includes=basicSettings.RELOAD_INCLUDES,
    )