#!/bin/bash

# download from here: https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/

# Comment out whciever bits you don't need

# TIP : To view the \t and \n characters in these files you can use the 
# following command in order to make them more visible:
#
# cat -vte nodes.dmp
#


# --------------------------- Nodes -------------------
# nodes.dmp
# 
# 	tax_id					-- node id in GenBank taxonomy database
#  	parent tax_id			-- parent node id in GenBank taxonomy database
#  	rank					-- rank of this node (superkingdom, kingdom, ...) 
#  	embl code				-- locus-name prefix; not unique
#  	division id				-- see division.dmp file
#  	inherited div flag  (1 or 0)		-- 1 if node inherits division from parent
#  	genetic code id				-- see gencode.dmp file
#  	inherited GC  flag  (1 or 0)		-- 1 if node inherits genetic code from parent
#  	mitochondrial genetic code id		-- see gencode.dmp file
#  	inherited MGC flag  (1 or 0)		-- 1 if node inherits mitochondrial gencode from parent
#  	GenBank hidden flag (1 or 0)            -- 1 if name is suppressed in GenBank entry lineage
#  	hidden subtree root flag (1 or 0)       -- 1 if this subtree has no sequence data yet
#  	comments				-- free-text comments and citations

# seems to work apart from the first entry
#file="/Volumes/My Passport/data/taxonomy/nodes.dmp"
#echo "Processing file: $file"
#head -10 "$file" | awk '{FS="[\t|]+"}{print $1 "|" $2 "|" $3}'



# --------------------------- Categories -------------------

# categories.dmp contains a single line for each node that is at or below the 
# species level in the NCBI Taxonomy database.

# The first column is the top-level category -
# A = Archaea
# B = Bacteria
# E = Eukaryota
# V = Viruses and Viroids
# U = Unclassified
# O = Other

# The third column is the taxid itself
# The second column is the corresponding species-level taxid

# Example note how in the first entry the 3rd column is the same as the 2nd - must be a parent?
#A       242703  242703
#A       242703  666510

#file="/Volumes/My Passport/data/taxonomy/categories.dmp"
#file="../../data/taxonomy/categories.dmp"

#echo "Processing file: $file"

# ---- these 3 all work and do different things

# 1. Output only eukaryotic taxonomies - works
#cat "$file" | awk '{FS="\t"}{if (($1~/E/)) print $1 "|" $2 "|" $3}' >> categories_E.dat

# 2. Output only eukaryotic entries where column 2 is not the same as column 3
#cat "$file" | awk '{FS="\t"}{if (($1~/E/) && ($2 != $3)) print $1 "|" $2 "|" $3}'

# 3. Output only eukaryotic entries where column 2 is not the same as column 3
#cat "$file" | awk '{FS="\t"}{if (($1~/E/) && ($2 == $3)) print $1 "|" $2 "|" $3}'




# --------------------------- Names -------------------


# Taxonomy names file has these fields:

# 	tax_id					-- the id of node associated with this name
# 	name_txt				-- name itself
# 	unique name				-- the unique variant of this name if name not unique
# 	name class				-- (synonym, common name, ...)

# Reconciliation
# There are 2,588,170 entries with the class "scientific name"
# Command: grep -c "scientific name" "../../data/taxonomy/names.dmp"

# NOTE
# The formatting of this file seems quite hard to parse as they do not always put a token
# between a separator, it's hard to get a regexp to work for the root entry. Also the
# awk separator was working differently when executed from vscode terminal as a script
# compared to entering from the command line.
#       The command line option gave the same results as grep -c so I used that

#file="/Volumes/My Passport/data/taxonomy/names.dmp"
file="../../data/taxonomy/names.dmp"

echo "Processing file: $file"

# SCRIPT OPTION  - CAN'T BE TRUSTED
#
# This seemed to work OK when executed from this script but it only found 2,578,772 entries
#cat "$file" | awk '{FS="[\t|]+"}{ if ($3~/scientific/) print $1, ":", $2, ":", $3, ":" $4}' >> scientific_names.dat

# COMMAND LINE OPTION - WORKS BEST
# In the end I used this from the command line - but add back in the first root entry
# this gives 2,588,170 results which is the same amount as returned by grep -c "scientific name" "../../data/taxonomy/names.dmp"
cat "../../data/taxonomy/names.dmp" | awk '{FS="\t.[\t]?"} {if ($4~/scientific/) print $1 "|" $2}' >> scientific_names_20240802.dat
