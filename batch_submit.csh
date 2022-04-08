#!/bin/tcsh

mkdir -p data

set FULL_REMOTE_PATH="$1"

set FOLDERS_=`./rclone lsf $FULL_REMOTE_PATH`
# set FOLDERS_=`./rclone --drive-shared-with-me lsf $FULL_REMOTE_PATH` 

foreach FOLDER_ ( $FOLDERS_ )
    
    echo "Processing $FOLDER_"

    rclone copy "$FULL_REMOTE_PATH" data -P --stats-one-line
    # rclone --drive-shared-with-me copy "$FULL_REMOTE_PATH" data -P --stats-one-line

    tar -xf "data/$FOLDER_" --directory data

    rm data/*.tar

    set INPUT_FOLDER=`echo $FOLDER_ | cut -f 1 -d '.'`

    echo "FOLDER: $INPUT_FOLDER"

    set IMAGES_DIR=`find data/$INPUT_FOLDER -maxdepth 0`
    set IMAGES_DIR="$PWD/$IMAGES_DIR"

    set JOB_TIME=`python helpers.py --job-time $IMAGES_DIR`
    sed -i "/#BSUB -W/c\#BSUB -W $JOB_TIME" megadetector_job.csh

    bsub -env "IMAGES_DIR='$IMAGES_DIR', GROUP='$GROUP', USER='$USER'" < megadetector_job.csh

    sleep 2
end
