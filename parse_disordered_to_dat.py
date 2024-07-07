import duckdb
import re
import csv
import xml.etree.ElementTree as ElementTree

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

file = '/Users/patrick/dev/ucl/comp0158_mscproject/data/disordered/extra.10000.xml'
db_string = "/Users/patrick/dev/ucl/comp0158_mscproject/database/proteins.db"

def create_table():
    con = duckdb.connect(database=db_string) 
    con.execute("\
    CREATE TABLE DISORDER_TOKEN(\
        UNIPROT_ID VARCHAR,\
        START USMALLINT,\
        END USMALLINT")
    con.close()
    
def parse_file():
    # get an iterable
    context = ElementTree.iterparse(file, events=("start", "end"))

    # turn it into an iterator
    context = iter(context)

    # get the root element
    event, root = next(context)
    #con = duckdb.connect(database=ProteinDB.db_string)

    for event, protein in context:
        if event == "end" and protein.tag == "protein":
            # print(elem.attrib['id'])
            for match in protein:
                if 'MOBIDBLT' in match.attrib['dbname']:
                    for coords in match:
                        uniprot_id = protein.attrib['id']
                        word_type="DISORDER"
                        start_pos = coords.attrib['start']
                        end_pos = coords.attrib['end']
                        
                        print(protein.attrib['id']+"\tIPRXXXXXX\t" +
                                match.attrib['name']+"\t"+match.attrib['id']+"\t" +
                                coords.attrib['start']+"\t"+coords.attrib['end'])
                        
                        #con.execute("INSERT INTO PROTEIN_WORD (UNIPROT_ID, WORD_TYPE, START_POS, END_POS) VALUES(?,?,?,?)", (uniprot_id, word_type, start_pos, end_pos))
            # exit()
            root.clear()
        #con.close()
        
parse_file()