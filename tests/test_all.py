import zget


def test_version_installed():
    import pkg_resources
    assert pkg_resources.get_distribution("zget").version == zget.__version__
