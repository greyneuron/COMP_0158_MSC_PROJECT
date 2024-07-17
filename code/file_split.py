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
'''
[ec2-user@ip-10-0-1-15 ucl]$ sudo python3 file_split.py 
splitting from 0 to 5000000 file: /data/dev/ucl/data/disorder/extra_part_1.xml
split 1 in:	 246.3716413974762 s	total time:	 246.37164545059204 s
splitting from 5000000 to 10000000 file: /data/dev/ucl/data/disorder/extra_part_2.xml
split 2 in:	 445.18198919296265 s	total time:	 691.5549104213715 s
splitting from 10000000 to 15000000 file: /data/dev/ucl/data/disorder/extra_part_3.xml
split 3 in:	 650.8876001834869 s	total time:	 1342.4425621032715 s
splitting from 15000000 to 20000000 file: /data/dev/ucl/data/disorder/extra_part_4.xml
split 4 in:	 856.3099727630615 s	total time:	 2198.752578020096 s
splitting from 20000000 to 25000000 file: /data/dev/ucl/data/disorder/extra_part_5.xml
split 5 in:	 1065.350376367569 s	total time:	 3264.102992296219 s
splitting from 25000000 to 30000000 file: /data/dev/ucl/data/disorder/extra_part_6.xml
split 6 in:	 1255.8556699752808 s	total time:	 4519.9587025642395 s
splitting from 30000000 to 35000000 file: /data/dev/ucl/data/disorder/extra_part_7.xml
split 7 in:	 1459.1527664661407 s	total time:	 5979.111508607864 s
splitting from 35000000 to 40000000 file: /data/dev/ucl/data/disorder/extra_part_8.xml
split 8 in:	 1674.2471599578857 s	total time:	 7653.35870885849 s
splitting from 40000000 to 45000000 file: /data/dev/ucl/data/disorder/extra_part_9.xml
split 9 in:	 1911.2676434516907 s	total time:	 9564.628689289093 s
splitting from 45000000 to 50000000 file: /data/dev/ucl/data/disorder/extra_part_10.xml
split 10 in:	 2173.349065065384 s	total time:	 11737.980268001556 s
splitting from 50000000 to 55000000 file: /data/dev/ucl/data/disorder/extra_part_11.xml
split 11 in:	 2375.8305299282074 s	total time:	 14113.81326842308 s
splitting from 55000000 to 60000000 file: /data/dev/ucl/data/disorder/extra_part_12.xml
split 12 in:	 2614.4903304576874 s	total time:	 16728.307777643204 s
splitting from 60000000 to 65000000 file: /data/dev/ucl/data/disorder/extra_part_13.xml
split 13 in:	 2847.5823051929474 s	total time:	 19575.891444683075 s
splitting from 65000000 to 70000000 file: /data/dev/ucl/data/disorder/extra_part_14.xml
split 14 in:	 3073.040769338608 s	total time:	 22648.93333721161 s
splitting from 70000000 to 75000000 file: /data/dev/ucl/data/disorder/extra_part_15.xml
split 15 in:	 3350.9117743968964 s	total time:	 25999.849335432053 s
splitting from 75000000 to 80000000 file: /data/dev/ucl/data/disorder/extra_part_16.xml
split 16 in:	 3619.2104892730713 s	total time:	 29619.05987381935 s
splitting from 80000000 to 85000000 file: /data/dev/ucl/data/disorder/extra_part_17.xml




'''


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

