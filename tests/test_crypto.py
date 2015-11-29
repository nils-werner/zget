from zget import crypto

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

    while True:
        data = infile.read(1024 * 8)  # chunksize taken from urllib
        if not data:
            break
        tmpfile.write(cipher.process(data))
    tmpfile.write(cipher.finalize())
    tmpfile.seek(0)

    while True:
        data = tmpfile.read(1024 * 8)  # chunksize taken from urllib
        if not data:
            break
        outfile.write(decipher.process(data))
    outfile.write(decipher.finalize())

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
    while True:
        data = infile.read(1024 * 8)  # chunksize taken from urllib
        if not data:
            break

    infile.close()
