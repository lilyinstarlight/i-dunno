#!/bin/sh -e
IFS="$(printf '\n\b')"

printf '{\n'
for code in $(curl -LSs https://www.unicode.org/notes/tn36/Categories.txt | sort -u | grep -P '\tSymbol\t' | cut -f1); do
	printf '    '"'"'\\U%08x'"'"',\n' "0x$code"
done | paste -s -d'       \n' - | sed -e 's/, \+/, /g'
printf '}\n'
