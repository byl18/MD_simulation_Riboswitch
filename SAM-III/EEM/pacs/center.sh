#!/bin/sh
#$ -cwd
#$ -l gpu_1=1
#$ -l h_rt=24:00:00
#$ -N test_trial
##$ -hold_jid 6573865

module purge
module load cuda/12.3.2
module load openmpi/5.0.2-gcc
module load gromacs

echo "Center" "System" | gmx_mpi trjconv -f ../6_cmd-1/cmd5.xtc -s ../6_cmd-1/cmd5.tpr -n ../2_md-preparation/gleap.ndx -b 200000 -e 200000 -o ../6_cmd-1/cmd5_center.gro -pbc mol -center
