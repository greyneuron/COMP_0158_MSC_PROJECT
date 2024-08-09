------------------------------------------------------------------
			 Installation Instructions
------------------------------------------------------------------

These are for a Macbook

- Conda
- Sqlite
- Various conda packages
- Python3
- Brew (for installation)

--- SQLite

- Database
% brew install sqlite

Test:
% sqlite3 to open a session
CTRL-D to exit that session



------------------------------------------------------------------
			 SQLite  - Database Instructions
------------------------------------------------------------------

% brew install sqlite

# open a session to check it works, CTRL-D to exit
% sqlite3


# Create a database
# Note I had to chmod 777 the directory for this to work

# From terminal
% sqlite3 /Users/patrick/dev/ucl/comp0158_mscproject/database/sqlite/W2V.db

# From Jupyter Notebook
- see database/sqlite_db_tools.ipynb


-----------------------------------------------------------------------------
			 Data Load - PROTEINS from Uniprot
-----------------------------------------------------------------------------
Download 	:	95272305 proteins 	:  	grep -c '>' uniref_100only_2759-95272305_0804.fasta
Conversion	:	95272305 lines		:	wc -l uniref100only_2759-95272305_20240805.dat
Database entry file used 			: uniref100only_2759-95272305_20240805.dat
SQLite		:	95272305 in			: W2V_PROTEIN_UREF100_E
				958565305 in 		: W2V_PROTEIN_UREF100_E2 *** DO NOT USE IMPORTED FROM SQLITE COMMAND LINE ***
DuckDB		:	95272305 in 		: W2V_PROTEIN_UREF100_E

Download from here: https://www.uniprot.org

- Select UniRef100
- Search for taxonomy 2759
- Also set percentage to 100%
- There should be 95,272,305 entries

- I saved locally, unzipped and saved as : uniref_100only_2759-95272305_0804.fasta
- Check number of entries:
% grep -c '>' uniref_100only_2759-95272305_0804.fasta
95272305

- Extract what we need:
- Run python code to convert to dat: parse_uniref_fasta_to_dat.py
- NB : Putting a count variable in helps enormously with joins later
output : uniref100only_2759-95272305_20240805.dat
% wc -l uniref100only_2759-95272305_20240805.dat
95272305

DuckDB
SELECT COUNT(*) FROM W2V_PROTEIN_UREF100_E
95272305 rows in table W2V_PROTEIN_UREF100_E

SQLite:
sqlite> select count(*) from W2V_PROTEIN_UREF100_E;
95272305


Output has: record_count, uniprot_id, len, start, end, n_members, tax_id, tax_name

Load into SQLite - 2 options

* Option 1 - From Python - Way slower than DuckDB
  See database/sqlite_db_tools.ipynb


* Option 2 - From command line - much quicker but stil
	- To connect from command line
	sqlite3 sqlite/W2V-SQLITE.db

	- To import from command line

First create your tables, then from command line
sqlite3 sqlite/W2V-SQLITE.db
.mode csv
.separator |
.import <csv file> <table name>

Example:
.import /Users/patrick/dev/ucl/comp0158_mscproject/data/protein/uniref100only_2759-95272305_20240805.dat W2V_PROTEIN_UREF100_E2

Select count gives 95,856,593 entries  - Hmm

HOWE

------------------------------------------------------------------
			 Data Load - PFAM ENTRIES from Interpro
------------------------------------------------------------------
Download	: 296017815 PFAM references in  protein2ipr.dat	:	grep -c '\tPF[0-9]*\t' /Volumes/My\ Passport/data/pfam/protein2ipr.dat

Conversion	: 296017815 lines in protein2ipr_pfam_20240715.dat 	: (wc -l protein2ipr_pfam_20240715.dat)
File to load into db : 	protein2ipr_pfam_20240715.dat

DuckDB		: 296,017,815 PFAM entries in W2V-TOKEN WHERE TYPE = PFAM
SQLLite 	: Not entered yet

Download from here: https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/
File : protein2ipr.dat.gz (19GB)


------------------------------------------------------------------
			 Data Load - Disorder entries
------------------------------------------------------------------
Download from here: https://ftp.ebi.ac.uk/pub/databases/interpro/current_release/
File : extra.xml (16GB - zipped)

