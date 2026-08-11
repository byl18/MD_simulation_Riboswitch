#!/bin/sh
#$ -cwd
#$ -l gpu_1=1
#$ -l h_rt=24:00:00
#$ -N i_hb
##$ -hold_jid 6503659


cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/pacs/post_analysis
# /gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python -u /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/pacs/post_analysis/interactions_hbond.py
# /gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python -u /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/pacs/post_analysis/interactions_hbond_plot.py
/gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python -u /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/pacs/post_analysis/interactions_hbond_plot2.py

