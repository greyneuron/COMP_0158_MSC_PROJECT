# COMP_0158_MSC_PROJECT

Download rawdata
> From Interpro : protein2ipr.dat - contains domains
> From uniref : uniref90 : contains fasta protein amino chains

Interpo Sample:
A0A001  IPR036640       ABC transporter type 1, transmembrane domain superfamily        G3DSA:1.20.1560.10      1       301

Uniref fasta:
LLVSYSLRMVDGTIPLEVVMTFSETADVSTADPSTITLISGMGVSSNNSILTLSSATKVT


-- Unix commands --
- Count lines in unix: wc -l <filename>
- AWK to extract 1st and 4th token if tab deliiited : awk  'BEGIN{FS="\t"} {print $1, $4}' data/protein2ipr.dat | grep "PF"
- Extract only pfam entries: grep 'PF[0-9]*' data/protein2ipr.dat > data/protein2ipr_pfam.dat

- Extract only proteins of unknown function : grep 'Protein of unknown' data/protein2ipr_pfam.dat > data/protein2ipr_pfam_puf.dat
- Extract only domains of unknown function : grep 'Domain of unknown' data/protein2ipr_pfam.dat > data/protein2ipr_pfam_duf.dat
- Only entries with pfam ids but witout duf or puf : grep -v 'of unknown function' protein2ipr_pfam.dat > protein2ipr_pfam_no_uf.dat

wc -l data/uniref90.fasta 
 1380493376 data/uniref90.fasta

 1,380,493,376


wc -l data/protein2ipr.dat
 1355591115 data/protein2ipr.dat
1,355,591,115



Using awk: 



-- Protein of unknown function
grep 'Protein of unknown' data/protein2ipr_pfam.dat > data/protein2ipr_pfam_puf.dat

Instructions
1. Download and unzip interpro file
2. Open a unix prompt at the file location
3. Extract only pfam entries: 
    grep 'PF[0-9]*' data/protein2ipr.dat > data/protein2ipr_pfam.dat
4. TODO : Get disordered entries
5. Extract protein ids (first column) into a separate file of ids:
    awk 'BEGIN{FS="\t"} {print $1}' protein2ipr_pfam.dat > pfam_protein_ids.dat
6. Loop through these ids to get the entries from the fasta file
    - Do this in python

