from zget import crypto, utils

from six import BytesIO
import random
import string
import pytest
import cryptography.exceptions


@pytest.fixture(params=[
    1,                # tiny blocks
    12,
    277,
    1024*8,           # exactly 1 block
    1024*16,          # exactly 2 blocks
    1024*62 - 1,      # some half-empty last blocks
    1024*32 - 33
])
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


@pytest.fixture(params=[True, False])
def corrupt(request):
    return request.param


def test_invertibility(size, suite, payload, corrupt):
    infile = BytesIO()
    tmpfile = BytesIO()
    outfile = BytesIO()

    infile.write(payload)
    infile.seek(0)

    cipher = suite.encrypt("mykey")
    decipher = suite.decrypt("mykey")

    for data in cipher(utils.iter_content(infile)):
        tmpfile.write(data)

    length = tmpfile.tell()
    tmpfile.seek(0)

    if corrupt:
        tmpfile.seek(length // 2)
        tmpfile.write(b"garbage")
        tmpfile.seek(0)

    if corrupt and suite != crypto.bypass:
        with pytest.raises(cryptography.exceptions.InvalidSignature):
            for data in decipher(utils.iter_content(tmpfile)):
                outfile.write(data)
    else:
        for data in decipher(utils.iter_content(tmpfile)):
            outfile.write(data)

    if suite != crypto.bypass:
        assert payload != tmpfile.getvalue()

    if corrupt:
        assert payload != outfile.getvalue()
    else:
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
