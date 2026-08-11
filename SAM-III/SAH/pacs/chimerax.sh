#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N merge_traj
##$ -hold_jid 6573865

/gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAH/test_trial/pacs/trace.py
