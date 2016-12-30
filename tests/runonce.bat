@ECHO ON

START "" zput -vv -q -t 10 -p foobar LICENSE
zget -vv -q -t 10 -p foobar LICENSE recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1
md5 -cd4999f5a6fb5ebee9c8fb5496d57050f recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1

START "" zput -vv -q -t 10 -p foobar -a 127.0.0.1 LICENSE
zget -vv -q -t 10 -p foobar LICENSE recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1
md5 -cd4999f5a6fb5ebee9c8fb5496d57050f recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1

START "" zput -vv -q -t 10 -p foobar -P 8808 LICENSE
zget -vv -q -t 10 -p foobar LICENSE recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1
md5 -cd4999f5a6fb5ebee9c8fb5496d57050f recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1

START "" zput -q -t 10 -p foobar LICENSE
zget -q -t 10 -p foobar LICENSE recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1
md5 -cd4999f5a6fb5ebee9c8fb5496d57050f recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1

START "" zput -t 10 -p foobar LICENSE
zget -t 10 -p foobar LICENSE recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1
md5 -cd4999f5a6fb5ebee9c8fb5496d57050f recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1

START "" zput -t 10 --bypass-encryption LICENSE
zget -t 10 -p foobar --bypass-encryption LICENSE nul
IF ERRORLEVEL 1 EXIT /B 1
md5 -cd4999f5a6fb5ebee9c8fb5496d57050f recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1

START "" zput -vv -q -t 10 -p foobar "tests/filename with spaces"
zget -vv -q -t 10 -p foobar "filename with spaces" recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1

START "" zput -vv -q -t 10 -p foobar LICENSE asd
zget -vv -q -t 10 -p foobar LICENSE recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1
md5 -cd4999f5a6fb5ebee9c8fb5496d57050f recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1

START "" zput -vv -q -t 10 -p foobar LICENSE asd
zget -vv -q -t 10 -p foobar asd recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1
md5 -cd4999f5a6fb5ebee9c8fb5496d57050f recv_LICENSE
IF ERRORLEVEL 1 EXIT /B 1

@ECHO OFF
