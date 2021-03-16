#!/bin/sh -e
printf '{\n'
curl -LSs 'https://www.unicode.org/Public/security/latest/confusables.txt' | tail -n+2 | grep -v '^\s*$' | grep -v '^\s*#' | grep -v '\x{feff}' | sed -e 's/\s*#.*$//' -e 's/\s*;\s*MA\s*$//' | tr '[:upper:]' '[:lower:]' | sed -e 's/^/\\U/' -e 's/\s*;\s*/\n\\U/' -e 's/ /\\U/g' | sort -u | sed -e "s/^/    '/" -e "s/\$/',/" | paste -s -d'       \n' - | sed -e 's/, \+/, /g' \
    | sed -E -e 's/U([a-f0-9]{4})\b/U0000\1/g' \
    | sed -E -e 's/U([a-f0-9]{5})\b/U000\1/g' \
    | sed -E -e 's/U([a-f0-9]{6})\b/U00\1/g' \
    | sed -E -e 's/U([a-f0-9]{7})\b/U0\1/g'
printf '}\n'
