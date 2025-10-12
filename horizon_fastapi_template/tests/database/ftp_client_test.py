# tests/test_async_ftp_client_basic.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock

from ..._internal.database.ftp_client import AsyncFTPClient


# ------------------------------
# Helper: async context manager patch for _get_client
# ------------------------------

@pytest.fixture
def ftp_client_patch():
    """Provides a helper to patch _get_client with a mock client."""
    def _patch(ftp_instance, client_mock):
        class AsyncCM:
            async def __aenter__(self):
                return client_mock
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
        return patch.object(ftp_instance, "_get_client", return_value=AsyncCM())
    return _patch

@pytest.fixture
def stream_patch():
    """Patches stream to return a mock context manager."""
    def _patch(client_mock, write_mock = None, read_mock = None):
        class AsyncStreamCM:
            def __init__(self):
                self.write = write_mock
                self.read = read_mock
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client_mock.upload_stream = Mock(return_value=AsyncStreamCM())
        client_mock.download_stream = Mock(return_value=AsyncStreamCM())
    return _patch

# ------------------------------ tests ------------------------------

# ------------------------------ pwd ------------------------------
@pytest.mark.asyncio
async def test_pwd_returns_current_directory(ftp_client_patch):
    client_mock = AsyncMock()
    client_mock.get_current_directory.return_value = "/home/test"

    ftp = AsyncFTPClient("host", "user", "pass")
    with ftp_client_patch(ftp, client_mock):
        cwd = await ftp.pwd()
        assert cwd == "/home/test"
        client_mock.get_current_directory.assert_awaited_once()


# ------------------------------ cd ------------------------------

@pytest.mark.asyncio
async def test_cd_changes_directory(ftp_client_patch):
    client_mock = AsyncMock()
    ftp = AsyncFTPClient("host", "user", "pass")
    with ftp_client_patch(ftp, client_mock):
        await ftp.cd("/new_dir")
        client_mock.change_directory.assert_awaited_once_with("/new_dir")

# ------------------------------ list ------------------------------

@pytest.mark.asyncio
async def test_list_returns_file_names(ftp_client_patch):
    file_mock = MagicMock()
    file_mock.name = "file1.txt"
    client_mock = AsyncMock()
    client_mock.list.return_value = [(file_mock,)]

    ftp = AsyncFTPClient("host", "user", "pass")
    with ftp_client_patch(ftp, client_mock):
        files = await ftp.list()
        assert files == ["file1.txt"]
        client_mock.list.assert_awaited_once()

# ------------------------------ file_exists ------------------------------

@pytest.mark.asyncio
async def test_file_exists_returns_true_or_false(ftp_client_patch):
    file_mock = MagicMock()
    file_mock.name = "exist.txt"
    client_mock = AsyncMock()
    client_mock.list.return_value = [(file_mock,)]

    ftp = AsyncFTPClient("host", "user", "pass")
    with ftp_client_patch(ftp, client_mock):
        exists = await ftp.file_exists("exist.txt")
        not_exists = await ftp.file_exists("missing.txt")
        assert exists is True
        assert not_exists is False

# ------------------------------ delete ------------------------------

@pytest.mark.asyncio
async def test_delete_calls_remove_file(ftp_client_patch):
    client_mock = AsyncMock()
    ftp = AsyncFTPClient("host", "user", "pass")
    with ftp_client_patch(ftp, client_mock):
        await ftp.delete("file.txt")
        client_mock.remove_file.assert_awaited_once_with("file.txt")

# ------------------------------ upload ------------------------------

@pytest.mark.asyncio
async def test_upload_calls_upload_file(ftp_client_patch, stream_patch):
    client_mock = AsyncMock()
    write_mock = AsyncMock()

    ftp = AsyncFTPClient("host", "user", "pass")
    ftp.rename = AsyncMock()
    ftp.file_exists = AsyncMock(side_effect=[False, False])

    stream_patch(client_mock, write_mock=write_mock)
    with ftp_client_patch(ftp, client_mock):
        await ftp.upload("file.txt", b"data")

        client_mock.upload_stream.assert_called_once_with("file.txt.tmp")

        write_mock.assert_called_once_with(b"data")

        # rename should have been awaited
        ftp.rename.assert_awaited_once_with("file.txt.tmp", "file.txt")

# ------------------------------ download ------------------------------

@pytest.mark.asyncio
async def test_download_calls_download_file(ftp_client_patch, stream_patch):
    client_mock = AsyncMock()
    read_mock = AsyncMock(return_value=b"data")

    ftp = AsyncFTPClient("host", "user", "pass")
    stream_patch(client_mock, read_mock=read_mock)
    with ftp_client_patch(ftp, client_mock):
        data = await ftp.download("file.txt")

        client_mock.download_stream.assert_called_once_with("file.txt")

        read_mock.assert_called_once()

        assert data == b"data"


# ------------------------------ rename ------------------------------

@pytest.mark.asyncio
async def test_rename_calls_rename(ftp_client_patch):
    client_mock = AsyncMock()
    ftp = AsyncFTPClient("host", "user", "pass")

    ftp.file_exists = AsyncMock(side_effect=[True, False])

    with ftp_client_patch(ftp, client_mock):
        await ftp.rename("old.txt", "new.txt")
        client_mock.rename.assert_awaited_once_with("old.txt", "new.txt")

@pytest.mark.asyncio
async def test_rename_calls_rename_if_override_and_dest_exist(ftp_client_patch):
    client_mock = AsyncMock()
    ftp = AsyncFTPClient("host", "user", "pass", override=True)

    ftp.file_exists = AsyncMock(side_effect=[True, True])

    with ftp_client_patch(ftp, client_mock):
        await ftp.rename("old.txt", "new.txt")
        client_mock.rename.assert_awaited_once_with("old.txt", "new.txt")

@pytest.mark.asyncio
async def test_rename_raises_if_dest_exists_and_no_override(ftp_client_patch):
    client_mock = AsyncMock()
    ftp = AsyncFTPClient("host", "user", "pass", override=False)

    ftp.file_exists = AsyncMock(side_effect=[True, True])

    with ftp_client_patch(ftp, client_mock):
        with pytest.raises(FileExistsError):
            await ftp.rename("old.txt", "new.txt")
        client_mock.rename.assert_not_awaited()

@pytest.mark.asyncio
async def test_rename_raises_if_source_missing(ftp_client_patch):
    client_mock = AsyncMock()
    ftp = AsyncFTPClient("host", "user", "pass")

    ftp.file_exists = AsyncMock(side_effect=[False, False])

    with ftp_client_patch(ftp, client_mock):
        with pytest.raises(FileNotFoundError):
            await ftp.rename("old.txt", "new.txt")
        client_mock.rename.assert_not_awaited()

