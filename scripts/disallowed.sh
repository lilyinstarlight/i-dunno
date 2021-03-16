#!/bin/sh -e
IFS="$(printf '\n\b')"

printf '{\n'
for range in $(curl -LSs 'https://www.unicode.org/Public/idna/latest/IdnaMappingTable.txt' | sort -u | grep '\bdisallowed' | grep -v '# NA\b' | grep -v '<reserved\|<surrogate\|<private-use\|<noncharacter' | sed -e 's/\s*;.*$//'); do
	if echo "$range" | grep -qF ..; then
		for num in $(seq "$(echo "$range" | sed -e 's/\.\..*$//' -e 's/^/0x/' | xargs printf '%d\n')" "$(echo "$range" | sed -e 's/^[^.]*\.\.//' -e 's/^/0x/' | xargs printf '%d\n')"); do
			printf '    '"'"'\\U%08x'"'"',\n' "$num"
		done
	else
		printf '    '"'"'\\U%08x'"'"',\n' "0x$range"
	fi
done | paste -s -d'       \n' - | sed -e 's/, \+/, /g'
printf '}\n'
