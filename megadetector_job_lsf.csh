#!/bin/tcsh
#BSUB -n 1
#BSUB -W 02:00
#BSUB -J %J
#BSUB -o logs/%J.out
#BSUB -e logs/%J.err
#BSUB -q gpu
#BSUB -R "select[rtx2080||gtx1080||p100]"
#BSUB -gpu "num=1:mode=shared:mps=yes"

module load conda cuda tensorflow
nvidia-smi
echo "DIRECTORY: $IMAGES_DIR"

python megadetector-lite.py --images-dir "$IMAGES_DIR" --jobid "$LSB_JOBID" --resume
