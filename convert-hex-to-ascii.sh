#!/bin/bash
# Convert JavaScript hex escapes to backslash escapes in code-links.js

FILE="docs/javascripts/code-links.js"

if [ ! -f "$FILE" ]; then
    echo "Error: $FILE not found"
    exit 1
fi

# Create backup
cp "$FILE" "${FILE}.bak"

# Convert hex escapes to backslash escapes
# \x5b → [  (left bracket)
# \x5d → ]  (right bracket)
# \x28 → (  (left parenthesis)
# \x29 → )  (right parenthesis)

sed -i \
    -e 's/\\x5b/\[/g' \
    -e 's/\\x5d/\]/g' \
    -e 's/\\x28/\(/g' \
    -e 's/\\x29/\)/g' \
    "$FILE"

echo "Converted hex escapes to backslash escapes in $FILE"
echo "Backup saved to ${FILE}.bak"

# Show the result
echo ""
echo "Result:"
grep "replace" "$FILE"
