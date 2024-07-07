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
