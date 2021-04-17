import i_dunno
import ipaddress
import pytest
from random import randint

def test_decode():
    """Decode a form with known antecedent

    Note the last two bytes are UTF for U+00f0 whose binary
    representation has exactly 8 significant bits.
    >>> bin(ord(b'\xc3\xb0'.decode("utf-8")))
    '0b11110000'
    """
    form = b'g&\x10\xc3\xb0'
    v4addr = '206.152.128.240'
    assert i_dunno.decode(form) == ipaddress.ip_address(v4addr)

def randaddr(af):
    """Return a random IP address"""
    if af == "ip":
        val = randint(1, 2**32 - 1)
    else:
        val = randint(2**32, 2**128 - 1)
    return ipaddress.ip_address(val)

@pytest.mark.parametrize("af, level, nbaddrs", [
    ("ip",   "minimum",      30),
    ("ipv6", "minimum",      30),
    ("ip",   "satisfactory", 30),
    ("ipv6", "satisfactory", 30),
    ("ip",   "delightful",   30),
    ("ipv6", "delightful",   30),
])
def test_random(af, level, nbaddrs):
    """Check decode(encode(addr)) is idempotent for each confusion level"""
    for i in range(nbaddrs):
        run_random_one(af, level)

def run_random_one(af, level):
    """Generate a random address; check decode(encode(addr)) is idempotent"""
    formfound = False
    while not formfound:
        addr = randaddr(af)
        try:
            form = i_dunno.encode(addr, level=level)
            formfound = True
        except ValueError:
            continue
    assert i_dunno.decode(form) == addr
