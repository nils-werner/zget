from zget import utils


def test_minchunksize():
    data = ["a" * 8, "b" * 4]
    assert list(utils.minimum_chunksize(data, minlength=8)) == ["".join(data)]

    data = ["a" * 8, "b" * 8]
    assert list(utils.minimum_chunksize(data, minlength=8)) == data
