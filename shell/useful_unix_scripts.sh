#!/bin/bash
#filename="data/protein2.dat"


# ***************** AWK ******************

# Counts total bytes of all files changed in November
ls -l | awk '$6 == "Nov" { sum += $5 }
             END { print sum }'

grep "dbname=" match_complete.xml | awk '{FS="dbname="}{print $2}' | awk '{print $1}' | sort |uniq -c


#
# grep a zip or gz but only output 10000 lines
#
zgrep . -m 10000 data/disordered/extra.xml.gz > data/disordered/extra.10000.xml

# ---------------------

#
# parse lines like this:
# A0A000	IPR015421	Pyridoxal phosphate-dependent transferase, major domain	G3DSA:3.40.640.10	48	288
# took 20mins to parse protein2ipr.dat for "^[A0A0-9]*A8KBH6"
#

SECONDS=0

filename="/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr.dat"
word="^[A0A0-9]*A8KBH6"

grep $word $filename

t=$SECONDS

printf 'Time taken: %d days, %d minutes\n' "$(( t/86400 ))" "$(( t/60 - 1440*(t/86400) ))"

# ----------------------------

#
# not sure if this works
#

# Define the filenames
proteins_file="/Users/patrick/dev/ucl/comp0158_mscproject/data/10_proteins.dat"
pfam_file="/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr_pfam.dat"

# Loop through each entry in the tokens file
while IFS= read -r token; do
    echo "Searching for: $token"
    # Use grep to find the entry in the search file
    grep -Hn "$token" "$pfam_file" | while IFS= read -r line; do
        echo "Protein: $token"
        echo "Line:" $line
    done
done < "$proteins_file"

# ----------------------------