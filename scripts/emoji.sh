#!/bin/sh -e
IFS="$(printf '\n\b')"

printf '{\n'
for range in $(curl -LSs 'https://www.unicode.org/Public/emoji/latest/emoji-sequences.txt' | sort -u | grep -v '^\s*$' | grep -v '^\s*#' | sed -e 's/\s*;.*$//'); do
	if echo "$range" | grep -qF ..; then
		for num in $(seq "$(echo "$range" | sed -e 's/\.\..*$//' -e 's/^/0x/' | xargs printf '%d\n')" "$(echo "$range" | sed -e 's/^[^.]*\.\.//' -e 's/^/0x/' | xargs printf '%d\n')"); do
			printf '    '"'"'\\U%08x'"'"',\n' "$num"
		done
	elif echo "$range" | grep -qF ' '; then
		printf '    '"'"
		(
			IFS=" "
			for char in $range; do
				printf '\\U%08x' "0x$char"
			done
		)
		printf "'"',\n'
	else
		printf '    '"'"'\\U%08x'"'"',\n' "0x$range"
	fi
done | paste -s -d'       \n' - | sed -e 's/, \+/, /g'
printf '}\n'
