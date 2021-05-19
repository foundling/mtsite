#!/bin/bash

user=$1
host=$2

usage() {
    echo usage: push [user] [host]
    exit 1
}

[ -z "$1" ] || [ -z "$2" ] && usage


echo building and pushing ...

rm -rf ./build/* && python freeze.py && rsync -aP build/* $user@$host:~/www/machinetonemusic.com/ 

echo done!
