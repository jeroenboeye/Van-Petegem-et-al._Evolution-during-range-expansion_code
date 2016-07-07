#!/bin/sh
#PBS -N MAIN_SHELL
#PBS -l walltime=02:00:00
#PBS -l nodes=1:ppn=1
#PBS -q short
#PBS -o outputmain_exp.file
#PBS -e errormain.file

mort=(0.9)
carry=(200)
muta=(0.01)
rlim=(10)
devto=(0.1 0.2 0.5)
repto=(0.1 0.2 0.5)

for M in "${mort[@]}"
do
for K in "${carry[@]}"
do
for U in "${muta[@]}"
do
for L in "${rlim[@]}"
do
for D in "${devto[@]}"
do
for R in "${repto[@]}"
do
for RE in $(seq 1 20)
do
export MOR=$M
export CAR=$K
export MUT=$U
export LIM=$L
export DTO=$D
export RTO=$R
export REP=$RE
qsub sub_shell_ng.sh -v MOR,CAR,MUT,LIM,DTO,RTO,REP
done
done
done
done
done
done
done