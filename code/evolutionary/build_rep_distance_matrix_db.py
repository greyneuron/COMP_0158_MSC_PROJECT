import sys
import numpy as np
import glob
import csv
import os

### Usage
# python ./scripts/rep_distance_matrix/build_rep_distance_matrix.py /home/dbuchan/Data/pfam/ ./results_data/distance_matrix/pfam_rep_all_against_all/
###


def get_dom_list():
    dom_list = []
    for file in sorted(glob.glob(f'{sys.argv[1]}*_random')):
        # print(file[len(sys.argv[1]):])
        with open(file, "r", encoding="utf-8") as fhIn:
            for line in fhIn:
                if line.startswith(">"):
                    line = line[1:]
                    line = line.rstrip()
                    dom_list.append(line)
    return(dom_list)


def build_distance_matrix():
    # print(dom_list)
    dom_list = get_dom_list()
    similarity_matrix = np.empty((len(dom_list), len(dom_list)), dtype=float)
    
    # populate with values from file
    for file in sorted(glob.glob(f'{sys.argv[2]}*.csv')):
        print(file[len(sys.argv[2]):])
        with open(file, 'r') as pffile:
            reader = csv.reader(pffile, delimiter=',')
            next(reader)
            for row in reader:
                # try:
                x = dom_list.index(row[0])-1
                y = dom_list.index(row[1])-1
                # except Exception:
                #    continue
                # print(x, y)
                # print(row[2])
                similarity_matrix[x][y] = row[2]
        # break
    return similarity_matrix

similarity_matrix = None
if os.path.isfile("non-normalised_similarity_matrix.npy"):
    print("Reading in matrix")
    similarity_matrix = np.load("non-normalised_similarity_matrix.npy")
    # similarity_matrix = np.load("hmm_rep_distance_matrix.npy")
    # print(similarity_matrix)
    # read this npy
else:
    print("Building matrix")
    similarity_matrix = build_distance_matrix()
    print(similarity_matrix)
    with open("non-normalised_similarity_matrix.npy", "wb") as f:
        np.save(f, similarity_matrix)

# now scale/normalise to 0 and 1, flip and fill diagonal
np.fill_diagonal(similarity_matrix, (np.max(similarity_matrix)*1.2))
# print(np.min(similarity_matrix))
# print(np.max(similarity_matrix))
dom_list = get_dom_list()
normalized_similarity_matrix = (similarity_matrix-np.min(similarity_matrix))/(np.max(similarity_matrix)-np.min(similarity_matrix))
flipped_sim_matrix = 1.0 - normalized_similarity_matrix
# now save out distance matrix and dom_list
with open("hmm_rep_distance_matrix.npy", "wb") as f:
    np.save(f, flipped_sim_matrix)
    np.save(f, dom_list)