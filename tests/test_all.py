import os
import zget
import pytest


def test_version_installed():
    import pkg_resources
    assert pkg_resources.get_distribution("zget").version == zget.__version__


def test_raises_timeout():
    with pytest.raises(zget.TimeoutException):
        zget.get("as", "", timeout=1)

    with pytest.raises(zget.TimeoutException):
        zget.put("asd", timeout=1)


def test_raises_interface():
    with pytest.raises(ValueError):
        zget.put("as", interface="asd")


def test_unique_filenames(monkeypatch):
    monkeypatch.setattr("os.path.exists", lambda x: True)
    with pytest.raises(IOError):
        zget.utils.unique_filename("foo", limit=1)

    def fail_4_times(x):
        if fail_4_times.i < 4:
            fail_4_times.i += 1
            return True
    fail_4_times.i = 0

    monkeypatch.setattr("os.path.exists", fail_4_times)
    zget.utils.unique_filename("foo")
