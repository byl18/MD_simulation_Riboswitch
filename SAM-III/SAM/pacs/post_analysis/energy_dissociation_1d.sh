#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N post_pacs
##$ -hold_jid 6503659

export OPENBLAS_NUM_THREADS=8
export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export NUMEXPR_NUM_THREADS=8
export VECLIB_MAXIMUM_THREADS=8

cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/pacs/post_analysis
# /gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python -u /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/pacs/post_analysis/energy_dissociation_1d.py
/gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python -u /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/pacs/post_analysis/energy_dissociation_1d_plot.py
