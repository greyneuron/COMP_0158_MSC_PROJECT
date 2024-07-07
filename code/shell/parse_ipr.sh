#!/bin/bash
#filename="data/protein2.dat"

SECONDS=0
#
# took 20mins to parse protein2ipr.dat for "^[A0A0-9]*A8KBH6"
#

filename="/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr.dat"
word="^[A0A0-9]*A8KBH6"

#grep $word $filename
#grep ">" data/protein2ipr_pfam.dat

grep $word $filename

t=$SECONDS

printf 'Time taken: %d days, %d minutes\n' "$(( t/86400 ))" "$(( t/60 - 1440*(t/86400) ))"