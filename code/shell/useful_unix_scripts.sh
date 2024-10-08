# find files of a certain size
find . -type f -size +2G -exec ls -lh {} + | awk '{ print $5, $9 }' | sort -h

find . -type f -name "pattern" -exec du -h {} +

find . -name "*mc8*model" -exec du -h {} +

# output the number of pfam entries in the corpus by pfam
awk '{ for (i = 1; i <= NF; i++) { if ($i ~ /PF[0-9]*/) { count[$i]++ } } } END { for (word in count) { print word, "|", count[word] } }' uniref100_e_corpus.dat | sort -k3,3nr



# recursively rename files to remove '0920' from the start of their name
find . -type f -name '0920*' | while read file; do new_name="$(dirname "$file")/$(basename "$file" | sed 's/^0920//')"; mv "$file" "$new_name"; done

# recursively rename files to rename from .model to _g50.model
find . -type f -name '*.model' | while read file; do new_name="$(dirname "$file")/$(basename "$file" | sed 's/\.model/_g50\.model/')"; mv "$file" "$new_name"; done

# rename files to have cbow or skip
find . -type f -name '*.model' | while read file; do new_name="$(dirname "$file")/$(basename "$file" | sed 's/_0_/_cbow_/')"; echo "$file" "$new_name"; done


find . -type f -name 'w2v*_1_*g50*' | while read file; do new_name="$(dirname "$file")/$(basename "$file" | sed 's/_1_/_skip_/')"; echo "$(basename "$file")" "-->" "$new_name"; done

find . -type f -name 'w2v*_1_*g50*' | while read file; do new_name="$(dirname "$file")/$(basename "$file" | sed 's/_1_/_skip_/')"; mv "$file" "$new_name"; done
find . -type f -name 'w2v*_0_*g50*' | while read file; do new_name="$(dirname "$file")/$(basename "$file" | sed 's/_0_/_cbow_/')"; mv "$file" "$new_name"; done


#
# -------------------------------- latex - replace pipe with ampersands for a table
#
#awk '{FS="|"}{print $1, "&", $3, "&" $4, "&" $5}' 202409250825_0910_g1_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g
awk '{FS="|"} { if ($3 == 2) print $1, "&", $3, "&" $4, "&" $5} ' 202409251819_0922_g100_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g
awk '{FS="|"} { if ($3 == 10) print $1, "&", $3, "&" $4, "&" $5} ' 202409251819_0922_g100_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g 
awk '{FS="|"} { if ($3 == 25) print $1, "&", $3, "&" $4, "&" $5} ' 202409251819_0922_g100_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g 
awk '{FS="|"} { if ($3 == 50) print $1, "&", $3, "&" $4, "&" $5} ' 202409251819_0922_g100_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g 
awk '{FS="|"} { if ($3 == 100) print $1, "&", $3, "&" $4, "&" $5} ' 202409251819_0922_g100_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g
awk '{FS="|"} { if ($3 == 150) print $1, "&", $3, "&" $4, "&" $5} ' 202409251819_0922_g100_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g
awk '{FS="|"} { if ($3 == 200) print $1, "&", $3, "&" $4, "&" $5} ' 202409251819_0922_g100_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g 
awk '{FS="|"} { if ($3 == 250) print $1, "&", $3, "&" $4, "&" $5} ' 202409251819_0922_g100_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g 


awk '{FS="|"} { if ($1 == 250) print $1, "&", $3, "&" $4, "&" $5} ' 202409251659_0920_g50_km_results.txt | sort -k7,7nr | sed 's/_/\\_/'g





#
# -------------------------------- ec2 stuff ---------------------------------------- 
#
# scp files from a local dir to a remote dir
scp -i "w2v_rsa_key_04" ../../../hpc/w2v_batch.py ec2-user@$dns:/word2vec/code


# copy all .gz files from a remote directory to the cbow directory
scp -i "w2v_rsa_key_04" ec2-user@$dns:'/word2vec/models/*.gz' cbow                                                           

# -----------------------------------------------------------------------------------



# find all .gz files in current directory and unzip them
find . -name "*gz" -exec gzip -d -v {} \;





# ---- send files to s3 from ec2
ssh to ec2
aws configure
aws s3 cp /data/dev/ucl/data/precorpus_78M_sql_extract.tar.gz s3://w2v-bucket/corpus/precorpus_78M_sql_extract.tar.gz


# print names of all models with various param configs - these all work
for mc in 1 3 5 8; do echo "hi $mc"; done
for mc in 1 3 5 8; do find . -name "*mc$mc*model"; done
for mc in 1 3 5 8; do find . -name "*mc$mc*model" | wc -l; done

for mc in 1 3 5 8; do for ws in 3 5 8 13 21 44; do echo "*mc$mc" w"$ws"; done; done
for mc in 1 3 5 8; do for ws in 3 5 8 13 21 44; do find . -name "*mc$mc*w$ws*model"; done; done
for mc in 1 3 5 8; do for ws in 3 5 8 13 21 44; do find . -name "*mc$mc*w$ws*model" | wc -l; done; done
for mc in 1 3 5 8; do for ws in 3 5 8 13 21 44; do echo "mc$mc" w"$ws" : ; find . -name "*mc$mc*w$ws*model" | wc -l; done; done



cd models/cbow
for mc in 1 3 5 8; do for ws in 3 5 8 13 21 44; do echo mc$mc_w$ws; grep "*mc$mc" 20240904_dist_matrix_mantel.txt | wc -l; done; done


find . -name "*gz" -exec gzip -d -v {} \;



# ***************** AWK ******************

# Counts total bytes of all files changed in November
ls -l | awk '$6 == "Nov" { sum += $5 }
             END { print sum }'

grep "dbname=" match_complete.xml | awk '{FS="dbname="}{print $2}' | awk '{print $1}' | sort |uniq -c


#
# grep a zip or gz but only output 10000 lines
#
zgrep . -m 10000 data/disordered/extra.xml.gz > data/disordered/extra.10000.xml

# ---------------------

#
# parse lines like this:
# A0A000	IPR015421	Pyridoxal phosphate-dependent transferase, major domain	G3DSA:3.40.640.10	48	288
# took 20mins to parse protein2ipr.dat for "^[A0A0-9]*A8KBH6"
#

SECONDS=0

filename="/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr.dat"
word="^[A0A0-9]*A8KBH6"

grep $word $filename

t=$SECONDS

printf 'Time taken: %d days, %d minutes\n' "$(( t/86400 ))" "$(( t/60 - 1440*(t/86400) ))"

# ----------------------------

#
# not sure if this works
#

# Define the filenames
proteins_file="/Users/patrick/dev/ucl/comp0158_mscproject/data/10_proteins.dat"
pfam_file="/Users/patrick/dev/ucl/comp0158_mscproject/data/protein2ipr_pfam.dat"

# Loop through each entry in the tokens file
while IFS= read -r token; do
    echo "Searching for: $token"
    # Use grep to find the entry in the search file
    grep -Hn "$token" "$pfam_file" | while IFS= read -r line; do
        echo "Protein: $token"
        echo "Line:" $line
    done
done < "$proteins_file"

# ----------------------------