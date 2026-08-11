#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N test_trial
##$ -hold_jid 6573865

module purge
module load cuda/12.3.2
module load openmpi/5.0.2-gcc
module load gromacs/2024.2-plumed

cd /gs/bs/tga-KitaoLab-NexusYtec/yilan/projects/SAM/EEM/test_trial/6_cmd-1
gmx_mpi trjcat -f cmd{1..5}.skip10.whole.target.xtc -o cmd.skip10.whole.target.xtc -cat
