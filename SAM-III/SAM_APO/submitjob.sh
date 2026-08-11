#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N sam_apo
#$ -hold_jid 7918841

module load gromacs 

bash md_total.sh 




