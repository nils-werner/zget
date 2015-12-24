from zget import crypto, utils

from six import BytesIO
import random
import string
import pytest


@pytest.fixture(params=[1, 12, 277, 1024*8, 1024*16, 1024*62 - 1])
def size(request):
    return request.param


@pytest.fixture
def payload(size):
    return bytearray(
        ''.join(
            random.choice(
                string.ascii_uppercase + string.digits
            ) for _ in range(size)
        ),
        "latin-1"
    )


@pytest.fixture(params=[crypto.aes, crypto.bypass])
def suite(request):
    return request.param


def test_invertibility(size, suite, payload):
    infile = BytesIO()
    tmpfile = BytesIO()
    outfile = BytesIO()

    infile.write(payload)
    infile.seek(0)

    cipher = suite.encrypt("mykey")
    decipher = suite.decrypt("mykey")

    for data in cipher(utils.iter_content(infile)):
        tmpfile.write(data)
    tmpfile.seek(0)

    for data in decipher(utils.iter_content(tmpfile)):
        outfile.write(data)

    if suite != crypto.bypass:
        assert payload != tmpfile.getvalue()
    assert payload == outfile.getvalue()
    infile.close()
    tmpfile.close()
    outfile.close()


def test_encrypt(size, suite, payload):
    infile = BytesIO()

    infile.write(payload)
    infile.seek(0)

    cipher = suite.encrypt("mykey")
    for data in cipher(utils.iter_content(infile)):
        pass

    infile.close()
