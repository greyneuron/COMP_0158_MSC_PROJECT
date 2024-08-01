import duckdb
import re
import csv
import xml.etree.ElementTree as ElementTree
import time
import os
import sys

# Looks for chunked extra.xml files in a folder and extracts information into a single tab delimited file
# The output .dat file can then be loaded into a database (although this was also a challenge)
# Note that I ran this on an EC2 instance

# BACKGROUND
# The extra.xml file from ecbi is huge (4bn lines), so use chunk_disorder_xml.py (or .cpp) to split it up first
#
# 4BN lines: wc -l extra.xml
# 4,007,237,378
#
# 57mn mobidb entries (each with potentially mutlple entries)
# grep -c "disorder_prediction\" dbname=\"MOBIDBLT\"" /Volumes/My\ Passport/downloads/extra.xml
# 57,013,227
#
# 81MN disorder entries

# EC2 Execution time - July 19th 2024
#
# t3.large (died)       : First 1M elements processed in 4s (40,056 proteins - 26,709 disorder records)
#                       : Killed after 87s = 778,258 proteins
# t3.2xlarge (died)     : First 1M elements processed in 3.8s
#                       : 778,258 proteins after 84.45s
#                       : 3M proteins in 308s = 5min
#                       : Killed after 3.28M proteins (81M elements) in 352s
# r5d.2xlarge (works)   : First 1M elements processed in 2.8s
#                       : 778,258 proteins in 62.88s 
#                       : 3M proteins in 239s (starts to stuggle on 3.8M proteins but then reovers)
#                       : 4,909,040 in 382s then waits
#                       : extra_part_01.xml = 4,998,283 proteins = 419s (7mins)
#                       : extra_part_02.xml = 4,998,283 proteins = 346s (7mins)
#                       : extra_part_03.xml = 4,973,799 proteins = 411s
#                       : extra_part_04.xml = 4,976,468 proteins = 386s
#                       : extra_part_04.xml = 4,996,557 proteins = 384s
#                       : consistently like that until the end
#
# Total records found : 81,257,100
# % wc -l disordered_tokens.dat_20240719.dat
#

''' last disorder entry in extras_01.xml
<protein id="A0A0B1TV04" name="A0A0B1TV04_OESDE" length="107" crc64="DD962B54888583AE">
  <match id="mobidb-lite" name="disorder_prediction" dbname="MOBIDBLT" status="T" model="mobidb-lite" evd="MobiDBlite">
    <lcn start="1" end="25" sequence-feature="Polyampholyte"/>
    <lcn start="1" end="38" sequence-feature="Consensus Disorder Prediction"/>
    <lcn start="78" end="107" sequence-feature="Consensus Disorder Prediction"/>
'''


#
# utility method - find files in a certain folder starting with a certain name
#
def find_file_names(root_folder, search_string):
    files = os.listdir(root_folder)
    filtered_files = [file for file in files if file.startswith(search_string)]
    sorted_files = sorted(filtered_files)
    return sorted_files


