zput LICENSE &
zget LICENSE /dev/null

zput "tests/filename with spaces" &
zget "filename with spaces" /dev/null
