#!/bin/sh
#$ -cwd
#$ -l gpu_1=1
#$ -l h_rt=24:00:00
#$ -N Q0.1
#$ -hold_jid 5980150   

module load gromacs 

bash md_total.sh 




