#!/bin/tcsh
#BSUB -n 1
#BSUB -W 48:00
#BSUB -J %J
#BSUB -o logs/%J.out
#BSUB -e logs/%J.err
#BSUB -q gpu
#BSUB -R "select[rtx2080||gtx1080||p100]"
#BSUB -gpu "num=1:mode=shared:mps=yes"
#BSUB -R "rusage[mem=32GB]"
#BSUB -x


module load conda cuda tensorflow
nvidia-smi
echo "DIRECTORY: $DATA_DIR"

python megadetector-lite.py --images-dir "$DATA_DIR"

cd $DATA_DIR
DATA_FILES=$(../rclone lsf -R --files-only --include "*.json" --filter "- ckpt.json" .) &&
zip 'results.zip' $DATA_FILES &&
mv 'results.zip' ..
cd ..

python filter_megadetector_output.py -d "$DATA_DIR" -c "$CONF" &&

echo "Finished. Upload relevant logs."
