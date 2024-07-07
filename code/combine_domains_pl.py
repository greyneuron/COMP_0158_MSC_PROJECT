import sys
from collections import defaultdict


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

#
# creates a dictoinary keyed by protein id pointing to an entry which is a line
#
def read_dat_file(path, dat):
    with open(path) as data:
        for line in data:
            entries = line.split(",")
            dat[entries[0]].append(line)
    return(dat)



accessions = defaultdict(list)
accessions = read_dat_file("/scratch1/NOT_BACKED_UP/dbuchan/interpro/derived/"
                           "masked_regions_taxonomy_E.dat", accessions)
accessions = read_dat_file("/scratch1/NOT_BACKED_UP/dbuchan/interpro/derived/"
                           "disorder_regions_taxonomy_E.dat", accessions)
# accessions = read_dat_file("/scratch1/NOT_BACKED_UP/dbuchan/interpro/"
#                            "test_disorder.dat", accessions)

# accessions now has a list of lines - one per protein
# line_cache 

# read a line from the pfam file and add it to a line cache
previous_uniprot = "XXX"
line_cache = []
with open("/scratch1/NOT_BACKED_UP/dbuchan/interpro/derived/"
          "protein2ipr_pfam_taxonomy_E.dat") as pfam:
#          "test_pfam.dat") as pfam:

    # read the first entry from pfaam and get the uniprot id
    first_line = pfam.readline()
    entries = first_line.split(",")
    line_cache.append(first_line)
    previous_uniprot = entries[0] # uniprot id

    # now with the pfam file open, coninue through each line
    for line in pfam:
        entries = line.split(",")
        
        # if the current id is not one we are  already looking at - then its a new uniprot id
        if entries[0] not in previous_uniprot:
            
            # print out what we have in the line cache (as it's now the previous
            # protein and there's no more info). Create a new line cache for the current line
            for line2 in line_cache:
                print(line2.rstrip())
            line_cache = []
            line_cache.append(line)

            if previous_uniprot in accessions:
                for line2 in accessions[previous_uniprot]:
                    print(line2.rstrip())
            previous_uniprot = entries[0]
        else:
            line_cache.append(line)


for line in line_cache:
    print(line.rstrip())
    if previous_uniprot in accessions:
        for line2 in accessions[previous_uniprot]:
            print(line2.rstrip())
