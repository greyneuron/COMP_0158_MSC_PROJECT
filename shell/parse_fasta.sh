#!/bin/bash
filename="data/protein2ipr_pfam.dat"
word=">"
#grep $word $filename

#grep ">" data/protein2ipr_pfam.dat

grep $word $filename | awk '{print $1}'