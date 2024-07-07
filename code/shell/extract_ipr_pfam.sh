#!/bin/bash

# This script parses an ipr file and extracts only entries with pfam domains
# It writes these entries to a new file and also removes the descriptive text
# It assumes that fields in the protein2ipr.dat file are tab delimited

#
# This took 1 hour to execute on my 2020 Macbook against the 98.7GB protein2ipr.dat
#

# VARIABLES
ipr_filename="/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr.dat"
output_file="/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr_pfam.dat"


#
# output start time
#
start="$(date +"%Y%m%d_%H%m%S")"
echo "start:" $start

# ---------------------------------------------------------

#
# PARSE FILE - 2 OPTIONS
#

# use this to only parse a few lines
num_lines=1000
#head -$num_lines $ipr_filename | grep "\tPF[0-9]*\t" | awk 'BEGIN{FS="\t"} {print $1, $2, $4, $5, $6}' > $output_file

# or this to parse entire file
grep "\tPF[0-9]*\t" $ipr_filename | awk 'BEGIN{FS="\t"} {print $1, $2, $4, $5, $6}' > $output_file


# ---------------------------------------------------------

#
# output end time
#
end="$(date +"%Y%m%d_%H%m%S")"
echo "end:" $end