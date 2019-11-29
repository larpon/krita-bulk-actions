SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR/../bulk-actions/"
# https://stackoverflow.com/questions/7694887/is-there-a-command-line-utility-for-rendering-github-flavored-markdown
jq --slurp --raw-input '{"text": "\(.)", "mode": "markdown"}' < Manual.md | curl --data @- https://api.github.com/markdown > Manual.html

# Using pandoc
# cd "$SCRIPT_DIR/../bulk-actions/"
# cp ../README.md ./Manual.md && pandoc -o Manual.html Manual.md