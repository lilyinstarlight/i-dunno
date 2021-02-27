#!/bin/sh -e
printf '{\n'
curl -LSs 'https://www.unicode.org/Public/security/latest/confusables.txt' | grep -v '^\s*$' | grep -v '^\s*#' | grep -v '\x{feff}' | sed -e 's/\s*#.*$//' -e 's/\s*;\s*MA\s*$//' | tr '[:upper:]' '[:lower:]' | sed -e 's/^/\\u/' -e 's/\s*;\s*/\n\\u/' -e 's/ /\\u/g' | sort -u | sed -e "s/^/    '/" -e "s/\$/',/" | paste -s -d'       \n' - | sed -e 's/, \+/, /g'
printf '}\n'
