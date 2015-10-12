set -e
set -o xtrace

if [[ `uname` == 'Darwin' ]]; then
    IFACE='lo0'
else
    IFACE='lo'
fi


# Regular transfer
zput -vv -q -t 3 LICENSE &
zget -vv -q -t 3 LICENSE /dev/null

# Set interface
zput -vv -q -i $IFACE -t 3 LICENSE &
zget -vv -q -t 3 LICENSE /dev/null

# Set IP address
zput -vv -q -t 3 -a 127.0.0.1 LICENSE &
zget -vv -q -t 3 LICENSE /dev/null

# Set Port
zput -vv -q -t 3 -p 8808 LICENSE &
zget -vv -q -t 3 LICENSE /dev/null

# Set non-verbose
zput -q -t 3 LICENSE &
zget -q -t 3 LICENSE /dev/null

# Set non-quiet
zput -t 3 LICENSE &
zget -t 3 LICENSE /dev/null

# Filenames with spaces
zput -vv -q -t 3 "tests/filename with spaces" &
zget -vv -q -t 3 "filename with spaces" /dev/null

# Transfer alias, requesting file
zput -vv -q -t 3 LICENSE asd &
zget -vv -q -t 3 LICENSE /dev/null

# Transfer alias, requesting alias
zput -vv -q -t 3 LICENSE asd &
zget -vv -q -t 3 asd /dev/null
