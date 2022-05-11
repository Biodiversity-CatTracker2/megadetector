#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --job-name='megadetector'
#SBATCH --partition='gpu'
#SBATCH --gres=gpu
#SBATCH --constraint=gpu_v100
#SBATCH --mem=32gb
#SBATCH --mail-type=ALL
#SBATCH --error=%J.err
#SBATCH --output=%J.out

module unload python
module load tensorflow-gpu
module load cuda/11.2

nvidia-smi

python megadetector-lite.py --images-dir data
