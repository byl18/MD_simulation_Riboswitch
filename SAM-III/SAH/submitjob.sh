#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N sah
#$ -hold_jid 7918838

module load gromacs 

bash md_total.sh 




