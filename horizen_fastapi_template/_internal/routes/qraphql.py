from pathlib import Path

import strawberry
from fastapi import FastAPI
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

from ..models.graphql import GraphQLVersion

def create_graphql_route(
        app: FastAPI,
        version: GraphQLVersion,
        static_files_path: Path
) -> None:

    schema = strawberry.Schema(query=version.query)

    graphql_app = GraphQLRouter(schema, graphql_ide="graphiql", context_getter=version.context_getter)

    # Add the GraphQL route to FastAPI
    app.include_router(graphql_app, prefix=f"/graphql/{version.version}")

    app.mount(
        f"/graphql/{version.version}/playground/static",
        StaticFiles(directory=f"{static_files_path}/static"),
        name="static"
    )

    @app.get(f"/graphql/{version.version}/playground", include_in_schema=False)
    async def playground():
        return FileResponse(f"{static_files_path}/index.html", media_type="text/html")