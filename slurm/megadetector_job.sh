#!/bin/bash
#SBATCH --time=48:00:00  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !
#SBATCH --job-name='megadetector'
#SBATCH --partition='gpu'
#SBATCH --gres=gpu
#SBATCH --constraint=gpu_v100
#SBATCH --mem=32gb
#SBATCH --mail-type=ALL
#SBATCH --error=%J.err
#SBATCH --output=%J.out


# -----------------------------------------------------------------------------

DATA_DIR=""  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !
CONF=""  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !
NOTIFY_CHANNEL_ID=""  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !
RCLONE_SOURCE=""  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !

# -----------------------------------------------------------------------------

module unload python
module load tensorflow-gpu cuda/11.2 rclone

export PATH="$PATH"  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !

nvidia-smi

# -----------------------------------------------------------------------------

curl https://notify.run/$NOTIFY_CHANNEL_ID -d "Started"

rclone copy "$RCLONE_SOURCE" $DATA_DIR -P --transfers 32

curl https://notify.run/$NOTIFY_CHANNEL_ID -d "Ended"
sleep 10

# -----------------------------------------------------------------------------

python megadetector-lite.py --images-dir $DATA_DIR &&

# -----------------------------------------------------------------------------

cd $DATA_DIR
DATA_FILES=$(rclone lsf -R --files-only --include "*.json" --filter "- ckpt.json" .) &&
zip 'results.zip' $DATA_FILES &&
rclone copy 'results.zip' "$RCLONE_SOURCE/results" &&
mv 'results.zip' ..
cd ..


# -----------------------------------------------------------------------------

python filter_megadetector_output.py -d "$DATA_DIR" -c "$CONF" &&

cp 'detections_per_conf_lvl.json' 'detections_per_conf_lvl_count.json' 'failed.json' filtered_data

# -----------------------------------------------------------------------------

rclone copy filtered_data "$RCLONE_SOURCE/results" -P --transfers 32

echo "Finished. Upload relevant logs."
