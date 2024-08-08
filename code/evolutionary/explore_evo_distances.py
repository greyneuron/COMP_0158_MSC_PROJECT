import numpy as np
import pickle

evo_npy_file = "/Users/patrick/dev/ucl/comp0158_mscproject/code/evolutionary/pfam_rep_distance_matrix.npy"
evo_pfam_ids_out = "/Users/patrick/dev/ucl/comp0158_mscproject/code/evolutionary/evo_pfam_ids.dat"
#
#  just to let me explore the distances in the evolutionary matrix
#

    
def read_evo_files(evo_npy_file):
    #dist_matrix = np.load(evo_file)
    #dom_list = np.load(evo_file)
    #other_thing = np.load(evo_file)

    #print(f"PFAM {dom_list}")
    #print(f"Matrix shape: {dist_matrix.shape}")
    #print(f"Other thing {other_thing}")
    
    with open(evo_npy_file, 'rb') as f:
        distance_matrix = np.load(f)
        pfam_vector_file = np.load(f)
    
    return distance_matrix, pfam_vector_file


def parse_pfam_list(pfam_vector):
    print(f"{len(pfam_vector)}")
    
    of = open(evo_pfam_ids_out, "w")
    
    counter = 0
    for i in range (len(pfam_vector)):
        line = pfam_vector[i]
        tokens = line.split('|')
        pfam_id = tokens[1]
        pfam_id = pfam_id.rstrip()
        pfam_id = pfam_id.lstrip()
        buffer = "|".join([str(counter), pfam_id])
        of.write(buffer + '\n')
        #print(buffer)
        counter+=1
    of.close()




#read_evo_matrix()
distance_matrix, pfam_vector = read_evo_files(evo_npy_file)
parse_pfam_list(pfam_vector)