This file has entries for all proteins and had to be split (chunk_disorder_xml.cpp). I did this in chunks of protein entries and created a separate xml file for each one.

Full file	: 230,397,847 instances of '<protein' 	: grep -c '<protein' /Volumes/My\ Passport/data/disorder/raw/extra.xml

Split files of 500000 proteins each : 
- This was done on AWS due to compute requirements but so was the .dat creation 

Converion to dat : disordered_tokens_20240719.dat
- This was also done on AWS
- The .dat file has 81,257,100 lines - each being a disprder region for any protein (not just eukaryotic)

extras_part_01.xml to extras_part_024.xml 

Reconciliation :
RAW	:	grep -c '<protein extra.xml		: 

SPLIT :
	grep -c '<protein extra01.xml 	: 500000 entries
	grep -c '<protein extra024.xml 	: 500000

CONVERTED:
	wc -l disordered_tokens_20240719.dat
	81257100

DUCKDB W2V_TOKEN WHERE TYPE='DISORDER'
	81257100


---------------------------------------------------------------------
	Data Load - Extracting tokens from DB for eukaryotic proteins
---------------------------------------------------------------------
Disorder and PFAM tokens are stored in the W2V_TOKEN table. As each token entry also has a uniprot_id, it is a
relatively simple matter to create a join with the protein table to get all tokens for the eukaryotic proteins.

I did this in chunks of 1M tokens and ouput to separate files e.g. uniref100_e_tokens_20240808_1.dat has the
tokens for the forsat 1M proteins in W2V_PROTEIN_UREF100_E. 

These are concatenated together (see concat_files.sh) into 

uniref100_e_tokens_20240808_ALL.dat


Code : 
- duckdb_dat_loader extract_eukaryotic_tokens()
- concat_files.sh
- final output : uniref100_e_tokens_20240808_ALL.dat

------------------------------------------------------------------
			 Data Load - Creating Pre-Corpus
------------------------------------------------------------------
The precorpus is simply a manipulation of uniref100_e_tokens_20240808_ALL.dat from the last step
to create a new file with a single line per protein containing all tokens for that protein. 

This is the precursor step to creating the actual corpus for word2vec

Combined token files with one line per token - basically concatenating via concat_files.sh
-------------------------------------
Example
A0A010PZJ8|493|DISORDER|Negative Polyelectrolyte|1|30
A0A010PZJ8|493|DISORDER|Consensus Disorder Prediction|1|32
A0A010PZJ8|493|DISORDER|Consensus Disorder Prediction|468|493
A0A010PZJ8|493|PFAM|PF01399|335|416

wc -l uniref100_e_tokens_20240808_ALL.dat
142908355

Combined file with one line per protein - essentially combining all tokens for a protein into a single line:
-------------------------------------
Example: A0A010PZJ8:493:4:1:3|DISORDER:1:30|DISORDER:1:32|DISORDER:468:493|PF01399:335:416
wc -l uniref100_e_tokens_20240808_ALL_COMBINED.dat
50249678

reconciliation:
142908355 lines processed in 256.3s. 50249678 lines written to /Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/tokens_combined/uniref100_e_tokens_20240808_ALL_COMBINED.dat


Details
input	:	uniref100_e_tokens_20240808_ALL.dat
output	:	uniref100_e_tokens_20240808_ALL_COMBINED.dat
code	: 	combine_e_protein_tokens.py


------------------------------------------------------------------
			 Data Load - Creating Corpus
------------------------------------------------------------------
THis uses uniref100_e_tokens_20240808_ALL_COMBINED.dat to create a sentence per protein. This means:
- Remiving overlaps
- Removing lines with no pfam entries
- Removing lines with no entries at all

Details
input	:	uniref100_e_tokens_20240808_ALL_COMBINED.dat
output	:	uniref100_e_corpus_20240808.txt
			uniref100_e_corpus_20240808_ignored.txt (for proteins with no pfam entries)
code	: 	create_corpus.py


Stats:
- input file: 	uniref100_e_tokens_20240808_ALL_COMBINED.dat	:	50249678 lines
- output	:	uniref100_e_corpus_20240808.txt					:	45909435 lines
				uniref100_e_corpus_20240808_ignored.txt			: 	 4340243 lines
- Corpus created in 232.38s


------------------------------------------------------------------
			 Creating Models
------------------------------------------------------------------