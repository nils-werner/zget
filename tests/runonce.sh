set -e
set -o xtrace

if [[ `uname` == 'Darwin' ]]; then
    IFACE='lo0'
else
    IFACE='lo'
fi

LANGS=( "de_DE" "en_US" )

for LANG in "${LANGS[@]}"; do
    export LANGUAGE=$LANG
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

    # Transfer alias, requesting file
    zput -vv -q -t 3 LICENSE asd &
    zget -vv -q -t 3 LICENSE /dev/null

    # Transfer alias, requesting alias
    zput -vv -q -t 3 LICENSE asd &
    zget -vv -q -t 3 asd /dev/null
done
