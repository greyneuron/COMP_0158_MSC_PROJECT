#!/bin/bash

echo "creating direcortories files"

# find . -name "*M_*M" -exec rm -R {} \;

mkdir output
for i in $(seq 0 2) 
do
    for j in $(seq 0 2);
    do
        mkdir output/${i}${j}M_${j}M

        for k in $(seq 0 2);
        do
            touch output/${i}${j}M_${j}M/sqloutput_${i}${j}M_${k}.txt
        done
    done
done