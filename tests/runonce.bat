@ECHO ON

START "" zput -vv -q -t 10 LICENSE
zget -vv -q -t 10 LICENSE nul

START "" zput -vv -q -t 10 -a 127.0.0.1 LICENSE
zget -vv -q -t 10 LICENSE nul

START "" zput -vv -q -t 10 -p 8808 LICENSE
zget -vv -q -t 10 LICENSE nul

START "" zput -q -t 10 LICENSE
zget -q -t 10 LICENSE nul

START "" zput -t 10 LICENSE
zget -t 10 LICENSE nul

START "" zput -vv -q -t 10 "tests/filename with spaces"
zget -vv -q -t 10 "filename with spaces" nul

START "" zput -vv -q -t 10 LICENSE asd
zget -vv -q -t 10 LICENSE nul

START "" zput -vv -q -t 10 LICENSE asd
zget -vv -q -t 10 asd nul

@ECHO OFF
