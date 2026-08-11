#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N post_pacs
##$ -hold_jid 6503659

module load gromacs
cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial/pacs/post_analysis
echo "Target" | gmx_mpi trjconv -f /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial/6_cmd-1/cmd5_center.gro  -s  /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial/6_cmd-1/cmd5_center.gro -n  /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial/2_md-preparation/gleap.ndx -o dissociation_direction/ref_target.pdb
