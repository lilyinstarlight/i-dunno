#!/bin/sh -e
printf '[\n'
for range in $(curl -Ss 'https://www.unicode.org/Public/idna/latest/IdnaMappingTable.txt' | grep '\bdisallowed' | grep -v '# NA\b' | grep -v '<reserved\|<surrogate\|<private-use\|<noncharacter' | sed -e 's/\s*;.*$//'); do
	if echo "$range" | grep -qF ..; then
		for num in $(seq "$(echo "$range" | sed -e 's/\.\..*$//' -e 's/^/0x/' | xargs printf '%d\n')" "$(echo "$range" | sed -e 's/^[^.]*\.\.//' -e 's/^/0x/' | xargs printf '%d\n')"); do
			printf '    '"'"'\\u%04x'"'"',\n' "$num"
		done
	else
		printf '    '"'"'\\u%04x'"'"',\n' "0x$range"
	fi
done
printf ']\n'
