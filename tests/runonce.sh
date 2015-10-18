set -e
set -o xtrace

if [[ `uname` == 'Darwin' ]]; then
    IFACE='lo0'
else
    IFACE='lo'
fi


zput -vv -q -t 3 LICENSE &
zget -vv -q -t 3 LICENSE /dev/null

zput -vv -q -i $IFACE -t 3 LICENSE &
zget -vv -q -t 3 LICENSE /dev/null

zput -vv -q -t 3 -a 127.0.0.1 LICENSE &
zget -vv -q -t 3 LICENSE /dev/null

zput -vv -q -t 3 -p 8808 LICENSE &
zget -vv -q -t 3 LICENSE /dev/null

zput -q -t 3 LICENSE &
zget -q -t 3 LICENSE /dev/null

zput -t 3 LICENSE &
zget -t 3 LICENSE /dev/null

zput -vv -q -t 3 "tests/filename with spaces" &
zget -vv -q -t 3 "filename with spaces" /dev/null

# In normal use tokens would be automatically generated, but specifying them
# manually exercises the same code.
zput "tests/filename with spaces" T0KN &
cd `mktemp -d`
zget T0KN
ls
test -f "filename with spaces"
