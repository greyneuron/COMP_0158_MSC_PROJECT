#!/bin/bash
filename="/Users/patrick/dev/ucl/comp0158_mscproject/data/uniref100_10M.fasta"
word=">"

SECONDS=0

#grep $word $filename
#grep ">" data/protein2ipr_pfam.dat
#grep $word $filename | awk '{FS="\t"}{print $1}'
grep $word $filename | awk '{print $1}' | awk '{FS="_"}{print $2}'

t=$SECONDS
printf 'Time taken: %d days, %d minutes\n' "$(( t/86400 ))" "$(( t/60 - 1440*(t/86400) ))"