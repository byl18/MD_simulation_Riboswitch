#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N i_hb
##$ -hold_jid 6503659


cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/PreQ0/trial01/pacs2/post_analysis
# /gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python -u /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/PreQ0/trial01/pacs2/post_analysis/interactions_hbond.py
# /gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python -u /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/PreQ0/trial01/pacs2/post_analysis/interactions_hbond_plot.py
/gs/bs/tga-KitaoLab-NexusYtec/yilan/softwares/miniconda3/envs/pacsmd/bin/python -u /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/PreQ0/trial01/pacs2/post_analysis/interactions_hbond_plot2.py
