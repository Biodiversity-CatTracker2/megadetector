#!/bin/tcsh
#BSUB -n 1
#BSUB -W 02:00
#BSUB -J %J
#BSUB -o logs/%J.out
#BSUB -e logs/%J.err
#BSUB -q gpu
#BSUB -R "select[rtx2080||gtx1080||p100]"
#BSUB -gpu "num=1:mode=shared:mps=yes"
#BSUB -x  # exclusive node to avoid running out of memory

module load conda cuda tensorflow
nvidia-smi

set PARENT_IMAGES_DIR="/gpfs_common/share03/$GROUP/$USER/megadetector/$IMAGES_DIR"
echo "DIRECTORY: $PARENT_IMAGES_DIR"

python megadetector.py --images-dir "$PARENT_IMAGES_DIR" --confidence "$CONFIDENCE" --resume
