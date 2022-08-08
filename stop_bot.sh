#!/bin/bash

LOG_FILE=$1

bot_file_name="rand_gift_bot.py"

stop_bot() {
    pid=$(ps aux | grep -w "$bot_file_name" | grep -vw grep | awk '{print $2}')

    if [ -n "$pid" ]; then
        kill $pid
        sleep 1
        pid=$(ps aux | grep -w "$bot_file_name" | grep -vw grep | awk '{print $2}')
        if [ -n "$pid" ]; then
            kill -9 $pid
            echo "Bot killed"
        else
            echo "Bot stopped"
        fi
    else
        echo "Bot not found"
    fi
}

if [ -n "$LOG_FILE" ]; then
    touch $LOG_FILE
    if [ ! -f "$LOG_FILE" ]; then
        echo "File $LOG_FILE does not exist"
    fi
fi

if [ -z "$LOG_FILE" ] || [ ! -f "$LOG_FILE" ]; then
    stop_bot
else
    stop_bot 2>&1 | tee -a $LOG_FILE
fi
