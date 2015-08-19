set -e

if [[ `uname` == 'Darwin' ]]; then
    IFACE='lo0'
else
    IFACE='lo'
fi

zput -vv -i $IFACE -t 3 LICENSE &
zget -vv -t 3 LICENSE /dev/null

zput -vv -t 3 -a 127.0.0.1 LICENSE &
zget -vv -t 3 LICENSE /dev/null

zput -vv -t 3 -p 8808 LICENSE &
zget -vv -t 3 LICENSE /dev/null

zput -q -t 3 LICENSE &
zget -q -t 3 LICENSE /dev/null

zput -vv -t 3 LICENSE &
zget -vv -t 3 LICENSE /dev/null

zput -vv -t 3 "tests/filename with spaces" &
zget -vv -t 3 "filename with spaces" /dev/null
