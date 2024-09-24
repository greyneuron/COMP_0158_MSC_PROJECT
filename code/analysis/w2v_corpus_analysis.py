import w2v_clan_utils
from collections import defaultdict
import time

corpus_file ='/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/corpus_validation_sep/uniref_e_corpus_mutlipfamlines.dat'
model_dir   ="/Users/patrick/dev/ucl/word2vec/comp_0158_msc_project/data/models_validation_sep/"
model_name  = 'w2v_20240911_sg1_mc1_w3_v25'
model_path  = model_dir+model_name+'.model'


# Initialize dictionaries to store counts
before_count = defaultdict(lambda: defaultdict(int))
after_count = defaultdict(lambda: defaultdict(int))
beside_count = defaultdict(lambda: defaultdict(int))

s = time.time()
#
# ----------- utility to parse a line
#
def process_line(line, word_set):
    words = line.split()  # Tokenize the sentence into words
    for i, word1 in enumerate(words):
        if word1 not in word_set:
            continue
        for j, word2 in enumerate(words):
            if word2 not in word_set or i == j:
                continue
            # Count before: if word1 appears before word2
            if i < j:
                before_count[word1][word2] += 1
            # Count after: if word1 appears after word2
            if i > j:
                after_count[word1][word2] += 1
            # Count beside: if word1 and word2 are beside each other
            if abs(i - j) == 1:
                beside_count[word1][word2] += 1
                

# -----------------------------------------------------------------------------
# get list of words and convert to set
pfams = w2v_clan_utils.get_pfam_vocab(model_path)
print(f"Processing {len(pfams)} words")
word_set = set(pfams)

# -----------------------------------------------------------------------------
print(f"Processing lines")
i = 0
with open(corpus_file, 'r') as file:
    for line in file:
        line.strip()
        process_line(line, word_set)
        if i% 10000000 ==0:
            print(f"{i} lines processed")
        i+=1

e = time.time()
print(f"Lines processed in {round(e-s,2)}s. Interpreting...")
# Output the results (example for printing word1 -> word2 relationships)
print(f" A | B | A_BEFORE_B | A_AFTER_B | A_BESIDE_B")
for word1 in word_set:
    for word2 in word_set:
        if word1 != word2:
            print(f"{word1} | {word2} | {before_count[word1][word2]} | {after_count[word1][word2]} | {beside_count[word1][word2]}")
            #print(f"before | {word1} | {word2} | {before_count[word1][word2]}")
            #print(f"after | {word1} | {word2} | {after_count[word1][word2]}")
            #print(f"beside | {word1} | {word2} | {beside_count[word1][word2]}")

e2 = time.time()
print(f"Total time : {round(e2-s,2)}s")
