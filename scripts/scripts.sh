#!/bin/sh -e
IFS="$(printf '\n\b')"

printf '{\n'
for script in $(curl -LSs 'https://www.unicode.org/Public/UCD/latest/ucd/Scripts.txt' | sort -u | grep -v '^\s*$' | grep -v '^\s*#' | sed -e 's/\s*#.*$//'); do
	range="$(echo "$script" | sed -e 's/\s*;.*$//')"
	name="$(echo "$script" | sed -e 's/^[^;]*;\s*//')"
	if echo "$range" | grep -qF ..; then
		lower="$(echo "$range" | sed -e 's/\.\..*$//')"
		upper="$(echo "$range" | sed -e 's/^[^.]*\.\.//')"
	else
		lower="$range"
		upper="$range"
	fi
	printf '    (0x%04x, 0x%04x): '"'"'%s'"'"',\n' "0x$lower" "0x$upper" "$name"
done | paste -s -d'   \n' - | sed -e 's/, \+/, /g'
printf '}\n'
