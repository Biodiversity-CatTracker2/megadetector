#!/bin/bash
#SBATCH --time=48:00:00  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !
#SBATCH --job-name='track-progress'
#SBATCH --mem=8gb
#SBATCH --mail-type=ALL
#SBATCH --mail-user=malyeta@ncsu.edu
#SBATCH --error=%J.err
#SBATCH --output=%J.out


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTANT !!
# run `python progress_manager.py -d "$DATA_DIR"` before starting this script!
# IMPORTANT !! <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# -----------------------------------------------------------------------------

export PATH="$PATH"  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !

DATA_DIR=''  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !
NOTIFY_CHANNEL_ID=''  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !

# -----------------------------------------------------------------------------

module unload python
module load tensorflow-gpu

export PATH="$PATH"  # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE !

# -----------------------------------------------------------------------------

if [[ "$NOTIFY_CHANNEL_ID" == '' ]]; then
    echo -e '\033[0;31mERROR: Missing a channel id!\033[0m'
    echo 'Get a channel ID from https://notify.run and pass it as an argument to this script.'
    exit 1
fi

while true; do
    PROGRESS=$(python progress_manager.py -d "$DATA_DIR" --show-progress | tail -1)
    curl https://notify.run/$1 -d "$PROGRESS"
    sleep 10
done
