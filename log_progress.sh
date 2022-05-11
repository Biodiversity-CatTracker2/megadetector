#!/bin/bash

# Get a channel ID from https://notify.run and pass it as an argument to this script

while true; do
    PROGRESS=$(python progress_manager.py --show-progress | tail -1)
    curl https://notify.run/$1 -d "$PROGRESS"
    sleep 10
done
