#!/bin/sh

#PBS -N SUB_SHELL
#PBS -l walltime=11:59:00
#PBS -l nodes=1:ppn=1
#PBS -q short
#PBS -e suberror_exp.file

module load scripts
module load Python/2.7.3-ictce-4.1.13
chmod 770 mite_model_ng.py 
python mite_model_ng.py $MOR $CAR $MUT $LIM $DTO $RTO $REP

