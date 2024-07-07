import argparse
from Bio import SeqIO
import re

import csv


#
# Extract fasta entry for a protein id
#    
def extract_fasta(start_token, end_token):
    fasta_filename = '/Volumes/My Passport/ucl/MSc/uniref100.fasta'
    # Read the contents of the file
    with open(fasta_filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Define the regex pattern to match text between the start and end tokens
    pattern = re.compile(re.escape(start_token) + r'(.*?)' + re.escape(end_token), re.DOTALL)
    
    # Find all matches
    matches = pattern.findall(content)
    
    return matches




#
# read and parse interpro file and get ids
#
def parse_interpro():
    interpro_filename = '/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr_pfam.dat'
    fasta_filename = '/Volume/My Passport/ucl/MSc/uniref100.fasta'

    # Open the file and create a CSV reader object with tab delimiter
    with open(interpro_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            protein_id = row[0]
            
            # lookup fasta entry
        
            

def main():
    """
    Main function to run pre-training, fine-tuning, baseline or testing modes for a GAN model based on command line arguments.
    """
    print('***********************************************')
    print('    MSc Dissertation - Protein Embeddings      ')
    print('***********************************************')
    
    parse_interpro()
    #fasta_entry = extract_fasta('UniRef100_Q197F8', 'UniRef100')
    
    #print(fasta_entry)
    
    
    

if __name__ == '__main__':
    main()