import duckdb
import re
import csv
import xml.etree.ElementTree as ElementTree
import time

#
# THIS WILL ERROR IF YOU ONLY USE A PARTIAL FILE
#

# This works directly on the uncompressed .gz file
# No space on laptop for fully extracted extra.xml
#

# Used this command to extract first 10000 lines into a separate file:
#
# zgrep . -m 10000 data/disordered/extra.xml.gz > data/disordered/extra.10000.xml
#


'''
File header:
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE interproextra SYSTEM "extra.dtd">
<interproextra>
<release>
  <dbinfo dbname="PFAM-N" version="36.0"/>
  <dbinfo dbname="FUNFAM" version="4.3.0"/>
  <dbinfo dbname="MOBIDBLT" version="2.0"/>
  <dbinfo dbname="PHOBIUS" version="1.01"/>
  <dbinfo dbname="ELM" version="2023.04.11"/>
  <dbinfo dbname="SIGNALP_E" version="4.1"/>
  <dbinfo dbname="TMHMM" version="2.0c"/>
  <dbinfo dbname="SIGNALP_G+" version="4.1"/>
  <dbinfo dbname="SIGNALP_G-" version="4.1"/>
  <dbinfo dbname="COILS" version="2.2.1"/>
</release>

This is followed immediately by a number of protein entries


<protein id="Z9JZ37" name="Z9JZ37_9MICO" length="742" crc64="64394712D3B6312F">
  <match id="PF02922" name="" dbname="PFAM-N" status="T" model="PF02922" evd="">
    <lcn start="15" end="99"/>
  </match>
  <match id="PF00128" name="" dbname="PFAM-N" status="T" model="PF00128" evd="">
    <lcn start="197" end="290"/>
  </match>
  <match id="mobidb-lite" name="disorder_prediction" dbname="MOBIDBLT" status="T" model="mobidb-lite" evd="MobiDBlite">
    <lcn start="496" end="514" sequence-feature="Polyampholyte"/>
    <lcn start="496" end="529" sequence-feature="Consensus Disorder Prediction"/>
    <lcn start="680" end="717" sequence-feature="Consensus Disorder Prediction"/>
  </match>
</protein>

And the past </protein> tag is followed by this:

</interproextra>
'''


def create_table():
    db_string   = "/Users/patrick/dev/ucl/comp0158_mscproject/database/proteins.db"
    con = duckdb.connect(database=db_string) 
    con.execute("\
    CREATE TABLE DISORDER_TOKEN(\
        UNIPROT_ID VARCHAR,\
        START USMALLINT,\
        END USMALLINT")
    con.close()


#
#
#
import re
import xml.etree.ElementTree as ElementTree
import time

# grep -c "disorder_prediction\" dbname=\"MOBIDBLT\"" /Volumes/My\ Passport/downloads/extra.xml
# 57,013,227

#wc -l extra.xml
#4,007,237,378

def parse_extra_file():
    file        = "/Volumes/My Passport/downloads/extra.xml"
    output      = "/Users/patrick/dev/ucl/comp0158_mscproject/data/disordered/disordered_tokens_test.dat"
    
    file        = "/data/my_extra.xml"
    output      = "/data/disordered_tokens.dat"

    iteration_count = 0
    start_time      = time.time()
    mid_time_start  = time.time()
    first_line      = True
    
    output_file = open(output, "w")
    
    # get an iterable
    context = ElementTree.iterparse(file, events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)
    #con = duckdb.connect(database=ProteinDB.db_string)


    ELEMENT_LIMIT   = -1  # elements in xml to parse
    OUTPUT_LIMIT    = 2000000   # number of elements how often to print a progress message
    BUFFER_SIZE     = 500       # number of dat entries before flushing
    
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
                        
                        dat_line = "|".join([uniprot_id, start, end])
                        output_buffer += dat_line + '\n'
                        
                        dat_record_count   += 1
                        total_record_count += 1
                        
                        if(dat_record_count % BUFFER_SIZE == 0):
                            output_file.write(output_buffer)
                            output_buffer = ""
                            dat_record_count = 0
        
        if (element_count % OUTPUT_LIMIT == 0):
            mid_time_end = time.time()
            exec_time = mid_time_end - mid_time_start
            mid_time_start = mid_time_end
            print(element_count,'elements processed', total_record_count, 'total entries found\t',total_record_count, 'time taken last batch:\t', round(exec_time,2), '\ttime to date:\t', round(mid_time_end - start_time,2))
                            
        if(ELEMENT_LIMIT != -1):
            if element_count >= ELEMENT_LIMIT:
                print(element_count, 'elements processed.', protein_count, 'proteins found. Total dat entries:', total_record_count, 'Current dat record count to flush:', dat_record_count)
                if(dat_record_count >0 ):
                    output_file.write(output_buffer)
                output_file.close()
                #con.close()
                print('*')
                root.clear()
                return
    output_file.close()
    #con.close()
    print('*')
    root.clear()
parse_extra_file()



# --------------------------------------------

# *************  DATABASE STUFF  *************

# --------------------------------------------

db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/test.db"

# load csv (or pipe delimited file)
def load_disorder_dat_db():
    con = duckdb.connect(database=db_string)           
    con.execute("CREATE TABLE DISORDER_TOKEN AS SELECT * FROM read_csv_auto('/Users/patrick/dev/ucl/comp0158_mscproject/data/disordered/disordered_tokens.dat', columns={'uniprot_id' :'VARCHAR', 'start': 'USMALLINT', 'end': 'USMALLINT'})")
    description = con.execute("DESCRIBE DISORDER_TOKEN").fetchall()
    print(description)
    con.close()
#load_disorder_dat_db()

# check its there
def db_test():
    con = duckdb.connect(database=db_string)           
    count = con.execute("SELECT COUNT(*) FROM DISORDER_TOKEN").fetchall()
    print(count)
    con.close()
#db_test()

# apply index
def db_index():
    con = duckdb.connect(database=db_string)          
    res = con.execute("CREATE INDEX DS_TKN_IDX ON DISORDER_TOKEN(UNIPROT_ID)")
    print(res)
    con.close()
#db_index()

# run a query
def db_query():
    con = duckdb.connect(database=db_string)          
    res = con.execute("SELECT * FROM DISORDER_TOKEN WHERE UNIPROT_ID=(?)", ['A0A0T6ANQ5']).fetchall()
    print(res)
    con.close()
db_query()