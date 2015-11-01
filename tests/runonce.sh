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
    zput -vv -q -t 10 LICENSE &
    zget -vv -q -t 10 LICENSE /dev/null

    zput -vv -q -i $IFACE -t 10 LICENSE &
    zget -vv -q -t 10 LICENSE /dev/null

    zput -vv -q -t 10 -a 127.0.0.1 LICENSE &
    zget -vv -q -t 10 LICENSE /dev/null

    zput -vv -q -t 10 -p 8808 LICENSE &
    zget -vv -q -t 10 LICENSE /dev/null

    zput -q -t 10 LICENSE &
    zget -q -t 10 LICENSE /dev/null

    zput -t 10 LICENSE &
    zget -t 10 LICENSE /dev/null

    zput -vv -q -t 10 "tests/filename with spaces" &
    zget -vv -q -t 10 "filename with spaces" /dev/null

    # Transfer alias, requesting file
    zput -vv -q -t 10 LICENSE asd &
    zget -vv -q -t 10 LICENSE /dev/null

    # Transfer alias, requesting alias
    zput -vv -q -t 10 LICENSE asd &
    zget -vv -q -t 10 asd /dev/null
done
