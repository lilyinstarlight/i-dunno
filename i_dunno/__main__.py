import argparse
import ipaddress
import sys

from . import encode


def main():
    argparser = argparse.ArgumentParser(description='convert IPv6 or IPv4 addresses into RFC8771-compliant I-DUNNO representation')
    argparser.add_argument('-l', '--confusion-level', default='minimum', choices=['minimum', 'satisfactory', 'delightful'], dest='level', help='desired confusion level of I-DUNNO representation')
    argparser.add_argument('addr', type=ipaddress.ip_address, help='IPv6 or IPv4 address in standard notation')

    args = argparser.parse_args()

    i_dunno = encode(args.addr, args.level)
    if i_dunno is not None:
        sys.stdout.buffer.write(i_dunno)
        if sys.stdout.isatty():
            sys.stdout.buffer.write(b'\n')
    else:
        print(f'Could not represent given address "{args.addr}" as valid I-DUNNO at confusion level "{args.level}"', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
