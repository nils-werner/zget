zput -vv LICENSE &
zget -vv LICENSE /dev/null

zput -vv "tests/filename with spaces" &
zget -vv "filename with spaces" /dev/null
