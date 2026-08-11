#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N sam
#$ -hold_jid 7918840

module load gromacs 

cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM/test_trial/6_cmd-1

gmx_mpi trjcat -f cmd1.skip10.whole.xtc cmd2.skip10.whole.xtc cmd3.skip10.whole.xtc cmd4.skip10.whole.xtc cmd5.skip10.whole.xtc -o cmd.skip10.whole.xtc -cat

echo "RNA" | gmx_mpi trjconv \
	-s /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM_APO/6_cmd-1/cmd2.whole.gro \
	-f cmd.skip10.whole.xtc \
	-n ../2_md-preparation/gleap.ndx \
	-o SAM_RNA.xtc



printf "RNA\n" | gmx_mpi convert-tpr \
	    -s cmd2.tpr \
	        -n ../2_md-preparation/gleap.ndx \
		    -o SAM_ref_RNA.tpr

printf "System\nSystem\n" | gmx_mpi trjconv \
	-s SAM_ref_RNA.tpr \
	-f SAM_RNA.xtc \
	-o SAM_RNA_fit.xtc \
	-fit rot+trans

