#!/usr/bin/env python3
import collections
import functools
import ipaddress
import itertools
import random
import sys


__all__ = ['encode', 'decode']


__version__ = '0.1.0'


utf8_lengths = [(0, 7), (8, 11), (12, 16), (17, 21)]


confusion_constraints = {
    'multi-octet': {
        'language': None,
        'check': lambda bytestr: any(num >= 0b11000000 for num in bytestr),
    },
    'disallowed': {
        'language': [
            '\u0000', '\u0001', '\u0002', '\u0003', '\u0004', '\u0005', '\u0006', '\u0007',
            '\u0008', '\u0009', '\u000a', '\u000b', '\u000c', '\u000d', '\u000e', '\u000f',
            '\u0010', '\u0011', '\u0012', '\u0013', '\u0014', '\u0015', '\u0016', '\u0017',
            '\u0018', '\u0019', '\u001a', '\u001b', '\u001c', '\u001d', '\u001e', '\u001f',
            '\u0020', '\u0021', '\u0022', '\u0023', '\u0024', '\u0025', '\u0026', '\u0027',
            '\u0028', '\u0029', '\u002a', '\u002b', '\u002c', '\u002f', '\u003a', '\u003b',
            '\u003c', '\u003d', '\u003e', '\u003f', '\u0040', '\u005b', '\u005c', '\u005d',
            '\u005e', '\u005f', '\u0060', '\u007b', '\u007c', '\u007d', '\u007e', '\u007f',
            '\u0080', '\u0081', '\u0082', '\u0083', '\u0084', '\u0085', '\u0086', '\u0087',
            '\u0088', '\u0089', '\u008a', '\u008b', '\u008c', '\u008d', '\u008e', '\u008f',
            '\u0090', '\u0091', '\u0092', '\u0093', '\u0094', '\u0095', '\u0096', '\u0097',
            '\u0098', '\u0099', '\u009a', '\u009b', '\u009c', '\u009d', '\u009e', '\u009f',
            '\u00a0', '\u00a8', '\u00af', '\u00b4', '\u00b8', '\u02d8', '\u02d9', '\u02da',
            '\u02db', '\u02dc', '\u02dd', '\u037a', '\u037e', '\u0384', '\u0385', '\u04c0',
            '\u0600', '\u0601', '\u0602', '\u0603', '\u0604', '\u0605', '\u061c', '\u06dd',
            '\u070f', '\u08e2', '\u10a0', '\u10a1', '\u10a2', '\u10a3', '\u10a4', '\u10a5',
            '\u10a6', '\u10a7', '\u10a8', '\u10a9', '\u10aa', '\u10ab', '\u10ac', '\u10ad',
            '\u10ae', '\u10af', '\u10b0', '\u10b1', '\u10b2', '\u10b3', '\u10b4', '\u10b5',
            '\u10b6', '\u10b7', '\u10b8', '\u10b9', '\u10ba', '\u10bb', '\u10bc', '\u10bd',
            '\u10be', '\u10bf', '\u10c0', '\u10c1', '\u10c2', '\u10c3', '\u10c4', '\u10c5',
            '\u115f', '\u1160', '\u1680', '\u17b4', '\u17b5', '\u1806', '\u180e', '\u1fbd',
            '\u1fbf', '\u1fc0', '\u1fc1', '\u1fcd', '\u1fce', '\u1fcf', '\u1fdd', '\u1fde',
            '\u1fdf', '\u1fed', '\u1fee', '\u1fef', '\u1ffd', '\u1ffe', '\u2000', '\u2001',
            '\u2002', '\u2003', '\u2004', '\u2005', '\u2006', '\u2007', '\u2008', '\u2009',
            '\u200a', '\u200e', '\u200f', '\u2017', '\u2024', '\u2025', '\u2026', '\u2028',
            '\u2029', '\u202a', '\u202b', '\u202c', '\u202d', '\u202e', '\u202f', '\u203c',
            '\u203e', '\u2047', '\u2048', '\u2049', '\u205f', '\u2061', '\u2062', '\u2063',
            '\u2066', '\u2067', '\u2068', '\u2069', '\u206a', '\u206b', '\u206c', '\u206d',
            '\u206e', '\u206f', '\u207a', '\u207c', '\u207d', '\u207e', '\u208a', '\u208c',
            '\u208d', '\u208e', '\u2100', '\u2101', '\u2105', '\u2106', '\u2132', '\u2183',
            '\u2260', '\u226e', '\u226f', '\u2474', '\u2475', '\u2476', '\u2477', '\u2478',
            '\u2479', '\u247a', '\u247b', '\u247c', '\u247d', '\u247e', '\u247f', '\u2480',
            '\u2481', '\u2482', '\u2483', '\u2484', '\u2485', '\u2486', '\u2487', '\u2488',
            '\u2489', '\u248a', '\u248b', '\u248c', '\u248d', '\u248e', '\u248f', '\u2490',
            '\u2491', '\u2492', '\u2493', '\u2494', '\u2495', '\u2496', '\u2497', '\u2498',
            '\u2499', '\u249a', '\u249b', '\u249c', '\u249d', '\u249e', '\u249f', '\u24a0',
            '\u24a1', '\u24a2', '\u24a3', '\u24a4', '\u24a5', '\u24a6', '\u24a7', '\u24a8',
            '\u24a9', '\u24aa', '\u24ab', '\u24ac', '\u24ad', '\u24ae', '\u24af', '\u24b0',
            '\u24b1', '\u24b2', '\u24b3', '\u24b4', '\u24b5', '\u2a74', '\u2a75', '\u2a76',
            '\u2ff0', '\u2ff1', '\u2ff2', '\u2ff3', '\u2ff4', '\u2ff5', '\u2ff6', '\u2ff7',
            '\u2ff8', '\u2ff9', '\u2ffa', '\u2ffb', '\u3000', '\u309b', '\u309c', '\u3164',
            '\u3200', '\u3201', '\u3202', '\u3203', '\u3204', '\u3205', '\u3206', '\u3207',
            '\u3208', '\u3209', '\u320a', '\u320b', '\u320c', '\u320d', '\u320e', '\u320f',
            '\u3210', '\u3211', '\u3212', '\u3213', '\u3214', '\u3215', '\u3216', '\u3217',
            '\u3218', '\u3219', '\u321a', '\u321b', '\u321c', '\u321d', '\u321e', '\u3220',
            '\u3221', '\u3222', '\u3223', '\u3224', '\u3225', '\u3226', '\u3227', '\u3228',
            '\u3229', '\u322a', '\u322b', '\u322c', '\u322d', '\u322e', '\u322f', '\u3230',
            '\u3231', '\u3232', '\u3233', '\u3234', '\u3235', '\u3236', '\u3237', '\u3238',
            '\u3239', '\u323a', '\u323b', '\u323c', '\u323d', '\u323e', '\u323f', '\u3240',
            '\u3241', '\u3242', '\u3243', '\u33c2', '\u33c7', '\u33d8', '\ufb29', '\ufc5e',
            '\ufc5f', '\ufc60', '\ufc61', '\ufc62', '\ufc63', '\ufdfa', '\ufdfb', '\ufe10',
            '\ufe12', '\ufe13', '\ufe14', '\ufe15', '\ufe16', '\ufe19', '\ufe30', '\ufe33',
            '\ufe34', '\ufe35', '\ufe36', '\ufe37', '\ufe38', '\ufe47', '\ufe48', '\ufe49',
            '\ufe4a', '\ufe4b', '\ufe4c', '\ufe4d', '\ufe4e', '\ufe4f', '\ufe50', '\ufe52',
            '\ufe54', '\ufe55', '\ufe56', '\ufe57', '\ufe59', '\ufe5a', '\ufe5b', '\ufe5c',
            '\ufe5f', '\ufe60', '\ufe61', '\ufe62', '\ufe64', '\ufe65', '\ufe66', '\ufe68',
            '\ufe69', '\ufe6a', '\ufe6b', '\ufe70', '\ufe72', '\ufe74', '\ufe76', '\ufe78',
            '\ufe7a', '\ufe7c', '\ufe7e', '\uff01', '\uff02', '\uff03', '\uff04', '\uff05',
            '\uff06', '\uff07', '\uff08', '\uff09', '\uff0a', '\uff0b', '\uff0c', '\uff0f',
            '\uff1a', '\uff1b', '\uff1c', '\uff1d', '\uff1e', '\uff1f', '\uff20', '\uff3b',
            '\uff3c', '\uff3d', '\uff3e', '\uff3f', '\uff40', '\uff5b', '\uff5c', '\uff5d',
            '\uff5e', '\uffa0', '\uffe3', '\ufff9', '\ufffa', '\ufffb', '\ufffc', '\ufffd',
            '\u110bd', '\u110cd', '\u13430', '\u13431', '\u13432', '\u13433', '\u13434', '\u13435',
            '\u13436', '\u13437', '\u13438', '\u1d173', '\u1d174', '\u1d175', '\u1d176', '\u1d177',
            '\u1d178', '\u1d179', '\u1d17a', '\u1f100', '\u1f101', '\u1f102', '\u1f103', '\u1f104',
            '\u1f105', '\u1f106', '\u1f107', '\u1f108', '\u1f109', '\u1f10a', '\u1f110', '\u1f111',
            '\u1f112', '\u1f113', '\u1f114', '\u1f115', '\u1f116', '\u1f117', '\u1f118', '\u1f119',
            '\u1f11a', '\u1f11b', '\u1f11c', '\u1f11d', '\u1f11e', '\u1f11f', '\u1f120', '\u1f121',
            '\u1f122', '\u1f123', '\u1f124', '\u1f125', '\u1f126', '\u1f127', '\u1f128', '\u1f129',
            '\u2f868', '\u2f874', '\u2f91f', '\u2f95f', '\u2f9bf', '\ue0001', '\ue0020', '\ue0021',
            '\ue0022', '\ue0023', '\ue0024', '\ue0025', '\ue0026', '\ue0027', '\ue0028', '\ue0029',
            '\ue002a', '\ue002b', '\ue002c', '\ue002d', '\ue002e', '\ue002f', '\ue0030', '\ue0031',
            '\ue0032', '\ue0033', '\ue0034', '\ue0035', '\ue0036', '\ue0037', '\ue0038', '\ue0039',
            '\ue003a', '\ue003b', '\ue003c', '\ue003d', '\ue003e', '\ue003f', '\ue0040', '\ue0041',
            '\ue0042', '\ue0043', '\ue0044', '\ue0045', '\ue0046', '\ue0047', '\ue0048', '\ue0049',
            '\ue004a', '\ue004b', '\ue004c', '\ue004d', '\ue004e', '\ue004f', '\ue0050', '\ue0051',
            '\ue0052', '\ue0053', '\ue0054', '\ue0055', '\ue0056', '\ue0057', '\ue0058', '\ue0059',
            '\ue005a', '\ue005b', '\ue005c', '\ue005d', '\ue005e', '\ue005f', '\ue0060', '\ue0061',
            '\ue0062', '\ue0063', '\ue0064', '\ue0065', '\ue0066', '\ue0067', '\ue0068', '\ue0069',
            '\ue006a', '\ue006b', '\ue006c', '\ue006d', '\ue006e', '\ue006f', '\ue0070', '\ue0071',
            '\ue0072', '\ue0073', '\ue0074', '\ue0075', '\ue0076', '\ue0077', '\ue0078', '\ue0079',
            '\ue007a', '\ue007b', '\ue007c', '\ue007d', '\ue007e', '\ue007f',
        ],
        'check': lambda bytestr: any(char in confusion_constraints['disallowed']['language'] for char in bytestr.decode('utf-8')),
    },
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
        if constraints[constraint]['check'](bytestr):
            satisfied += 1

    return satisfied >= confusion_level['required']


def encode(addr, level='satisfactory'):
    """
    Encode an ipaddress.IPv6Address or an ipaddress.IPv4Address object into a random, valid I-DUNNO representation at the given confusion level

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

    return None


def decode(i_dunno):
    """
    Decode an I-DUNNO representation into an ipaddress.IPv6Address or an ipaddress.IPv4Address object

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
