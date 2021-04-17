import i_dunno
import ipaddress

def test_with_padding():
    """Decode a form that has extra padding"""
    form = b'S\xef\x99\x94\x1a1\xc7\xa4"w\xe5\xa7\x86\xd0\xb4\xd9\x92\xe9\x85\x8d\xd2\x87\xc2\xae'
    v6addr = "a7ec:a869:89e4:45dd:671a:1a65:2914:d90e"
    assert i_dunno.decode(form) == ipaddress.ip_address(v6addr)
