#!/bin/bash

pid=$(ps aux | grep 'rand_gift_bot.py' | grep -vw grep | awk '{print $2}')

if [ -n "$pid" ]; then
    kill $pid
    sleep 1
    pid=$(ps aux | grep 'rand_gift_bot.py' | grep -vw grep | awk '{print $2}')
    if [ -n "$pid" ]; then
        kill -9 $pid
        echo "Random gift bot killed"
    else
        echo "Random gift bot stopped"
    fi
else
    echo "Random gift bot not found"
fi

