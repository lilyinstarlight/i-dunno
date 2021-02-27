"""
An RFC 8771-compliant implementation of the Internationalized Deliberately Unreadable Network Notation (shortened as I-DUNNO)
"""


import collections
import functools
import ipaddress
import itertools
import random

from . import data


__all__ = ['encode', 'decode']


__version__ = '0.1.0'


utf8_lengths = [(0, 7), (8, 11), (12, 16), (17, 21)]


confusion_constraints = {
    'multi-octet': lambda bytestr: any(num >= 0b11000000 for num in bytestr),
    'disallowed': lambda bytestr: any(char in data.idna_disallowed for char in bytestr.decode('utf-8')),
    'non-printable': lambda bytestr: not any(char.isprintable() for char in bytestr.decode('utf-8')),
    'multiple-scripts': lambda bytestr: len({data.character_script(char) for char in bytestr.decode('utf-8')}) > 1,
    'category-symbol': lambda bytestr: any(char in data.category_symbols for char in bytestr.decode('utf-8')),
    'multiple-directionalities': lambda bytestr: len({data.character_bidi(char) for char in bytestr.decode('utf-8')}) > 1,
    'confusables': lambda bytestr: (lambda string: any(confusable in string for confusable in data.confusables))(bytestr.decode('utf-8')),
    'emoji': lambda bytestr: (lambda string: any(emoji in string for emoji in data.emoji))(bytestr.decode('utf-8')),
}


confusion_levels = collections.OrderedDict([
    ('minimum', {
        'required': 2,
        'constraints': ('multi-octet', 'disallowed'),
        'inherit': (),
    }),
    ('satisfactory', {
        'required': 2,
        'constraints': ('non-printable', 'multiple-scripts', 'category-symbol'),
        'inherit': ('minimum',),
    }),
    ('delightful', {
        'required': 2,
        'constraints': ('multiple-directionalities', 'confusables', 'emoji'),
        'inherit': ('satisfactory',),
    }),
])


def int_to_bits(num, length=8):
    return list(1 if num & (1 << idx) else 0 for idx in range(length - 1, -1, -1))


def bytes_to_bits(bytestr):
    return list(itertools.chain.from_iterable((1 if byte & (1 << idx) else 0 for idx in range(7, -1, -1)) for byte in bytestr))


def bits_to_bytes(bits):
    aligned_bits = type(bits)((0,)) * ((8 - len(bits)) % 8) + bits
    return bytes(sum(bit << (7 - idx) for idx, bit in enumerate(aligned_bits[sidx:sidx + 8])) for sidx in range(0, len(aligned_bits), 8))


@functools.lru_cache
def packed_combinations(bits, lengths):
    if not bits:
        return [b'']

    bytestrs = []

    for minimum, length in lengths:
        if len(bits) < length:
            continue

        val = int.from_bytes(bits_to_bytes(bits[:length]), 'big')

        if minimum > 0 and val < (1 << minimum):
            continue

        try:
            part = chr(val).encode('utf-8')
        except (ValueError, UnicodeEncodeError):
            continue

        for combination in packed_combinations(bits[length:], lengths):
            try:
                bytestr = part + combination
                bytestr.decode('utf-8')
                bytestrs.append(bytestr)
            except UnicodeDecodeError:
                continue

    return bytestrs


def confusion_check(bytestr, level, levels, constraints):
    confusion_level = levels[level]

    if not all(confusion_check(bytestr, inherited_level, levels, constraints) for inherited_level in confusion_level['inherit']):
        return False

    satisfied = 0

    for constraint in confusion_level['constraints']:
        if constraints[constraint](bytestr):
            satisfied += 1

    return satisfied >= confusion_level['required']


def encode(addr, level='satisfactory'):
    """
    Encode an ipaddress.IPv6Address or an ipaddress.IPv4Address object into a random, valid I-DUNNO representation at the given confusion level.
    A ValueError is raised if valid I-DUNNO for the given arguments does not exist.

    The output of this function MAY be presented to humans, as recommended by RFC8771.
    """
    if level not in confusion_levels:
        raise ValueError(f'unknown confusion level: {level}')

    bits = bytes_to_bits(addr.packed)

    bytestrs = list(packed_combinations(tuple(bits), tuple(utf8_lengths)))
    random.shuffle(bytestrs)

    for bytestr in bytestrs:
        if confusion_check(bytestr, level, confusion_levels, confusion_constraints):
            return bytestr

    raise ValueError(f'could not represent given address "{addr}" as valid I-DUNNO at confusion level "{level}"')


def decode(i_dunno):
    """
    Decode an I-DUNNO representation into an ipaddress.IPv6Address or an ipaddress.IPv4Address object.
    A ValueError is raised if decoding fails due to invalid notation or resulting IP address is invalid.

    The output of this function SHOULD NOT be presented to humans, as recommended by RFC8771.
    """
    bits = []

    for char in i_dunno.decode('utf-8'):
        num = ord(char)

        for minimum, length in utf8_lengths:
            if num < (1 << length) and (minimum == 0 or num >= (1 << minimum)):
                bits += int_to_bits(num, length)
                break
        else:
            raise ValueError('invalid I-DUNNO notation')

    addr = bits_to_bytes(bits)

    if len(addr) == 16:
        cls = ipaddress.IPv6Address
    elif len(addr) == 4:
        cls = ipaddress.IPv4Address
    else:
        raise ValueError('invalid I-DUNNO notation')

    try:
        return cls(addr)
    except ipaddress.AddressValueError:
        raise ValueError('invalid IP address')
