#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N sam
#$ -hold_jid 7918840

module load gromacs 

cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/6_cmd-1

printf "RNA\n" | gmx_mpi convert-tpr \
	    -s cmd2.tpr \
	        -n ../2_md-preparation/gleap.ndx \
		    -o SAM_ref_RNA.tpr

printf "System\nSystem\n" | gmx_mpi trjconv \
	-s SAM_ref_RNA.tpr \
	-f SAM_RNA.xtc \
	-o SAM_RNA_fit.xtc \
	-fit rot+trans

