#!/bin/tcsh

mkdir -p data

set GDRIVE_PARENT="$1"

set FOLDERS_=`./rclone --drive-shared-with-me lsf $GDRIVE_PARENT`

foreach FOLDER_ ( $FOLDERS_ )
    
    echo "Processing $FOLDER_"

    ./rclone --drive-shared-with-me copy $GDRIVE_PARENT/$FOLDER_ data -P --stats-one-line

    tar -xf "data/$FOLDER_" --directory data

    ./detox data -r

    rm data/*.tar

    set INPUT_FOLDER=`echo $FOLDER_ | cut -f 1 -d '.'`

    set IMAGES_DIR=`find data/$INPUT_FOLDER* -maxdepth 0`
    set IMAGES_DIR="$PWD/$IMAGES_DIR"

    set JOB_TIME=`python helpers.py --job-time $IMAGES_DIR`
    sed -i "/#BSUB -W/c\#BSUB -W $JOB_TIME" megadetector_job.csh

    set CONFIDENCE="0.8"

    bsub -env "IMAGES_DIR='$IMAGES_DIR', CONFIDENCE='$CONFIDENCE', GROUP='$GROUP', USER='$USER'" < megadetector_job.csh

    sleep 2
end
