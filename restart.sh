#!/usr/bin/env bash

pid=$(ps x | grep python | grep -v grep | awk '{print $1}')
if [[ ! -z $pid ]]; then
    kill $pid
fi
nohup python start.py > rjj.log 2>&1 &

