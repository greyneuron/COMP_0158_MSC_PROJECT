#!/bin/bash

# --------------------------------------------------------------------------
#    queries pfam to get clans
# --------------------------------------------------------------------------


# works
#for pfam in PF00096 PF00400	PF00069	PF00041	PF12796; do clan=$(curl -s https://www.ebi.ac.uk/interpro/api/entry/pfam/"${pfam}"/ | sed -n 's/.*set_info\(.\{15\}\)\(.\{8\}\).*/\2/p'); echo $pfam : $clan; done



#vocab_file="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/data/clusters/20240905_model_vocab.txt"
vocab_file="/Users/patrick/dev/ucl/word2vec/COMP_0158_MSC_PROJECT/code/hpc/unmatched_pfam_clans.txt"

while read -r pfam; do
    #echo $pfam;
    clan=$(curl -s https://www.ebi.ac.uk/interpro/api/entry/pfam/"${pfam}"/ | sed -n 's/.*set_info\(.\{16\}\)\(.\{6\}\).*/\2/p'); 
    echo $pfam "|" $clan;
done < $vocab_file