#
#
#
def parse_extra_file(source_folder, source_file_name, output_file):

    source_file = source_folder + source_file_name
    print('parsing file:', source_file)
    
    iteration_count = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    first_line      = True

    # get an iterable
    context = ElementTree.iterparse(source_file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)
    #con = duckdb.connect(database=ProteinDB.db_string)


    ELEMENT_LIMIT   = -1  # elements in each xml to parse
    OUTPUT_LIMIT    = 1000000   # number of elements how often to print a progress message
    BUFFER_SIZE     = 100  # number of dat entries before flushing
    
    protein_count       = 0
    element_count       = 0
    dat_record_count    = 0
    total_record_count  = 0
    output_buffer       = ""
    
    for event, protein in context:
        element_count +=1
        if event == "end" and protein.tag == "protein":
            protein_count += 1
            
            # look within the protein tag
            for match in protein:
                if 'MOBIDBLT' in match.attrib['dbname']:
                    for coords in match:
                        # get the entries for a single dat line
                        uniprot_id  = protein.attrib['id']
                        start       = coords.attrib['start']
                        end         = coords.attrib['end']
                        description = coords.attrib['sequence-feature']
                        
                        dat_line = "|".join([uniprot_id, "DISORDER", description, start, end])
                        output_buffer += dat_line + '\n'
                        
                        dat_record_count   += 1
                        total_record_count += 1
                        
                        if(dat_record_count % BUFFER_SIZE == 0):
                            #print('flushing buffer before:', sys.getsizeof(output_buffer))
                            output_file.write(output_buffer)
                            output_buffer = ""
                            #print('flushing buffer after:', sys.getsizeof(output_buffer))
                            dat_record_count = 0
        
        # this just prints a progress message
        if (element_count % OUTPUT_LIMIT == 0):
            mid_time_end = time.time()
            exec_time = mid_time_end - mid_time_start
            mid_time_start = mid_time_end
            print(source_file_name, ':', element_count,'elements\t',protein_count, 'proteins\t', total_record_count, 'disorder records \t tot time:\t', round(mid_time_end - start_time,2))
                            
        if(ELEMENT_LIMIT != -1):
            if element_count >= ELEMENT_LIMIT:
                print(source_file_name, ':', element_count, 'elements processed.', protein_count, 'proteins found. Total dat entries:', total_record_count, 'Current dat record count to flush:', dat_record_count)
                if(dat_record_count >0 ):
                    output_file.write(output_buffer)
                #output_file.close()
                #con.close()
                print('*')
                root.clear()
                return
    #output_file.close()
    #con.close()
    print('*')
    root.clear()
    
    
    
#
# THIS IS THE MAIN METHOD
# This assumes the xml files have been split into smaler files named "extras_part_" ....
#
def parse_extra_files():

    root_folder     = "/data/dev/ucl/data/disorder/"
    target_file     = "/data/dev/ucl/data/disorder/dat/disordered_tokens_20240719.dat"
    
    search_string   = "extra_part_"
        
    sorted_files = find_file_names(root_folder, search_string)
    
    # open file for appending
    tfh = open(target_file, "a+")
    
    # do something with each file
    for source_file in sorted_files:
        print('found file:', root_folder + source_file)
        parse_extra_file(root_folder, source_file, tfh)
    
    # close the file
    tfh.close()
    
#parse_extra_files()
 
# --------------------------------------------
    








'''

# --------------------------------------------

# *************  DATABASE STUFF  *************

# --------------------------------------------

db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"


def create_table():
    con = duckdb.connect(database=db_string) 
    con.execute("CREATE TABLE PROTEIN_FEATURE( UNIPROT_ID VARCHAR, FEATURE_TYPE VARCHAR, DESCRIPTION VARCHAR,START USMALLINT, END USMALLINT")
    con.close()
#create_table()



# load csv (or pipe delimited file)
def load_disorder_dat_db():
    con = duckdb.connect(database=db_string)           
    con.execute("CREATE TABLE PROTEIN_FEATURE AS SELECT * FROM read_csv_auto('/Users/patrick/dev/ucl/comp0158_mscproject/data/disordered/disordered_tokens_20240714_1216.dat', columns={'UNIPROT_ID' :'VARCHAR', 'FEATURE_TYPE' : 'VARCHAR', 'DESCRIPTION' :'VARCHAR','start': 'USMALLINT', 'end': 'USMALLINT'})")
    con.close()
#load_disorder_dat_db()

# check its there
def db_test():
    con = duckdb.connect(database=db_string)           
    count = con.execute("SELECT COUNT(*) FROM PROTEIN_FEATURE").fetchall()
    print(count)
    con.close()
#db_test()

# apply index
def db_index():
    con = duckdb.connect(database=db_string)          
    res = con.execute("CREATE INDEX PFTR_IDX ON PROTEIN_FEATURE(UNIPROT_ID)")
    print(res)
    con.close()
#db_index()

# run a query
def db_query():
    con = duckdb.connect(database=db_string)
    s = time.time()        
    res = con.execute("SELECT * FROM PROTEIN_FEATURE WHERE UNIPROT_ID=(?)", ['A0A506QE59']).fetchall()
    e = time.time()
    print(res)
    print('Time taken :', e -s)
    con.close()
db_query()
'''