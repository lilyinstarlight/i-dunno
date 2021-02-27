#!/bin/sh -e
IFS="$(printf '\n\b')"

printf '{\n'
for bidi in $(curl -LSs 'https://www.unicode.org/Public/UCD/latest/ucd/extracted/DerivedBidiClass.txt' | sort -u | grep -v '^\s*$' | grep -v '^\s*#' | sed -e 's/\s*#.*$//'); do
	range="$(echo "$bidi" | sed -e 's/\s*;.*$//')"
	class="$(echo "$bidi" | sed -e 's/^[^;]*;\s*//')"
	if echo "$range" | grep -qF ..; then
		lower="$(echo "$range" | sed -e 's/\.\..*$//')"
		upper="$(echo "$range" | sed -e 's/^[^.]*\.\.//')"
	else
		lower="$range"
		upper="$range"
	fi
	printf '    (0x%04x, 0x%04x): '"'"'%s'"'"',\n' "0x$lower" "0x$upper" "$class"
done | paste -s -d'   \n' - | sed -e 's/, \+/, /g'
printf '}\n'
