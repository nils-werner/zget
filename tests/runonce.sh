set -e

zput -vv -i lo LICENSE &
zget -vv LICENSE /dev/null

zput -vv -a 127.0.0.1 LICENSE &
zget -vv LICENSE /dev/null

zput -vv -p 8808 LICENSE &
zget -vv LICENSE /dev/null

zput -q LICENSE &
zget -q LICENSE /dev/null

zput -vv LICENSE &
zget -vv LICENSE /dev/null

zput -vv "tests/filename with spaces" &
zget -vv "filename with spaces" /dev/null
