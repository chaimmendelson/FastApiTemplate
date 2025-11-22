from typing import Callable, Dict, Annotated

import strawberry
from pydantic import BaseModel, Field
from strawberry.fastapi import BaseContext

class GraphQLVersion(BaseModel):
    """GraphQL API version configuration."""

    model_config = {"arbitrary_types_allowed": True}

    version: str = Field(
        pattern=r"^v\d+$",
        description="GraphQL API version in the format 'v' followed by digits (e.g., 'v1', 'v2').",
        default="v1"
    )

    graphql_schema: strawberry.Schema = Field(
        description="GraphQL schema.",
    )

    context_getter: Callable = Field(
        description="Context object for GraphQL requests.",
        default=lambda: BaseContext()
    )



