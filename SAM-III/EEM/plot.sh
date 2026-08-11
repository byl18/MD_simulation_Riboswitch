#!/bin/sh
#$ -cwd
#$ -l gpu_1=1
#$ -l h_rt=24:00:00
#$ -N test_trial
##$ -hold_jid 6573865
module load gromacs
cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial

# bash step5_npt.sh > step5_npt.log
/gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python xvg_plot.py -f /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial/pacs_density.xvg -t density -o pacs_density

