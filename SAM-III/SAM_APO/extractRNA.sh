#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N sam
#$ -hold_jid 7918840

module load gromacs 

cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM_APO/6_cmd-1
printf "RNA\n" | gmx_mpi trjconv \
	    -s cmd2.whole.gro \
	        -f cmd2.whole.gro \
		    -n ../2_md-preparation/gleap.ndx \
		        -o SAM_APO_ref_RNA.gro
