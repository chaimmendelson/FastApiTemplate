from fastapi_template import create_app

app = create_app()
settings = app.state.settings
logger_config = app.state.logger_config


if __name__ == "__main__":
    import uvicorn

    if settings.DEBUG:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=int(settings.PORT),
            log_config=logger_config.dict_config,
            reload=True,
            reload_includes=settings.RELOAD_INCLUDES,
        )

    else:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(settings.PORT),
            log_config=logger_config.dict_config,
        )
