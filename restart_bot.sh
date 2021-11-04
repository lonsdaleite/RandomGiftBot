#!/bin/bash

dir=$(dirname $0)
cd $dir

./stop_bot.sh

nohup python3 ./rand_gift_bot.py >> ./rand_gift_bot.log 2>&1 &
echo "Random gift bot started"
