from Bio import SeqIO
import re
import csv
import duckdb

# internal representation
from protein_db import ProteinDB

pdb = ProteinDB()

#
# PARSE TREMBL FASTA 
#
# >tr|A0A7C4TRX0|A0A7C4TRX0_9EURY Probable GTP 3',8-cyclase OS=Archaeoglobus sp. OX=1872626 GN=moaA PE=3 SV=1
#
def parse_trembl_fasta(dom_type):
    path        = "/Users/patrick/dev/ucl/comp0158_mscproject/data/uniprot_trembl_10M.fasta"
    
    #uniprot_re  = "tr\|([A-Z0-9]+)\|"
    regex       = "tr\|([A-Z0-9]+)\|.*OX=([0-9]+)"
    #regex       = "tr\|([A-Z0-9]+)\|"
    
    #con = duckdb.connect(database=ProteinDB.db_string) 
    
    PROCESS_LIMIT = 10
    record_count = 0
    
    for record in SeqIO.parse(path, "fasta"):
            
        # -------- check for termination ------------
        #
        if(PROCESS_LIMIT != -1):
            if record_count >= PROCESS_LIMIT:
                print('Last entry:', record.name)
                print('Processing limit reached %s stopping' % (PROCESS_LIMIT))
                break
        record_count += 1
        # ------------------------------------

        #print('processing :', record.description)
        
        result      = re.search(regex, record.description)
        if (result is not None):
            uniprot_id  = result.group(1)
            tax_id      = result.group(2)
            print(uniprot_id, tax_id)
            #print(uniprot_id)
        
        
        '''       
        pfam_res = con.execute("SELECT * FROM PROTEIN_WORD WHERE UNIPROT_ID = ?", [uniprot_id]).fetchall()
        if pfam_res is not None:
            if len(pfam_res) > 0:
                print(uniprot_id)
                print(pfam_res)
        
        #con.execute("INSERT INTO PROTEIN (UNIPROT_ID, SHORT_DESCRIPTION, TAX_NAME, TAX_ID, DOM_TYPE, REP_ID, START_POS, END_POS) VALUES##(?,?,?,?,?,?,?,?)", (uniprot_id, short_desc, tax_name, tax_id, dom_type, rep_id, start, end))
     
    #con.close()
    '''

parse_trembl_fasta("LowComplexity")
#parse_trembl_fasta(file, "CoiledCoil")