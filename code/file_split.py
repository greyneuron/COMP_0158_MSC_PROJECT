import re
import csv
import time


header="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\
<!DOCTYPE interproextra SYSTEM \"extra.dtd\">\n\
<interproextra>\n\
<release>\n\
  <dbinfo dbname=\"PFAM-N\" version=\"36.0\"/>\n\
  <dbinfo dbname=\"FUNFAM\" version=\"4.3.0\"/>\n\
  <dbinfo dbname=\"MOBIDBLT\" version=\"2.0\"/>\n\
  <dbinfo dbname=\"PHOBIUS\" version=\"1.01\"/>\n\
  <dbinfo dbname=\"ELM\" version=\"2023.04.11\"/>\n\
  <dbinfo dbname=\"SIGNALP_E\" version=\"4.1\"/>\n\
  <dbinfo dbname=\"TMHMM\" version=\"2.0c\"/>\n\
  <dbinfo dbname=\"SIGNALP_G+\" version=\"4.1\"/>\n\
  <dbinfo dbname=\"SIGNALP_G-\" version=\"4.1\"/>\n\
  <dbinfo dbname=\"COILS\" version=\"2.2.1\"/>\n\
</release>\n"

footer="</interproextra>"


# splits an xml file into separte files each with a header and footer
# the split is based upon the number of protein tags. The original file was 
# 188.47GB, each split is about 4GB
#
# Macbook
# Locally on mac: A split of 5M proteins per xml was taking up to 10min
# and got progressively worse - should really not go through the whole
# file each time. 

#
# EC2
# Trying on ec2 with d2.2xlarge and ebs : 246s (4 min for 500M proteins)
# extra_part-1.xml  : 246s
# extra_part-2.xml  : 691s
#
# extra_part_6.xml : 4,510 s

def split_file_from_protein(from_count, to_count, file_count):
    #path    = "/Volumes/My Passport/downloads/extra.xml"
    #output  = "/Volumes/My Passport/downloads/extras_part_02" + str(file_count) +".xml"
    
    path    = "/data/dev/ucl/data/disorder/extra.xml"
    output  = "/data/dev/ucl/data/disorder/extra_part_" + str(file_count) +".xml"
    
    print('splitting from', from_count, 'to', to_count, 'file:', output)
    
    rexp  = "^<protein id="
    end_exp  = "^<\/interproextra"
    protein_count = 0
    start = False
    
    output_file = open(output, "w")
    output_file.write(header)
    
    with open(path, 'r') as input_file:
        for line_number, line in enumerate(input_file):
            
            # if I've reached the end of the file
            if re.search(end_exp, line):
                print("last entry reached, finishing")
                output_file.write(footer)
                input_file.close()
                output_file.close()
                return
            
            # if current entry is for a protein, increase the counter
            if re.search(rexp, line):
                protein_count += 1
                start = True # want to avoid writing out header
                
            # if before starting point
            if protein_count < from_count:
                continue
            # write out a ine as long as I'm in range
            if protein_count > from_count and protein_count <= to_count:
                if start:
                    output_file.write(line)
                    continue
            # if I'm at the end of the range, write 
            elif protein_count > to_count:
                if start:
                    output_file.write(footer)
                    input_file.close()
                    output_file.close()
                    return
                    
#
# Loop to split file
#
def split():
    PROTEIN_LIMIT = 5000000 # number of proteins per file = 5M
    #MAX_PROTEINS  = 100000000
    MAX_PROTEINS  = 10000000000
    
    ts = time.time()
    file_count = 0
    
    for i in range(0, MAX_PROTEINS, PROTEIN_LIMIT):
        file_count +=1
        s = time.time()
        split_file_from_protein(i, i+PROTEIN_LIMIT, file_count)
        e = time.time()
        print('split', file_count, 'in:\t', str(e-s), 's\ttotal time:\t', str(e-ts),'s')
split()

