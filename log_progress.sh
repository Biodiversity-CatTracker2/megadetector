#!/bin/bash

if [[ "$1" == '' ]]; then
    echo -e '\033[0;31mERROR: Missing a channel id!\033[0m'
    echo 'Get a channel ID from https://notify.run and pass it as an argument to this script.'
    exit 1
fi

NUM_TOTAL_FILES=$(python progress_manager.py --total-files)

while true; do
    PROGRESS=$(python progress_manager.py $NUM_TOTAL_FILES | tail -1)
    curl https://notify.run/$1 -d "$PROGRESS"
    sleep 10
done
