zput -v LICENSE &
zget -v LICENSE /dev/null

zput -v "tests/filename with spaces" &
zget -v "filename with spaces" /dev/null
