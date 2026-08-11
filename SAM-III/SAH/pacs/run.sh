#!/bin/sh
#$ -cwd
#$ -l gpu_1=1
#$ -l h_rt=24:00:00
#$ -N merge_traj
##$ -hold_jid 6573865
module load gromacs
echo 0 | gmx_mpi trjconv -f trial001/prd.target.trjcat-all.pbc.skip10.xtc -s ../2_md-preparation/gleap.target.gro -o trial001/prd.target.trjcat-all.skip100.xtc -skip 10