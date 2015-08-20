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
