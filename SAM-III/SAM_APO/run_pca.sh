#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N apo
#$ -hold_jid 7918840

module load gromacs 

cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM_APO/6_cmd-1

gmx_mpi trjcat -f cmd1.skip10.whole.xtc cmd2.skip10.whole.xtc cmd3.skip10.whole.xtc cmd4.skip10.whole.xtc cmd5.skip10.whole.xtc -o cmd.skip10.whole.xtc -cat

echo "RNA" | gmx_mpi trjconv \
	-s /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/SAM_APO/6_cmd-1/cmd2.whole.gro \
	-f cmd.skip10.whole.xtc \
	-n ../2_md-preparation/gleap.ndx \
	-o SAM_APO_RNA.xtc


