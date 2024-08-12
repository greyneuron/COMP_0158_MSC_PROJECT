#!/bin/bash

# File containing the list of words (one per line)
words_to_search="/Users/patrick/dev/ucl/comp0158_mscproject/data/analysis/w2v_20240810_v5_w2_missing_pfams.txt"

# File in which to search for the words
search_file="/Users/patrick/dev/ucl/comp0158_mscproject/data/corpus/uniref100_e_corpus_20240810.txt"

# Loop through each word in the words file
echo "Searching for words without vectors - are they in the corpus?"

# Check if both files exist
if [[ ! -f "$words_to_search" ]]; then
  echo "Missing words file '$words_to_search' does not exist."
  exit 1
fi

if [[ ! -f "$search_file" ]]; then
  echo "Corpus file '$search_file' does not exist."
  exit 1
fi


while IFS= read -r word; do
  # Use grep to search for the word in the search file
  #grep -n -m 1 -w "$word" "$search_file" | sed -e 's/ /[SPACE]/g' -e 's/\t/[TAB]/g' -e 's/\n/[NL]/g'

  # this outputs how many times a pfam word that is not in the w2v vocab appeaars in the corpus file

  #echo $word grep -c -w "$word" "$search_file"

  count=$(grep -o -w "$word" "$search_file" | wc -l)
  echo "$word,$count"

done < "$words_to_search"
