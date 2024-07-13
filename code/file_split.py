import re
import csv
import time
import duckdb


header="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\
<!DOCTYPE interproextra SYSTEM \"extra.dtd\">\
<interproextra>\
<release>\
  <dbinfo dbname=\"PFAM-N\" version=\"36.0\"/>\
  <dbinfo dbname=\"FUNFAM\" version=\"4.3.0\"/>\
  <dbinfo dbname=\"MOBIDBLT\" version=\"2.0\"/>\
  <dbinfo dbname=\"PHOBIUS\" version=\"1.01\"/>\
  <dbinfo dbname=\"ELM\" version=\"2023.04.11\"/>\
  <dbinfo dbname=\"SIGNALP_E\" version=\"4.1\"/>\
  <dbinfo dbname=\"TMHMM\" version=\"2.0c\"/>\
  <dbinfo dbname=\"SIGNALP_G+\" version=\"4.1\"/>\
  <dbinfo dbname=\"SIGNALP_G-\" version=\"4.1\"/>\
  <dbinfo dbname=\"COILS\" version=\"2.2.1\"/>\
</release>"

footer="</interproextra>"

def split_file_from_line(from_line, to_line):
    path        = "/Volumes/My Passport/downloads/extra.xml"
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/disordered/extras_head.xml"
    
    uniprot_id  = ""
    output_file = open(output, "a+")
    
    record_count    = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    
    with open(path, 'r') as input_file:
        for line_number, line in enumerate(input_file):
            if line_number > from_line:
                if to_line == -1:
                    output_file.write(line)
                    continue
                elif line_number <= to_line:
                    output_file.write(line)
                    continue
                else:
                    break
            else:
                continue
    output_file.close()

#split_file_from_line(271373695)
split_file_from_line(271373695,-1)

