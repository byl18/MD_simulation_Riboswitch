#!/bin/sh
#$ -cwd
#$ -l node_q=1
#$ -l h_rt=24:00:00
#$ -N eem
#$ -hold_jid 7932403

module load gromacs 


#bash step5_npt.sh > step5_npt.log
bash md_total.sh 




