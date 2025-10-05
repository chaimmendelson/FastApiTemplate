from typing import Dict, Union, Optional, List
import httpx
from pathlib import Path
from .basic_api import BaseAPI


class BitbucketAPI(BaseAPI):
    """
    Bitbucket API client for repository file operations.
    """

    def __init__(
            self,
            username: str,
            app_password: str,
            workspace: str,
            repo_slug: str,
            branch: str = "main",
            verify: bool = False,
    ):
        super().__init__(
            base_url="https://api.bitbucket.org/2.0",
            verify=verify,
            auth=(username, app_password),
        )
        self.username = username
        self.app_password = app_password
        self.workspace = workspace
        self.repo_slug = repo_slug
        self.branch = branch

    async def _commit_files(
            self,
            files: Dict[str, Union[str, bytes]],
            message: str,
            delete: Optional[List[str]] = None,
    ) -> httpx.Response:
        endpoint = f"/repositories/{self.workspace}/{self.repo_slug}/src"
        data: Dict[str, str] = {"branch": self.branch, "message": message}

        # Prepare files payload
        files_payload = [
            (
                path,
                (
                    path.split("/")[-1],
                    content.encode("utf-8") if isinstance(content, str) else content,
                    "application/octet-stream",
                ),
            )
            for path, content in files.items()
        ]

        # Handle deletions
        if delete:
            data["files"] = "\n".join(delete)

        response = await self.post(endpoint, data=data, files=files_payload)
        if response.status_code >= 400:
            raise RuntimeError(f"Commit failed: {response.status_code}, {response.text}")
        return response

    async def add_or_edit_file(
            self, path: str, content: Union[str, bytes], message: str = "Add/Edit file"
    ) -> None:
        await self._commit_files(files={path: content}, message=message)

    async def delete_file(self, path: str, message: str = "Delete file") -> None:
        await self._commit_files(files={}, message=message, delete=[path])

    async def get_file_content(self, path: str) -> bytes:
        endpoint = f"/repositories/{self.workspace}/{self.repo_slug}/src/{self.branch}/{path}"
        response = await self.get(endpoint)
        if response.status_code == 200:
            return response.content
        if response.status_code == 404:
            raise FileNotFoundError(f"File not found: {path}")
        raise RuntimeError(f"Get file content failed: {response.status_code}, {response.text}")

    async def list_files(self, path: str = "") -> List[str]:
        files: List[str] = []
        next_url = f"/repositories/{self.workspace}/{self.repo_slug}/src/{self.branch}/{path}"

        while next_url:
            response = await self.get(next_url)
            if response.status_code >= 400:
                raise RuntimeError(f"List files failed: {response.status_code}, {response.text}")

            data = response.json()
            for entry in data.get("values", []):
                if entry.get("type") == "commit_directory":
                    sub_files = await self.list_files(entry["path"])
                    files.extend(sub_files)
                else:
                    files.append(entry["path"])

            next_url = data.get("next")

        return files

    # ---------------------- CONTEXT MANAGER ---------------------- #
    class CommitContext:
        """
        Async context manager to accumulate file changes and commit them when exiting.
        Supports adding entire directories recursively.
        """

        def __init__(self, api: "BitbucketAPI", message: str = "Commit via context"):
            self.api = api
            self.message = message
            self.files: Dict[str, Union[str, bytes]] = {}
            self.delete: List[str] = []

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                await self.api._commit_files(files=self.files, message=self.message, delete=self.delete)

        def add_or_edit_file(self, path: str, content: Union[str, bytes]):
            self.files[path] = content

        def delete_file(self, path: str):
            self.delete.append(path)

        def add_directory(self, local_dir: Union[str, Path], repo_prefix: str = ""):
            """
            Recursively add a local directory to the commit.

            Args:
                local_dir: Path to local directory
                repo_prefix: Optional prefix path in the repository
            """
            local_dir = Path(local_dir)
            if not local_dir.is_dir():
                raise ValueError(f"{local_dir} is not a directory")

            for path in local_dir.rglob("*"):
                if path.is_file():
                    relative_path = str(path.relative_to(local_dir))
                    repo_path = f"{repo_prefix}/{relative_path}".lstrip("/")
                    with path.open("rb") as f:
                        content = f.read()
                    self.files[repo_path] = content

    def commit_context(self, message: str = "Commit via context") -> "CommitContext":
        return self.CommitContext(self, message)
